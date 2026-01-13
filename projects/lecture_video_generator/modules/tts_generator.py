"""
TTS Generator - Gemini API로 음성 생성 (google-genai SDK)

Usage:
    from modules.tts_generator import TTSGenerator
    
    generator = TTSGenerator()
    audio_files = generator.generate_for_lecture(lecture)
"""
import sys
import time
import struct
import mimetypes
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GOOGLE_API_KEY, TTS_MODEL, TTS_VOICE, OUTPUT_DIR
from modules.tts_preprocessor import TTSPreprocessor


@dataclass
class TTSResult:
    """TTS 결과"""
    section_num: int
    audio_path: str
    text: str
    duration_estimate: float


class TTSGenerator:
    """Gemini TTS 음성 생성기 (google-genai SDK)"""
    
    def __init__(self, api_key: str = None, voice: str = None):
        self.api_key = api_key or GOOGLE_API_KEY
        self.voice = voice or TTS_VOICE
        self.model = TTS_MODEL
        self.preprocessor = TTSPreprocessor()
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of GenAI client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not set. Check .env file.")
            
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        
        return self._client
    
    def generate(self, text: str, output_path: str) -> bool:
        """단일 텍스트 TTS 생성 (스트리밍)"""
        try:
            from google.genai import types
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=text)],
                )
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=self.voice
                        )
                    )
                ),
            )
            
            # 스트리밍으로 오디오 수신
            audio_data = b""
            mime_type = None
            
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                    
                part = chunk.candidates[0].content.parts[0]
                if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                    audio_data += part.inline_data.data
                    if mime_type is None:
                        mime_type = part.inline_data.mime_type
            
            if audio_data:
                # WAV 변환
                wav_data = self._convert_to_wav(audio_data, mime_type or "audio/L16;rate=24000")
                
                with open(output_path, "wb") as f:
                    f.write(wav_data)
                
                # 정적(Silence) 제거 (FFmpeg)
                self._trim_silence(output_path)
                return True
            
            print(f"⚠️ 오디오 데이터를 찾을 수 없습니다")
            return False
                
        except Exception as e:
            print(f"❌ TTS 생성 실패: {e}")
            return False
    
    def _convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Raw PCM 데이터를 WAV로 변환"""
        # MIME 타입에서 파라미터 추출
        bits_per_sample = 16
        sample_rate = 24000
        
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    sample_rate = int(param.split("=", 1)[1])
                except (ValueError, IndexError):
                    pass
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass
        
        # WAV 헤더 생성
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size
        
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            chunk_size,
            b"WAVE",
            b"fmt ",
            16,
            1,
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_size
        )
        
        return header + audio_data
    
    def _trim_silence(self, audio_path: str):
        """FFmpeg로 오디오 끝부분 침묵 제거"""
        try:
            import subprocess
            
            trimmed_path = audio_path.replace(".wav", "_trimmed.wav")
            
            # silenceremove 필터: 끝부분의 침묵(-30dB 이하) 제거
            cmd = [
                "ffmpeg", "-y", "-v", "quiet",
                "-i", audio_path,
                "-af", "silenceremove=stop_periods=-1:stop_duration=1:stop_threshold=-30dB",
                trimmed_path
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0 and Path(trimmed_path).exists():
                # 원본 교체
                Path(trimmed_path).replace(audio_path)
                # print(f"      ✂️ 침묵 제거 완료")
        except Exception as e:
            print(f"      ⚠️ 침묵 제거 실패: {e}")

    def generate_for_section(
        self,
        section,
        output_dir: str,
        preprocess: bool = True,
        max_chunk_chars: int = 2000
    ) -> List[TTSResult]:
        """섹션별 TTS 생성 (긴 텍스트는 청킹)"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 텍스트 전처리
        text = section.content
        if preprocess:
            text = self.preprocessor.process(text)
        
        # 텍스트 청킹
        chunks = self.preprocessor.split_for_tts(text, max_chars=max_chunk_chars)
        
        print(f"   🔊 섹션 {section.number}: {section.title}")
        print(f"      텍스트 길이: {len(text)}자 → {len(chunks)}개 청크")
        
        results = []
        
        for chunk_idx, chunk in enumerate(chunks):
            duration_estimate = self.preprocessor.estimate_duration(chunk)
            
            # 청크가 1개면 기존 방식, 여러 개면 섹션-청크 번호
            if len(chunks) == 1:
                audio_file = output_path / f"audio_{section.number:02d}.wav"
                file_label = audio_file.name
            else:
                audio_file = output_path / f"audio_{section.number:02d}-{chunk_idx+1}.wav"
                file_label = f"{audio_file.name} ({len(chunk)}자, ~{duration_estimate:.0f}초)"
            
            print(f"      청크 {chunk_idx+1}/{len(chunks)}: {len(chunk)}자, 예상: {duration_estimate:.0f}초...", end=" ")
            
            # TTS 생성
            success = self.generate(chunk, str(audio_file))
            
            if success:
                print("✅")
                results.append(TTSResult(
                    section_num=section.number,
                    audio_path=str(audio_file),
                    text=chunk,
                    duration_estimate=duration_estimate
                ))
            else:
                print("❌")
        
        return results
    
    def _generate_section_task(self, args) -> List[TTSResult]:
        """병렬 처리용 섹션 TTS 태스크"""
        section, output_path = args
        return self.generate_for_section(section, output_path)
    
    def generate_for_lecture(
        self,
        lecture,
        output_dir: str = None,
        parallel_workers: int = 2
    ) -> List[TTSResult]:
        """전체 강의 TTS 생성 (병렬 처리)"""
        from concurrent.futures import ThreadPoolExecutor
        
        output_path = Path(output_dir or OUTPUT_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🔊 TTS 생성 시작: {lecture.title}")
        print(f"   모델: {self.model}")
        print(f"   Voice: {self.voice}")
        print(f"   🚀 병렬 처리: {parallel_workers} workers")
        print()
        
        # 태스크 준비
        tasks = [(section, str(output_path)) for section in lecture.sections]
        
        # 병렬 실행
        all_results = []
        with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
            section_results = list(executor.map(self._generate_section_task, tasks))
        
        # 결과 병합
        for results in section_results:
            all_results.extend(results)
        
        print()
        print(f"✅ TTS 생성 완료: {len(all_results)}개 오디오 파일")
        
        total_duration = sum(r.duration_estimate for r in all_results)
        print(f"   총 예상 길이: {total_duration / 60:.1f}분")
        
        return all_results


def main():
    """테스트"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from modules.lecture_parser import LectureParser
    
    if len(sys.argv) < 2:
        print("Usage: python tts_generator.py <lecture.md>")
        sys.exit(1)
    
    parser = LectureParser()
    lecture = parser.parse(sys.argv[1])
    
    generator = TTSGenerator()
    
    # 첫 번째 섹션만 테스트
    if lecture.sections:
        section = lecture.sections[0]
        result = generator.generate_for_section(section, "output/tts_test")
        if result:
            print(f"\n✅ 테스트 성공: {result.audio_path}")


if __name__ == "__main__":
    main()
