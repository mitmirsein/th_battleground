# Markdown to Document CLI

> 🚀 전문 출판 수준의 EPUB/PDF 변환 도구 | v1.2.7

마크다운 문서를 **완벽한 품질의 EPUB/PDF**로 변환하는 CLI 도구입니다. 옵시디언 플러그인 "Markdown to Document Pro"의 핵심 기능을 NPM/NPX 패키지로 제공합니다.

**🔒 보안 강화 (2026-01-06)**: SSH 인증 기반 Git 작업, 환경변수 토큰 주입 차단, 안전한 credential 관리 완료

## ✨ 주요 기능

### 📚 핵심 변환 기능
- **EPUB 3.3 / PDF** 형식 지원
- **자동 표지 생성**: 테마별 고해상도 SVG(EPUB) 및 HTML(PDF) 표지 자동 삽입
- **4가지 타이포그래피 프리셋** (소설, 발표, 리뷰, 전자책)
- **자동 목차 생성** (계층형 네비게이션)
- **챕터별 파일 분리** (H1 기준)
- **한글 최적화**: Noto Sans/Serif KR 임베딩 및 가독성 높은 레이아웃

### 🔍 8개 검증 모듈 (자동 수정)
1. **Frontmatter 검증**: YAML 구문 오류 자동 수정
2. **제목 검증**: H1 중복 감지, 레벨 갭 수정
3. **링크 검증**: Obsidian 링크 자동 변환 (`[[링크]]` → `[링크](링크)`)
4. **이미지 검증**: 파일 존재, 크기, alt 텍스트 확인
5. **표 검증**: 열 일관성, 헤더 자동 추가
6. **구문 검증**: 닫히지 않은 코드 블록 자동 수정
7. **특수문자 검증**: 이모지 처리, ASCII 다이어그램 경고
8. **접근성 검증**: WCAG 2.1 AA 표준 준수

### 🎨 타이포그래피 프리셋

| 프리셋 | 용도 | 특징 |
|--------|------|------|
| **소설** | 장편 소설, 에세이 | 16pt, 들여쓰기, 양쪽 정렬, 세리프 폰트 |
| **발표** | 프레젠테이션, 강의 | 18pt, 큰 글씨, 넓은 여백, 산세리프 폰트 |
| **리뷰** | 검토용 문서 | 15pt, 촘촘한 레이아웃, 코드 블록 강조 |
| **전자책** | 일반 전자책 | 14pt, 균형잡힌 레이아웃, 산세리프 폰트 |

### 🔧 고급 기능

#### TypographyService
- **11개 프리셋 지원**: Basic(4), Content-focused(4), Document Type(3) 카테고리별 레이아웃 최적화
- **동적 CSS 생성**: 타이포그래피 프리셋 기반 자동 스타일링
- **한국어 최적화**: `word-break: keep-all`, `orphans/widows` 제어 등 전문 출판 수준의 가독성
- **한국어 폰트 스택**: Noto Sans CJK KR, Noto Serif CJK KR 지원
- **페이지 마진 설정**: 각 프리셋별 최적화된 여백
- **제목 스케일**: H1-H6 비율 자동 계산
- **하이픈 처리**: 단어 끊기 옵션 지원

#### CoverService
- **15개 테마 지원**: Basic(6), Professional(3), Creative(4), Seasonal(3) 카테고리별 다양한 디자인
- **EPUB 최적화**: 고해상도 벡터 SVG 표지 생성 및 임베딩
- **PDF 최적화**: HTML Fragment 기술을 이용한 전면 페이지 레이아웃 구현
- **메타데이터 연동**: 입력된 제목과 저자명을 표지에 자동 반영
- **99% 크기 감소**: 사용된 문자만 포함하여 폰트 최적화
- **캐싱 메커니즘**: 재사용을 위한 폰트 캐시
- **다양한 형식**: WOFF2, TTF, OTF 지원
- **문자 분석**: 문서 내 사용된 문자 자동 추출

#### PandocService 통합
- **자동 CSS 적용**: 변환 시 타이포그래피 CSS 자동 적용
- **임시 디렉토리 관리**: 안전한 임시 파일 처리
- **버전 호환성**: Pandoc 2.x 및 3.x 지원

## 📦 설치

### NPX로 바로 사용 (권장)

```bash
npx markdown-to-document-cli@latest input.md
```

### 전역 설치

```bash
npm install -g markdown-to-document-cli
```

### 로컬 설치

```bash
npm install markdown-to-document-cli
```

## 🚀 사용법

### 📁 파일 경로 입력 방법

**올바른 경로 입력 (권장)**:
```bash
# 방법 1: 드래그 앤 드롭 (가장 쉬움)
# 파일을 터미널 창으로 드래그하면 경로가 자동 입력됩니다

# 방법 2: 절대 경로
m2d /Users/username/documents/my-document.md

# 방법 3: 상대 경로
m2d ./docs/document.md
m2d ../project/README.md
```

**⚠️ 피해야 할 경로 입력**:
```bash
# ❌ 백슬래시 이스케이프가 포함된 경로
m2d /Users/username/My\ Documents/file.md

# ✅ 대신 이렇게 (따옴표 사용 또는 드래그 앤 드롭)
m2d "/Users/username/My Documents/file.md"
```

**자동 경로 정리 기능**:
- 백슬래시 이스케이프 자동 제거
- 따옴표 자동 제거
- 공백이 포함된 경로 자동 처리
- 상대 경로를 절대 경로로 자동 변환

### Interactive Mode (권장)

```bash
# 대화형 모드로 실행
npx markdown-to-document-cli interactive
# 또는
m2d i
```

**간소화된 3단계 워크플로우**:

| Step | 내용 |
|------|------|
| **Step 1** | 📄 파일 선택 |
| **Step 2** | 🚀 변환 모드 선택 + 자동 문서 분석 |
| **Step 3** | ⚡ 변환 실행 |

**2가지 변환 모드**:
- **⚡ 빠른 변환** - 출력 형식만 선택, 스마트 기본값 자동 적용 (권장)
- **⚙️ 상세 설정** - 프리셋, 테마, 제목/저자 직접 선택

**스마트 기능**:
- 문서 분석 기반 프리셋 자동 추천
- frontmatter에서 title/author 자동 추출
- Obsidian 문법 감지 시 자동 전처리

### 기본 사용법

```bash
# 기본 변환 (권장: EPUB + PDF)
npx markdown-to-document-cli document.md

# PDF 변환
npx markdown-to-document-cli document.md --format pdf

# EPUB + PDF 동시 변환
npx markdown-to-document-cli document.md --format both

# 전역 설치 후 사용
m2d document.md
```

### 옵션

```bash
m2d document.md [options]

옵션:
  -o, --output <path>          출력 디렉토리
  --title <title>              책 제목 (frontmatter title 또는 파일명 기본값)
  --author <author>            저자명 (frontmatter author 기본값)
  -f, --format <format>        출력 형식 (epub, pdf, both) [기본값: both]
  -t, --typography <preset>    타이포그래피 프리셋 (auto 포함) [기본값: auto]
                               Basic: novel, presentation, review, ebook
                               Content: text_heavy, table_heavy, image_heavy, balanced
                               Document: report, manual, magazine
  -c, --cover <theme>          표지 테마
                               Basic: apple, modern_gradient, dark_tech, nature, classic_book, minimalist
                               Professional: corporate, academic, magazine
                               Creative: sunset, ocean, aurora, rose_gold
                               Seasonal: spring, autumn, winter
  --no-validate                콘텐츠 검증 건너뛰기
  --no-auto-fix                자동 수정 비활성화
  --toc-depth <number>         목차 깊이 [기본값: 2]
  --no-toc                     목차 비활성화
  --pdf-engine <engine>        PDF 엔진 (auto, pdflatex, xelatex, weasyprint) [기본값: auto]
  --paper-size <size>          용지 크기 (a4, letter) [기본값: a4]
  --font-subsetting            폰트 서브세팅 활성화
  --css <path>                 커스텀 CSS 파일 경로
  --pandoc-path <path>         Pandoc 실행 파일 경로
  -v, --verbose                상세 출력
  -h, --help                   도움말 표시
```

### 예제

```bash
# 소설용 타이포그래피로 EPUB 변환
m2d novel.md --format epub --typography novel

# 발표용 PDF 생성
m2d presentation.md --format pdf --typography presentation --pdf-engine weasyprint

# 출력 디렉토리 지정
m2d document.md --output ./output

# 커스텀 CSS 적용
m2d document.md --css ./custom.css

# 검증 없이 빠르게 변환
m2d document.md --no-validate --no-auto-fix

# 상세 로그 출력
m2d document.md --verbose
```

### 인터랙티브 모드

```bash
m2d interactive
# 또는
m2d i
```

인터랙티브 모드는 사용자 친화적인 프롬프트를 통해 변환 옵션을 선택할 수 있습니다:

- ✅ 따옴표가 포함된 파일 경로 자동 처리
- 🎨 색상 코딩된 프롬프트와 이모지
- 📊 개선된 스피너 애니메이션
- 📦 더 나은 출력 포맷팅
- 📖 책 제목과 저자명 직접 입력 가능

가이드에 따라 옵션을 선택할 수 있습니다.

### 프리셋 및 테마 목록

```bash
# 타이포그래피 프리셋 목록
m2d list-presets

# 표지 테마 목록
m2d list-themes
```

### 의존성 확인 (권장)

변환을 시작하기 전에 필요한 도구들이 모두 설치되어 있는지 확인하세요:

```bash
m2d check
```

**자동으로 확인하는 항목**:
- ✅ Node.js (필수)
- ✅ Pandoc (필수)
- ✅ PDF 엔진: WeasyPrint, XeLaTeX, PDFLaTeX 중 최소 1개
- ⚪ Python (WeasyPrint 사용 시 필요)

**설치되지 않은 도구가 있으면**:
- 플랫폼별(macOS, Linux, Windows) 맞춤 설치 명령어 제공
- 복사해서 바로 사용할 수 있는 명령어
- 각 도구의 역할 설명

**예시 출력**:
```
🔍 의존성 확인 중...

필수 의존성:
  ✅ Node.js (v20.10.0)
  ✅ Pandoc (v3.1.2)

PDF 생성 엔진 (최소 1개 필요):
  ✅ WeasyPrint (v60.1)
  ⚪ XeLaTeX - 미설치
  ⚪ PDFLaTeX - 미설치

✅ 모든 의존성이 준비되었습니다!

🚀 준비 완료! 지금 바로 문서 변환을 시작할 수 있습니다.
```

## ⚙️ 필수 요구사항

### Pandoc 설치

Pandoc 2.19+ 이상이 필요합니다.

#### macOS
```bash
brew install pandoc
```

#### Windows
```bash
winget install --id JohnMacFarlane.Pandoc
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install pandoc
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install pandoc
```

### WeasyPrint (PDF 생성, 선택사항)

```bash
pip install weasyprint
```

## 📝 프로그래밍 방식 사용

```javascript
import { MarkdownToDocument } from 'markdown-to-document-cli';

const converter = new MarkdownToDocument();

// 초기화
await converter.initialize();

// 변환
const result = await converter.convert({
  inputPath: './document.md',
  outputPath: './output',
  format: 'epub',
  typographyPreset: 'ebook',
  validateContent: true,
  autoFix: true,
});

if (result.success) {
  console.log('변환 성공!', result.epubPath);
} else {
  console.error('변환 실패:', result.errors);
}
```

## 🎯 YAML Frontmatter

문서 상단에 메타데이터를 추가할 수 있습니다:

```yaml
---
title: 문서 제목
subtitle: 부제목
author: 저자명
language: ko
date: 2025-01-05
description: 문서 설명
isbn: 978-0-1234-5678-9
publisher: 출판사명
---

# 문서 내용
```

## 🔬 검증 리포트 예시

```
=== 검증 완료 ===

✅ 수정됨: 5건
  • Obsidian 링크 3개 변환
  • 코드 블록 1개 자동 닫기
  • 제목 공백 1개 조정

⚠️ 경고: 2건
  • 긴 제목 감지 (자동 조정됨)
  • ASCII 다이어그램 (이미지 권장)

❌ 오류: 0건

총 7개 문제 발견, 5개 자동 수정
```

## 📊 기술 스택

- **언어**: TypeScript 5.3+
- **런타임**: Node.js 18+
- **변환 엔진**: Pandoc 2.19+
- **CLI 프레임워크**: Commander.js
- **PDF 엔진**: WeasyPrint (선택사항)

## 🐛 문제 해결

### ❌ PDF 변환 실패: "xelatex not found" 또는 "PDF 엔진을 찾을 수 없습니다"

**🤔 왜 이런 오류가 나올까요?**

PDF를 만들려면 **"PDF 제작 엔진"**이 필요합니다. 마치 빵을 굽기 위해 오븐이 필요한 것처럼요!

이 오류는 "오븐이 없어서 빵을 구울 수 없어요"라는 뜻입니다. 아래 방법 중 하나를 선택해서 해결하세요.

#### 옵션 1: WeasyPrint 설치 (추천 ⭐)

**가장 쉽고 빠른 방법!** 한글도 완벽하게 지원합니다.

```bash
# Python pip 사용
pip install weasyprint

# 또는 Python 3
pip3 install weasyprint
```

💡 **Python이 없다면?** [python.org](https://www.python.org/downloads/)에서 먼저 설치하세요.

#### 옵션 2: XeLaTeX 설치 (한글 최적화)

**한글 폰트를 아름답게!** 전문 출판 수준의 품질을 원한다면 이걸로!

```bash
# macOS (Homebrew)
brew install --cask basictex
# 설치 후 PATH 업데이트
eval "$(/usr/libexec/path_helper)"

# 또는 전체 TeX Live 설치
brew install --cask mactex

# Linux (Ubuntu/Debian)
sudo apt-get install texlive-xetex texlive-fonts-recommended

# Linux (Fedora)
sudo dnf install texlive-xetex
```

⚠️ **중요**: 설치 후 터미널을 다시 시작하세요!

#### 옵션 3: PDFLaTeX 설치

```bash
# macOS
brew install --cask basictex

# Linux (Ubuntu/Debian)
sudo apt-get install texlive-latex-base
```

#### ✓ 설치 확인하기

오븐이 제대로 설치되었는지 확인해 봅시다:

```bash
# WeasyPrint 확인
weasyprint --version

# XeLaTeX 확인
xelatex --version

# PDFLaTeX 확인
pdflatex --version
```

버전 번호가 나오면 성공! 🎉

#### 💡 프로 팁: 특정 엔진 지정하기

여러 개를 설치했다면, 원하는 엔진을 직접 선택할 수 있습니다:

```bash
# 자동 선택 (기본값 - 권장)
m2d document.md --pdf-engine auto

# WeasyPrint로 PDF 만들기
m2d document.md --pdf-engine weasyprint

# XeLaTeX로 PDF 만들기
m2d document.md --pdf-engine xelatex

# PDFLaTeX로 PDF 만들기
m2d document.md --pdf-engine pdflatex
```

---

### Pandoc을 찾을 수 없음

```bash
# Pandoc 설치 확인
pandoc --version

# 커스텀 경로 지정
m2d document.md --pandoc-path /path/to/pandoc
```

**설치 방법**:
- macOS: `brew install pandoc`
- Windows: `winget install --id JohnMacFarlane.Pandoc`
- Linux (Ubuntu/Debian): `sudo apt-get update && sudo apt-get install pandoc`
- Linux (Fedora/RHEL): `sudo dnf install pandoc`

---

### 파일 경로 오류

**증상**: "파일을 찾을 수 없습니다" 또는 경로에 백슬래시(`\`)가 포함됨

**해결 방법**:
1. **드래그 앤 드롭 사용** (가장 쉬움)
   - 파일을 터미널 창으로 드래그하세요
   - 경로가 자동으로 입력됩니다

2. **따옴표로 감싸기**
   ```bash
   m2d "/Users/username/My Documents/file.md"
   ```

3. **백슬래시 제거**
   ```bash
   # ❌ 잘못된 예
   m2d /Users/username/My\ Documents/file.md
   
   # ✅ 올바른 예
   m2d "/Users/username/My Documents/file.md"
   ```

**자동 수정 기능**: CLI가 자동으로 경로를 정리하고 검증합니다.

### 이미지를 찾을 수 없음

이미지 파일이 마크다운 파일과 동일한 디렉토리 또는 `images/`, `attachments/`, `assets/`, `media/` 폴더에 있는지 확인하세요.

**지원하는 이미지 형식**: PNG, JPG/JPEG, GIF, SVG, WebP

---

### 📚 더 많은 문제 해결

이미지 오류, 한글 깨짐, 검증 문제 등 다양한 상황에 대한 해결책은 [전체 문제 해결 가이드](./TroubleShooting.md)를 참고하세요.

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 파일 참조

## 🙏 감사의 말

- [Obsidian](https://obsidian.md) 팀의 훌륭한 플랫폼
- [Pandoc](https://pandoc.org) 개발자들
- 원본 옵시디언 플러그인 [Markdown to Document Pro](https://github.com/bluelion79/obsidian-markdown-to-document)

## 📧 문의

- **GitHub**: [@goodlookingprokim](https://github.com/goodlookingprokim)
- **Repository**: https://github.com/goodlookingprokim/markdown-to-document-cli
- **Email**: edulovesai@gmail.com

---

**Made with ❤️ by 잘생김프로쌤**
