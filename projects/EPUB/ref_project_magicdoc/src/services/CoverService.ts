/**
 * Cover Service - Generates cover pages for EPUB and PDF
 */

import * as fs from 'fs';
import * as path from 'path';
import { COVER_THEMES } from '../utils/constants.js';
import { getTempDir } from '../utils/fileUtils.js';
import { Logger } from '../utils/common.js';

export interface CoverData {
    title: string;
    author?: string;
    themeId: string;
}

export class CoverService {
    /**
     * Generate an SVG cover for EPUB
     */
    async generateEpubCover(data: CoverData): Promise<string> {
        const theme = COVER_THEMES[data.themeId] || COVER_THEMES.apple;
        const tempDir = getTempDir();
        const coverPath = path.join(tempDir, `cover-${Date.now()}.svg`);

        // Calculate title layout with dynamic sizing
        const titleLayout = this.calculateTitleLayout(data.title);
        const titleTspans = this.generateTitleTspans(
            this.escapeXml(data.title),
            800,
            titleLayout.startY,
            titleLayout.fontSize,
            titleLayout.lineHeight,
            titleLayout.maxCharsPerLine
        );

        const svg = `
<svg width="1600" height="2400" viewBox="0 0 1600 2400" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:${theme.colors.primary};stop-opacity:1" />
            <stop offset="100%" style="stop-color:${theme.colors.secondary};stop-opacity:1" />
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="20" />
            <feOffset dx="10" dy="10" result="offsetblur" />
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.5" />
            </feComponentTransfer>
            <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="100%" height="100%" fill="${theme.style === 'gradient' ? 'url(#bgGrad)' : theme.colors.background}" />
    
    <!-- Accent Line/Border -->
    <rect x="80" y="80" width="1440" height="2240" fill="none" stroke="${theme.colors.accent}" stroke-width="4" opacity="0.5" />
    
    <!-- Title Area -->
    <g filter="url(#shadow)">
        <text x="800" font-family="'Noto Sans KR', sans-serif" font-size="${titleLayout.fontSize}" font-weight="900" fill="${theme.colors.text}" text-anchor="middle">
            ${titleTspans}
        </text>
    </g>
    
    <!-- Decorative Element -->
    <line x1="400" y1="${titleLayout.dividerY}" x2="1200" y2="${titleLayout.dividerY}" stroke="${theme.colors.accent}" stroke-width="2" opacity="0.8" />
    
    <!-- Author Area -->
    <text x="800" y="2100" font-family="'Noto Sans KR', sans-serif" font-size="80" font-weight="300" fill="${theme.colors.text}" text-anchor="middle" letter-spacing="10">
        ${this.escapeXml(data.author || 'Unknown Author').toUpperCase()}
    </text>
</svg>
        `.trim();

        fs.writeFileSync(coverPath, svg, 'utf-8');
        Logger.info(`Generated EPUB cover (SVG): ${coverPath}`);
        return coverPath;
    }

    /**
     * Generate HTML fragment and CSS for PDF cover
     * Uses fixed A4 dimensions (210mm x 297mm) for reliable full-bleed rendering
     */
    async generatePdfCoverData(data: CoverData): Promise<{ html: string; css: string }> {
        const theme = COVER_THEMES[data.themeId] || COVER_THEMES.apple;

        // Smart title line breaking for long titles
        const titleLines = this.splitTitleIntoLines(data.title, 14);
        const titleFontSize = titleLines.length > 2 ? '36pt' : titleLines.length > 1 ? '42pt' : '48pt';
        const titleHtml = titleLines.map(line =>
            `<span style="display: block;">${this.escapeXml(line)}</span>`
        ).join('\n');

        const css = `
            /* PDF Cover Page - Full bleed using fixed A4 dimensions */
            .pdf-cover-page {
                width: 210mm;
                height: 297mm;
                margin: 0;
                padding: 0;
                background: ${theme.style === 'gradient' ? `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})` : theme.colors.background};
                color: ${theme.colors.text};
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                box-sizing: border-box;
                overflow: hidden;
                break-after: page;
                page-break-after: always;
            }
            .pdf-cover-frame {
                width: 85%;
                height: 85%;
                border: 1px solid ${theme.colors.accent}44;
                border-radius: 4px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 3cm 2cm;
                box-sizing: border-box;
            }
            .pdf-cover-title-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                width: 100%;
            }
            .pdf-cover-title-group h1 {
                font-size: ${titleFontSize};
                font-weight: 900;
                margin: 0;
                line-height: 1.3;
                color: ${theme.colors.text} !important;
                border: none !important;
                padding: 0 !important;
                word-break: keep-all;
                max-width: 100%;
            }
            .pdf-cover-divider {
                width: 80px;
                height: 3px;
                background: ${theme.colors.accent};
                margin: 2em auto;
                border-radius: 2px;
            }
            .pdf-cover-author {
                font-size: 18pt;
                font-weight: 300;
                letter-spacing: 0.15em;
                color: ${theme.colors.text};
                opacity: 0.9;
                margin-top: auto;
                padding-top: 2em;
            }
        `;

        const html = `
            <div class="pdf-cover-page">
                <div class="pdf-cover-frame">
                    <div class="pdf-cover-title-group">
                        <h1>${titleHtml}</h1>
                        <div class="pdf-cover-divider"></div>
                    </div>
                    <div class="pdf-cover-author">${this.escapeXml(data.author || '')}</div>
                </div>
            </div>
        `;

        return { html, css };
    }

    /**
     * Split title into multiple lines for better readability
     * Korean characters are wider, so we use smaller max chars per line
     */
    private splitTitleIntoLines(title: string, maxCharsPerLine: number = 14): string[] {
        if (title.length <= maxCharsPerLine) {
            return [title];
        }

        // Check if title contains spaces (for word-based breaking)
        const words = title.split(/\s+/);
        if (words.length > 1) {
            const lines: string[] = [];
            let currentLine = '';

            for (const word of words) {
                const testLine = currentLine ? `${currentLine} ${word}` : word;
                if (testLine.length > maxCharsPerLine && currentLine) {
                    lines.push(currentLine);
                    currentLine = word;
                } else {
                    currentLine = testLine;
                }
            }
            if (currentLine) {
                lines.push(currentLine);
            }
            return lines;
        }

        // For single long word (common in Korean), break by character count
        const lines: string[] = [];
        for (let i = 0; i < title.length; i += maxCharsPerLine) {
            lines.push(title.slice(i, i + maxCharsPerLine));
        }
        return lines;
    }

    /**
     * Calculate title layout parameters based on title length and content
     * Returns font size, line height, and positioning for optimal display
     */
    private calculateTitleLayout(title: string): {
        fontSize: number;
        lineHeight: number;
        maxCharsPerLine: number;
        startY: number;
        dividerY: number;
    } {
        // Count Korean characters (they are wider than Latin characters)
        const koreanChars = (title.match(/[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]/g) || []).length;
        const totalChars = title.length;
        const koreanRatio = koreanChars / totalChars;

        // Effective length considers Korean chars as 1.5x width
        const effectiveLength = totalChars + (koreanChars * 0.5);

        // Determine font size and layout based on effective length
        let fontSize: number;
        let lineHeight: number;
        let maxCharsPerLine: number;

        if (effectiveLength <= 10) {
            // Very short title - large font
            fontSize = 160;
            lineHeight = 180;
            maxCharsPerLine = 12;
        } else if (effectiveLength <= 18) {
            // Short title - standard large font
            fontSize = 140;
            lineHeight = 160;
            maxCharsPerLine = koreanRatio > 0.5 ? 10 : 14;
        } else if (effectiveLength <= 28) {
            // Medium title - medium font
            fontSize = 120;
            lineHeight = 140;
            maxCharsPerLine = koreanRatio > 0.5 ? 12 : 16;
        } else if (effectiveLength <= 40) {
            // Long title - smaller font
            fontSize = 100;
            lineHeight = 120;
            maxCharsPerLine = koreanRatio > 0.5 ? 14 : 18;
        } else {
            // Very long title - smallest font
            fontSize = 80;
            lineHeight = 100;
            maxCharsPerLine = koreanRatio > 0.5 ? 16 : 22;
        }

        // Calculate number of lines for vertical positioning
        const lines = this.splitTitleIntoLinesSvg(title, maxCharsPerLine);
        const numLines = lines.length;
        const totalTextHeight = numLines * lineHeight;

        // Center title vertically in the upper portion (between y=400 and y=1100)
        const titleAreaCenter = 750;
        const startY = titleAreaCenter - (totalTextHeight / 2) + (lineHeight / 2);

        // Position divider below the title with some spacing
        const dividerY = startY + totalTextHeight + 80;

        return {
            fontSize,
            lineHeight,
            maxCharsPerLine,
            startY: Math.max(400, startY), // Ensure minimum top margin
            dividerY: Math.min(1300, Math.max(1000, dividerY)) // Keep divider in reasonable range
        };
    }

    /**
     * Split title into lines for SVG rendering
     * Handles both space-separated words and continuous Korean text
     */
    private splitTitleIntoLinesSvg(title: string, maxCharsPerLine: number): string[] {
        // First, check if title is short enough for single line
        if (title.length <= maxCharsPerLine) {
            return [title];
        }

        // Check for natural break points (spaces, hyphens, etc.)
        const hasSpaces = /\s/.test(title);

        if (hasSpaces) {
            // Word-based breaking for titles with spaces
            const words = title.split(/\s+/);
            const lines: string[] = [];
            let currentLine = '';

            for (const word of words) {
                const testLine = currentLine ? `${currentLine} ${word}` : word;
                if (testLine.length > maxCharsPerLine && currentLine) {
                    lines.push(currentLine.trim());
                    currentLine = word;
                } else {
                    currentLine = testLine;
                }
            }
            if (currentLine) {
                lines.push(currentLine.trim());
            }
            return lines;
        } else {
            // Character-based breaking for continuous text (common in Korean)
            const lines: string[] = [];
            for (let i = 0; i < title.length; i += maxCharsPerLine) {
                lines.push(title.slice(i, i + maxCharsPerLine));
            }
            return lines;
        }
    }

    /**
     * Generate SVG tspan elements for title with proper positioning
     */
    private generateTitleTspans(
        title: string,
        x: number,
        startY: number,
        fontSize: number,
        lineHeight: number,
        maxCharsPerLine: number
    ): string {
        const lines = this.splitTitleIntoLinesSvg(title, maxCharsPerLine);

        return lines.map((line, i) => {
            const y = startY + (i * lineHeight);
            return `<tspan x="${x}" y="${y}">${line}</tspan>`;
        }).join('\n            ');
    }

    private escapeXml(unsafe: string): string {
        return unsafe.replace(/[<>&"']/g, (c) => {
            switch (c) {
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '&': return '&amp;';
                case '"': return '&quot;';
                case "'": return '&apos;';
                default: return c;
            }
        });
    }
}
