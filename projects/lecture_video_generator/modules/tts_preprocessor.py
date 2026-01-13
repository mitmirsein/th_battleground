"""
TTS Preprocessor - 강의 텍스트 정제 (TTS용)

Usage:
    from modules.tts_preprocessor import TTSPreprocessor
    
    preprocessor = TTSPreprocessor()
    clean_text = preprocessor.process(section.content)
"""
import re
from typing import List


class TTSPreprocessor:
    """TTS용 텍스트 전처리"""
    
    def __init__(self):
        # 제거할 패턴들
        self.remove_patterns = [
            r'\[.*?\]',           # [대괄호 내용]
            r'\(.*?\)',           # (괄호 내용) - 선택적
            r'#{1,6}\s*',         # 마크다운 헤딩
            r'\*{1,2}(.*?)\*{1,2}',  # **굵게** 또는 *기울임*
            r'`[^`]+`',           # `코드`
        ]
        
        # 숫자 패턴 (읽기 쉽게 변환)
        self.number_patterns = [
            (r'(\d+)강', r'\1강'),  # N강 유지
            (r'(\d+)\.\s+', r''),   # "1. 서론" → "서론" (소제목 번호 제거)
        ]
    
    def process(self, text: str, remove_subheadings: bool = True) -> str:
        """텍스트 정제"""
        result = text
        
        # 소제목 제거 (N. 제목 형태)
        if remove_subheadings:
            # 줄 시작의 "N. " 패턴 제거
            result = re.sub(r'^(\d+)\.\s+(.+?)(?:\r?\n|\r)', '', result, flags=re.MULTILINE)
        
        # 지문/스테이지 디렉션 제거 (TTS가 읽지 않도록)
        # 예: (차분한 톤으로), (잠시 멈춤), (강조하며) 등
        result = re.sub(r'\([^)]*톤[^)]*\)', '', result)
        result = re.sub(r'\([^)]*멈춤[^)]*\)', '', result)
        result = re.sub(r'\([^)]*강조[^)]*\)', '', result)
        result = re.sub(r'\([^)]*웃으며[^)]*\)', '', result)
        result = re.sub(r'\([^)]*조용히[^)]*\)', '', result)
        
        # 마크다운 강조 제거하고 내용만 유지
        result = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', result)
        
        # 대괄호 내용 제거 (참조 등)
        result = re.sub(r'\[(\d+)\]', '', result)  # [1] 같은 각주 참조
        
        # 연속 공백 정리
        result = re.sub(r'[ \t]+', ' ', result)
        
        # 연속 줄바꿈 정리
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # 따옴표 정규화
        result = result.replace('"', '"').replace('"', '"')
        result = result.replace(''', "'").replace(''', "'")
        
        return result.strip()
    
    def split_for_tts(self, text: str, max_chars: int = 2000) -> List[str]:
        """긴 텍스트를 TTS 청크로 분할
        
        우선순위:
        1. 단락 경계 (빈 줄)
        2. 문장 경계 (. ! ?)
        3. 절대 문장 중간에서 끊기지 않음
        """
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        
        # 1단계: 단락 단위로 먼저 분할
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 단락이 max_chars 이하면 청크에 추가
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk += para + "\n\n"
            else:
                # 현재 청크 저장
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 단락 자체가 max_chars 초과하면 문장 단위로 분할
                if len(para) > max_chars:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_chars:
                            current_chunk += sentence + " "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + " "
                else:
                    current_chunk = para + "\n\n"
        
        # 마지막 청크 저장
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def estimate_duration(self, text: str, chars_per_second: float = 5.0) -> float:
        """예상 음성 길이 (초) 계산
        
        한국어 평균: 약 5자/초 (보통 속도)
        """
        clean_text = re.sub(r'\s+', '', text)  # 공백 제거
        return len(clean_text) / chars_per_second


def main():
    """테스트"""
    sample = """1. 서론
오늘 우리는 매우 도발적이지만 동시에 우리 삶의 근본을 뒤흔드는 질문을 안고 만났습니다. 
바로 '인격적인 삶의 근거'로서의 신(神)을 재탐색하는 여정입니다.
신에 대해 이야기할 때, 여러분은 어떤 이미지를 떠올리십니까? 
전지전능함의 상징인 '하늘의 왕'입니까, 아니면 "하나님이 정말로 자전거를 탈 수 있을까?"라는 질문이 보여주듯이 
신은 우리의 **상상을 멈추게** 하는 의문입니까?[1]
"""
    
    preprocessor = TTSPreprocessor()
    clean = preprocessor.process(sample)
    
    print("원본:")
    print(sample)
    print("\n" + "=" * 50 + "\n")
    print("정제 후:")
    print(clean)
    print(f"\n예상 길이: {preprocessor.estimate_duration(clean):.1f}초")


if __name__ == "__main__":
    main()
