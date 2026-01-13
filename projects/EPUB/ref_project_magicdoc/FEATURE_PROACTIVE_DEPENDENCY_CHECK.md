# 새로운 기능: 사전 의존성 체크 및 설치 안내

## 🎯 목표

사용자가 CLI를 실행할 때 오류가 발생한 후에 해결책을 찾는 것이 아니라, **미리 필요한 것을 확인하고 설치 방법을 안내**하여 더 나은 사용자 경험을 제공합니다.

## ✨ 주요 기능

### 1. 자동 의존성 체크
사용자가 변환 명령을 실행하면 자동으로:
- Node.js 확인
- Pandoc 확인
- PDF 엔진 확인 (WeasyPrint, XeLaTeX, PDFLaTeX)
- Python 확인 (선택사항)

### 2. 플랫폼별 설치 안내
사용자의 운영체제(macOS, Linux, Windows)를 자동 감지하여 **맞춤형 설치 명령어** 제공

### 3. 새로운 `check` 명령어
언제든지 의존성 상태를 확인할 수 있는 독립 명령어

## 📋 사용 예시

### 시나리오 1: 모든 의존성이 준비된 경우

```bash
$ m2d document.md

📚 Markdown to Document CLI

🔍 의존성 확인 중...

필수 의존성:
  ✅ Node.js (v20.10.0)
  ✅ Pandoc (v3.1.2)

PDF 생성 엔진 (최소 1개 필요):
  ✅ WeasyPrint (v60.1)
  ⚪ XeLaTeX - 미설치
  ⚪ PDFLaTeX - 미설치

선택 의존성:
  ✅ Python (v3.11.5)

✅ 모든 의존성이 준비되었습니다!

⠋ Initializing...
```

### 시나리오 2: Pandoc이 없는 경우

```bash
$ m2d document.md

📚 Markdown to Document CLI

🔍 의존성 확인 중...

필수 의존성:
  ✅ Node.js (v20.10.0)
  ❌ Pandoc - 설치 필요

PDF 생성 엔진 (최소 1개 필요):
  ⚪ WeasyPrint - 미설치
  ⚪ XeLaTeX - 미설치
  ⚪ PDFLaTeX - 미설치

⚠️  필수 의존성이 누락되었습니다!

📦 Pandoc 설치 방법:
   문서 변환 엔진 - EPUB/PDF 생성의 핵심

   macOS:
   $ brew install pandoc

   💡 Pandoc 2.19 이상 필요

❌ 필수 의존성을 먼저 설치해 주세요.
```

### 시나리오 3: PDF 엔진이 없는 경우 (PDF 변환 시도)

```bash
$ m2d document.md --format pdf

📚 Markdown to Document CLI

🔍 의존성 확인 중...

필수 의존성:
  ✅ Node.js (v20.10.0)
  ✅ Pandoc (v3.1.2)

PDF 생성 엔진 (최소 1개 필요):
  ⚪ WeasyPrint - 미설치
  ⚪ XeLaTeX - 미설치
  ⚪ PDFLaTeX - 미설치

선택 의존성:
  ⚪ Python - 미설치

⚠️  PDF 생성 엔진이 없습니다!

PDF 파일을 생성하려면 최소 1개의 PDF 엔진이 필요합니다.
EPUB만 생성하려면 이 단계를 건너뛸 수 있습니다.

📦 WeasyPrint 설치 방법:
   PDF 생성 엔진 (추천) - 가장 쉽고 한글 지원 우수

   macOS:
   $ pip3 install weasyprint
   $ 또는 pip install weasyprint

   💡 Python이 필요합니다: https://python.org

또는 다른 PDF 엔진을 선택하세요:
  • XeLaTeX: PDF 생성 엔진 (한글 최적화) - 전문 출판 품질
  • PDFLaTeX: PDF 생성 엔진 (기본) - 표준 LaTeX

💡 전체 설치 가이드: https://github.com/goodlookingprokim/markdown-to-document-cli#-필수-요구사항
```

### 시나리오 4: `check` 명령어 사용

```bash
$ m2d check

🔍 의존성 확인 중...

필수 의존성:
  ✅ Node.js (v20.10.0)
  ✅ Pandoc (v3.1.2)

PDF 생성 엔진 (최소 1개 필요):
  ✅ WeasyPrint (v60.1)
  ✅ XeLaTeX (v3.141592653)
  ⚪ PDFLaTeX - 미설치

선택 의존성:
  ✅ Python (v3.11.5)

✅ 모든 의존성이 준비되었습니다!

🚀 준비 완료! 지금 바로 문서 변환을 시작할 수 있습니다.

사용 예시:
  m2d document.md
  m2d interactive
```

## 🔧 기술 구현

### DependencyChecker 클래스

새로운 유틸리티 클래스 `src/utils/dependencyChecker.ts`:

```typescript
export class DependencyChecker {
    // 명령어 사용 가능 여부 확인
    async isCommandAvailable(command: string): Promise<boolean>
    
    // 모든 의존성 체크
    async checkAll(): Promise<DependencyStatus>
    
    // 설치 안내 표시
    displayInstallInstructions(dep: DependencyStatus): void
    
    // 종합 리포트 표시
    async displayDependencyReport(): Promise<boolean>
    
    // 빠른 체크 (변환 전)
    async quickCheck(format: 'epub' | 'pdf' | 'both'): Promise<boolean>
}
```

### CLI 통합

**일반 모드**:
```typescript
// 변환 옵션 준비 후
const depChecker = new DependencyChecker();
const isReady = await depChecker.quickCheck(conversionOptions.format);

if (!isReady) {
    await depChecker.displayDependencyReport();
    console.log(chalk.red('\n❌ 필수 의존성을 먼저 설치해 주세요.\n'));
    process.exit(1);
}
```

**인터랙티브 모드**:
```typescript
// Step 3: 변환 실행 전
const depChecker = new DependencyChecker();
const isReady = await depChecker.quickCheck(format);

if (!isReady) {
    await depChecker.displayDependencyReport();
    process.exit(1);
}
```

## 🎨 사용자 경험 개선

### Before (기존)
```
사용자: m2d document.md --format pdf
시스템: ⠋ Converting...
시스템: ❌ Error: xelatex not found
사용자: ??? (구글 검색 시작...)
```

### After (개선)
```
사용자: m2d document.md --format pdf
시스템: 🔍 의존성 확인 중...
시스템: ⚠️ PDF 생성 엔진이 없습니다!
시스템: 📦 WeasyPrint 설치 방법:
        $ pip install weasyprint
사용자: (명령어 복사 → 붙여넣기 → 설치)
사용자: m2d document.md --format pdf
시스템: ✅ 모든 의존성이 준비되었습니다!
시스템: ⠋ Converting...
시스템: ✅ 변환 완료!
```

## 📊 장점

1. **사전 예방**: 오류 발생 전에 문제 해결
2. **시간 절약**: 구글 검색 없이 바로 해결책 제공
3. **플랫폼 맞춤**: OS별 최적화된 설치 명령어
4. **학습 효과**: 사용자가 의존성 구조 이해
5. **자신감 향상**: "무엇을 설치해야 하는지" 명확히 알 수 있음

## 🚀 추가 명령어

### `m2d check`
시스템 상태를 확인하고 준비 여부를 알려줍니다.

```bash
# 의존성 확인
m2d check

# 결과:
# - 설치된 것: ✅ 녹색 체크
# - 필수이지만 없는 것: ❌ 빨간색 X + 설치 방법
# - 선택사항이고 없는 것: ⚪ 회색 동그라미
```

## 💡 파인만 기법 적용

복잡한 기술 용어를 쉽게 설명:

- **"의존성"** → "필요한 도구들"
- **"PDF 엔진"** → "PDF를 만드는 오븐"
- **"설치"** → "도구 상자에 추가"
- **"버전"** → "도구의 모델 번호"

## 📝 문서 업데이트 필요

- [x] `src/utils/dependencyChecker.ts` 생성
- [x] `src/cli.ts` 통합
- [ ] `README.md`에 `m2d check` 명령어 추가
- [ ] `UserGuide.md`에 의존성 체크 섹션 추가
- [ ] `index.html`에 사전 체크 기능 소개

## 🎯 결론

이제 사용자는:
1. **오류를 보고 당황하지 않고**
2. **무엇이 필요한지 명확히 알고**
3. **어떻게 설치하는지 바로 확인하고**
4. **자신감 있게 문서 변환을 진행**할 수 있습니다!

---

**"오류 발견 → 해결"에서 "사전 확인 → 안내 → 성공"으로!**
