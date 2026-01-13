# 초보 개발자를 위한 NPM/NPX 완전 정복 가이드

> 🎯 이 가이드는 코딩을 처음 시작하는 분들을 위해, 파인만 기법과 스토리텔링로 쉽고 재미있게 설명합니다!

---

## 📖 이야기 시작: "마법의 도구 상자" 만들기

상상해 보세요. 여러분이 **"마법의 도구 상자"**를 만들려고 합니다.

이 도구 상자에는 **"마크다운 문서를 전자책으로 바꾸는 마법"**이 들어있어요.

- **NPM**: "마법 도구 상자"를 보관하는 **"국제 도구 창고"** 🏪
- **NPX**: 도구 창고에서 **"바로 꺼내 쓰는 마법 주문"** ✨
- **우리의 프로젝트**: 도구 창고에 등록할 **"우리만의 마법 도구"** 🧰

---

## 🎬 1단계: 개발 환경 설정 - "마법사의 작업실 준비하기"

### 왜 필요한가요?

마법사가 마법을 부리려면 **작업실**이 필요하죠? 
우리도 마법(코드)을 작성하려면 **개발 환경**이 필요합니다!

### 📋 체크리스트

#### 1. Node.js 설치 (마법의 기본 재료)

**비유**: Node.js는 마법사의 **"기본 마법 지팡이"**입니다. 이 없으면 아무 마법도 부릴 수 없어요!

**설치 확인**:
```bash
node --version
```

**출력 예시**:
```
v18.17.0  ✅ (18.0 이상이면 OK!)
```

**❌ 버전이 없거나 너무 낮다면?**

[Node.js 공식 사이트](https://nodejs.org/)에서 **LTS 버전**을 다운로드하세요.

> 💡 **팁**: LTS는 "Long Term Support"의 약자로, **"장기적으로 안정적인 버전"**이라는 뜻이에요. 초보자는 항상 LTS를 선택하세요!

---

#### 2. npm 확인 (국제 도구 창고 접속 확인)

**비유**: npm은 Node.js와 함께 자동으로 설치되는 **"도구 창고 앱"**입니다.

**설치 확인**:
```bash
npm --version
```

**출력 예시**:
```
9.6.7  ✅
```

---

#### 3. 프로젝트 폴더로 이동

**비유**: 우리의 "마법 도구 상자"를 만들 **작업실**로 들어가는 과정입니다.

```bash
cd /Users/jmacpro/tmp/windsurf/NpxMagicDoc
```

**현재 위치 확인**:
```bash
pwd
```

**출력 예시**:
```
/Users/jmacpro/tmp/windsurf/NpxMagicDoc  ✅
```

---

#### 4. 의존성 설치 (마법 재료 모으기)

**비유**: 마법 도구를 만들려면 **"마법 재료"**가 필요해요. npm이 이 재료들을 자동으로 모아줍니다!

**설치 명령어**:
```bash
npm install
```

**무슨 일이 일어나나요?**

```
📦 npm이 package.json을 읽습니다
📋 필요한 재료 목록을 확인합니다
🌍 인터넷에서 재료들을 다운로드합니다
📁 node_modules 폴더에 재료들을 저장합니다
✅ 설치 완료!
```

**설치 확인**:
```bash
ls -la node_modules | head -10
```

**출력 예시**:
```
drwxr-xr-x  ... commander
drwxr-xr-x  ... chalk
drwxr-xr-x  ... ora
drwxr-xr-x  ... inquirer
...  ✅ (많은 폴더가 보이면 성공!)
```

> 💡 **왜 이렇게 많은 폴더가 생기나요?**
> 
> 각 폴더는 **"작은 마법 도구"**입니다. 
> - `commander`: 명령어를 처리하는 도구
> - `chalk`: 터미널에 색깔을 입히는 도구
> - `ora`: 로딩 스피너를 보여주는 도구
> - `inquirer`: 사용자에게 질문하는 도구
> 
> 이 모든 도구들이 합쳐져서 우리의 "마법 도구 상자"가 됩니다!

---

#### 5. TypeScript 설치 (마법 언어 번역기)

**비유**: TypeScript는 우리가 쓴 **"마법 주문"**을 컴퓨터가 이해하는 **"기계어"**로 번역해주는 도구입니다.

**설치 확인**:
```bash
npm list typescript
```

**출력 예시**:
```
markdown-to-document-cli@1.2.7
└── typescript@5.3.3  ✅
```

---

### ✅ 1단계 완료 체크!

```bash
# 모든 것이 제대로 설치되었는지 확인
node --version    # v18.17.0 이상 ✅
npm --version     # 9.0 이상 ✅
ls node_modules   # 많은 폴더가 보임 ✅
```

---

## 🎬 2단계: 프로젝트 빌드 - "마법 도구 만들기"

### 왜 필요한가요?

우리가 작성한 **TypeScript 코드**는 컴퓨터가 바로 이해할 수 없어요. 
**"빌드"** 과정을 통해 **JavaScript**로 변환해야 합니다!

### 📋 빌드 과정

#### 1. TypeScript 컴파일 (마법 주문 번역)

**비유**: 우리가 쓴 **"마법 주문(TypeScript)"**을 컴퓨터가 이해하는 **"기계어(JavaScript)"**로 번역합니다.

**빌드 명령어**:
```bash
npm run build
```

**무슨 일이 일어나나요?**

```
📖 TypeScript 컴파일러가 src 폴더를 읽습니다
🔍 모든 .ts 파일을 찾습니다
🔄 .ts 파일을 .js 파일로 변환합니다
📁 dist 폴더에 변환된 파일들을 저장합니다
✅ 빌드 완료!
```

**출력 예시**:
```
> markdown-to-document-cli@1.2.7 build
> tsc

✅ 빌드 성공!
```

**빌드 결과 확인**:
```bash
ls -la dist
```

**출력 예시**:
```
drwxr-xr-x  ... types
drwxr-xr-x  ... utils
drwxr-xr-x  ... services
-rw-r--r--  ... index.js
-rw-r--r--  ... cli.js
...  ✅ (.js 파일들이 생성됨)
```

> 💡 **왜 dist 폴더가 생기나요?**
> 
> `dist`는 **"distribution"**의 약자로, **"배포용 폴더"**라는 뜻이에요. 
> 
> - `src/`: 우리가 작성한 원본 코드 (개발용)
> - `dist/`: 변환된 코드 (배포용)
> 
> 마치 **"요리 레시피(src)"**와 **"완성된 요리(dist)"**의 관계와 비슷해요!

---

#### 2. 로컬 테스트 (마법 도구 시험)

**비유**: 도구 창고에 보내기 전에, 우리의 **"마법 도구"**가 제대로 작동하는지 **시험**해봐야 합니다!

**로컬 링크 명령어**:
```bash
npm link
```

**무슨 일이 일어나나요?**

```
🔗 npm이 우리의 프로젝트를 전역 설치합니다
🌍 시스템 어디서든 우리의 도구를 사용할 수 있게 됩니다
✅ 링크 완료!
```

**테스트 명령어**:
```bash
m2d check
```

**출력 예시**:
```
🔍 Checking Dependencies...

✅ All dependencies are installed!
```

> 🎉 **축하합니다!** 
> 
> 이제 여러분의 컴퓨터 어디서든 `m2d` 명령어를 사용할 수 있어요!

---

### ✅ 2단계 완료 체크!

```bash
# 빌드 확인
ls dist  # .js 파일들이 있나요? ✅

# 로컬 테스트
m2d check  # 정상 작동하나요? ✅

# 도움말 확인
m2d --help  # 사용법이 보이나요? ✅
```

---

## 🎬 4단계: 타이포그래피 프리셋 이해 - "글꼴 디자인 마법 스크롤"

### 왜 필요한가요?

마법사가 마법을 부릴 때 **"마법 스크롤"**이 있으면 더 강력하고 아름다운 마법을 부릴 수 있죠?

우리의 도구도 **"타이포그래피 프리셋"**이라는 **"글꼴 디자인 마법 스크롤"**이 있어서 더 아름다운 전자책을 만들 수 있어요!

### 🎨 4가지 마법 스크롤 (프리셋)

#### 1. 소설 (Novel) - "동화책 마법 스크롤"

**비유**: 아름다운 동화책처럼 읽기 편한 스타일

- **용도**: 장편 소설, 에세이
- **특징**:
  - 📖 세리프 폰트 (책처럼 읽기 편한 폰트)
  - 📏 16pt 크기 (적당한 크기)
  - ↔️ 양쪽 정렬 (깔끔한 레이아웃)
  - ↩️ 들여쓰기 (첫 문단 들여쓰기)

**사용법**:
```bash
m2d novel.md --typography novel
```

#### 2. 발표 (Presentation) - "강의실 마법 스크롤"

**비유**: 강의실에서 발표할 때처럼 크고 명확한 스타일

- **용도**: 프레젠테이션, 강의 자료
- **특징**:
  - 🔤 산세리프 폰트 (모니터에서 읽기 편한 폰트)
  - 📏 18pt 크기 (큰 글씨)
  - 📐 넓은 여백 (깨끔한 공간)
  - ➡️ 왼쪽 정렬 (가독성 향상)

**사용법**:
```bash
m2d presentation.md --typography presentation
```

#### 3. 리뷰 (Review) - "검토실 마법 스크롤"

**비유**: 기술 문서처럼 정보가 많고 촘촘한 스타일

- **용도**: 검토용 문서, 기술 문서
- **특징**:
  - 🔤 산세리프 폰트
  - 📏 15pt 크기 (촘촘한 레이아웃)
  - 💻 코드 강조 (코드 블록 배경색)
  - 📝 인용구 스타일 (왼쪽 테두리)

**사용법**:
```bash
m2d review.md --typography review
```

#### 4. 전자책 (E-book) - "전자책 리더 마법 스크롤"

**비유**: 일반 전자책 리더에 최적화된 스타일

- **용도**: 일반 전자책
- **특징**:
  - 🔤 산세리프 폰트
  - 📏 14pt 크기 (균형잡힌 크기)
  - 📖 1.6 줄 간격 (읽기 편한 간격)
  - 🖼️ 이미지 캡션 (중앙 정렬)

**사용법**:
```bash
m2d ebook.md --typography ebook
```

#### 5. 표지 테마 - "마법의 책 커버"

**비유**: 책의 얼굴을 예쁘게 꾸며주는 마법입니다.

- **지원 테마**: Apple, Modern Gradient, Dark Tech, Nature
- **효과**: EPUB에는 고해상도 SVG 이미지가, PDF에는 전면 HTML 페이지가 자동으로 추가됩니다.

**사용법**:
```bash
m2d document.md --cover modern_gradient
```

### 🎯 프리셋 선택 가이드

| 문서 종류 | 추천 프리셋 | 이유 |
|-----------|-------------|------|
| 소설, 에세이 | `novel` | 책처럼 읽기 편함 |
| 발표 자료 | `presentation` | 크고 명확함 |
| 기술 문서 | `review` | 정보 밀도 높음 |
| 일반 전자책 | `ebook` | 균형잡힌 스타일 |

---

## 🎬 5단계: 폰트 서브세팅 이해 - "마법 폰트 축소술"

### 왜 필요한가요?

**비유**: 마법사가 **"거대한 마법 폰트"**를 가지고 있지만, 실제로는 **"필요한 글자만"** 사용해요!

폰트 파일은 매우 큽니다 (수십 MB!). 하지만 우리 문서에 실제로 사용되는 글자는 일부분뿐이에요.

**폰트 서브세팅**은 **"필요한 글자만 남기고 나머지는 삭제"**해서 파일 크기를 **99% 감소**시키는 마법입니다!

### 🔮 마법 작동 원리

```
1. 전체 폰트: 50MB (한글 + 영문 + 특수문자 + 이모지...)
   ↓
2. 문서 분석: 우리 문서에 어떤 글자가 있는지 확인
   ↓
3. 필요한 글자만 추출: 예) "가나다라ABC123!"
   ↓
4. 서브셋 생성: 필요한 글자만 포함한 폰트 생성
   ↓
5. 결과: 0.5MB (99% 감소!) ✨
```

### 📊 실제 예시

**전체 폰트**:
- 크기: 50MB
- 포함: 모든 한글, 영문, 특수문자, 이모지...

**서브셋 폰트**:
- 크기: 0.5MB
- 포함: 문서에 실제 사용된 글자만

### 🚀 사용법

```bash
m2d document.md --font-subsetting
```

### 💡 장점

1. **파일 크기 감소**: 99% 크기 감소
2. **빠른 로딩**: 작은 파일로 빠른 로딩
3. **캐싱**: 재사용을 위한 폰트 캐시
4. **다양한 형식**: WOFF2, TTF, OTF 지원

---

## 🎬 6단계: NPM 계정 생성 - "국제 도구 창고 회원가입"

### 왜 필요한가요?

우리의 "마법 도구"를 **"국제 도구 창고(NPM)"**에 등록하려면 **"회원가입"**이 필요해요!

### 📋 계정 생성 과정

#### 1. NPM 웹사이트 방문

**URL**: https://www.npmjs.com/

#### 2. 회원가입

1. **Sign Up** 버튼 클릭
2. **이메일** 입력
3. **사용자명(username)** 입력
   - 💡 **팁**: 이 이름이 패키지 이름 앞에 붙습니다!
   - 예: `@username/package-name`
4. **비밀번호** 입력
5. **이메일 인증**

#### 3. 터미널에서 로그인

**비유**: 도구 창고에 **"출입 카드"**를 찍는 과정입니다.

**로그인 명령어**:
```bash
npm login
```

**입력해야 할 정보**:
```
Username: your-username
Password: ********
Email: your-email@example.com
```

**출력 예시**:
```
Logged in as your-username on https://registry.npmjs.org/  ✅
```

**로그인 확인**:
```bash
npm whoami
```

**출력 예시**:
```
your-username  ✅
```

---

### ✅ 6단계 완료 체크!

```bash
# 로그인 확인
npm whoami  # 사용자명이 보이나요? ✅
```

---

## 🎬 7단계: 패키지 배포 - "도구 창고에 도구 등록하기"

### 왜 필요한가요?

우리의 "마법 도구"를 **전 세계 사람들이 사용할 수 있도록** 도구 창고에 등록하는 과정입니다!

### 📋 배포 과정

#### 1. package.json 확인

**비유**: 도구 창고에 등록할 **"도구 설명서"**를 확인합니다.

**파일 열기**:
```bash
cat package.json
```

**중요 필드 확인**:

```json
{
  "name": "markdown-to-document-cli",  // 패키지 이름
  "version": "1.1.5",                   // 버전
  "description": "...",                 // 설명
  "main": "dist/index.js",              // 진입점
  "bin": {
    "m2d": "dist/cli.js"               // CLI 명령어
  },
  "author": "your-name",                // 작성자
  "license": "MIT"                      // 라이선스
}
```

> 💡 **패키지 이름 규칙**:
> - 소문자만 사용
> - 하이픈(-)으로 단어 구분
> - 이미 존재하는 이름은 사용 불가
> - 예: `markdown-to-document-cli` ✅

---

#### 2. 배포 전 최종 테스트

**비유**: 도구 창고에 보내기 전, 마지막으로 **"도구가 제대로 작동하는지"** 확인합니다.

**빌드 재확인**:
```bash
npm run build
```

**로컬 테스트**:
```bash
m2d check
```

---

#### 3. 패키지 배포

**비유**: 드디어 우리의 "마법 도구"를 **"국제 도구 창고"**에 등록합니다!

**배포 명령어**:
```bash
npm publish
```

**무슨 일이 일어나나요?**

```
📦 npm이 package.json을 읽습니다
📁 dist 폴더의 모든 파일을 압축합니다
🌍 NPM 레지스트리로 업로드합니다
✅ 패키지 등록 완료!
```

**출력 예시**:
```
npm notice 
npm notice 📦  markdown-to-document-cli@1.1.5
npm notice === Tarball Contents === 
npm notice 1.2kB  dist/types/index.d.ts
npm notice ...
npm notice === Tarball Details === 
npm notice name:          markdown-to-document-cli
npm notice version:       1.1.5
npm notice version:       1.0.0
npm notice ...
npm notice 
+ markdown-to-document-cli@1.0.0
```

> 🎉 **축하합니다!** 
> 
> 이제 전 세계 누구나 여러분의 "마법 도구"를 사용할 수 있어요!

---

#### 4. 배포 확인

**웹사이트에서 확인**:
1. https://www.npmjs.com/package/markdown-to-document-cli 방문
2. 패키지 정보 확인

**터미널에서 확인**:
```bash
npm view markdown-to-document-cli
```

**출력 예시**:
```
{
  name: 'markdown-to-document-cli',
  version: '1.0.0',
  description: '...',
  ...
}  ✅
```

---

### ✅ 4단계 완료 체크!

```bash
# 패키지 정보 확인
npm view markdown-to-document-cli  # 정보가 보이나요? ✅

# 웹사이트 확인
# https://www.npmjs.com/package/markdown-to-document-cli
```

---

## 🎬 5단계: NPX 사용 - "마법 주문으로 도구 사용하기"

### 왜 필요한가요?

**NPX**는 **"설치 없이 바로 사용하는 마법 주문"**입니다!

### 📋 NPX 사용법

#### 1. 기본 사용

**비유**: 도구 창고에서 **"마법 주문"**을 외우면, 도구가 **"바로 나타나서 작동"**합니다!

**명령어**:
```bash
npx markdown-to-document-cli --help
```

**출력 예시**:
```
Usage: m2d [options] [command]

Options:
  -V, --version        output the version number
  -h, --help           display help for command

Commands:
  interactive          Interactive mode
  list-presets         List available typography presets
  list-themes          List available cover themes
  check                Check dependencies
```

---

#### 2. 실제 변환 테스트

**테스트 파일 생성**:
```bash
echo "# 테스트 문서

이것은 테스트 문서입니다.

## 첫 번째 챕터

테스트 내용입니다.
" > test.md
```

**변환 실행**:
```bash
npx markdown-to-document-cli test.md
```

**출력 예시**:
```
📚 Markdown to Document CLI

🔍 Checking Dependencies...
✅ All dependencies are installed!

📄 Input: /Users/username/test.md
📤 Format: BOTH
🎨 Typography: 균형 레이아웃

🔄 Converting document...
✅ Conversion completed!

✅ Output files:
  📖 EPUB:  /Users/username/test.epub
  📄 PDF:   /Users/username/test.pdf

🎉 Conversion successful!
```

---

#### 3. NPX vs npm install

| 비교 항목 | NPX | npm install |
|---------|-----|-------------|
| **설치** | 필요 없음 | 필요함 |
| **사용** | `npx package-name` | `package-name` |
| **속도** | 첫 실행 느림 | 빠름 |
| **디스크** | 임시 저장 | 영구 저장 |
| **용도** | 일회성 사용 | 자주 사용 |

**비유**:
- **NPX**: **"렌터카"** - 필요할 때 빌려서 쓰고 반납
- **npm install**: **"내 차"** - 한 번 사서 계속 사용

---

### ✅ 5단계 완료 체크!

```bash
# NPX 테스트
npx markdown-to-document-cli --help  # 도움말이 보이나요? ✅

# 실제 변환
npx markdown-to-document-cli test.md  # EPUB/PDF 파일이 생성되나요? ✅
```

---

## 🎬 6단계: 버전 업데이트 - "마법 도구 개선하기"

### 왜 필요한가요?

도구를 개선하면 **"새 버전"**으로 등록해야 해요!

### 📋 버전 업데이트 과정

#### 1. 버전 규칙 (Semantic Versioning)

**형식**: `MAJOR.MINOR.PATCH`

- **MAJOR (주 버전)**: 호환되지 않는 변경
  - 예: `1.0.0` → `2.0.0`
- **MINOR (부 버전)**: 새로운 기능 추가 (호환됨)
  - 예: `1.0.0` → `1.1.0`
- **PATCH (수정 버전)**: 버그 수정
  - 예: `1.0.0` → `1.0.1`

**비유**:
- **MAJOR**: "완전히 새로운 도구" 만들기
- **MINOR**: "기능 추가" 하기
- **PATCH**: "고장 난 부분" 수리하기

---

#### 2. 버전 업데이트

**명령어**:
```bash
# PATCH 버전 업데이트
npm version patch

# MINOR 버전 업데이트
npm version minor

# MAJOR 버전 업데이트
npm version major
```

**출력 예시**:
```
v1.0.1
```

**package.json 확인**:
```bash
cat package.json | grep version
```

**출력 예시**:
```
"version": "1.0.1",  ✅
```

---

#### 3. 재배포

**빌드**:
```bash
npm run build
```

**배포**:
```bash
npm publish
```

---

### ✅ 6단계 완료 체크!

```bash
# 버전 확인
npm view markdown-to-document-cli version  # 새 버전이 보이나요? ✅
```

---

## 🎉 전체 과정 요약

### 📋 체크리스트

```bash
✅ 1단계: 개발 환경 설정
   - Node.js 설치 (v18+)
   - npm 확인
   - 프로젝트 폴더 이동
   - npm install (의존성 설치)

✅ 2단계: 프로젝트 빌드
   - npm run build (TypeScript 컴파일)
   - npm link (로컬 테스트)
   - m2d check (작동 확인)

✅ 3단계: NPM 계정 생성
   - npmjs.com 가입
   - npm login (터미널 로그인)
   - npm whoami (로그인 확인)

✅ 4단계: 패키지 배포
   - package.json 확인
   - npm publish (배포)
   - npm view (배포 확인)

✅ 5단계: NPX 사용
   - npx markdown-to-document-cli --help
   - npx markdown-to-document-cli test.md
   - 변환 결과 확인

✅ 6단계: 버전 업데이트
   - npm version patch/minor/major
   - npm run build
   - npm publish
```

---

## 🎓 핵심 개념 정리

### NPM (Node Package Manager)

**비유**: **"국제 도구 창고"** 🏪

- **역할**: 수많은 도구들을 보관하고 배포
- **사용**: 도구 설치, 관리, 공유
- **명령어**: `npm install`, `npm publish`

### NPX (Node Package eXecute)

**비유**: **"마법 주문"** ✨

- **역할**: 설치 없이 도구 바로 실행
- **사용**: 일회성 도구 사용
- **명령어**: `npx package-name`

### Package.json

**비유**: **"도구 설명서"** 📋

- **역할**: 패키지 정보 정의
- **내용**: 이름, 버전, 의존성, 스크립트
- **필수**: 모든 NPM 패키지에 필요

### node_modules

**비유**: **"마법 재료 창고"** 📦

- **역할**: 설치된 패키지들 저장
- **자동 생성**: `npm install` 실행 시
- **무시**: `.gitignore`에 포함

### dist (Distribution)

**비유**: **"배포용 폴더"** 📁

- **역할**: 변환된 코드 저장
- **생성**: `npm run build` 실행 시
- **내용**: .js 파일들

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: npm install이 너무 오래 걸려요!

**A**: 네트워크 속도나 의존성 수량에 따라 다릅니다.
- **해결책**: 인내심을 가지고 기다리세요! ☕

### Q2: 배포할 때 "403 Forbidden" 오류가 떠요!

**A**: 패키지 이름이 이미 사용 중입니다.
- **해결책**: `package.json`에서 이름을 변경하세요.

### Q3: NPX가 작동하지 않아요!

**A**: NPM 버전이 너무 낮을 수 있습니다.
- **해결책**: `npm install -g npm@latest`로 업그레이드하세요.

### Q4: 배포 후 수정하고 싶어요!

**A**: 새 버전으로 배포해야 합니다.
- **해결책**: `npm version patch` → `npm publish`

### Q5: 패키지를 삭제하고 싶어요!

**A**: NPM 웹사이트에서 삭제할 수 있습니다.
- **해결책**: 24시간 이내에만 가능합니다!

---

## 🎯 다음 단계

이제 여러분은 **"마법 도구 상자"**를 만들고 **"국제 도구 창고"**에 등록하는 모든 과정을 마쳤습니다!

### 계속 배우고 싶다면:

1. **다른 패키지들 살펴보기**
   ```bash
   npm view react
   npm view lodash
   ```

2. **내 패키지 개선하기**
   - 새로운 기능 추가
   - 버그 수정
   - 문서 개선

3. **오픈소스 기여하기**
   - 다른 사람의 패키지에 기여
   - 이슈 리포트
   - 풀 리퀘스트

---

## 🌟 축하합니다!

여러분은 이제 **NPM/NPX 마법사**가 되었습니다! 🎉

전 세계 개발자들이 여러분의 "마법 도구"를 사용할 수 있게 되었습니다.

계속해서 더 멋진 도구들을 만들어 보세요!

---

**작성자**: 잘생김프로쌤  
**마지막 업데이트**: 2026-01-06 (v1.2.7)

---

## 📞 도움이 필요하시면?

- **GitHub Issues**: https://github.com/goodlookingprokim/markdown-to-document-cli/issues
- **Email**: edulovesai@gmail.com
- **NPM 패키지**: https://www.npmjs.com/package/markdown-to-document-cli

---

**행운을 빕니다! 🍀**
