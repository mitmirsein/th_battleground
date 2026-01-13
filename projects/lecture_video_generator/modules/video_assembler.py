"""
Video Assembler - FFmpeg로 슬라이드 + 오디오 → MP4 영상 조립

Usage:
    from modules.video_assembler import VideoAssembler
    
    assembler = VideoAssembler()
    final_video = assembler.assemble(
        slides_dir="output/lecture/",
        audio_dir="output/lecture/",
        output_file="output/lecture/final.mp4"
    )
"""
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_DIR


@dataclass
class VideoSegment:
    """영상 세그먼트"""
    slide_path: str
    audio_path: str
    output_path: str
    duration: float = 0.0


class VideoAssembler:
    """FFmpeg 영상 조립"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """FFmpeg 설치 확인"""
        try:
            result = subprocess.run(
                [self.ffmpeg, "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError("FFmpeg not working properly")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Install with: brew install ffmpeg"
            )
    
    def get_audio_duration(self, audio_path: str) -> float:
        """오디오 파일 길이 조회 (초)"""
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "json", audio_path
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
        return 0.0
    
    def create_segment(
        self,
        slide_path: str,
        audio_path: str,
        output_path: str,
        end_padding: float = 2.0  # 슬라이드 전환용 패딩 (초)
    ) -> bool:
        """단일 세그먼트 생성 (슬라이드 + 오디오 + 전환 패딩)"""
        # 오디오 끝에 패딩 추가하는 필터
        audio_filter = f"apad=pad_dur={end_padding}"
        
        cmd = [
            self.ffmpeg,
            "-y",  # 덮어쓰기
            "-loop", "1",  # 이미지 반복
            "-i", slide_path,  # 슬라이드 이미지
            "-i", audio_path,  # 오디오
            "-af", audio_filter,  # 오디오 끝에 2초 패딩
            "-c:v", "libx264",
            "-preset", "ultrafast",  # 빠른 인코딩
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",  # 오디오 길이에 맞춤
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    def _create_segment_task(self, args) -> Tuple[int, str, bool, float]:
        """병렬 처리용 세그먼트 생성 태스크 (청킹된 오디오 지원)"""
        idx, slide, audios, output = args  # audios는 리스트
        
        # 여러 오디오 파일이면 먼저 병합
        if len(audios) > 1:
            merged_audio = output.parent / f"merged_audio_{idx:02d}.wav"
            concat_success = self._concat_audio_files(audios, str(merged_audio))
            if not concat_success:
                return (idx, str(output), False, 0.0)
            audio_file = str(merged_audio)
        else:
            audio_file = str(audios[0])
        
        duration = self.get_audio_duration(audio_file)
        success = self.create_segment(str(slide), audio_file, str(output))
        
        # 임시 병합 오디오 정리
        if len(audios) > 1:
            Path(audio_file).unlink(missing_ok=True)
        
        return (idx, str(output), success, duration)
    
    def _concat_audio_files(self, audio_files: List[Path], output_path: str) -> bool:
        """여러 오디오 파일 병합"""
        concat_file = Path(output_path).parent / "audio_concat_list.txt"
        
        with open(concat_file, "w") as f:
            for audio in audio_files:
                abs_path = Path(audio).absolute()
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            self.ffmpeg,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if concat_file.exists():
            concat_file.unlink()
        
        return result.returncode == 0
    
    def concat_segments_with_fade(
        self,
        segment_paths: List[str],
        output_path: str,
        fade_duration: float = 1.0
    ) -> bool:
        """세그먼트들을 페이드 효과와 함께 병합 (xfade)"""
        if len(segment_paths) < 2:
            # 하나뿐이면 그냥 복사
            return self.concat_segments(segment_paths, output_path)
            
        inputs = []
        filter_complex = []
        
        # 현재 누적 오프셋 (첫 영상은 0부터 시작)
        offset = 0.0
        
        # 첫 번째 영상 입력
        inputs.append("-i")
        inputs.append(segment_paths[0])
        
        # 첫 영상 길이
        duration = self.get_audio_duration(segment_paths[0])
        
        # 누적 오프셋 업데이트 (영상 길이 - 페이드 시간)
        # 예: 10초 영상, 1초 페이드 → 다음 영상은 9초에 시작
        offset += duration - fade_duration
        
        # 필터 체인 구성
        # [0][1]xfade=...[v1]; [v1][2]xfade=...[v2]...
        last_stream = "0"
        
        for i in range(1, len(segment_paths)):
            # 입력 추가
            inputs.append("-i")
            inputs.append(segment_paths[i])
            
            next_stream = f"v{i}"
            if i == len(segment_paths) - 1:
                next_stream = "v_out" # 마지막 비디오 스트림 이름
            
            # xfade 필터 (비디오)
            # transition=fade:duration=1:offset=9
            filter_complex.append(
                f"[{last_stream}][{i}:v]xfade=transition=fade:duration={fade_duration}:offset={offset:.3f}[{next_stream}]"
            )
            
            # 오디오 크로스페이드 (acrossfade)
            # [0:a][1:a]acrossfade=d=1:c1=tri:c2=tri[a1]; [a1][2:a]acrossfade...
            # 오디오는 별도 처리가 복잡하므로 간단히 mix 또는 concat 사용 권장되나
            # 여기서는 concat 필터를 사용해 오디오는 컷 전환 (보통 음성은 공백이 있어 자연스러움)
            # 또는 믹싱을 해야 함.
            # 영상 싱크를 위해 오디오도 offset에 맞춰 믹싱하는게 정석이나, 
            # FFmpeg 명령어가 너무 길어질 수 있음.
            
            # 다음 오프셋 계산
            dur = self.get_audio_duration(segment_paths[i])
            offset += dur - fade_duration
            
            last_stream = next_stream

        # 오디오 처리를 위한 단순 concat (페이드 없이 이어붙임 - 대사 겹침 방지)
        # 하지만 비디오가 겹치므로(fade duration 만큼), 오디오도 겹쳐야 싱크가 맞음.
        # 따라서 오디오도 acrossfade 필요.
        
        # 오디오 필터 체인 재구성
        a_last_stream = "0:a"
        a_filter_complex = []
        
        for i in range(1, len(segment_paths)):
            a_next_stream = f"a{i}"
            if i == len(segment_paths) - 1:
                a_next_stream = "a_out"
                
            a_filter_complex.append(
                f"[{a_last_stream}][{i}:a]acrossfade=d={fade_duration}:c1=tri:c2=tri[{a_next_stream}]"
            )
            a_last_stream = a_next_stream
            
        full_filter = ";".join(filter_complex + a_filter_complex)
        
        cmd = [
            self.ffmpeg,
            "-y",
            *inputs,
            "-filter_complex", full_filter,
            "-map", "[v_out]",
            "-map", "[a_out]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        
        # 명령어가 너무 길 경우 파일로 저장해서 실행하는 방법은 filter_complex_script 사용
        # 여기서는 직접 실행 시도
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ xfade 실패, 단순 병합으로 전환: {result.stderr[-200:]}")
                return self.concat_segments(segment_paths, output_path)
            return True
        except OSError:
            print("⚠️ 명령어 길이 초과 등 오류, 단순 병합으로 전환")
            return self.concat_segments(segment_paths, output_path)

    def concat_segments(
        self,
        segment_paths: List[str],
        output_path: str
    ) -> bool:
        """세그먼트들을 하나로 병합 (단순 concat)"""
        # concat 리스트 파일 생성
        concat_file = Path(output_path).parent / "concat_list.txt"
        
        with open(concat_file, "w") as f:
            for seg in segment_paths:
                # 절대 경로 사용
                abs_path = Path(seg).absolute()
                f.write(f"file '{abs_path}'\n")
        
        cmd = [
            self.ffmpeg,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 임시 파일 정리
        if concat_file.exists():
            concat_file.unlink()
        
        return result.returncode == 0
    
    def assemble(
        self,
        slides_dir: str,
        audio_dir: str = None,
        output_file: str = None,
        cleanup_segments: bool = True,
        parallel_workers: int = 4,
        use_fade: bool = True,
        fade_duration: float = 1.0
    ) -> Optional[str]:
        """전체 영상 조립 (병렬 처리)"""
        from concurrent.futures import ThreadPoolExecutor
        
        slides_path = Path(slides_dir)
        audio_path = Path(audio_dir or slides_dir)
        
        # 슬라이드 파일 찾기 (PNG)
        slide_files = sorted(slides_path.glob("slide_*.png"))
        if not slide_files:
            print("❌ 슬라이드 파일을 찾을 수 없습니다 (slide_*.png)")
            return None
        
        # 오디오 파일 찾기 (WAV)
        audio_files = sorted(audio_path.glob("audio_*.wav"))
        if not audio_files:
            print("❌ 오디오 파일을 찾을 수 없습니다 (audio_*.wav)")
            return None
        
        # 매칭
        pairs = self._match_files(slide_files, audio_files)
        if not pairs:
            print("❌ 슬라이드-오디오 매칭 실패")
            return None
        
        print(f"📊 매칭된 쌍: {len(pairs)}개")
        print(f"🚀 병렬 처리: {parallel_workers} workers")
        
        # 세그먼트 디렉토리 생성
        segment_dir = slides_path / "segments"
        segment_dir.mkdir(exist_ok=True)
        
        # 태스크 준비
        tasks = []
        for i, (slide, audio) in enumerate(pairs, 1):
            segment_file = segment_dir / f"segment_{i:02d}.mp4"
            tasks.append((i, slide, audio, segment_file))
        
        # 병렬 세그먼트 생성
        print(f"   🎬 세그먼트 생성 중...")
        segments = []
        
        with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
            results = list(executor.map(self._create_segment_task, tasks))
        
        # 결과 정렬 및 출력
        for idx, output, success, duration in sorted(results):
            if success:
                print(f"      ✅ 세그먼트 {idx}: {duration:.0f}초")
                segments.append(output)
            else:
                print(f"      ❌ 세그먼트 {idx}")
        
        if not segments:
            print("❌ 세그먼트 생성 실패")
            return None
        
        # 병합
        output = output_file or str(slides_path / "final.mp4")
        
        if use_fade:
            print(f"\n🔗 세그먼트 병합 중 (Fade: {fade_duration}s)...")
            success = self.concat_segments_with_fade(segments, output, fade_duration)
        else:
            print(f"\n🔗 세그먼트 병합 중 (컷 전환)...")
            success = self.concat_segments(segments, output)
        
        if success:
            # 세그먼트 정리
            if cleanup_segments:
                for seg in segments:
                    Path(seg).unlink()
                segment_dir.rmdir()
            
            # 최종 영상 정보
            total_duration = self.get_audio_duration(output)
            print(f"✅ 최종 영상: {output}")
            print(f"   길이: {total_duration / 60:.1f}분")
            
            return output
        else:
            print("❌ 병합 실패")
            return None
    
    def _match_files(
        self,
        slides: List[Path],
        audios: List[Path]
    ) -> List[Tuple[Path, List[Path]]]:
        """슬라이드-오디오 매칭 (청킹된 오디오 지원)"""
        import re
        
        # 슬라이드 번호 추출
        slide_dict = {}
        for s in slides:
            # slide_01.png → 01
            match = s.stem.split("_")[-1]
            if match.isdigit():
                slide_dict[int(match)] = s
        
        # 오디오 번호 추출 (청킹 지원: audio_01.wav, audio_01-1.wav, audio_01-2.wav)
        audio_dict = {}  # {섹션번호: [오디오파일들]}
        for a in audios:
            # audio_01.wav → 01, audio_01-1.wav → 01
            stem = a.stem  # "audio_01" or "audio_01-1"
            match = re.match(r'audio_(\d+)(?:-\d+)?$', stem)
            if match:
                section_num = int(match.group(1))
                if section_num not in audio_dict:
                    audio_dict[section_num] = []
                audio_dict[section_num].append(a)
        
        # 오디오 정렬 (audio_01-1, audio_01-2 순서)
        for section_num in audio_dict:
            audio_dict[section_num] = sorted(audio_dict[section_num])
        
        # 공통 번호 매칭
        pairs = []
        common_nums = set(slide_dict.keys()) & set(audio_dict.keys())
        
        for num in sorted(common_nums):
            pairs.append((slide_dict[num], audio_dict[num]))
        
        return pairs


def main():
    """테스트"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_assembler.py <output_dir>")
        sys.exit(1)
    
    assembler = VideoAssembler()
    result = assembler.assemble(sys.argv[1])
    
    if result:
        print(f"\n🎉 영상 생성 완료: {result}")
    else:
        print("\n❌ 영상 생성 실패")


if __name__ == "__main__":
    main()
