# TroubleShooting.md - 문제 해결 가이드

이 가이드는 Markdown to Document CLI 사용 중 발생할 수 있는 일반적인 문제와 해결 방법을 제공합니다.

## 목차

1. [설치 문제](#설치-문제)
2. [Pandoc 관련 문제](#pandoc-관련-문제)
3. [변환 문제](#변환-문제)
4. [이미지 문제](#이미지-문제)
5. [PDF 관련 문제](#pdf-관련-문제)
6. [타이포그래피 관련 문제](#타이포그래피-관련-문제)
7. [폰트 서브세팅 관련 문제](#폰트-서브세팅-관련-문제)
8. [성능 문제](#성능-문제)
9. [기타 문제](#기타-문제)

---

## 설치 문제

### 문제: "command not found: m2d"

**증상**:
```bash
m2d document.md
# zsh: command not found: m2d
```

**원인**:
- 전역 설치가 완료되지 않음
- PATH에 npm global bin이 포함되지 않음

**해결 방법**:

1. 전역 설치 확인:
```bash
npm list -g markdown-to-document-cli
```

2. 재설치:
```bash
npm uninstall -g markdown-to-document-cli
npm install -g markdown-to-document-cli
```

3. PATH 확인:
```bash
# npm global bin 경로 확인
npm config get prefix

# PATH에 추가 (macOS/Linux)
export PATH="$(npm config get prefix)/bin:$PATH"

# .zshrc 또는 .bashrc에 영구 추가
echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

4. 또는 npx 사용:
```bash
npx markdown-to-document-cli document.md
```

### 문제: "Cannot find module 'xxx'"

**증상**:
```bash
Error: Cannot find module 'commander'
```

**원인**:
- node_modules가 설치되지 않음
- 의존성 손상

**해결 방법**:

```bash
# node_modules 삭제
rm -rf node_modules package-lock.json

# 재설치
npm install

# 빌드
npm run build
```

### 문제: TypeScript 컴파일 오류

**증상**:
```bash
error TS2307: Cannot find module 'fs'
```

**원인**:
- @types/node가 설치되지 않음

**해결 방법**:

```bash
npm install --save-dev @types/node
```

---

## Pandoc 관련 문제

### 문제: "Pandoc을 찾을 수 없습니다"

**증상**:
```
❌ Error: Pandoc을 찾을 수 없습니다. Pandoc을 설치하세요.
```

**원인**:
- Pandoc이 설치되지 않음
- PATH에 Pandoc이 없음

**해결 방법**:

1. Pandoc 설치 확인:
```bash
pandoc --version
```

2. Pandoc 설치:

**macOS**:
```bash
brew install pandoc
```

**Windows**:
```bash
winget install --id JohnMacFarlane.Pandoc
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install pandoc
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install pandoc
```

3. 커스텀 경로 지정:
```bash
m2d document.md --pandoc-path /usr/local/bin/pandoc
```

4. 의존성 확인:
```bash
m2d check
```

### 문제: "Pandoc version too old"

**증상**:
```
Error: Pandoc 2.19+ is required
```

**원인**:
- Pandoc 버전이 너무 오래됨

**해결 방법**:

1. 현재 버전 확인:
```bash
pandoc --version
```

2. 업그레이드:

**macOS**:
```bash
brew upgrade pandoc
```

**Windows**:
```bash
winget upgrade --id JohnMacFarlane.Pandoc
```

**Linux**:
```bash
sudo apt-get update
sudo apt-get install --only-upgrade pandoc
```

### 문제: Pandoc 변환 실패

**증상**:
```
❌ EPUB 변환 실패: pandoc: error ...
```

**원인**:
- Pandoc 인자 오류
- 입력 파일 문제
- Pandoc 버전 호환성

**해결 방법**:

1. 상세 로그 확인:
```bash
m2d document.md --verbose
```

2. Pandoc 버전 확인:
```bash
pandoc --version
```

3. 입력 파일 검증:
```bash
# 파일 존재 확인
ls -la document.md

# 파일 내용 확인
cat document.md | head -20
```

4. 간단한 테스트:
```bash
# 직접 Pandoc 실행
pandoc document.md -o test.epub
```

---

## 변환 문제

### 문제: 파일 경로에 백슬래시가 포함되어 오류 발생

**증상**:
```
❌ 파일을 찾을 수 없습니다: /Users/username/My\ Documents/file.md
>> 파일을 찾을 수 없습니다.
```

**원인**:
- 경로에 백슬래시 이스케이프(`\`)가 포함됨
- 공백이 있는 디렉토리명에서 자주 발생
- 터미널 자동완성이나 복사-붙여넣기 시 발생

**해결 방법**:

**방법 1: 드래그 앤 드롭 (가장 쉬움)**
```bash
# 파일을 터미널 창으로 드래그하세요
# 경로가 자동으로 올바르게 입력됩니다
```

**방법 2: 따옴표로 감싸기**
```bash
# 큰따옴표 사용
m2d "/Users/username/My Documents/file.md"

# 작은따옴표 사용
m2d '/Users/username/My Documents/file.md'
```

**방법 3: 백슬래시 제거**
```bash
# ❌ 잘못된 예
m2d /Users/username/My\ Documents/file.md

# ✅ 올바른 예
m2d "/Users/username/My Documents/file.md"
```

**자동 수정 기능**:
CLI가 자동으로 다음을 처리합니다:
- 백슬래시 이스케이프 제거
- 따옴표 제거
- 경로 정규화
- 파일 존재 여부 확인

---

### 문제: "입력 파일을 찾을 수 없습니다"

**증상**:
```
❌ Error: Input file not found: /path/to/document.md
```

**원인**:
- 파일 경로 오류
- 파일이 존재하지 않음

**해결 방법**:

1. 파일 존재 확인:
```bash
ls -la /path/to/document.md
```

2. 상대 경로 사용:
```bash
# 현재 디렉토리
m2d document.md

# 상대 경로
m2d ./docs/document.md
```

3. 절대 경로 사용:
```bash
m2d /Users/username/docs/document.md
```

### 문제: "검증 오류: N개 발견"

**증상**:
```
❌ 검증 오류: 3개 발견
```

**원인**:
- 문서에 구문 오류가 있음
- 검증 모듈이 문제를 감지

**해결 방법**:

1. 상세 로그 확인:
```bash
m2d document.md --verbose
```

2. 자동 수정 활성화:
```bash
m2d document.md
```

3. 검증 건너뛰기:
```bash
m2d document.md --no-validate
```

4. 수동 수정:
검증 리포트를 확인하고 문제를 직접 수정

### 문제: YAML 구문 오류

**증상**:
```
⚠️ YAML 구문 오류: 콜론(:)이 누락됨
```

**원인**:
- YAML frontmatter 구문 오류

**해결 방법**:

**잘못된 예**:
```yaml
---
title 문서 제목
author 저자명
---
```

**올바른 예**:
```yaml
---
title: 문서 제목
author: 저자명
---
```

### 문제: Obsidian 링크 변환 오류

**증상**:
```
⚠️ 경고: Obsidian 링크 발견
```

**원인**:
- Obsidian 링크 문법 사용

**해결 방법**:

1. 자동 수정 확인:
```bash
m2d document.md
```

2. 수동 변환:
```markdown
<!-- Obsidian 문법 -->
[[링크]]

<!-- 표준 마크다운 -->
[링크](링크.md)
```

---

## 이미지 문제

### 문제: "Image not found"

**증상**:
```
⚠️ Image not found: ./images/photo.png
```

**원인**:
- 이미지 파일이 존재하지 않음
- 경로가 잘못됨

**해결 방법**:

1. 이미지 존재 확인:
```bash
ls -la ./images/photo.png
```

2. 이미지 위치 확인:
이미지는 다음 위치에서 검색됩니다:
- 마크다운 파일과 동일한 디렉토리
- `images/` 폴더
- `attachments/` 폴더
- `assets/` 폴더
- `media/` 폴더

3. 절대 경로 사용:
```markdown
![설명](/absolute/path/to/image.png)
```

4. 이미지 복사:
```bash
cp /path/to/image.png ./images/
```

### 문제: "지원하지 않는 이미지 형식"

**증상**:
```
⚠️ 지원하지 않는 이미지 형식: bmp
```

**원인**:
- 지원하지 않는 이미지 형식 사용

**해결 방법**:

지원하는 형식:
- PNG
- JPG/JPEG
- GIF
- SVG
- WebP

변환:
```bash
# BMP → PNG
convert image.bmp image.png

# 또는 온라인 변환 도구 사용
```

### 문제: 이미지 alt 텍스트 경고

**증상**:
```
⚠️ 이미지 alt 텍스트가 없습니다.
```

**원인**:
- 접근성을 위해 alt 텍스트가 필요함

**해결 방법**:

```markdown
<!-- 잘못된 예 -->
![](image.png)

<!-- 올바른 예 -->
![이미지 설명](image.png)
```

---

## PDF 관련 문제

### 문제: "PDF 변환 실패 - PDF 엔진을 찾을 수 없습니다"

**증상**:
```
❌ PDF 변환 실패: xelatex not found. Please select a different --pdf-engine or install xelatex
```
또는
```
❌ PDF 엔진을 찾을 수 없습니다. WeasyPrint, XeLaTeX, 또는 PDFLaTeX를 설치하세요.
```

**원인**:
- PDF 생성에 필요한 엔진(WeasyPrint, XeLaTeX, PDFLaTeX)이 설치되지 않음
- `--pdf-engine=auto` 옵션 사용 시 사용 가능한 엔진이 없음

**해결 방법**:

**옵션 1: WeasyPrint 설치 (권장)**
```bash
# Python pip 사용
pip install weasyprint

# 또는 Python 3
pip3 install weasyprint
```

**옵션 2: XeLaTeX 설치 (한글 지원 우수)**
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

# Windows
# https://www.tug.org/texlive/ 에서 설치 프로그램 다운로드
```

**옵션 3: PDFLaTeX 설치**
```bash
# macOS
brew install --cask basictex

# Linux (Ubuntu/Debian)
sudo apt-get install texlive-latex-base

# Windows
# https://www.tug.org/texlive/ 에서 설치 프로그램 다운로드
```

**설치 확인**:
```bash
# WeasyPrint 확인
weasyprint --version

# XeLaTeX 확인
xelatex --version

# PDFLaTeX 확인
pdflatex --version
```

**특정 엔진 지정**:
```bash
# 자동 선택 (기본값)
m2d document.md --pdf-engine auto

# WeasyPrint 사용
m2d document.md --pdf-engine weasyprint

# XeLaTeX 사용
m2d document.md --pdf-engine xelatex

# PDFLaTeX 사용
m2d document.md --pdf-engine pdflatex
```

### 문제: 한글 폰트 렌더링 오류

**증상**:
```
PDF에서 한글이 깨짐
```

**원인**:
- PDF 엔진이 한글 폰트를 찾지 못함

**해결 방법**:

1. XeLaTeX 사용:
```bash
m2d document.md --format pdf --pdf-engine xelatex
```

2. 시스템 폰트 확인:
```bash
# macOS
fc-list :lang=ko

# Linux
fc-list :lang=ko
```

3. 커스텀 CSS 사용:
```css
@font-face {
  font-family: 'Noto Sans CJK KR';
  src: url('/path/to/NotoSansCJKkr-Regular.otf');
}

body {
  font-family: 'Noto Sans CJK KR', sans-serif;
}
```

### 문제: PDF 페이지 레이아웃 오류

**증상**:
```
PDF에서 여백이나 페이지 크기가 이상함, 또는 레이아웃이 완전히 엉망으로 표시됨
```

**원인**:
- 구 버전(v1.1.4 이하): 표지 생성 시 전체 HTML 구조 중복으로 인한 레이아웃 붕괴
- `box-sizing` 설정 미비로 인한 여백 계산 오류
- 한글 텍스트의 부자연스러운 줄바꿈

**해결 방법**:

1. **최신 버전 업데이트 (권장)**:
   v1.1.5부터는 HTML Fragment 방식을 사용하여 레이아웃 붕괴 문제를 완전히 해결했습니다.
   ```bash
   npx markdown-to-document-cli@latest interactive
   ```

2. **커스텀 CSS 조정**:
   여백 문제가 지속된다면 `box-sizing: border-box`가 적용되어 있는지 확인하세요.

3. **한글 가독성 설정**:
   v1.1.5+ 에서는 `word-break: keep-all`이 기본 적용되어 단어 단위로 줄바꿈이 일어납니다.

---

## 타이포그래피 관련 문제

### 문제: "Typography preset not found"

**증상**:
```bash
Error: Typography preset not found: custom
```

**원인**:
- 존재하지 않는 타이포그래피 프리셋 지정

**해결 방법**:

1. 사용 가능한 프리셋 확인:
```bash
m2d list-presets
```

2. 올바른 프리셋 사용:
```bash
# 올바른 프리셋
m2d document.md --typography novel
m2d document.md --typography presentation
m2d document.md --typography review
m2d document.md --typography ebook
```

### 문제: 폰트가 올바르게 적용되지 않음

**증상**:
```
변환된 문서에서 폰트가 기본 폰트로 표시됨
```

**원인**:
- 시스템에 해당 폰트가 설치되지 않음
- CSS가 올바르게 적용되지 않음

**해결 방법**:

1. 한국어 폰트 설치 확인:
```bash
# macOS
fc-list | grep -i "noto"

# Linux
fc-list | grep -i "noto"
```

2. 커스텀 CSS 사용:
```bash
m2d document.md --css custom.css
```

`custom.css` 예시:
```css
@font-face {
  font-family: 'Noto Sans CJK KR';
  src: url('NotoSansCJKKR-Regular.woff2') format('woff2');
}

body {
  font-family: 'Noto Sans CJK KR', sans-serif;
}
```

3. 시스템 폰트 사용:
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

### 문제: 페이지 여백이 올바르지 않음

**증상**:
```
PDF에서 여백이 너무 넓거나 좁음
```

**원인**:
- 타이포그래피 프리셋의 여백 설정이 적합하지 않음

**해결 방법**:

1. 다른 프리셋 시도:
```bash
# 넓은 여백이 필요한 경우
m2d document.md --typography presentation

# 좁은 여백이 필요한 경우
m2d document.md --typography review
```

2. 커스텀 CSS로 여백 조정:
```css
@page {
  margin-top: 20mm;
  margin-bottom: 20mm;
  margin-left: 15mm;
  margin-right: 15mm;
}
```

### 문제: EPUB에서 한글 폰트가 깨지거나 기본 서체로 보임

**증상**:
```
전자책 리더기에서 한글이 명조/고딕이 아닌 시스템 기본 서체로 표시됨
```

**원인**:
- EPUB 파일 내부에 폰트가 직접 포함(Embedding)되지 않음

**해결 방법**:

1. **자동 임베딩 사용 (v1.1.4+)**:
   최신 버전은 macOS 시스템의 Noto Sans/Serif KR 폰트를 자동으로 찾아 EPUB에 포함시킵니다. 별도의 설정 없이 변환하세요.

2. **폰트 서브세팅 활성화**:
   파일 용량을 줄이면서 폰트를 확실히 포함하려면 `--font-subsetting` 옵션을 사용하세요.
   ```bash
   m2d document.md --font-subsetting
   ```

---

## 폰트 서브세팅 관련 문제

### 문제: "Font not found"

**증상**:
```bash
Error: Input font not found: /path/to/font.ttf
```

**원인**:
- 폰트 파일 경로가 올바르지 않음
- 폰트 파일이 존재하지 않음

**해결 방법**:

1. 폰트 파일 경로 확인:
```bash
ls -la /path/to/font.ttf
```

2. 상대 경로 사용:
```bash
# 프로젝트 내 fonts 폴더
m2d document.md --font-subsetting
```

3. 절대 경로 사용:
```bash
m2d document.md --font-subsetting --font-path /absolute/path/to/font.ttf
```

### 문제: 폰트 서브세팅이 작동하지 않음

**증상**:
```
폰트 서브세팅 옵션을 사용해도 파일 크기가 감소하지 않음
```

**원인**:
- fontkit이 설치되지 않음
- 폰트 형식이 지원되지 않음

**해결 방법**:

1. fontkit 설치 확인:
```bash
npm list fontkit
```

2. fontkit 재설치:
```bash
npm uninstall fontkit
npm install fontkit
```

3. 지원되는 폰트 형식 확인:
```bash
# 지원되는 형식: TTF, OTF, WOFF, WOFF2
file font.ttf
```

4. 폰트 형식 변환:
```bash
# TTF을 WOFF2로 변환 (예시)
pip install fonttools
pyftsubset font.ttf --output-file=font.woff2 --flavor=woff2
```

### 문제: 캐시 문제

**증상**:
```
폰트 캐시가 오래된 폰트를 사용함
```

**원인**:
- 폰트 캐시가 갱신되지 않음

**해결 방법**:

1. 캐시 삭제:
```bash
# 프로젝트 내 캐시 삭제
rm -rf .font-cache

# 시스템 임시 캐시 삭제
rm -rf /tmp/markdown-to-document-pandoc/font-cache
```

2. 캐시 비활성화 후 재시도:
```bash
m2d document.md --no-cache
```

---

## 성능 문제

### 문제: 변환이 너무 느림

**증상**:
```
대용량 문서 변환 시 시간이 오래 걸림
```

**원인**:
- 많은 이미지
- 복잡한 문서 구조
- 느린 PDF 엔진

**해결 방법**:

1. 이미지 최적화:
```bash
# 이미지 압축
convert image.png -quality 85 image-optimized.png

# 이미지 크기 조정
convert image.png -resize 1920x1080 image-resized.png
```

2. 검증 건너뛰기:
```bash
m2d document.md --no-validate
```

3. 더 빠른 PDF 엔진 사용:
```bash
m2d document.md --format pdf --pdf-engine pdflatex
```

4. 폰트 서브세팅:
```bash
m2d document.md --font-subsetting
```

### 문제: 메모리 부족

**증상**:
```
JavaScript heap out of memory
```

**원인**:
- 대용량 문서 처리
- Node.js 메모리 제한

**해결 방법**:

```bash
# 메모리 증가
NODE_OPTIONS="--max-old-space-size=4096" m2d document.md
```

---

## 기타 문제

### 문제: 권한 오류

**증상**:
```
Error: EACCES: permission denied
```

**원인**:
- 쓰기 권한 없음
- 전역 설치 권한 문제

**해결 방법**:

1. 출력 디렉토리 권한 확인:
```bash
ls -la ./output
chmod 755 ./output
```

2. sudo 사용 (macOS/Linux):
```bash
sudo npm install -g markdown-to-document-cli
```

3. npx 사용 (권한 문제 회피):
```bash
npx markdown-to-document-cli document.md
```

### 문제: 임시 파일 정리

**증상**:
```
임시 파일이 남아있음
```

**원인**:
- 변환 중단으로 임시 파일 미정리

**해결 방법**:

```bash
# 임시 파일 삭제
rm -rf /tmp/markdown-to-document

# 또는
rm -rf $TMPDIR/markdown-to-document
```

### 문제: 디버깅

**증상**:
```
자세한 오류 정보가 필요함
```

**해결 방법**:

1. 상세 로그 활성화:
```bash
m2d document.md --verbose
```

2. DEBUG 환경 변수:
```bash
DEBUG=true m2d document.md
```

3. Pandoc 직접 실행:
```bash
pandoc document.md -o test.epub --verbose
```

---

## 도움 요청

위의 해결 방법으로 문제가 해결되지 않으면:

1. **정보 수집**:
```bash
# 버전 정보
m2d --version
node --version
npm --version
pandoc --version

# 상세 로그
m2d document.md --verbose > debug.log 2>&1
```

2. **GitHub Issues**:
   - [새 이슈 생성](https://github.com/goodlookingprokim/markdown-to-document-cli/issues)
   - 디버그 로그와 오류 메시지 포함

3. **Email**:
   - edulovesai@gmail.com

---

## 자주 묻는 질문 (FAQ)

### Q: 옵시디언 없이 사용할 수 있나요?
A: 네, 옵시디언 플러그인에서 독립형 CLI 도구로 변환되었습니다. 옵시디언 없이 사용할 수 있습니다.

### Q: Windows에서 사용할 수 있나요?
A: 네, Windows, macOS, Linux 모두 지원합니다.

### Q: 상업적으로 사용할 수 있나요?
A: 네, MIT 라이선스로 상업적 사용이 가능합니다.

### Q: 한글 지원하나요?
A: 네, 완벽하게 한글을 지원합니다.

### Q: 배치 처리가 가능한가요?
A: 현재는 단일 파일만 지원합니다. 배치 처리는 향후 계획에 있습니다.

---

**마지막 업데이트**: 2026-01-06 (v1.2.7)
