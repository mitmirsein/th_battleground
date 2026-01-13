# 설치 및 빌드 가이드

---

**마지막 업데이트**: 2026-01-06 (v1.2.7)

---

## 의존성 설치

```bash
npm install
```

## 빌드

```bash
npm run build
```

## 개발 모드

```bash
npm run dev
```

## 테스트

```bash
npm test
```

## 전역 설치 (선택사항)

```bash
npm link
```

이후 `m2d` 명령어로 어디서든 사용할 수 있습니다.

## NPM 배포

```bash
# 로그인
npm login

# 배포
npm publish
```

## 필수 시스템 요구사항

### Pandoc 설치

```bash
# macOS
brew install pandoc

# Windows
winget install --id JohnMacFarlane.Pandoc

# Linux
sudo apt-get install pandoc
```

### WeasyPrint (PDF 생성, 선택사항)

```bash
pip install weasyprint
```

## 문제 해결

### 빌드 오류

```bash
# node_modules 삭제 후 재설치
rm -rf node_modules
npm install
npm run build
```

### Pandoc 경로 문제

```bash
# Pandoc 경로 확인
which pandoc

# 커스텀 경로 지정
m2d document.md --pandoc-path /path/to/pandoc
```
