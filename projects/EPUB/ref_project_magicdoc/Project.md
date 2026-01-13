# Project.md - Markdown to Document CLI

> **Current Version**: v1.2.7 | **Last Updated**: 2026-01-06

## 프로젝트 개요

**Markdown to Document CLI**는 옵시디언 플러그인 "Markdown to Document Pro"의 핵심 기능을 NPM/NPX 패키지로 변환한 프로젝트입니다. 마크다운 문서를 전문 출판 수준의 EPUB/PDF로 변환하는 CLI 도구를 제공합니다.

## 프로젝트 목표

1. **옵시디언 종속성 제거**: 옵시디언 플러그인 API 의존성을 제거하고 독립형 CLI 도구로 변환
2. **NPM/NPX 패키지화**: 전역 설치 없이 `npx`로 바로 사용 가능한 패키지 제공
3. **핵심 기능 유지**: 8개 검증 모듈, 타이포그래피 프리셋, 자동 수정 등 핵심 기능 보존
4. **사용성 향상**: 인터랙티브 모드, 상세한 오류 메시지, 진행 상황 표시
5. **보안 강화**: SSH 기반 Git 인증, 환경변수 토큰 주입 차단, 안전한 credential 관리

## 기술 스택

### 핵심 기술
- **언어**: TypeScript 5.3+
- **런타임**: Node.js 18+
- **모듈 시스템**: ES Modules (`type: "module"`)
- **번들러**: TypeScript Compiler (tsc)

### CLI 프레임워크
- **Commander.js**: CLI 인터페이스 프레임워크
- **Chalk**: 터미널 색상 출력
- **Ora**: 로딩 스피너
- **Inquirer**: 인터랙티브 프롬프트

### 변환 엔진
- **Pandoc 2.19+**: 문서 변환 엔진
- **WeasyPrint**: PDF 생성 엔진 (선택사항)

### 유틸리티
- **fontkit**: 폰트 처리 및 서브세팅
- **glob**: 파일 패턴 매칭
- **yaml**: YAML 파싱

## 아키텍처

### 디렉토리 구조

```
src/
├── types/              # 타입 정의
│   ├── index.ts       # 핵심 타입 (ConversionOptions, ConversionResult, etc.)
│   └── validators.ts  # 검증기 타입
├── utils/             # 유틸리티 함수
│   ├── constants.ts   # 상수 및 설정 (TYPOGRAPHY_PRESETS, COVER_THEMES)
│   ├── fileUtils.ts   # 파일 처리 유틸리티
│   ├── markdownUtils.ts  # 마크다운 처리 유틸리티
│   └── common.ts      # 공통 유틸리티 (Logger, etc.)
├── services/          # 핵심 서비스
│   ├── PandocService.ts       # Pandoc 변환 엔진
│   ├── TypographyService.ts   # 타이포그래피 프리셋 관리
│   ├── FontSubsetter.ts       # 폰트 서브세팅
│   ├── MarkdownPreprocessor.ts  # 마크다운 전처리
│   └── ContentValidator.ts    # 8개 검증 모듈
├── index.ts           # 메인 API (MarkdownToDocument 클래스)
└── cli.ts             # CLI 인터페이스
```

### 핵심 컴포넌트

#### 1. MarkdownToDocument (메인 클래스)
- **역할**: 변환 프로세스 조율
- **주요 메서드**:
  - `initialize()`: 의존성 확인 (Pandoc)
  - `convert()`: 전체 변환 프로세스 실행

#### 2. PandocService
- **역할**: Pandoc을 통한 EPUB/PDF 변환
- **주요 메서드**:
  - `checkPandocAvailable()`: Pandoc 설치 확인
  - `toEpub()`: EPUB 변환 (폰트 임베딩 및 표지 포함)
  - `toPdf()`: PDF 변환 (HTML Fragment 표지 및 통합 CSS 적용)
  - `generateTypographyCSS()`: 동적 CSS 생성
- **통합 서비스**:
  - TypographyService: 타이포그래피 프리셋 적용
  - FontSubsetter: 폰트 서브세팅
  - CoverService: 자동 표지 생성

#### 3. TypographyService
- **역할**: 타이포그래피 프리셋 관리 및 CSS 생성
- **프리셋**: novel, presentation, review, ebook
- **주요 메서드**:
  - `getPreset()`: 프리셋 조회
  - `generatePresetCSS()`: 프리셋 기반 CSS 생성
- **기능**:
  - 한국어 폰트 스택 (Noto Sans CJK KR, Noto Serif CJK KR)
  - 페이지 마진 설정
  - 제목 스케일 계산
  - 하이픈 처리

#### 4. FontSubsetter
- **역할**: 폰트 서브세팅으로 파일 크기 최적화
- **주요 메서드**:
  - `analyzeFont()`: 폰트 분석
  - `subsetFont()`: 폰트 서브셋 생성
  - `subsetFontsInDirectory()`: 디렉토리 내 모든 폰트 서브세팅
- **기능**:
  - 99% 크기 감소
  - 캐싱 메커니즘
  - WOFF2, TTF, OTF 지원
  - 문자 추출 및 분석

#### 5. MarkdownPreprocessor
- **역할**: 마크다운 전처리 (Obsidian 문법 변환, 이미지 경로 해결)
- **주요 메서드**:
  - `preprocess()`: 전처리 파이프라인 실행
  - `generateCleanMarkdown()`: YAML frontmatter 포함 마크다운 생성

#### 6. ContentValidator
- **역할**: 8개 검증 모듈 실행
- **검증 모듈**:
  1. Frontmatter 검증
  2. 제목 검증
  3. 링크 검증
  4. 이미지 검증
  5. 표 검증
  6. 구문 검증
  7. 특수문자 검증
  8. 접근성 검증
- **주요 메서드**:
  - `validate()`: 전체 검증 실행
  - `autoFix()`: 자동 수정 적용

#### 7. CoverService
- **역할**: EPUB/PDF용 표지 생성
- **주요 메서드**:
  - `generateEpubCover()`: SVG 기반 표지 이미지 생성
  - `generatePdfCoverData()`: HTML Fragment 및 통합 CSS 생성
- **기능**:
  - 테마별 색상 및 레이아웃 자동 적용
  - 텍스트 래핑 및 XML 이스케이프 처리

```
1. 입력 파일 검증
   ↓
2. 콘텐츠 검증 (8개 모듈)
   ↓
3. 자동 수정 (선택사항)
   ↓
4. 마크다운 전처리
   - Obsidian 문법 변환
   - 이미지 경로 해결
   - YAML frontmatter 생성 (제목/저자명 명시적 반영)
   ↓
5. 표지 생성 (CoverService)
   - EPUB용 SVG 또는 PDF용 HTML Fragment 생성
   ↓
6. 타이포그래피 CSS 생성
   - TypographyService로 프리셋 적용
   - 표지 CSS 통합 (PDF의 경우)
   - 폰트 스택 및 한글 가독성 설정
   ↓
7. 폰트 서브세팅 (선택사항)
   - FontSubsetter로 문자 추출
   - 폰트 서브셋 생성
   - 파일 크기 최적화
   ↓
8. 임시 파일 생성
   ↓
9. Pandoc 변환
   - EPUB 변환 (폰트 임베딩 포함)
   - PDF 변환 (--include-before-body 사용)
   ↓
10. 출력 파일 생성
   ↓
11. 임시 파일 정리
```

## 타이포그래피 프리셋

### 소설 (Novel)
- **용도**: 장편 소설, 에세이
- **특징**: 16pt, 들여쓰기, 양쪽 정렬, 1.8 줄 간격
- **폰트**: Noto Serif CJK KR

### 발표 (Presentation)
- **용도**: 프레젠테이션, 강의
- **특징**: 18pt, 큰 글씨, 넓은 여백, 1.6 줄 간격
- **폰트**: Noto Sans CJK KR

### 리뷰 (Review)
- **용도**: 검토용 문서
- **특징**: 15pt, 촘촘한 레이아웃, 1.4 줄 간격
- **폰트**: Noto Sans CJK KR

### 전자책 (Ebook)
- **용도**: 일반 전자책
- **특징**: 14pt, 균형잡힌 레이아웃, 1.6 줄 간격
- **폰트**: Noto Sans CJK KR

### 학술 (Academic)
- **용도**: 학술 논문
- **특징**: 12pt, 두껍고 가는 글씨, 1.2 줄 간격
- **폰트**: Noto Serif CJK KR

### 신문 (Newspaper)
- **용도**: 신문 기사
- **특징**: 10pt, 가는 글씨, 1.1 줄 간격
- **폰트**: Noto Sans CJK KR

### 블로그 (Blog)
- **용도**: 블로그 포스트
- **특징**: 14pt, 가는 글씨, 1.4 줄 간격
- **폰트**: Noto Sans CJK KR

### 서신 (Letter)
- **용도**: 편지
- **특징**: 12pt, 가는 글씨, 1.2 줄 간격
- **폰트**: Noto Serif CJK KR

### 보고서 (Report)
- **용도**: 보고서
- **특징**: 11pt, 가는 글씨, 1.1 줄 간격
- **폰트**: Noto Sans CJK KR

### 프레젠테이션 (Slide)
- **용도**: 프레젠테이션 슬라이드
- **특징**: 24pt, 큰 글씨, 넓은 여백, 1.6 줄 간격
- **폰트**: Noto Sans CJK KR

## 검증 모듈 상세

### 1. Frontmatter 검증
- **목적**: YAML 구문 오류 감지
- **검사 항목**: 콜론(:) 누락, 잘못된 구문
- **자동 수정**: 없음 (경고만)

### 2. 제목 검증
- **목적**: 제목 구조 검증
- **검사 항목**: H1 중복, 레벨 갭
- **자동 수정**: 없음 (경고만)

### 3. 링크 검증
- **목적**: 링크 형식 검증
- **검사 항목**: Obsidian 링크, 빈 URL
- **자동 수정**: Obsidian 링크 → 표준 마크다운 링크

### 4. 이미지 검증
- **목적**: 이미지 접근성 검증
- **검사 항목**: alt 텍스트, 파일 형식
- **자동 수정**: 없음 (경고만)

### 5. 표 검증
- **목적**: 표 구조 검증
- **검사 항목**: 열 일관성
- **자동 수정**: 없음 (경고만)

### 6. 구문 검증
- **목적**: 코드 블록 구문 검증
- **검사 항목**: 닫히지 않은 코드 블록, 인라인 코드
- **자동 수정**: 닫히지 않은 코드 블록 자동 닫기

### 7. 특수문자 검증
- **목적**: 렌더링 문제 가능성 검증
- **검사 항목**: 이모지, ASCII 다이어그램
- **자동 수정**: 없음 (경고만)

### 8. 접근성 검증
- **목적**: WCAG 2.1 AA 표준 준수
- **검사 항목**: H1 존재, 긴 문단
- **자동 수정**: 없음 (경고만)

## CLI 명령어

### 기본 변환
```bash
m2d <input.md> [options]
```

### 인터랙티브 모드
```bash
m2d interactive
```

### 유틸리티 명령어
```bash
m2d list-presets    # 타이포그래피 프리셋 목록
m2d list-themes     # 표지 테마 목록
m2d check           # 의존성 확인
```

## 환경 변수

- `DEBUG`: 상세 로그 출력 (`true`로 설정)
- `TMPDIR`: 임시 파일 디렉토리 (기본값: 시스템 기본값)

## 의존성 관리

### 필수 의존성
- Node.js 18+
- Pandoc 2.19+

### 선택적 의존성
- WeasyPrint (PDF 생성)

### NPM 의존성
- **프로덕션**: commander, chalk, ora, inquirer, yaml, fontkit, glob
- **개발**: @types/node, @types/inquirer, typescript, eslint, prettier

## 빌드 및 배포

### 빌드
```bash
npm run build
```

### 로컬 테스트
```bash
npm link
m2d check
```

### NPM 배포
```bash
npm login
npm publish
```

## 테스트 전략

### 단위 테스트 (계획)
- 각 서비스 클래스별 테스트
- 유틸리티 함수 테스트
- 검증 모듈 테스트

### 통합 테스트 (계획)
- 전체 변환 프로세스 테스트
- 다양한 입력 파일 테스트
- 에러 처리 테스트

## 성능 최적화

### 이미지 처리
- 병렬 이미지 경로 해결
- 중복 이미지 검사 제거

### 파일 I/O
- 임시 파일 재사용
- 비동기 파일 처리

### Pandoc 호출
- execFile 사용 (보안 및 성능)
- 버전별 최적화된 인자 사용

## 보안 고려사항

### 명령 인젝션 방지
- `execFile` 사용 (인자를 배열로 전달)
- 경로 검증 (특수문자 차단)

### 파일 접근
- 절대 경로 사용
- 입력 파일 검증

### 임시 파일
- 시스템 임시 디렉토리 사용
- 사용 후 자동 정리

## 향후 계획

### 단기 (v1.1)
- [x] 단위 테스트 환경 구축
- [x] 폰트 서브세팅 및 임베딩 기능 완성
- [x] 자동 표지 생성 기능 구현 (CoverService)
- [x] PDF 레이아웃 엔진 최적화

### 중기 (v1.5)
- [ ] 커스텀 CSS 템플릿
- [ ] 배치 처리 모드
- [ ] 플러그인 시스템

### 장기 (v2.0)
- [ ] 웹 UI
- [ ] 클라우드 변환
- [ ] 협업 기능

## 라이선스

MIT License

## 연락처

- **GitHub**: [@goodlookingprokim](https://github.com/goodlookingprokim)
- **Repository**: https://github.com/goodlookingprokim/markdown-to-document-cli
- **Email**: edulovesai@gmail.com

---

**마지막 업데이트**: 2026-01-06 (v1.2.7)
