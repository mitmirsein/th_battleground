/**
 * Path Validator - Robust file path handling and validation
 * 
 * Handles common path issues:
 * - Backslash escapes in paths
 * - Quoted paths
 * - Spaces in paths
 * - Relative vs absolute paths
 * - Path existence validation
 */

import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';

export interface PathValidationResult {
    valid: boolean;
    normalizedPath?: string;
    error?: string;
    suggestions?: string[];
}

export class PathValidator {
    /**
     * Normalize and clean a file path
     * Handles backslashes, quotes, and other common issues
     */
    static normalizePath(inputPath: string): string {
        let cleaned = inputPath.trim();

        // Remove surrounding quotes (single or double)
        cleaned = cleaned.replace(/^['"]|['"]$/g, '');

        // Replace escaped spaces (\ ) with regular spaces
        cleaned = cleaned.replace(/\\\s/g, ' ');

        // Replace other escaped characters
        cleaned = cleaned.replace(/\\(.)/g, '$1');

        // Normalize path separators and resolve
        cleaned = path.normalize(cleaned);

        // Resolve to absolute path if relative
        if (!path.isAbsolute(cleaned)) {
            cleaned = path.resolve(process.cwd(), cleaned);
        }

        return cleaned;
    }

    /**
     * Validate a file path and provide helpful feedback
     */
    static validatePath(inputPath: string): PathValidationResult {
        if (!inputPath || inputPath.trim() === '') {
            return {
                valid: false,
                error: '파일 경로가 비어있습니다.',
                suggestions: [
                    '파일을 터미널로 드래그 앤 드롭하세요',
                    '또는 절대 경로를 입력하세요: /Users/username/document.md'
                ]
            };
        }

        const normalizedPath = this.normalizePath(inputPath);

        // Check if file exists
        if (!fs.existsSync(normalizedPath)) {
            const suggestions = this.generatePathSuggestions(normalizedPath);
            return {
                valid: false,
                normalizedPath,
                error: `파일을 찾을 수 없습니다: ${normalizedPath}`,
                suggestions
            };
        }

        // Check if it's a file (not a directory)
        const stats = fs.statSync(normalizedPath);
        if (!stats.isFile()) {
            return {
                valid: false,
                normalizedPath,
                error: `디렉토리가 아닌 파일을 선택해야 합니다: ${normalizedPath}`,
                suggestions: [
                    '마크다운 파일(.md)을 선택하세요',
                    '디렉토리 내의 특정 파일을 지정하세요'
                ]
            };
        }

        // Check if it's a markdown file
        if (!normalizedPath.endsWith('.md')) {
            return {
                valid: false,
                normalizedPath,
                error: `마크다운 파일(.md)이 아닙니다: ${normalizedPath}`,
                suggestions: [
                    '파일 확장자가 .md인지 확인하세요',
                    '예: document.md, README.md'
                ]
            };
        }

        return {
            valid: true,
            normalizedPath
        };
    }

    /**
     * Generate helpful suggestions based on the invalid path
     */
    private static generatePathSuggestions(invalidPath: string): string[] {
        const suggestions: string[] = [];
        const dirname = path.dirname(invalidPath);
        const basename = path.basename(invalidPath);

        // Check if directory exists
        if (fs.existsSync(dirname)) {
            suggestions.push(`디렉토리는 존재합니다: ${dirname}`);

            // Try to find similar files
            try {
                const files = fs.readdirSync(dirname);
                const mdFiles = files.filter(f => f.endsWith('.md'));

                if (mdFiles.length > 0) {
                    suggestions.push(`이 디렉토리의 마크다운 파일:`);
                    mdFiles.slice(0, 5).forEach(f => {
                        suggestions.push(`  - ${path.join(dirname, f)}`);
                    });
                    if (mdFiles.length > 5) {
                        suggestions.push(`  ... 그 외 ${mdFiles.length - 5}개 파일`);
                    }
                }
            } catch {
                // Ignore permission errors
            }
        } else {
            suggestions.push('디렉토리가 존재하지 않습니다');
            suggestions.push('경로를 다시 확인하세요');
        }

        // Common mistakes
        if (invalidPath.includes('\\')) {
            suggestions.push('⚠️  백슬래시(\\)가 포함되어 있습니다');
            suggestions.push('파일을 드래그 앤 드롭하거나 따옴표 없이 경로를 입력하세요');
        }

        return suggestions;
    }

    /**
     * Display validation error with helpful suggestions
     */
    static displayValidationError(result: PathValidationResult): void {
        console.log(chalk.red(`\n❌ ${result.error}\n`));

        if (result.suggestions && result.suggestions.length > 0) {
            console.log(chalk.yellow('💡 도움말:'));
            result.suggestions.forEach(suggestion => {
                if (suggestion.startsWith('  -')) {
                    console.log(chalk.gray(suggestion));
                } else if (suggestion.startsWith('⚠️')) {
                    console.log(chalk.yellow(`   ${suggestion}`));
                } else {
                    console.log(chalk.cyan(`   • ${suggestion}`));
                }
            });
            console.log();
        }

        console.log(chalk.cyan('📝 올바른 경로 입력 방법:'));
        console.log(chalk.gray('   1. 파일을 터미널 창으로 드래그 앤 드롭'));
        console.log(chalk.gray('   2. 절대 경로 입력: /Users/username/document.md'));
        console.log(chalk.gray('   3. 상대 경로 입력: ./docs/document.md'));
        console.log();
    }

    /**
     * Interactive path input with validation
     */
    static async promptForValidPath(initialPath?: string): Promise<string | null> {
        let attempts = 0;
        const maxAttempts = 3;

        while (attempts < maxAttempts) {
            const inputPath = initialPath || '';
            const result = this.validatePath(inputPath);

            if (result.valid && result.normalizedPath) {
                return result.normalizedPath;
            }

            this.displayValidationError(result);
            attempts++;

            if (attempts >= maxAttempts) {
                console.log(chalk.red('❌ 최대 시도 횟수를 초과했습니다.\n'));
                return null;
            }
        }

        return null;
    }

    /**
     * Quick validation for CLI arguments
     */
    static quickValidate(inputPath: string): { valid: boolean; path?: string; error?: string } {
        const result = this.validatePath(inputPath);
        return {
            valid: result.valid,
            path: result.normalizedPath,
            error: result.error
        };
    }
}
