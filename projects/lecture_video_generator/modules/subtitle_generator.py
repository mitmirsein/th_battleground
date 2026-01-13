"""
Subtitle Generator - TTS 텍스트 + 오디오 길이 기반 SRT 자막 생성

Usage:
    from modules.subtitle_generator import SubtitleGenerator
    
    generator = SubtitleGenerator()
    generator.generate(
        tts_dir="output/7-2/",
        audio_dir="output/7-2/",
        output_path="output/7-2/final.srt"
    )
"""
import re
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class SubtitleEntry:
    """자막 항목"""
    index: int
    start_time: float  # 초
    end_time: float    # 초
    text: str


class SubtitleGenerator:
    """SRT 자막 생성기"""
    
    def __init__(self, max_chars_per_line: int = 30, max_lines: int = 2):
        self.max_chars_per_line = max_chars_per_line
        self.max_lines = max_lines
    
    def generate(
        self,
        tts_dir: str,
        audio_dir: str = None,
        output_path: str = None,
        padding: float = 2.0,
        transition_overlap: float = 0.0
    ) -> str:
        """자막 파일 생성"""
        tts_path = Path(tts_dir)
        audio_path = Path(audio_dir or tts_dir)
        output_file = output_path or str(tts_path / "final.srt")
        
        # TTS 텍스트 파일 찾기
        tts_files = sorted(tts_path.glob("tts_*.txt"))
        if not tts_files:
            print("❌ TTS 텍스트 파일을 찾을 수 없습니다")
            return None
        
        # 오디오 파일 찾기 및 길이 계산
        audio_durations = self._get_audio_durations(audio_path)
        
        print(f"📝 자막 생성 시작")
        print(f"   TTS 파일: {len(tts_files)}개")
        print(f"   오디오 파일: {len(audio_durations)}개")
        
        all_entries = []
        current_time = 0.0
        entry_index = 1
        
        for tts_file in tts_files:
            # 섹션 번호 추출 (tts_01.txt → 1)
            section_num = int(tts_file.stem.split("_")[1])
            
            # 해당 섹션의 오디오 길이 합산
            section_duration = sum(
                dur for num, dur in audio_durations 
                if num == section_num
            )
            
            if section_duration == 0:
                print(f"   ⚠️ 섹션 {section_num}: 오디오 없음, 스킵")
                continue
            
            # 텍스트 읽기
            text = tts_file.read_text(encoding="utf-8").strip()
            
            # 문장 분할
            sentences = self._split_sentences(text)
            
            # 문장별 시간 할당 (문장 길이 비례)
            total_chars = sum(len(s) for s in sentences)
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                # 시간 할당 (문장 길이 비례)
                sentence_duration = (len(sentence) / total_chars) * section_duration
                
                # 문장 길이별 자막 분할 처리
                # 문장이 너무 길면(2줄 초과) 여러 자막 블록으로 나눔
                subtitle_chunks = self._process_long_sentence(sentence, self.max_chars_per_line, self.max_lines)
                
                # 청크별 시간 배분
                chunk_total_chars = sum(len(c) for c in subtitle_chunks)
                
                for chunk_text in subtitle_chunks:
                    # 청크 시간 할당
                    # 마지막 청크는 남은 시간 모두 할당하여 오차 보정 가능하지만, 
                    # 여기서는 글자수 비례로 단순 배분
                    chunk_duration = (len(chunk_text.replace("\n", "")) / chunk_total_chars) * sentence_duration if chunk_total_chars > 0 else 0
                    
                    entry = SubtitleEntry(
                        index=entry_index,
                        start_time=current_time,
                        end_time=current_time + chunk_duration,
                        text=chunk_text
                    )
                    all_entries.append(entry)
                    
                    current_time += chunk_duration
                    entry_index += 1
            
            # 섹션 간 패딩 및 전환 겹침 보정
            # 영상 조립 시 2초 패딩 후 overlap만큼 겹쳐짐
            # 실질적인 간격 = padding - transition_overlap
            effective_gap = padding - transition_overlap
            current_time += max(0.0, effective_gap)
        
        # SRT 파일 작성
        srt_content = self._format_srt(all_entries)
        Path(output_file).write_text(srt_content, encoding="utf-8")
        
        print(f"✅ 자막 생성 완료: {output_file}")
        print(f"   총 자막 수: {len(all_entries)}개")
        
        return output_file
    
    def _get_audio_durations(self, audio_path: Path) -> List[Tuple[int, float]]:
        """오디오 파일 길이 조회 [(섹션번호, 길이), ...]"""
        durations = []
        
        for audio_file in sorted(audio_path.glob("audio_*.wav")):
            # audio_01.wav → 1, audio_01-1.wav → 1
            stem = audio_file.stem
            match = re.match(r'audio_(\d+)(?:-\d+)?$', stem)
            if match:
                section_num = int(match.group(1))
                duration = self._get_duration(str(audio_file))
                durations.append((section_num, duration))
        
        return durations
    
    def _get_duration(self, audio_path: str) -> float:
        """ffprobe로 오디오 길이 조회"""
        try:
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
        except Exception:
            pass
        return 0.0
    
    def _split_sentences(self, text: str) -> List[str]:
        """문장 단위 분할 (개선된 로직)"""
        # 0. 줄바꿈 기준 1차 분할 (문단/제목 분리)
        lines = text.split('\n')
        
        final_sentences = []
        
        # 1. 각 줄에 대해 문장 분할 수행
        pattern = r'([.!?]\s+|니다\.\s*|니까\?\s*|세요\.\s*)'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parts = re.split(pattern, line)
            
            candidates = []
            current = ""
            for part in parts:
                current += part
                # 분리 패턴이 포함된 경우 후보군에 추가
                if re.search(pattern, part) or part == parts[-1]:
                    candidates.append(current.strip())
                    current = ""
            
            if current:
                candidates.append(current.strip())
            
            # 2. 문맥 기반 병합 (괄호, 이니셜 등 처리)
            merged = self._merge_incomplete_sentences(candidates)
            final_sentences.extend(merged)
            
        return final_sentences

    def _merge_incomplete_sentences(self, candidates: List[str]) -> List[str]:
        """불완전한 문장 병합 (괄호, 약어 등 고려)"""
        if not candidates:
            return []
            
        merged = []
        buffer = ""
        
        for cand in candidates:
            if not cand:
                continue
                
            if buffer:
                buffer += " " + cand
            else:
                buffer = cand
            
            # 병합 조건 검사
            # 1. 괄호 불일치 (열린게 더 많음)
            if buffer.count('(') > buffer.count(')'):
                continue
            
            # 2. 이니셜/약어 끝남 (예: "F.", "W.", "U.S.")
            # 조건: 마침표로 끝나고, 그 앞이 대문자 알파벳 1개인 경우 (단어 경계 고려)
            if re.search(r'(^|\s)[A-Z]\.$', buffer):
                continue
                
            # 문장 완성으로 판단
            merged.append(buffer)
            buffer = ""
            
        # 남은 버퍼 처리
        if buffer:
            merged.append(buffer)
            
        return merged
    
    def _process_long_sentence(self, text: str, max_chars: int, max_lines: int) -> List[str]:
        """긴 문장을 여러 자막 블록으로 분할"""
        words = text.split()
        chunks = []
        current_chunk_lines = []
        current_line = ""
        
        for word in words:
            # 현재 줄에 단어 추가 가능한지 확인
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " + word if current_line else word)
            else:
                # 줄 꽉 참 -> 줄 추가
                if current_line:
                    current_chunk_lines.append(current_line)
                current_line = word
                
                # 블록(2줄) 꽉 참 -> 블록 완성 및 초기화
                if len(current_chunk_lines) >= max_lines:
                    chunks.append("\n".join(current_chunk_lines))
                    current_chunk_lines = []
        
        # 남은 줄 처리
        if current_line:
            current_chunk_lines.append(current_line)
        
        # 남은 블록 처리
        if current_chunk_lines:
            chunks.append("\n".join(current_chunk_lines))
            
        return chunks

    def _wrap_text(self, text: str) -> List[str]:
        """(Deprecated via _process_long_sentence) 단순 줄바꿈만 수행"""
        # 하위 호환성 유지용, 내부 로직은 _process_long_sentence와 유사하나 리스트 반환
        return self._process_long_sentence(text, self.max_chars_per_line, self.max_lines)[0].split("\n")
    
    def _format_srt(self, entries: List[SubtitleEntry]) -> str:
        """SRT 형식으로 포맷팅"""
        srt_lines = []
        
        for entry in entries:
            start = self._format_time(entry.start_time)
            end = self._format_time(entry.end_time)
            
            srt_lines.append(str(entry.index))
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(entry.text)
            srt_lines.append("")  # 빈 줄
        
        return "\n".join(srt_lines)
    
    def _format_time(self, seconds: float) -> str:
        """초 → SRT 시간 형식 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    """테스트"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python subtitle_generator.py <output_dir>")
        sys.exit(1)
    
    generator = SubtitleGenerator()
    result = generator.generate(sys.argv[1])
    
    if result:
        print(f"\n🎉 자막 생성 완료: {result}")


if __name__ == "__main__":
    main()
