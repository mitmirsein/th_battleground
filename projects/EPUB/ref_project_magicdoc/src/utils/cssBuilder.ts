/**
 * CSS Builder Utilities
 * Centralized CSS generation for PDF and EPUB formats
 */

// ============ Font Stacks ============

export const FONT_STACKS = {
    serif: '"Noto Serif KR", "Noto Serif CJK KR", "Source Han Serif KR", "Batang", "바탕", "AppleMyungjo", serif',
    sansSerif: '"Noto Sans KR", "Noto Sans CJK KR", "Source Han Sans KR", "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo", sans-serif',
    monospace: '"Noto Sans Mono KR", "Noto Sans Mono CJK KR", "D2Coding", "Source Code Pro", monospace',
} as const;

// ============ Common CSS Snippets ============

/**
 * Generate Google Fonts import for PDF
 */
export function buildFontImport(): string {
    return `@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&family=Noto+Serif+KR:wght@300;400;700&display=swap');`;
}

/**
 * Generate box-sizing reset
 */
export function buildBoxSizingReset(): string {
    return '* { box-sizing: border-box; }';
}

/**
 * Generate image styling CSS with responsive sizing for EPUB
 * Uses !important to override inline styles from markdown source
 */
export function buildImageStyles(): string[] {
    return [
        '/* Responsive image styling - override inline styles */',
        // Keep aspect ratio and avoid over-constraining layout (prevents big blank gaps)
        'img { max-width: 100% !important; max-height: 70vh !important; width: auto !important; height: auto !important; object-fit: contain; display: block; margin: 0.6em auto; }',
        '/* Override fixed-width containers for e-reader compatibility */',
        'div[style*="width:"], div[style*="width :"] { max-width: 100% !important; width: auto !important; }',
        '/* Image containers should be fluid */',
        'figure { margin: 0.8em 0; text-align: center; max-width: 100%; }',
        'figcaption { font-size: 0.9em; color: #666; margin-top: 0.5em; font-style: italic; }',
        '/* Hide iframe embeds that don\'t work in EPUB */',
        'iframe { display: none !important; }',
        '/* Center images in anchor links */',
        'a > img { display: block; margin: 0 auto; }'
    ];
}

/**
 * Generate table styling CSS
 */
export function buildTableStyles(): string[] {
    return [
        'table { width: 100%; border-collapse: collapse; margin: 1.2em 0; }',
        'th, td { border: 1px solid #ddd; padding: 0.5em; text-align: left; }',
        'th { background-color: #f9f9f9; }',
        '/* Table pagination: allow table to split across pages with repeated header */',
        'thead { display: table-header-group; }',
        'tfoot { display: table-footer-group; }',
        'tr { break-inside: avoid; page-break-inside: avoid; }',
        'table { break-inside: auto; page-break-inside: auto; }'
    ];
}

/**
 * Generate code block styling CSS
 */
export function buildCodeStyles(monospaceFont: string = FONT_STACKS.monospace): string[] {
    return [
        `code { font-family: ${monospaceFont}; background-color: #f4f4f4; padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }`,
        'pre { background-color: #f4f4f4; padding: 1em; border-radius: 5px; overflow-x: auto; margin: 1.5em 0; }',
        'pre code { background-color: transparent; padding: 0; font-size: 0.85em; }'
    ];
}

/**
 * Generate blockquote styling CSS
 */
export function buildBlockquoteStyles(): string {
    return 'blockquote { margin: 1.5em 0; padding: 0.5em 1em; border-left: 4px solid #ddd; color: #666; font-style: italic; }';
}

// ============ PDF-specific CSS ============

export interface PageMargins {
    top: string;
    bottom: string;
    left: string;
    right: string;
}

/**
 * Generate @page rules for PDF
 */
export function buildPdfPageRules(margins: PageMargins): string[] {
    return [
        '/* PDF Page Rules */',
        '@page {',
        '  size: A4;',
        `  margin: ${margins.top} ${margins.right} ${margins.bottom} ${margins.left};`,
        '',
        '  @bottom-center {',
        '    content: counter(page);',
        '    font-size: 10pt;',
        '    color: #666;',
        '  }',
        '}',
        '',
        '/* Cover page: no margins, no page number */',
        '@page :first {',
        '  margin: 0;',
        '  @top-center { content: none; }',
        '  @bottom-center { content: none; }',
        '}',
        '',
        '/* Blank pages: no page number */',
        '@page :blank {',
        '  @bottom-center { content: none; }',
        '}'
    ];
}

/**
 * Generate PDF-specific body styles
 */
export function buildPdfBodyExtras(): string[] {
    return [
        'word-break: keep-all;',
        'overflow-wrap: break-word;',
        'orphans: 3;',
        'widows: 3;'
    ];
}

/**
 * Generate PDF break-inside rules
 */
export function buildPdfBreakRules(): string {
    // Avoid breaking inside blockquotes/pre, but allow tables/images to flow across pages to prevent large blank gaps
    return 'blockquote, pre { break-inside: avoid; }';
}

/**
 * Generate PDF-specific image styling for proper page layout
 */
export function buildPdfImageStyles(): string[] {
    return [
        '/* PDF-specific image constraints */',
        // Allow images to be placed naturally with text; constrain height to avoid overflow
        'img { max-height: 70vh !important; object-fit: contain; }',
        '/* Ensure images don\'t overflow page width with margins */',
        'img { max-width: calc(100% - 2em) !important; }',
        '/* Image containers should be fluid */',
        'figure { max-width: 100%; }',
        '/* Add spacing before/after images for better layout */',
        'p + figure, p + img { margin-top: 0.8em; }',
        'figure + p, img + p { margin-top: 0.8em; }'
    ];
}

/**
 * Hide Pandoc title block for PDF
 */
export function buildPdfTitleBlockHide(): string {
    return '#title-block-header { display: none; }';
}

// ============ Heading Styles ============

export interface HeadingScale {
    h1: number;
    h2: number;
    h3: number;
    h4: number;
    h5: number;
    h6: number;
}

/**
 * Generate heading CSS for all levels
 */
export function buildHeadingStyles(
    scale: HeadingScale,
    format: 'epub' | 'pdf' = 'epub'
): string[] {
    const css: string[] = [];

    for (const [level, size] of Object.entries(scale)) {
        css.push(`${level} {`);
        css.push(`  font-size: ${size}em;`);
        css.push('  margin-top: 1.5em;');
        css.push('  margin-bottom: 0.5em;');
        css.push('  font-weight: bold;');
        css.push('  line-height: 1.2;');
        css.push('  color: #1a1a1a;');

        if (format === 'pdf') {
            if (level === 'h1') {
                css.push('  break-before: page;');
            }
            if (level === 'h1' || level === 'h2' || level === 'h3') {
                css.push('  page-break-after: avoid;');
                css.push('  break-after: avoid;');
            }
        }

        css.push('}');
        css.push('');
    }

    return css;
}

// ============ Body Styles ============

export interface BodyStyleOptions {
    fontFamily: string;
    fontSize: string;
    lineHeight: number;
    justification: 'left' | 'justify';
    hyphenation: boolean;
    format: 'epub' | 'pdf';
}

/**
 * Generate body CSS
 */
export function buildBodyStyles(options: BodyStyleOptions): string[] {
    const css: string[] = [
        'body {',
        `  font-family: ${options.fontFamily};`,
        `  font-size: ${options.fontSize};`,
        `  line-height: ${options.lineHeight};`,
        `  text-align: ${options.justification};`,
        '  color: #333;',
        '  margin: 0;'
    ];

    if (options.format === 'pdf') {
        css.push(...buildPdfBodyExtras().map(s => '  ' + s));
    }

    if (options.hyphenation) {
        css.push('  hyphens: auto;');
        css.push('  -webkit-hyphens: auto;');
        css.push('  -ms-hyphens: auto;');
    }

    css.push('}');
    return css;
}

// ============ Paragraph Styles ============

/**
 * Generate paragraph CSS
 */
export function buildParagraphStyles(
    spacing: string,
    textIndent?: string
): string[] {
    const css = [
        'p {',
        '  margin-top: 0;',
        `  margin-bottom: ${spacing};`
    ];

    if (textIndent) {
        css.push(`  text-indent: ${textIndent};`);
    }

    css.push('}');
    return css;
}

// ============ Composite Builders ============

/**
 * Build common element styles (images, tables, code, blockquotes)
 */
export function buildCommonElementStyles(format: 'epub' | 'pdf' = 'epub'): string[] {
    const css: string[] = [
        '',
        '/* Common Element Styles */',
        ...buildImageStyles(),
        buildBlockquoteStyles(),
    ];

    if (format === 'pdf') {
        css.push(buildPdfBreakRules());
    }

    css.push(...buildCodeStyles());
    css.push(...buildTableStyles());

    return css;
}
