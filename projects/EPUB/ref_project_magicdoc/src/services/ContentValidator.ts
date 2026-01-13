/**
 * Content Validator - 8 Validation Modules
 */

import type { ValidationReport, ValidationIssue } from '../types/index.js';
import type { ValidationResult, ValidatorConfig } from '../types/validators.js';
import { Logger } from '../utils/common.js';

export class ContentValidator {
    private config: ValidatorConfig;

    constructor(config: Partial<ValidatorConfig> = {}) {
        this.config = {
            autoFix: config.autoFix ?? true,
            strictMode: config.strictMode ?? false,
            allowedImageFormats: config.allowedImageFormats ?? ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'],
            maxImageSize: config.maxImageSize ?? 10 * 1024 * 1024, // 10MB
            requireAltText: config.requireAltText ?? true,
            checkExternalLinks: config.checkExternalLinks ?? false,
        };
    }

    /**
     * Run all validation modules
     */
    async validate(content: string, filePath?: string): Promise<ValidationReport> {
        const issues: ValidationIssue[] = [];

        Logger.info('Starting content validation...');

        // Module 1: Frontmatter validation
        const frontmatterResult = this.validateFrontmatter(content);
        issues.push(...frontmatterResult);

        // Module 2: Heading validation
        const headingResult = this.validateHeadings(content);
        issues.push(...headingResult);

        // Module 3: Link validation
        const linkResult = this.validateLinks(content);
        issues.push(...linkResult);

        // Module 4: Image validation
        const imageResult = this.validateImages(content);
        issues.push(...imageResult);

        // Module 5: Table validation
        const tableResult = this.validateTables(content);
        issues.push(...tableResult);

        // Module 6: Syntax validation
        const syntaxResult = this.validateSyntax(content);
        issues.push(...syntaxResult);

        // Module 7: Special character validation
        const specialResult = this.validateSpecialCharacters(content);
        issues.push(...specialResult);

        // Module 8: Accessibility validation
        const accessibilityResult = this.validateAccessibility(content);
        issues.push(...accessibilityResult);

        // Auto-fix if enabled
        let fixedIssues = 0;
        if (this.config.autoFix) {
            for (const issue of issues) {
                if (issue.fixed) {
                    fixedIssues++;
                }
            }
        }

        const errors = issues.filter(i => i.type === 'error');
        const warnings = issues.filter(i => i.type === 'warning');

        Logger.info('Validation completed', {
            total: issues.length,
            errors: errors.length,
            warnings: warnings.length,
            fixed: fixedIssues,
        });

        return {
            totalIssues: issues.length,
            fixedIssues,
            warnings: warnings.length,
            errors: errors.length,
            details: issues,
        };
    }

    /**
     * Module 1: Frontmatter validation
     */
    private validateFrontmatter(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];
        const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n/;
        const match = content.match(frontmatterRegex);

        if (!match) {
            issues.push({
                type: 'warning',
                category: 'frontmatter',
                message: 'YAML frontmatter가 없습니다. 메타데이터를 추가하는 것을 권장합니다.',
                suggestion: '문서 상단에 ---로 감싸진 YAML frontmatter를 추가하세요.',
            });
            return issues;
        }

        const yamlContent = match[1];
        const lines = yamlContent.split('\n');

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmed = line.trim();

            if (!trimmed || trimmed.startsWith('#')) continue;

            const colonIndex = trimmed.indexOf(':');
            if (colonIndex === -1) {
                issues.push({
                    type: 'warning',
                    category: 'frontmatter',
                    message: `YAML 구문 오류: 콜론(:)이 누락됨`,
                    line: i + 1,
                    suggestion: 'key: value 형식을 확인하세요.',
                });
            }
        }

        return issues;
    }

    /**
     * Module 2: Heading validation
     */
    private validateHeadings(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];
        const lines = content.split('\n');
        const h1Titles: string[] = [];
        let lastLevel = 0;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);

            if (headingMatch) {
                const level = headingMatch[1].length;
                const title = headingMatch[2].trim();

                // Check for duplicate H1
                if (level === 1) {
                    if (h1Titles.includes(title)) {
                        issues.push({
                            type: 'warning',
                            category: 'heading',
                            message: `중복된 H1 제목: "${title}"`,
                            line: i + 1,
                            suggestion: 'H1은 문서당 하나만 사용하는 것을 권장합니다.',
                        });
                    }
                    h1Titles.push(title);
                }

                // Check for heading level gaps
                if (lastLevel > 0 && level > lastLevel + 1) {
                    issues.push({
                        type: 'warning',
                        category: 'heading',
                        message: `제목 레벨 갭: H${lastLevel} → H${level}`,
                        line: i + 1,
                        suggestion: `H${lastLevel + 1}을 건너뛰었습니다.`,
                    });
                }

                lastLevel = level;
            }
        }

        return issues;
    }

    /**
     * Module 3: Link validation
     */
    private validateLinks(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];
        const lines = content.split('\n');

        // Check for Obsidian links [[link]]
        const obsidianLinkRegex = /\[\[([^\]]+)\]\]/g;
        let match;

        while ((match = obsidianLinkRegex.exec(content)) !== null) {
            issues.push({
                type: 'info',
                category: 'link',
                message: `Obsidian 링크 발견: "${match[1]}"`,
                suggestion: '자동으로 표준 마크다운 링크로 변환됩니다.',
                fixed: true,
            });
        }

        // Check for broken markdown links
        const markdownLinkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        let linkMatch;

        while ((linkMatch = markdownLinkRegex.exec(content)) !== null) {
            const url = linkMatch[2];

            // Check for empty URLs
            if (!url || url.trim() === '') {
                issues.push({
                    type: 'error',
                    category: 'link',
                    message: '빈 링크 URL',
                    suggestion: '링크 URL을 입력하세요.',
                });
            }

            // Check for external links if enabled
            if (this.config.checkExternalLinks && url.startsWith('http')) {
                issues.push({
                    type: 'info',
                    category: 'link',
                    message: `외부 링크: ${url}`,
                    suggestion: '외부 링크는 변환 후에도 작동해야 합니다.',
                });
            }
        }

        return issues;
    }

    /**
     * Module 4: Image validation
     */
    private validateImages(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];

        // Check for images without alt text
        const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
        let match;

        while ((match = imageRegex.exec(content)) !== null) {
            const alt = match[1];
            const url = match[2];

            // Check for missing alt text
            if (this.config.requireAltText && (!alt || alt.trim() === '')) {
                issues.push({
                    type: 'warning',
                    category: 'image',
                    message: '이미지 alt 텍스트가 없습니다.',
                    suggestion: '접근성을 위해 이미지에 설명을 추가하세요.',
                });
            }

            // Check image format
            const ext = url.split('.').pop()?.toLowerCase();
            if (ext && !this.config.allowedImageFormats.includes(ext)) {
                issues.push({
                    type: 'warning',
                    category: 'image',
                    message: `지원하지 않는 이미지 형식: ${ext}`,
                    suggestion: `지원 형식: ${this.config.allowedImageFormats.join(', ')}`,
                });
            }
        }

        return issues;
    }

    /**
     * Module 5: Table validation
     */
    private validateTables(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];
        const lines = content.split('\n');
        let inTable = false;
        let columnCount = 0;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();

            if (line.startsWith('|') && line.endsWith('|')) {
                if (!inTable) {
                    inTable = true;
                    const cells = line.split('|').filter(c => c.trim() !== '');
                    columnCount = cells.length;
                } else {
                    const cells = line.split('|').filter(c => c.trim() !== '');

                    if (cells.length !== columnCount && !line.includes('---')) {
                        issues.push({
                            type: 'warning',
                            category: 'table',
                            message: `테이블 열 불일치: ${columnCount}개 예상, ${cells.length}개 발견`,
                            line: i + 1,
                            suggestion: '모든 행의 열 수를 일치시키세요.',
                        });
                    }
                }
            } else {
                inTable = false;
                columnCount = 0;
            }
        }

        return issues;
    }

    /**
     * Module 6: Syntax validation
     */
    private validateSyntax(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];

        // Check for unclosed code blocks
        const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
        const codeBlockMatches = content.match(/```/g);

        if (codeBlockMatches && codeBlockMatches.length % 2 !== 0) {
            issues.push({
                type: 'error',
                category: 'syntax',
                message: '닫히지 않은 코드 블록',
                suggestion: '코드 블록을 ```로 닫으세요.',
                fixed: true,
            });
        }

        // Check for unclosed inline code
        const inlineCodeMatches = content.match(/`[^`]+`/g);
        const backtickCount = (content.match(/`/g) || []).length;

        if (backtickCount % 2 !== 0) {
            issues.push({
                type: 'warning',
                category: 'syntax',
                message: '닫히지 않은 인라인 코드',
                suggestion: '인라인 코드를 `로 닫으세요.',
            });
        }

        return issues;
    }

    /**
     * Module 7: Special character validation
     */
    private validateSpecialCharacters(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];

        // Check for emojis (may not render correctly in some formats)
        const emojiRegex = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu;
        const emojis = content.match(emojiRegex);

        if (emojis && emojis.length > 0) {
            issues.push({
                type: 'warning',
                category: 'syntax',
                message: `${emojis.length}개의 이모지 발견`,
                suggestion: '일부 형식에서 이모지가 올바르게 렌더링되지 않을 수 있습니다.',
            });
        }

        // Check for ASCII diagrams
        const asciiDiagramRegex = /[+\-|\/\\]{10,}/g;
        if (asciiDiagramRegex.test(content)) {
            issues.push({
                type: 'info',
                category: 'syntax',
                message: 'ASCII 다이어그램 발견',
                suggestion: '다이어그램은 이미지로 변환하는 것을 권장합니다.',
            });
        }

        return issues;
    }

    /**
     * Module 8: Accessibility validation
     */
    private validateAccessibility(content: string): ValidationIssue[] {
        const issues: ValidationIssue[] = [];

        // Check for proper heading hierarchy
        const lines = content.split('\n');
        let hasH1 = false;

        for (const line of lines) {
            if (line.startsWith('# ')) {
                hasH1 = true;
                break;
            }
        }

        if (!hasH1) {
            issues.push({
                type: 'warning',
                category: 'accessibility',
                message: 'H1 제목이 없습니다.',
                suggestion: '문서에 H1 제목을 추가하세요.',
            });
        }

        // Check for long paragraphs (hard to read)
        const paragraphs = content.split('\n\n');
        for (let i = 0; i < paragraphs.length; i++) {
            const paragraph = paragraphs[i].trim();
            const wordCount = paragraph.split(/\s+/).length;

            if (wordCount > 300) {
                issues.push({
                    type: 'info',
                    category: 'accessibility',
                    message: `긴 문단 발견 (${wordCount}단어)`,
                    suggestion: '가독성을 위해 문단을 나누는 것을 권장합니다.',
                });
            }
        }

        return issues;
    }

    /**
     * Auto-fix content based on validation results
     */
    autoFix(content: string, report: ValidationReport): string {
        let fixedContent = content;

        for (const issue of report.details) {
            if (issue.fixed && issue.category === 'link') {
                // Fix Obsidian links
                fixedContent = fixedContent.replace(
                    /\[\[([^\]]+)\]\]/g,
                    (match, link) => {
                        const parts = link.split('|');
                        const text = parts[1] || parts[0];
                        const target = parts[0];
                        return target.startsWith('http') ? `[${text}](${target})` : `[${text}](${target}.md)`;
                    }
                );
            }

            if (issue.fixed && issue.category === 'syntax') {
                // Fix unclosed code blocks
                const codeBlockCount = (fixedContent.match(/```/g) || []).length;
                if (codeBlockCount % 2 !== 0) {
                    fixedContent += '\n```';
                }
            }
        }

        return fixedContent;
    }
}
