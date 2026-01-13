# 🎬 Lecture Video Generator

신학 강의안(.md/.docx)을 영상으로 자동 변환하는 파이프라인

## ✨ 기능

| 명령어 | 기능 | 설명 |
|--------|------|------|
| `generate` | 강의안 → 슬라이드 | **Premium Design** 적용 (Deep Blue Gradient + Gold Accent) |
| `tts` | 텍스트 → 오디오 | Gemini TTS (Auto Silence Trimming 적용) |
| `assemble` | 슬라이드 + 오디오 → 영상 | Fade 효과(1초) + **SRT 자막 자동 생성** |
| `all` | 전체 파이프라인 | 원클릭 실행 |

---

## 🚀 설치

```bash
cd /Users/msn/Desktop/MS_Dev.nosync/projects/lecture_video_generator

# 공유 가상환경 활성화
source venv.nosync/bin/activate  # → shared_venv 심볼릭 링크

# FFmpeg 설치 (필수)
brew install ffmpeg

# API 키 설정
cp .env.example .env
# GOOGLE_API_KEY 입력
```

---

## 📖 사용법

### 1. 전체 파이프라인 (추천)

```bash
python pipeline.py all input/lecture.md
```

### 2. 단계별 실행

```bash
# 1단계: 개요 + 슬라이드 생성
python pipeline.py generate input/lecture.md

# 2단계: TTS 생성 (Gemini 2.5 Pro Preview)
python pipeline.py tts input/lecture.md

# 3단계: 영상 조립 (페이드 효과 + 자막 생성)
python pipeline.py assemble output/lecture/
```

### 3. 주요 옵션 (`assemble` / `all`)

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--no-fade` | 영상 전환 시 페이드 효과 끄기 | False (페이드 켬) |
| `--no-subtitle` | SRT 자막 파일 생성하지 않음 | False (자막 켬) |

```bash
# 예시: 페이드 없이 컷 전환만 사용
python pipeline.py assemble output/lecture/ --no-fade
```

---

## 📁 구조

```
lecture_video_generator/
├── pipeline.py             # 메인 CLI
├── config.py               # 설정 (디자인, 모델 등)
├── modules/
│   ├── lecture_parser.py       # MD/DOCX 파싱
│   ├── outline_generator.py    # Gemini 개요 생성
│   ├── slide_generator.py      # Premium SVG/PNG 슬라이드
│   ├── subtitle_generator.py   # SRT 자막 생성 (NEW)
│   ├── tts_preprocessor.py     # 텍스트 정제
│   ├── tts_generator.py        # Gemini TTS (Silence Trim)
│   └── video_assembler.py      # FFmpeg 영상 조립 (Fade)
├── docs/
│   ├── PRD.md              # 제품 요구사항
│   └── 7-1.md              # 샘플 강의안
├── input/                  # 강의안 입력
└── output/                 # 영상 출력
```

---

## ⚙️ 설정 (config.py)

### 디자인 커스터마이징
새로운 **Premium Design** 테마가 적용되었습니다.

```python
# Slide Colors
COLORS = {
    "bg_start": "#1E3A8A",  # Deep Blue Start
    "bg_mid": "#0F285A",    # Deep Blue Mid
    "bg_end": "#0A1A3C",    # Deep Blue End
    "accent": "#D4A017",    # Gold Accent
    "text_main": "#E0E0E0",
    "text_sub": "#A3BFFA",
    "pattern": "#D4A017",   # Pattern Color
}

# Fonts
FONTS = {
    "title": "Noto Sans KR",
    "body": "Noto Sans KR",
}
```

---

## 🛠️ 최근 업데이트 (Phase 4)

1.  **Premium Slide Design**: 딥 블루 그라데이션과 골드 포인트가 적용된 새로운 디자인.
2.  **Subtitle (SRT) Generation**: 
    - 최종 영상 싱크에 맞춘 자막 자동 생성.
    - 긴 문장 자동 분할 및 가독성 최적화 (30자 제한).
3.  **Video Transitions**: `xfade`를 이용한 1초 페이드 전환 효과.
4.  **Audio Optimization**: TTS 생성 시 불필요한 공백(Silence) 자동 제거.

---

## 📚 문서

- [PRD.md](docs/PRD.md) - 상세 제품 요구사항
