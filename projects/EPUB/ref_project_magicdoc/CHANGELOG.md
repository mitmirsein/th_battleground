# CHANGELOG.md

All notable changes to Markdown to Document CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.7] - 2026-01-06

### Changed
- **비대화형 CLI 기본값을 '최고품질 쉬운 모드'로 개선**:
  - 기본 출력 형식: `both` (EPUB + PDF 동시 생성)
  - 기본 타이포그래피: `auto` (문서 분석 기반 추천 프리셋 자동 적용)
  - PDF 엔진: `auto` (WeasyPrint 우선, 미설치 시 XeLaTeX로 fallback)

- **title/author 입력 UX 개선**:
  - 비대화형 CLI: `--title`, `--author` 없이도 frontmatter/파일명 기반으로 자동 추론
  - Interactive: 입력은 받되 Enter로 자동값 사용

### Fixed
- **EPUB에서 `--no-toc` 옵션이 무시되던 문제 수정**: EPUB 변환에서도 `includeToc` 설정이 반영되도록 수정
- **CLI 버전 표시 정합성 개선**: `package.json` 버전을 읽어 `m2d --version`에 표시

### Security
- **개발 환경 보안 강화**:
  - Git 원격 저장소를 HTTPS에서 SSH 인증 방식으로 전환
  - IDE 터미널 환경변수 자동 주입 차단 (`.vscode/settings.json`에 `GITHUB_TOKEN: null` 설정)
  - 쉘 설정 파일(`~/.zshrc.github`)에서 토큰 export 제거
  - Claude Desktop 설정 파일에서 하드코딩된 토큰 제거
  - GitHub CLI는 macOS Keychain 기반 안전한 인증 사용 확인

### Docs
- README/UserGuide/MarkdownGuide/BEGINNER_GUIDE/TroubleShooting/INSTALL 문서 내용을 현재 기본값/워크플로우에 맞게 정리

## [1.2.6] - 2026-01-06

### Changed
- **제목/저자 입력 강제 (자동 생성 방지)**:
  - Interactive 모드에서 책 제목/저자명을 변환 시작 전에 필수로 입력
  - CLI 변환 시 `--title`, `--author`를 필수 옵션으로 요구하고 입력값을 frontmatter에 항상 반영

- **레이아웃 품질 개선 (공백 최소화)**:
  - 이미지: 비율 유지 + 최대 높이 제한 + 여백 조정으로 페이지 내 자연스러운 배치
  - 테이블: 헤더 반복(`thead`) 및 행 단위 분할 방지(`tr break-inside: avoid`)로 여러 페이지에 자연스럽게 이어지도록 개선

## [1.2.5] - 2026-01-06

### Changed
- **변환 파이프라인 단순화**:
  - 출판용 마크다운 파일 저장 단계를 제거하고, 변환 과정 내부에서 자동 최적화/전처리 후 바로 EPUB/PDF 생성
  - Interactive 모드에서 `_preprocessed.md` 파일을 생성하지 않음

- **단계형 로그 고도화**:
  - Validate → Auto-fix → Preprocess → Assemble → Convert → Finalize 순서로 단계가 이어지도록 로그 정리

## [1.2.4] - 2026-01-06

### Fixed
- **YAML 파싱 에러 수정**: 
  - 콘텐츠 내 `---` 수평선이 YAML frontmatter로 오인되는 문제 해결 (`---` → `***` 변환)
  - YAML 문자열에 단일 따옴표 사용으로 특수문자 안전 처리
  - "YAML parse exception: did not find expected comment or line break" 오류 해결

- **EPUB 반응형 이미지 스타일링**:
  - `!important` 규칙으로 인라인 스타일 오버라이드
  - 고정 너비 컨테이너(`width: 600px` 등) 자동 조절
  - iframe 임베드 숨김 처리 (오프라인 EPUB 호환성)
  - 모든 이미지가 e-reader 화면 크기에 맞게 자동 조절

- **PDF 페이지 레이아웃 이미지 스타일링**:
  - `max-height: 85vh` 제한으로 이미지가 페이지 높이 초과 방지
  - `break-inside: avoid`로 이미지가 페이지 중간에 잘리지 않음
  - 이미지 컨테이너에 페이지 분할 방지 규칙 적용
  - 이미지 전후 적절한 여백 자동 추가

## [1.2.3] - 2026-01-06

### Changed
- **Interactive Mode UX 대폭 개선**:
  - **3단계 간소화된 워크플로우**: 파일 선택 → 모드 선택 → 변환 (기존 6단계 이상에서 축소)
  - **3가지 변환 모드 제공**:
    - ⚡ **빠른 변환**: 스마트 기본값으로 출력 형식만 선택 (권장)
    - ⚙️ **상세 설정**: 프리셋, 테마, 제목/저자 직접 선택
  - **스마트 기본값**: 문서 분석 결과 기반 프리셋/테마 자동 선택
  - **자동 전처리**: Obsidian 문법 감지 시 자동 최적화 적용
  - **간소화된 선택지**: 프리셋/테마 상위 6개만 표시, "더 보기" 옵션 제공
  - **메타데이터 자동 감지**: frontmatter에서 title/author 추출, 없을 때만 질문

- **EPUB 표지 제목 레이아웃 개선**:
  - 제목 길이에 따른 동적 폰트 크기 조절 (80px~160px)
  - 한글 문자 너비 고려 (한글은 1.5배 너비로 계산)
  - 멀티라인 제목의 수직 중앙 정렬
  - 구분선 위치 동적 배치

### Refactored
- `cli.ts` 코드 구조 개선:
  - `preprocessContent()`: 전처리 로직 함수로 분리
  - `extractMetadata()`: frontmatter 메타데이터 추출 함수
  - `getSimplifiedPresetChoices()`, `getSimplifiedThemeChoices()`: 간소화된 선택지 생성
- `CoverService` 개선:
  - `calculateTitleLayout()`: 제목 레이아웃 계산 로직
  - `splitTitleIntoLinesSvg()`: SVG용 제목 줄바꿈
  - `generateTitleTspans()`: SVG tspan 요소 생성

---

## [1.2.2] - 2026-01-06

### Added
- **전처리 완료 후 확인 단계 추가**:
  - 바로 PDF/EPUB로 변환
  - 전처리된 파일만 저장하고 종료
  - 전처리된 파일 미리보기 후 결정
- 전처리된 파일 미리보기 기능 (처음 50줄)
- 전처리 후 나중에 변환할 수 있도록 명령어 안내

---

## [1.2.1] - 2026-01-06

### Added
- **Interactive Mode 워크플로우 개선**:
  - **문서 분석 기능**: Obsidian 문법, 이미지/표/코드 블록 수, 잠재적 이슈 자동 감지
  - **워크플로우 선택**: 전처리(출력 최적화) 후 변환 vs 바로 변환 선택 가능
  - **전처리 옵션**:
    - Obsidian 이미지 문법 변환 (`![[image]]` → `![](image)`)
    - Obsidian 내부 링크 변환 (`[[link]]` → 텍스트)
    - 하이라이트 변환 (`==text==` → `**text**`)
    - 콜아웃 최적화 (`> [!note]` 등)
  - **스마트 프리셋 추천**: 문서 분석 결과 기반 Typography Preset 자동 권장
  - **카테고리별 선택 UI**: 테마/프리셋을 카테고리별로 그룹화하여 표시

- **MarkdownGuide.md 추가**:
  - PDF/EPUB 출력 최적화를 위한 Markdown 작성 가이드
  - 일반 Markdown + Obsidian 문법 호환 가이드
  - Interactive Mode 워크플로우 의사결정 기준 제공
  - 프리셋/테마 선택 가이드 및 체크리스트

### Improved
- Interactive Mode에서 문서 분석 결과 기반 권장 사항 표시
- Typography Preset 선택 시 권장 프리셋 하이라이트
- Cover Theme 선택 UI 카테고리별 그룹화

---

## [1.2.0] - 2026-01-06

### Refactored
- **코드 구조 개선**: 모듈화 및 책임 분리를 통한 유지보수성 향상
  - `src/utils/cssBuilder.ts`: CSS 생성 로직 중앙화
    - `buildFontImport()`, `buildBodyStyles()`, `buildHeadingStyles()` 등 재사용 가능한 빌더 함수
    - `buildPdfPageRules()`: PDF 페이지 규칙 (@page, :first, :blank) 통합
    - `buildCommonElementStyles()`: 공통 요소(이미지/표/코드) 스타일 추출
  - `src/utils/themeUtils.ts`: 테마/프리셋 유틸리티 함수 추가
    - `getCoverThemesByCategory()`, `getTypographyPresetsByCategory()`: 카테고리별 필터링
    - `isValidCoverTheme()`, `isValidTypographyPreset()`: 검증 함수
    - `generateCoverThemeHelpText()`, `generateTypographyPresetHelpText()`: CLI 도움말 자동 생성
  - `src/types/index.ts`: 타입 안전성 강화
    - `CoverThemeCategory`, `CoverThemeStyle`, `TypographyPresetCategory` enum 추가
    - `CoverThemeColors` 인터페이스 분리
  - `TypographyService.generatePresetCSS()`: CSS 빌더 사용으로 리팩토링
    - 중복 코드 제거, 테스트 용이성 향상
    - `FONT_STACKS` 중앙화 (cssBuilder.ts)

### Changed
- 폰트 스택 정의를 `cssBuilder.ts`로 이동하여 단일 소스 유지
- CSS 생성 로직을 모듈화하여 PDF/EPUB 별 확장 용이

---

## [1.1.7] - 2026-01-06

### Added
- **15개 Cover Theme 추가** (총 15개):
  - **Professional**: Corporate Blue, Academic, Magazine
  - **Creative**: Sunset, Ocean, Aurora, Rose Gold
  - **Seasonal**: Spring, Autumn, Winter
- **7개 Typography Preset 추가** (총 11개):
  - **Content-focused**: Text Heavy, Table Heavy, Image Heavy, Balanced
  - **Document Type**: Report, Manual, Magazine

### Improved
- **콘텐츠 유형별 레이아웃 최적화**:
  - `text_heavy`: 긴 글 위주 문서 - 좁은 여백, 촘촘한 줄간격
  - `table_heavy`: 표 중심 문서 - 넓은 표 영역, 작은 폰트
  - `image_heavy`: 이미지 중심 문서 - 이미지 최대화, 캡션 강조
  - `balanced`: 균형 레이아웃 - 텍스트/테이블/이미지 균형 배치
- **문서 유형별 전문 프리셋**:
  - `report`: 비즈니스 보고서 - 공식적, 구조화된 레이아웃
  - `manual`: 기술 매뉴얼 - 코드 블록, 단계별 설명 강조
  - `magazine`: 잡지 스타일 - 드롭캡, 시각적 강조

---

## [1.1.6] - 2026-01-06

### Added
- **PDF Page Numbers**: Automatic page numbering at the bottom center of each page
  - Uses CSS `@bottom-center { content: counter(page); }` for WeasyPrint
  - Page numbers hidden on cover and blank pages

### Improved
- **Full-Bleed Cover Page**: 
  - Added `@page :first { margin: 0; }` CSS rule for true full-bleed covers
  - Cover page now uses fixed A4 dimensions (210mm × 297mm) instead of relative units
  - Improved cover reliability across different PDF rendering scenarios
- **Smart Title Line Breaking**:
  - Implemented intelligent title wrapping for long titles (similar to Obsidian plugin's TitleOptimizer)
  - Automatic font size adjustment based on title length (48pt → 42pt → 36pt)
  - Korean-optimized character count per line (14 characters)
- **Figure/Image Styling**:
  - Added dedicated `figure` and `figcaption` CSS rules
  - Improved image presentation with centered captions

### Changed
- Cover author field now displays empty instead of "Unknown Author" when not specified

---

## [1.1.5] - 2026-01-05

### Fixed
- **PDF Layout Reconstruction**: 
  - Fixed major layout collapse by changing cover generation from full HTML to fragments using `--include-before-body`.
  - Implemented `box-sizing: border-box` across all elements to prevent layout calculation errors.
  - Added `#title-block-header { display: none; }` to suppress Pandoc's default title block.
  - Improved page breaking with `break-before: page` for H1 and `break-inside: avoid` for tables, code blocks, and blockquotes.
- **Korean Typography Optimization**:
  - Forced `word-break: keep-all` and `overflow-wrap: break-word` for better Korean text flow.
  - Integrated Noto Sans KR Google Fonts import into the main PDF stylesheet.
  - Added widow and orphan control (`orphans: 3`, `widows: 3`) for professional page flow.

---

## [1.1.4] - 2026-01-05

### Added
- **Automatic Cover Generation**: 
  - Integrated `CoverService` to generate professional book covers for both EPUB and PDF.
  - EPUB covers are generated as high-quality SVG images.
  - PDF covers are generated as full-page HTML templates.
  - Supports all defined themes (Apple, Modern Gradient, Dark Tech, etc.).
- **EPUB Font Embedding**:
  - Automatically embeds Noto Sans KR and Noto Serif KR fonts into EPUB files.
  - Ensures consistent typography across all e-reader devices.
- **PDF Readability Improvements**:
  - Enhanced PDF CSS template for better Korean font rendering.
  - Forced Noto Sans KR as the primary font for PDF generation via WeasyPrint.

### Fixed
- **Author/Title Recognition**:
  - Fixed "Unknown Author" issue by correctly prioritizing manual input from interactive mode.
  - Ensured metadata overrides are correctly written to the temporary Markdown frontmatter.
- **Conversion Quality**:
  - Improved CSS base styles for images, blockquotes, tables, and code blocks.

---

## [1.1.3] - 2026-01-05

### Changed
- **Interactive Mode Output Format Order**: Reordered output format options
  - Changed order to: Both EPUB and PDF, PDF only, EPUB only
  - Changed default format to 'both' for better user experience

---

## [1.1.2] - 2026-01-05

### Added
- **Custom Title and Author**: Interactive mode now allows manual input of book title and author
  - Custom title and author override auto-detected values
  - Empty values fall back to auto-detection
  - Improved flexibility for document metadata

### Changed
- **Interactive Mode UI**: Simplified header design with clean line separators
  - Replaced box-style borders with simple line separators
  - Better compatibility with various terminal widths
- **Enhanced Font Stacks**: Improved Korean font support with additional fallback fonts
  - Added Source Han Serif KR, Source Han Sans KR
  - Added AppleMyungjo, Apple SD Gothic Neo for macOS
  - Added Source Code Pro for monospace

### Fixed
- Interactive mode header rendering issues on different terminal widths

---

## [1.1.1] - 2026-01-05

### Added
- **Interactive Mode Improvements**: Enhanced user experience with better visual design
  - Box-style header with decorative borders
  - Color-coded prompts with emojis
  - Improved spinner animations
  - Better output formatting with separators

### Changed
- **Automatic Quote Removal**: File paths in interactive mode now automatically remove surrounding quotes
  - No need for users to manually remove quotes from copied paths
  - Applied to both validation and path resolution
  - Improved user experience for terminal users

### Fixed
- File path validation in interactive mode now handles quoted paths correctly

---

## [1.1.0] - 2026-01-05

### Added
- **TypographyService**: Advanced typography preset management with 4 presets (novel, presentation, review, ebook)
  - Custom font stacks for Korean fonts (Noto Sans CJK KR, Noto Serif CJK KR)
  - Detailed CSS rules for each preset
  - Page margin, line height, and heading scale configuration
- **FontSubsetter**: Font subsetting service for 99% file size reduction
  - Character extraction and analysis
  - Font caching mechanism
  - Support for WOFF2, TTF, OTF formats
- **PandocService Enhancements**: Integrated TypographyService and FontSubsetter
  - Dynamic CSS generation based on typography presets
  - Automatic typography CSS application during conversion
  - Enhanced temp directory management

### Changed
- Improved conversion quality to match original Obsidian plugin
- Better Korean font support with proper font stacks
- Enhanced CSS generation with typography presets
- Fixed fontkit import for ES module compatibility

### Fixed
- Fontkit CommonJS/ES module compatibility issues
- TypeScript type errors for fontkit API
- Typography preset CSS generation

---

## [1.0.1] - 2025-01-05

### Added
- GitHub repository integration
- Updated repository URL to goodlookingprokim/markdown-to-document-cli
- Updated homepage and bugs URLs

### Changed
- Updated package.json with correct GitHub repository information
- Updated documentation with new GitHub links

---

## [1.0.0] - 2025-01-05

### Added
- **Core Features**
  - Markdown to EPUB conversion
  - Markdown to PDF conversion
  - Simultaneous EPUB + PDF conversion
  - YAML frontmatter support
  - Automatic table of contents generation
  - Chapter splitting (H1-based)

- **Validation Modules**
  - Frontmatter validation (YAML syntax)
  - Heading validation (duplicate H1, level gaps)
  - Link validation (Obsidian links, empty URLs)
  - Image validation (alt text, file format)
  - Table validation (column consistency)
  - Syntax validation (unclosed code blocks)
  - Special character validation (emojis, ASCII diagrams)
  - Accessibility validation (H1 presence, long paragraphs)

- **Typography Presets**
  - Novel: 16pt, serif, justified, 1.8 line-height
  - Presentation: 18pt, sans-serif, left-aligned, 1.6 line-height
  - Review: 11pt, sans-serif, left-aligned, 1.4 line-height
  - Ebook: 14pt, sans-serif, justified, 1.6 line-height

- **CLI Features**
  - Interactive mode with guided prompts
  - Command-line options for all features
  - Progress indicators
  - Colored terminal output
  - Verbose logging
  - Dependency checking

- **Utilities**
  - `list-presets`: Show available typography presets
  - `list-themes`: Show available cover themes
  - `check`: Verify Pandoc installation

- **Documentation**
  - README.md with quick start guide
  - UserGuide.md with detailed usage instructions
  - Project.md with technical documentation
  - TroubleShooting.md with problem-solving guide
  - INSTALL.md with installation instructions

### Technical Details
- **Language**: TypeScript 5.3+
- **Runtime**: Node.js 18+
- **Module System**: ES Modules
- **Dependencies**:
  - commander: CLI framework
  - chalk: Terminal colors
  - ora: Loading spinners
  - inquirer: Interactive prompts
  - yaml: YAML parsing
  - fontkit: Font processing
  - glob: File pattern matching

### Dependencies
- **Required**: Node.js 18+, Pandoc 2.19+
- **Optional**: WeasyPrint (for PDF generation)

### Known Limitations
- Single file conversion only (batch processing planned for v1.5)
- Font subsetting not fully implemented (planned for v1.1)
- Cover generation not fully implemented (planned for v1.1)
- No web UI (planned for v2.0)

### Breaking Changes
- None (initial release)

---

## [Upcoming]

### [1.1.0] - Planned
- Font subsetting implementation
- Cover generation functionality
- Unit tests
- Performance improvements
- Bug fixes

### [1.5.0] - Planned
- Custom CSS templates
- Batch processing mode
- Plugin system
- More typography presets
- More cover themes

### [2.0.0] - Planned
- Web UI
- Cloud conversion
- Collaboration features
- Advanced formatting options
- Export to more formats (DOCX, RTF)

---

## Version History Format

### Version Numbering
- **Major version (X.0.0)**: Breaking changes, major features
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, minor improvements

### Change Types
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in future
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes

---

## Contributing to Changelog

When contributing to this project, please update this file:

1. Add entries under the `[Unreleased]` section
2. Use the format: `- **[Type]**: Description`
3. Be specific about what changed
4. Reference related issues if applicable

Example:
```markdown
### Added
- **Feature**: New typography preset for academic papers (#123)
- **CLI**: New `--batch` option for batch processing (#124)

### Fixed
- **Bug**: Fixed image path resolution on Windows (#125)
- **Performance**: Improved conversion speed for large documents (#126)
```

---

## Release Process

1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Create git tag
4. Publish to NPM
5. Create GitHub release

---

**Maintained by**: 잘생김프로쌤 (bluelion79)
**Last Updated**: 2025-01-05
