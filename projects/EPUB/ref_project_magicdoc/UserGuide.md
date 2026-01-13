# UserGuide.md - 사용자 가이드

## 시작하기

Markdown to Document CLI는 마크다운 문서를 전문 출판 수준의 EPUB/PDF로 변환하는 도구입니다. 이 가이드를 통해 기본 사용법부터 고급 기능까지 학습할 수 있습니다.

## 설치

### 방법 1: NPX로 바로 사용 (추천)

설치 없이 바로 사용할 수 있습니다:

```bash
npx markdown-to-document-cli document.md
```

### 방법 2: 전역 설치

시스템 전체에서 사용하려면 전역 설치:

```bash
npm install -g markdown-to-document-cli
```

설치 후 어디서든 `m2d` 명령어로 사용:

```bash
m2d document.md
```

### 방법 3: 프로젝트 로컬 설치

프로젝트에만 설치:

```bash
npm install markdown-to-document-cli
```

`npx`로 실행:

```bash
npx markdown-to-document-cli document.md
```

## 필수 요구사항

### 1. Node.js

Node.js 18.0 이상이 필요합니다:

```bash
node --version
```

### 2. Pandoc

Pandoc 2.19 이상이 필요합니다:

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

설치 확인:
```bash
pandoc --version
```

### 3. WeasyPrint (선택사항, PDF 생성용)

```bash
pip install weasyprint
```

## 📁 파일 경로 입력 방법

### 올바른 경로 입력 (권장)

**방법 1: 드래그 앤 드롭** (가장 쉬움)
- 파일을 터미널 창으로 드래그하면 경로가 자동으로 입력됩니다
- 백슬래시나 따옴표 걱정 없이 사용 가능

**방법 2: 절대 경로**
```bash
m2d /Users/username/documents/my-document.md
```

**방법 3: 상대 경로**
```bash
m2d ./docs/document.md
m2d ../project/README.md
```

### ⚠️ 피해야 할 경로 입력

```bash
# ❌ 백슬래시 이스케이프가 포함된 경로
m2d /Users/username/My\ Documents/file.md

# ✅ 대신 이렇게 (따옴표 사용 또는 드래그 앤 드롭)
m2d "/Users/username/My Documents/file.md"
```

### 자동 경로 정리 기능

CLI가 자동으로 다음을 처리합니다:
- ✅ 백슬래시 이스케이프 자동 제거
- ✅ 따옴표 자동 제거
- ✅ 공백이 포함된 경로 자동 처리
- ✅ 상대 경로를 절대 경로로 자동 변환
- ✅ 파일 존재 여부 확인 및 친절한 오류 메시지

---

## Interactive Mode (대화형 모드)

### 실행 방법

```bash
npx markdown-to-document-cli interactive
# 또는
m2d i
```

### 워크플로우

Interactive Mode는 **간소화된 3단계 워크플로우**로 구성됩니다:

| Step | 내용 | 설명 |
|------|------|------|
| **Step 1** | 📄 파일 선택 | 마크다운 파일 경로 입력 |
| **Step 2** | 🚀 모드 선택 | 변환 모드 선택 + 자동 문서 분석 |
| **Step 3** | ⚡ 변환 실행 | 자동 전처리 + 변환 |

### 2가지 변환 모드

| 모드 | 설명 | 사용 시기 |
|------|------|----------|
| **⚡ 빠른 변환** | 출력 형식만 선택, 나머지 스마트 기본값 | 대부분의 경우 (권장) |
| **⚙️ 상세 설정** | 프리셋, 테마, 제목/저자 직접 선택 | 세부 조정이 필요할 때 |

### 스마트 기능

- **자동 문서 분석**: Obsidian 문법, 이미지/표/코드 블록 자동 감지
- **스마트 기본값**: 분석 결과 기반 프리셋/테마 자동 추천
- **메타데이터 추출**: frontmatter에서 title/author 자동 감지
- **자동 전처리**: Obsidian 문법 감지 시 자동 최적화 적용

### 스마트 프리셋 추천

문서 분석 결과에 따라 최적의 Typography Preset을 자동으로 추천합니다:

| 문서 특성 | 추천 프리셋 |
|----------|------------|
| 이미지 10개 초과 | `image_heavy` |
| 표 5개 초과 | `table_heavy` |
| 코드 블록 10개 초과 | `manual` |
| 단어 10,000개 초과 | `text_heavy` |
| 기본 | `balanced` |

---

## 타이포그래피 프리셋

### 프리셋 개요

11가지 타이포그래피 프리셋을 제공하여 다양한 용도에 최적화된 출력을 생성합니다:

#### Basic 프리셋

| 프리셋 | 용도 | 폰트 크기 | 줄 간격 | 정렬 |
|--------|------|-----------|---------|------|
| **소설** | 장편 소설, 에세이 | 16pt | 1.8 | 양쪽 정렬 |
| **발표** | 프레젠테이션, 강의 | 18pt | 1.6 | 왼쪽 정렬 |
| **리뷰** | 검토용 문서 | 15pt | 1.7 | 왼쪽 정렬 |
| **전자책** | 일반 전자책 | 14pt | 1.6 | 왼쪽 정렬 |

### 소설 프리셋

장편 소설과 에세이에 최적화되어 있습니다:

- **세리프 폰트**: Noto Serif CJK KR
- **들여쓰기**: 첫 문단 2em
- **양쪽 정렬**: 깔끔한 레이아웃
- **하이픈 처리**: 단어 끊기 활성화
- **페이지 나누기**: 제목에서 페이지 나눔 방지

```bash
m2d novel.md --typography novel
```

### 발표 프리셋

프레젠테이션과 강의 자료에 적합합니다:

- **산세리프 폰트**: Noto Sans CJK KR
- **큰 글씨**: 18pt 기본 크기
- **넓은 여백**: 30mm 상하 여백
- **제목 강조**: H1-H2에 밑줄 추가
- **왼쪽 정렬**: 가독성 향상

```bash
m2d presentation.md --typography presentation
```

### 리뷰 프리셋

기술 문서와 검토용 자료에 적합합니다:

- **산세리프 폰트**: Noto Sans CJK KR
- **코드 강조**: 코드 블록 배경색
- **인용구 스타일**: 왼쪽 테두리
- **촘촘한 레이아웃**: 정보 밀도 높임

```bash
m2d review.md --typography review
```

### 전자책 프리셋

일반 전자책 리더에 최적화되어 있습니다:

- **산세리프 폰트**: Noto Sans CJK KR
- **균형잡힌 레이아웃**: 14pt, 1.6 줄 간격
- **페이지 나누기**: 최적화
- **이미지 캡션**: 중앙 정렬, 이탤릭체

```bash
m2d ebook.md --typography ebook
```

## 폰트 서브세팅

### 개요

FontSubsetter는 문서에 실제 사용된 문자만 포함하여 폰트 크기를 최대 99% 감소시킵니다.

### 장점

- **파일 크기 감소**: 전체 폰트 대비 99% 크기 감소
- **빠른 로딩**: 작은 파일 크기로 빠른 로딩
- **캐싱**: 재사용을 위한 폰트 캐시
- **다양한 형식**: WOFF2, TTF, OTF 지원

### 사용법

```bash
m2d document.md --font-subsetting
```

### 작동 방식

1. 문서 내 모든 문자 추출
2. 사용된 문자만 포함하여 폰트 서브셋 생성
3. WOFF2 형식으로 변환
4. 캐시에 저장하여 재사용

### 캐시 관리

캐시는 기본적으로 프로젝트 내 `.font-cache` 디렉토리에 저장됩니다.

## 고급 기능

### 동적 CSS 생성

TypographyService는 타이포그래피 프리셋을 기반으로 동적으로 CSS를 생성합니다:

- **루트 스타일**: 폰트 크기, 줄 간격
- **본문 스타일**: 폰트 패밀리, 정렬, 하이픈
- **페이지 스타일**: 여백, 크기 (PDF)
- **단락 스타일**: 간격, 들여쓰기
- **제목 스타일**: 크기, 여백, 폰트 두께

### 커스텀 CSS

자신만의 CSS를 추가할 수 있습니다:

```bash
m2d document.md --css custom.css
```

커스텀 CSS는 타이포그래피 프리셋 CSS 뒤에 적용됩니다.

### 한국어 폰트 지원

기본 한국어 폰트 스택:

- **세리프**: Noto Serif CJK KR, Noto Serif KR, Batang, 바탕
- **산세리프**: Noto Sans CJK KR, Noto Sans KR, Malgun Gothic, 맑은 고딕
- **모노스페이스**: Noto Sans Mono CJK KR, D2Coding

## 기본 사용법

### 첫 번째 변환

```bash
m2d my-document.md
```

이 명령은:
1. `my-document.md` 파일을 읽습니다
2. 콘텐츠를 검증하고 자동 수정합니다
3. 타이포그래피 프리셋 CSS를 생성합니다
4. EPUB + PDF 파일을 생성합니다 (`my-document.epub`, `my-document.pdf`)

### PDF 변환

```bash
m2d my-document.md --format pdf
```

### EPUB + PDF 동시 변환

```bash
m2d my-document.md --format both
```

## 옵션 상세

### 출력 형식 (`-f, --format`)

```bash
m2d document.md --format epub    # EPUB만
m2d document.md --format pdf     # PDF만
m2d document.md --format both    # 둘 다
```

### 출력 디렉토리 (`-o, --output`)

```bash
m2d document.md --output ./dist
```

### 타이포그래피 프리셋 (`-t, --typography`)

```bash
m2d document.md --typography auto          # 자동 추천 (기본값)
m2d document.md --typography novel         # 소설
m2d document.md --typography presentation  # 발표
m2d document.md --typography review        # 리뷰
m2d document.md --typography ebook         # 전자책
```

### 표지 테마 (`-c, --cover`)

자동으로 전문적인 책 표지를 생성합니다:

```bash
m2d document.md --cover apple            # Apple 스타일 (깔끔함)
m2d document.md --cover modern_gradient  # 현대적인 그라데이션
m2d document.md --cover dark_tech        # 어두운 테크 스타일
m2d document.md --cover nature           # 자연 친화적 디자인
```

- **EPUB**: 고품질 SVG 이미지가 표지로 삽입됩니다.
- **PDF**: 문서의 가장 첫 페이지에 전면 HTML 표지가 생성됩니다.

사용 가능한 테마 목록:
```bash
m2d list-themes
```

### 검증 옵션

```bash
# 검증 건너뛰기
m2d document.md --no-validate

# 자동 수정 비활성화
m2d document.md --no-auto-fix
```

### 목차 옵션

```bash
# 목차 깊이 설정
m2d document.md --toc-depth 3

# 목차 비활성화
m2d document.md --no-toc
```

### PDF 옵션

```bash
# PDF 엔진 선택
m2d document.md --format pdf --pdf-engine auto
m2d document.md --format pdf --pdf-engine weasyprint
m2d document.md --format pdf --pdf-engine pdflatex
m2d document.md --format pdf --pdf-engine xelatex

# 용지 크기
m2d document.md --format pdf --paper-size a4
m2d document.md --format pdf --paper-size letter
```

### 고급 옵션

```bash
# 폰트 서브세팅 (파일 크기 감소)
m2d document.md --font-subsetting

# 커스텀 CSS
m2d document.md --css ./custom.css

# 커스텀 Pandoc 경로
m2d document.md --pandoc-path /usr/local/bin/pandoc

# 상세 로그
m2d document.md --verbose
```

## 인터랙티브 모드

인터랙티브 모드는 사용자 친화적인 프롬프트를 통해 변환 옵션을 선택할 수 있습니다:

```bash
m2d interactive
# 또는
m2d i
```

### 기능

- ✅ **따옴표 자동 제거**: 파일 경로의 따옴표를 자동으로 제거하여 복사-붙여넣기 편의성 향상
- 🎨 **색상 코딩된 프롬프트**: 각 질문에 이모지와 색상으로 시각적 개선
- 📊 **개선된 스피너**: 변환 진행 상황을 더 명확하게 표시
- 📦 **더 나은 출력 포맷팅**: 결과를 구분선으로 구분하여 가독성 향상
- 📖 **책 제목/저자명 직접 입력**: 자동 감지된 메타데이터 대신 직접 입력 가능

### 사용 예시

단계별 질문에 답하면 됩니다:

```
────────────────────────────────────────────────────────────
  Markdown to Document - Interactive Mode
────────────────────────────────────────────────────────────

? 📄 Input markdown file path: ./my-document.md
? 📖 책 제목 (Enter=자동): My Custom Title
? ✍️  저자 (Enter=자동): John Doe
? 📤 Output format: � Both EPUB and PDF
? 🎨 Typography preset: Balanced - 균형 레이아웃
? 🖼️  Cover theme (optional): None
? 🔍 Enable content validation? Yes
? 🔧 Enable auto-fix for detected issues? Yes
? 📁 Output directory (leave empty for same as input): ./output

────────────────────────────────────────────────────────────

⚙️  Initializing...
✅ Initialized successfully

🔄 Converting document...
✅ Conversion completed!

────────────────────────────────────────────────────────────

📦 Output Files:

  📖 EPUB:  ./output/My Custom Title.epub

────────────────────────────────────────────────────────────

🎉 Conversion successful!
```

### 팁

- 파일 경로를 복사할 때 따옴표가 포함되어도 자동으로 처리됩니다
- 터미널에서 파일을 드래그 앤 드롭하여 경로를 입력할 수 있습니다
- 책 제목과 저자명을 직접 입력하면 자동 감지된 값을 대체합니다
- 빈 값으로 두면 자동 감지된 메타데이터를 사용합니다
- 모든 질문에 기본값이 제공되므로 Enter 키만 눌러도 됩니다

## YAML Frontmatter

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

### 필드 설명

| 필드 | 설명 | 필수 여부 |
|------|------|----------|
| `title` | 문서 제목 | 아니오 (파일명 사용) |
| `subtitle` | 부제목 | 아니오 |
| `author` | 저자명 | 아니오 |
| `language` | 언어 코드 | 아니오 (기본값: ko) |
| `date` | 날짜 | 아니오 (오늘 날짜 사용) |
| `description` | 설명 | 아니오 |
| `isbn` | ISBN | 아니오 |
| `publisher` | 출판사 | 아니오 |

## 타이포그래피 프리셋 상세

### 소설 (Novel)

**사용 사례**: 장편 소설, 에세이, 문학 작품

**특징**:
- 폰트 크기: 16pt
- 줄 간격: 1.8
- 정렬: 양쪽 정렬
- 들여쓰기: 있음
- 폰트: Noto Serif CJK KR (명조체)

**예시**:
```bash
m2d novel.md --typography novel
```

### 발표 (Presentation)

**사용 사례**: 프레젠테이션, 강의 자료, 슬라이드

**특징**:
- 폰트 크기: 18pt
- 줄 간격: 1.6
- 정렬: 왼쪽 정렬
- 여백: 넓음
- 폰트: Noto Sans CJK KR (고딕체)

**예시**:
```bash
m2d slides.md --typography presentation
```

### 리뷰 (Review)

**사용 사례**: 검토용 문서, 기술 문서, 보고서

**특징**:
- 폰트 크기: 11pt
- 줄 간격: 1.4
- 정렬: 왼쪽 정렬
- 레이아웃: 촘촘함
- 폰트: Noto Sans CJK KR (고딕체)

**예시**:
```bash
m2d review.md --typography review
```

### 전자책 (Ebook)

**사용 사례**: 일반 전자책, 가이드북, 매뉴얼

**특징**:
- 폰트 크기: 14pt
- 줄 간격: 1.6
- 정렬: 양쪽 정렬
- 레이아웃: 균형잡힘
- 폰트: Noto Sans CJK KR (고딕체)

**예시**:
```bash
m2d ebook.md --typography ebook
```

## 검증 기능

### 자동 검증

기본적으로 8개 검증 모듈이 자동으로 실행됩니다:

1. **Frontmatter 검증**: YAML 구문 오류
2. **제목 검증**: H1 중복, 레벨 갭
3. **링크 검증**: Obsidian 링크, 빈 URL
4. **이미지 검증**: alt 텍스트, 파일 형식
5. **표 검증**: 열 일관성
6. **구문 검증**: 닫히지 않은 코드 블록
7. **특수문자 검증**: 이모지, ASCII 다이어그램
8. **접근성 검증**: H1 존재, 긴 문단

### 자동 수정

기본적으로 자동 수정이 활성화됩니다:

- Obsidian 링크 → 표준 마크다운 링크
- 닫히지 않은 코드 블록 자동 닫기

### 검증 리포트

변환 완료 후 검증 리포트가 표시됩니다:

```
📊 Validation Report:
  ✅ Fixed: 5 issues
  ⚠️  Warnings: 2
  ❌ Errors: 0
```

## 이미지 처리

### 이미지 경로

이미지는 다음 위치에서 자동으로 검색됩니다:

1. 마크다운 파일과 동일한 디렉토리
2. `images/` 폴더
3. `attachments/` 폴더
4. `assets/` 폴더
5. `media/` 폴더

### 이미지 형식

지원하는 형식:
- PNG
- JPG/JPEG
- GIF
- SVG
- WebP

### 이미지 참조

```markdown
<!-- 표준 마크다운 -->
![이미지 설명](./images/photo.png)

<!-- Obsidian 문법 (자동 변환됨) -->
![[photo.png]]
![[photo.png|이미지 설명]]
```

## 프로그래밍 방식 사용

Node.js 코드에서 직접 사용할 수 있습니다:

```javascript
import { MarkdownToDocument } from 'markdown-to-document-cli';

const converter = new MarkdownToDocument();

// 초기화
const initResult = await converter.initialize();
if (!initResult.success) {
  console.error(initResult.error);
  process.exit(1);
}

// 변환
const result = await converter.convert({
  inputPath: './document.md',
  outputPath: './output',
  format: 'both',
  typographyPreset: 'balanced',
  validateContent: true,
  autoFix: true,
});

if (result.success) {
  console.log('변환 성공!', result.epubPath);
} else {
  console.error('변환 실패:', result.errors);
}
```

## 실전 예제

### 예제 1: 소설 EPUB 변환

```bash
m2d my-novel.md \
  --format epub \
  --typography novel \
  --output ./books
```

### 예제 2: 발표용 PDF

```bash
m2d presentation.md \
  --format pdf \
  --typography presentation \
  --pdf-engine weasyprint \
  --paper-size a4
```

### 예제 3: 기술 문서 (EPUB + PDF)

```bash
m2d technical-doc.md \
  --format both \
  --typography review \
  --output ./docs \
  --toc-depth 3
```

### 예제 4: 검증 없이 빠르게 변환

```bash
m2d quick-document.md \
  --format epub \
  --no-validate \
  --no-auto-fix
```

### 예제 5: 커스텀 CSS 적용

```bash
m2d styled-doc.md \
  --format epub \
  --css ./custom-styles.css
```

## 팁과 모범 사례

### 1. 파일 명명

의미 있는 파일명 사용:
```bash
# 좋은 예
m2d 2025-01-05-technical-guide.md

# 피해야 할 예
m2d doc.md
```

### 2. 디렉토리 구조

```
project/
├── documents/
│   ├── chapter1.md
│   ├── chapter2.md
│   └── images/
│       ├── diagram1.png
│       └── diagram2.png
├── output/
└── custom.css
```

### 3. YAML Frontmatter 사용

항상 frontmatter 추가:
```yaml
---
title: 명확한 제목
author: 저자명
date: 2025-01-05
---
```

### 4. 이미지 alt 텍스트

항상 alt 텍스트 추가:
```markdown
![시스템 아키텍처 다이어그램](./architecture.png)
```

### 5. 제목 구조

계층적 제목 사용:
```markdown
# H1 (문서당 하나만)

## H2

### H3

#### H4
```

## 유틸리티 명령어

### 프리셋 목록

```bash
m2d list-presets
```

### 테마 목록

```bash
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

## 도움말

```bash
m2d --help
```

---

## 🔧 문제 해결

### PDF 변환 실패: "xelatex not found" 또는 "PDF 엔진을 찾을 수 없습니다"

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
- Linux: `sudo apt-get install pandoc`

### 이미지를 찾을 수 없음

이미지 파일이 마크다운 파일과 동일한 디렉토리 또는 `images/`, `attachments/`, `assets/`, `media/` 폴더에 있는지 확인하세요.

**지원하는 이미지 형식**: PNG, JPG/JPEG, GIF, SVG, WebP

### 📚 더 많은 문제 해결

이미지 오류, 한글 깨짐, 검증 문제 등 다양한 상황에 대한 해결책은 [TroubleShooting.md](./TroubleShooting.md)를 참고하세요.

---

## 다음 단계

- [TroubleShooting.md](TroubleShooting.md) - 문제 해결 가이드
- [Project.md](Project.md) - 프로젝트 문서
- [CHANGELOG.md](CHANGELOG.md) - 변경 로그
- [GitHub Repository](https://github.com/goodlookingprokim/markdown-to-document-cli) - 소스 코드

---

**마지막 업데이트**: 2026-01-06 (v1.2.7)
