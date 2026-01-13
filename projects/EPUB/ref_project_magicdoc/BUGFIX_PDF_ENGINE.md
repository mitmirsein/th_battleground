# PDF Engine Detection Bug Fix

## 문제 (Problem)

사용자가 PDF 변환 시 다음과 같은 오류를 경험했습니다:

```
❌ PDF 변환 실패: xelatex not found. Please select a different --pdf-engine or install xelatex
```

## 원인 (Root Cause)

`PandocService.ts`의 `resolvePdfEngine()` 메서드가 PDF 엔진의 실제 설치 여부를 확인하지 않고 기본값으로 `xelatex`를 반환했습니다:

```typescript
// 이전 코드
private resolvePdfEngine(engine: 'pdflatex' | 'xelatex' | 'weasyprint' | 'auto'): {
    engine: 'pdflatex' | 'xelatex' | 'weasyprint';
    path: string;
} {
    if (engine === 'auto') {
        const weasyprintPath = this.findPdfEnginePath('weasyprint');
        if (weasyprintPath !== 'weasyprint') {
            return { engine: 'weasyprint', path: weasyprintPath };
        }
        // ❌ xelatex가 설치되어 있는지 확인하지 않음
        return { engine: 'xelatex', path: 'xelatex' };
    }
    return { engine, path: this.findPdfEnginePath(engine) };
}
```

## 해결 방법 (Solution)

### 1. PDF 엔진 가용성 검사 메서드 추가

```typescript
/**
 * Check if a PDF engine is available on the system
 */
private async checkPdfEngineAvailable(engine: string): Promise<boolean> {
    try {
        await execFileAsync(engine, ['--version'], { timeout: 3000 });
        return true;
    } catch {
        return false;
    }
}
```

### 2. resolvePdfEngine 메서드 개선

- 비동기 메서드로 변경 (`async`)
- 우선순위 순서대로 엔진 확인: WeasyPrint → XeLaTeX → PDFLaTeX
- 각 엔진의 실제 설치 여부를 확인
- 사용 가능한 엔진이 없으면 명확한 에러 메시지 제공

```typescript
private async resolvePdfEngine(engine: 'pdflatex' | 'xelatex' | 'weasyprint' | 'auto'): Promise<{
    engine: 'pdflatex' | 'xelatex' | 'weasyprint';
    path: string;
}> {
    if (engine === 'auto') {
        // Try engines in order of preference for Korean + typography support
        const enginePreferences: Array<{ name: 'weasyprint' | 'xelatex' | 'pdflatex'; path: string }> = [
            { name: 'weasyprint', path: this.findPdfEnginePath('weasyprint') },
            { name: 'xelatex', path: 'xelatex' },
            { name: 'pdflatex', path: 'pdflatex' },
        ];

        for (const { name, path } of enginePreferences) {
            const isAvailable = await this.checkPdfEngineAvailable(path);
            if (isAvailable) {
                Logger.debug(`[PDF Engine] Selected: ${name} (${path})`);
                return { engine: name, path };
            }
        }

        // No engine found - provide helpful error message
        throw new Error(
            'PDF 엔진을 찾을 수 없습니다. WeasyPrint, XeLaTeX, 또는 PDFLaTeX를 설치하세요.\n' +
            '설치 방법:\n' +
            '  WeasyPrint: pip install weasyprint\n' +
            '  XeLaTeX/PDFLaTeX: brew install basictex (macOS) 또는 https://www.tug.org/texlive/'
        );
    }

    // For specific engine selection, verify it's available
    const path = this.findPdfEnginePath(engine);
    const isAvailable = await this.checkPdfEngineAvailable(path);
    
    if (!isAvailable) {
        throw new Error(
            `지정된 PDF 엔진을 찾을 수 없습니다: ${engine}\n` +
            '다른 엔진을 선택하거나 --pdf-engine=auto 옵션을 사용하세요.'
        );
    }

    return { engine, path };
}
```

### 3. TroubleShooting.md 업데이트

PDF 엔진 설치 가이드를 추가하여 사용자가 쉽게 문제를 해결할 수 있도록 했습니다:

- WeasyPrint 설치 방법
- XeLaTeX 설치 방법 (macOS, Linux, Windows)
- PDFLaTeX 설치 방법
- 설치 확인 방법
- 특정 엔진 지정 방법

## 개선 사항 (Improvements)

1. **자동 폴백**: 사용 가능한 엔진을 자동으로 찾아 사용
2. **명확한 에러 메시지**: 설치 방법을 포함한 친절한 에러 메시지
3. **디버그 로깅**: 선택된 PDF 엔진을 로그에 기록
4. **문서화**: 상세한 트러블슈팅 가이드 추가

## 테스트 (Testing)

빌드 성공 확인:
```bash
npm run build
# ✅ Exit code: 0
```

## 사용자 가이드

### PDF 엔진이 없는 경우

```bash
# 자동 선택 (권장)
m2d document.md --pdf-engine auto

# 오류 발생 시 설치 안내 메시지 표시:
# "PDF 엔진을 찾을 수 없습니다. WeasyPrint, XeLaTeX, 또는 PDFLaTeX를 설치하세요."
```

### 특정 엔진 설치 후 사용

```bash
# WeasyPrint 설치
pip install weasyprint
m2d document.md --pdf-engine weasyprint

# XeLaTeX 설치 (macOS)
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"
m2d document.md --pdf-engine xelatex
```

## 파일 변경 사항

- `src/services/PandocService.ts`: PDF 엔진 감지 로직 개선
- `TroubleShooting.md`: PDF 엔진 설치 가이드 추가
