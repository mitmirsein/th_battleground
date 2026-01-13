/**
 * Typography Service - 타이포그래피 프리셋 관리 및 CSS 생성
 * Refactored to use centralized CSS builders
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  FONT_STACKS,
  buildFontImport,
  buildBoxSizingReset,
  buildBodyStyles,
  buildParagraphStyles,
  buildHeadingStyles,
  buildPdfPageRules,
  buildPdfTitleBlockHide,
  buildPdfImageStyles,
  buildCommonElementStyles,
  type HeadingScale,
  type PageMargins
} from '../utils/cssBuilder.js';

export type TypographyPresetId =
  | 'novel' | 'presentation' | 'review' | 'ebook'  // Basic
  | 'text_heavy' | 'table_heavy' | 'image_heavy' | 'balanced'  // Content-focused
  | 'report' | 'manual' | 'magazine';  // Document type

export interface TypographySettings {
  fontSize: string;
  lineHeight: number;
  textIndent?: string;
  paragraphSpacing: string;
  pageMargins: {
    top: string;
    bottom: string;
    left: string;
    right: string;
  };
  fontFamily: string;
  hyphenation: boolean;
  justification: 'left' | 'justify';
  headingScale: {
    h1: number;
    h2: number;
    h3: number;
    h4: number;
    h5: number;
    h6: number;
  };
}

export interface TypographyPreset {
  id: TypographyPresetId;
  name: string;
  nameKr: string;
  description: string;
  settings: TypographySettings;
  cssRules?: string;
}

export interface CSSGenerationOptions {
  includePageBreaks?: boolean;
  includeFonts?: boolean;
  outputFormat?: 'epub' | 'pdf';
  codeTheme?: string;
  additionalCss?: string;
}

export class TypographyService {
  private presets: Map<string, TypographyPreset>;
  // Use centralized font stacks from cssBuilder
  private defaultFontStacks = FONT_STACKS;

  constructor() {
    this.presets = new Map();
    this.initializePresets();
  }

  private initializePresets(): void {
    this.presets.set('novel', {
      id: 'novel',
      name: 'Novel',
      nameKr: '소설',
      description: '소설 및 에세이에 최적화된 설정',
      settings: {
        fontSize: '16pt',
        lineHeight: 1.8,
        textIndent: '2em',
        paragraphSpacing: '0.5em',
        pageMargins: {
          top: '25mm',
          bottom: '25mm',
          left: '20mm',
          right: '20mm',
        },
        fontFamily: this.defaultFontStacks.serif,
        hyphenation: true,
        justification: 'justify',
        headingScale: {
          h1: 1.8,
          h2: 1.6,
          h3: 1.4,
          h4: 1.2,
          h5: 1.1,
          h6: 1.0,
        },
      },
      cssRules: `
        p:first-of-type::first-letter {
          font-size: 3em;
          float: left;
          line-height: 1;
          margin-right: 0.1em;
          font-weight: bold;
        }
        hr {
          margin: 2em auto;
          width: 50%;
          border: none;
          border-top: 1px solid #999;
        }
      `,
    });

    this.presets.set('presentation', {
      id: 'presentation',
      name: 'Presentation',
      nameKr: '발표',
      description: '프레젠테이션 및 발표 자료용',
      settings: {
        fontSize: '18pt',
        lineHeight: 1.6,
        paragraphSpacing: '1em',
        pageMargins: {
          top: '30mm',
          bottom: '30mm',
          left: '25mm',
          right: '25mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 2.0,
          h2: 1.8,
          h3: 1.6,
          h4: 1.4,
          h5: 1.2,
          h6: 1.1,
        },
      },
      cssRules: `
        h1, h2, h3 {
          color: #2c3e50;
          border-bottom: 2px solid #3498db;
          padding-bottom: 0.3em;
        }
      `,
    });

    this.presets.set('review', {
      id: 'review',
      name: 'Review',
      nameKr: '리뷰',
      description: '리뷰 및 기술 문서용',
      settings: {
        fontSize: '15pt',
        lineHeight: 1.7,
        paragraphSpacing: '0.8em',
        pageMargins: {
          top: '22mm',
          bottom: '22mm',
          left: '22mm',
          right: '22mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.9,
          h2: 1.7,
          h3: 1.5,
          h4: 1.3,
          h5: 1.1,
          h6: 1.0,
        },
      },
      cssRules: `
        blockquote {
          border-left: 4px solid #3498db;
          padding-left: 1em;
          margin: 1.5em 0;
          color: #555;
        }
        code {
          background-color: #f4f4f4;
          padding: 0.2em 0.4em;
          border-radius: 3px;
          font-family: ${this.defaultFontStacks.monospace};
        }
      `,
    });

    this.presets.set('ebook', {
      id: 'ebook',
      name: 'E-book',
      nameKr: '전자책',
      description: '일반 전자책 리더에 최적화 (기본값)',
      settings: {
        fontSize: '14pt',
        lineHeight: 1.6,
        paragraphSpacing: '0.6em',
        pageMargins: {
          top: '20mm',
          bottom: '20mm',
          left: '18mm',
          right: '18mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.7,
          h2: 1.5,
          h3: 1.3,
          h4: 1.2,
          h5: 1.1,
          h6: 1.0,
        },
      },
      cssRules: `
        body {
          orphans: 2;
          widows: 2;
        }
        h1, h2, h3 {
          page-break-after: avoid;
        }
        figure figcaption {
          font-size: 0.9em;
          text-align: center;
          font-style: italic;
          margin-top: 0.5em;
        }
      `,
    });

    // === Content-focused Presets ===

    this.presets.set('text_heavy', {
      id: 'text_heavy',
      name: 'Text Heavy',
      nameKr: '텍스트 중심',
      description: '긴 글 위주의 문서에 최적화 - 좁은 여백, 촘촘한 줄간격',
      settings: {
        fontSize: '12pt',
        lineHeight: 1.5,
        textIndent: '1.5em',
        paragraphSpacing: '0.3em',
        pageMargins: {
          top: '15mm',
          bottom: '15mm',
          left: '15mm',
          right: '15mm',
        },
        fontFamily: this.defaultFontStacks.serif,
        hyphenation: true,
        justification: 'justify',
        headingScale: {
          h1: 1.5,
          h2: 1.3,
          h3: 1.2,
          h4: 1.1,
          h5: 1.05,
          h6: 1.0,
        },
      },
      cssRules: `
        p { margin-bottom: 0.2em; }
        h1, h2, h3, h4, h5, h6 { margin-top: 1em; margin-bottom: 0.3em; }
        blockquote { margin: 0.8em 1em; font-size: 0.95em; }
      `,
    });

    this.presets.set('table_heavy', {
      id: 'table_heavy',
      name: 'Table Heavy',
      nameKr: '테이블 중심',
      description: '표가 많은 문서에 최적화 - 넓은 여백, 작은 폰트',
      settings: {
        fontSize: '11pt',
        lineHeight: 1.4,
        paragraphSpacing: '0.5em',
        pageMargins: {
          top: '12mm',
          bottom: '12mm',
          left: '10mm',
          right: '10mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.6,
          h2: 1.4,
          h3: 1.2,
          h4: 1.1,
          h5: 1.0,
          h6: 0.95,
        },
      },
      cssRules: `
        table { 
          width: 100%; 
          font-size: 10pt; 
          margin: 1em 0;
          border-collapse: collapse;
        }
        th, td { 
          padding: 0.4em 0.6em; 
          border: 1px solid #ccc;
          vertical-align: top;
        }
        th { 
          background: #f5f5f5; 
          font-weight: 600;
          text-align: center;
        }
        caption {
          font-size: 0.9em;
          font-weight: bold;
          margin-bottom: 0.5em;
          text-align: left;
        }
        table + table { margin-top: 2em; }
      `,
    });

    this.presets.set('image_heavy', {
      id: 'image_heavy',
      name: 'Image Heavy',
      nameKr: '이미지 중심',
      description: '이미지가 많은 문서에 최적화 - 이미지 최대화, 캡션 강조',
      settings: {
        fontSize: '13pt',
        lineHeight: 1.5,
        paragraphSpacing: '0.8em',
        pageMargins: {
          top: '15mm',
          bottom: '20mm',
          left: '12mm',
          right: '12mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.8,
          h2: 1.5,
          h3: 1.3,
          h4: 1.15,
          h5: 1.05,
          h6: 1.0,
        },
      },
      cssRules: `
        img {
          max-width: 100%;
          height: auto;
          display: block;
          margin: 1.5em auto;
        }
        figure {
          margin: 2em 0;
          text-align: center;
          break-inside: avoid;
        }
        figure img {
          max-height: 80vh;
          object-fit: contain;
        }
        figcaption {
          font-size: 0.85em;
          color: #555;
          margin-top: 0.8em;
          font-style: italic;
          padding: 0 1em;
        }
        p { max-width: 90%; }
      `,
    });

    this.presets.set('balanced', {
      id: 'balanced',
      name: 'Balanced',
      nameKr: '균형 레이아웃',
      description: '텍스트, 테이블, 이미지를 균형있게 배치 - 가독성과 레이아웃 최적화',
      settings: {
        fontSize: '12pt',
        lineHeight: 1.55,
        paragraphSpacing: '0.6em',
        pageMargins: {
          top: '18mm',
          bottom: '18mm',
          left: '16mm',
          right: '16mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.7,
          h2: 1.45,
          h3: 1.25,
          h4: 1.1,
          h5: 1.0,
          h6: 0.95,
        },
      },
      cssRules: `
        img { max-width: 95%; margin: 1.2em auto; }
        figure { margin: 1.5em 0; break-inside: avoid; }
        figcaption { font-size: 0.9em; color: #666; text-align: center; margin-top: 0.5em; }
        table { width: 100%; font-size: 11pt; margin: 1.2em 0; }
        th, td { padding: 0.5em; border: 1px solid #ddd; }
        th { background: #f8f8f8; }
        blockquote { margin: 1em 1.5em; padding-left: 1em; border-left: 3px solid #ddd; }
        pre { font-size: 0.9em; padding: 1em; overflow-x: auto; }
      `,
    });

    // === Document Type Presets ===

    this.presets.set('report', {
      id: 'report',
      name: 'Report',
      nameKr: '보고서',
      description: '비즈니스 보고서용 - 공식적, 구조화된 레이아웃',
      settings: {
        fontSize: '11pt',
        lineHeight: 1.5,
        paragraphSpacing: '0.7em',
        pageMargins: {
          top: '25mm',
          bottom: '25mm',
          left: '25mm',
          right: '20mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'justify',
        headingScale: {
          h1: 1.8,
          h2: 1.5,
          h3: 1.3,
          h4: 1.15,
          h5: 1.05,
          h6: 1.0,
        },
      },
      cssRules: `
        h1 { 
          text-align: center; 
          border-bottom: 2px solid #333;
          padding-bottom: 0.5em;
          margin-bottom: 1em;
        }
        h2 { 
          color: #2c3e50;
          border-bottom: 1px solid #bdc3c7;
          padding-bottom: 0.3em;
        }
        h3 { color: #34495e; }
        table { font-size: 10pt; }
        th { background: #ecf0f1; }
        .toc { margin: 2em 0; }
        .toc a { color: inherit; text-decoration: none; }
      `,
    });

    this.presets.set('manual', {
      id: 'manual',
      name: 'Manual',
      nameKr: '매뉴얼',
      description: '기술 문서/매뉴얼용 - 코드 블록, 단계별 설명 강조',
      settings: {
        fontSize: '11pt',
        lineHeight: 1.6,
        paragraphSpacing: '0.8em',
        pageMargins: {
          top: '20mm',
          bottom: '20mm',
          left: '20mm',
          right: '20mm',
        },
        fontFamily: this.defaultFontStacks.sansSerif,
        hyphenation: false,
        justification: 'left',
        headingScale: {
          h1: 1.9,
          h2: 1.6,
          h3: 1.35,
          h4: 1.2,
          h5: 1.1,
          h6: 1.0,
        },
      },
      cssRules: `
        h1, h2, h3 { color: #1a5276; }
        h2 { border-left: 4px solid #3498db; padding-left: 0.5em; }
        code {
          background: #f4f4f4;
          padding: 0.15em 0.4em;
          border-radius: 3px;
          font-family: ${this.defaultFontStacks.monospace};
          font-size: 0.9em;
        }
        pre {
          background: #2d2d2d;
          color: #f8f8f2;
          padding: 1em;
          border-radius: 5px;
          overflow-x: auto;
          font-size: 0.85em;
        }
        pre code { background: transparent; color: inherit; padding: 0; }
        ol { counter-reset: step; list-style: none; padding-left: 2em; }
        ol > li { counter-increment: step; position: relative; }
        ol > li::before {
          content: counter(step) ".";
          position: absolute;
          left: -1.5em;
          font-weight: bold;
          color: #3498db;
        }
        blockquote {
          background: #e8f4fc;
          border-left: 4px solid #3498db;
          padding: 0.8em 1em;
          margin: 1em 0;
        }
      `,
    });

    this.presets.set('magazine', {
      id: 'magazine',
      name: 'Magazine',
      nameKr: '매거진',
      description: '잡지 스타일 - 다단 레이아웃, 드롭캡, 시각적 강조',
      settings: {
        fontSize: '11pt',
        lineHeight: 1.5,
        paragraphSpacing: '0.5em',
        pageMargins: {
          top: '15mm',
          bottom: '20mm',
          left: '15mm',
          right: '15mm',
        },
        fontFamily: this.defaultFontStacks.serif,
        hyphenation: true,
        justification: 'justify',
        headingScale: {
          h1: 2.2,
          h2: 1.7,
          h3: 1.4,
          h4: 1.2,
          h5: 1.1,
          h6: 1.0,
        },
      },
      cssRules: `
        h1 {
          font-size: 2.5em;
          font-weight: 900;
          line-height: 1.1;
          margin-bottom: 0.3em;
        }
        h2 { 
          font-weight: 700;
          color: #c0392b;
        }
        p:first-of-type::first-letter {
          font-size: 4em;
          float: left;
          line-height: 0.8;
          margin: 0.05em 0.1em 0 0;
          font-weight: bold;
          color: #c0392b;
        }
        img {
          max-width: 100%;
          margin: 1em 0;
        }
        figure {
          margin: 1.5em 0;
        }
        figcaption {
          font-size: 0.8em;
          color: #777;
          border-bottom: 1px solid #ddd;
          padding-bottom: 0.3em;
        }
        blockquote {
          font-size: 1.3em;
          font-style: italic;
          color: #555;
          border: none;
          text-align: center;
          margin: 1.5em 2em;
        }
        blockquote::before { content: '"'; font-size: 2em; color: #c0392b; }
        blockquote::after { content: '"'; font-size: 2em; color: #c0392b; }
      `,
    });
  }

  getPreset(id: string): TypographyPreset | undefined {
    return this.presets.get(id);
  }

  getAllPresets(): TypographyPreset[] {
    return Array.from(this.presets.values());
  }

  /**
   * Generate CSS for a preset
   * Refactored to use modular CSS builders for better maintainability
   */
  generatePresetCSS(presetId: string, options: CSSGenerationOptions = {}): string {
    const preset = this.presets.get(presetId);
    if (!preset) {
      throw new Error(`Typography preset not found: ${presetId}`);
    }

    const settings = preset.settings;
    const format = options.outputFormat || 'epub';

    // Build CSS using modular approach
    const css: string[] = this.buildPresetCss(preset, settings, format, options, presetId);

    return css.join('\n');
  }

  /**
   * Build CSS array for a preset (extracted for testability)
   */
  private buildPresetCss(
    preset: TypographyPreset,
    settings: TypographySettings,
    format: 'epub' | 'pdf',
    options: CSSGenerationOptions,
    presetId: string
  ): string[] {
    const css: string[] = [];

    // Header comment
    css.push('/* Typography Preset: ' + preset.nameKr + ' */');
    css.push('');

    // PDF-specific setup (font import, box-sizing)
    if (format === 'pdf') {
      css.push(buildFontImport());
      css.push('');
      css.push(buildBoxSizingReset());
      css.push('');
    }

    // Body styles using builder
    css.push(...buildBodyStyles({
      fontFamily: settings.fontFamily,
      fontSize: settings.fontSize,
      lineHeight: settings.lineHeight,
      justification: settings.justification,
      hyphenation: settings.hyphenation,
      format: format
    }));
    css.push('');

    // PDF title block hide
    if (format === 'pdf') {
      css.push(buildPdfTitleBlockHide());
      css.push('');
    }

    // PDF page rules
    if (format === 'pdf' && options.includePageBreaks !== false) {
      css.push(...buildPdfPageRules(settings.pageMargins));
      css.push('');
    }

    // PDF-specific image styling for proper page layout
    if (format === 'pdf') {
      css.push(...buildPdfImageStyles());
      css.push('');
    }

    // Paragraph styles
    const textIndent = (settings.textIndent && presetId === 'novel') ? settings.textIndent : undefined;
    css.push(...buildParagraphStyles(settings.paragraphSpacing, textIndent));
    css.push('');

    // Heading styles using builder
    css.push(...buildHeadingStyles(settings.headingScale as HeadingScale, format));

    // Common element styles (images, tables, code, blockquotes)
    css.push(...buildCommonElementStyles(format));
    css.push('');

    // Preset-specific custom CSS rules
    if (preset.cssRules) {
      css.push('/* Preset Custom Styles */');
      css.push(preset.cssRules);
    }

    // Additional CSS (e.g., cover styles)
    if (options.additionalCss) {
      css.push('');
      css.push('/* Additional Styles (Cover, etc.) */');
      css.push(options.additionalCss);
    }

    return css;
  }
}
