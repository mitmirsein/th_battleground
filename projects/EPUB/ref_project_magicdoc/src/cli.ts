#!/usr/bin/env node

/**
 * Markdown to Document CLI
 * 
 * Refactored for improved UX with streamlined Interactive Mode
 * 
 * Usage:
 *   npx markdown-to-document-cli <input.md>
 *   m2d <input.md> [options]
 *   m2d interactive (or m2d i)
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { MarkdownToDocument } from './index.js';
import { DEFAULT_CONFIG, TYPOGRAPHY_PRESETS, COVER_THEMES } from './utils/constants.js';
import { Logger } from './utils/common.js';
import { DependencyChecker } from './utils/dependencyChecker.js';
import { PathValidator } from './utils/pathValidator.js';
import * as path from 'path';
import * as fs from 'fs';
import { fileURLToPath } from 'url';

// ============ Type Definitions ============

type InteractiveMode = 'quick' | 'custom';
type OutputFormat = 'epub' | 'pdf' | 'both';

const program = new Command();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const getCliVersion = (): string => {
    try {
        const packageJsonPath = path.resolve(__dirname, '..', 'package.json');
        const raw = fs.readFileSync(packageJsonPath, 'utf-8');
        const parsed = JSON.parse(raw) as { version?: string };
        return parsed.version || '0.0.0';
    } catch {
        return '0.0.0';
    }
};

// ============ Helper Functions for Interactive Mode ============

interface MarkdownAnalysisResult {
    hasObsidianImages: boolean;
    hasObsidianLinks: boolean;
    hasHighlights: boolean;
    hasCallouts: boolean;
    hasLongCodeLines: boolean;
    hasComplexTables: boolean;
    hasMultipleH1: boolean;
    hasFrontmatter: boolean;
    imageCount: number;
    tableCount: number;
    codeBlockCount: number;
    wordCount: number;
    recommendPreprocess: boolean;
    recommendedPreset: string;
    issues: string[];
}

/**
 * Analyze markdown content for Obsidian syntax and output optimization needs
 */
function analyzeMarkdownContent(content: string): MarkdownAnalysisResult {
    const result: MarkdownAnalysisResult = {
        hasObsidianImages: false,
        hasObsidianLinks: false,
        hasHighlights: false,
        hasCallouts: false,
        hasLongCodeLines: false,
        hasComplexTables: false,
        hasMultipleH1: false,
        hasFrontmatter: false,
        imageCount: 0,
        tableCount: 0,
        codeBlockCount: 0,
        wordCount: 0,
        recommendPreprocess: false,
        recommendedPreset: 'ebook',
        issues: [],
    };

    // Check for YAML frontmatter
    result.hasFrontmatter = /^---\n[\s\S]*?\n---/.test(content);

    // Check for Obsidian image syntax: ![[image]]
    const obsidianImageMatches = content.match(/!\[\[([^\]]+)\]\]/g);
    result.hasObsidianImages = !!obsidianImageMatches;
    if (obsidianImageMatches) {
        result.issues.push(`Obsidian 이미지 문법 ${obsidianImageMatches.length}개 발견`);
    }

    // Check for Obsidian internal links: [[link]]
    const obsidianLinkMatches = content.match(/(?<!!)\[\[([^\]]+)\]\]/g);
    result.hasObsidianLinks = !!obsidianLinkMatches;
    if (obsidianLinkMatches) {
        result.issues.push(`Obsidian 내부 링크 ${obsidianLinkMatches.length}개 발견`);
    }

    // Check for highlights: ==text==
    const highlightMatches = content.match(/==([^=]+)==/g);
    result.hasHighlights = !!highlightMatches;
    if (highlightMatches) {
        result.issues.push(`하이라이트 문법 ${highlightMatches.length}개 발견`);
    }

    // Check for callouts: > [!type]
    const calloutMatches = content.match(/>\s*\[!(\w+)\]/g);
    result.hasCallouts = !!calloutMatches;
    if (calloutMatches) {
        result.issues.push(`콜아웃 ${calloutMatches.length}개 발견`);
    }

    // Count images (standard markdown)
    const standardImageMatches = content.match(/!\[([^\]]*)\]\([^)]+\)/g);
    result.imageCount = (obsidianImageMatches?.length || 0) + (standardImageMatches?.length || 0);

    // Count tables
    const tableMatches = content.match(/\|.*\|.*\n\|[-:| ]+\|/g);
    result.tableCount = tableMatches?.length || 0;

    // Check for complex tables (>5 columns or very long cells)
    if (tableMatches) {
        for (const table of tableMatches) {
            const columns = (table.match(/\|/g)?.length || 0) - 1;
            if (columns > 5) {
                result.hasComplexTables = true;
                result.issues.push('5열 초과 복잡한 표 발견');
                break;
            }
        }
    }

    // Count code blocks and check for long lines
    const codeBlockMatches = content.match(/```[\s\S]*?```/g);
    result.codeBlockCount = codeBlockMatches?.length || 0;
    if (codeBlockMatches) {
        for (const block of codeBlockMatches) {
            const lines = block.split('\n');
            for (const line of lines) {
                if (line.length > 100) {
                    result.hasLongCodeLines = true;
                    result.issues.push('100자 초과 코드 라인 발견 (PDF 잘림 위험)');
                    break;
                }
            }
            if (result.hasLongCodeLines) break;
        }
    }

    // Check for multiple H1
    const h1Matches = content.match(/^#\s+[^\n]+/gm);
    result.hasMultipleH1 = (h1Matches?.length || 0) > 1;
    if (result.hasMultipleH1) {
        result.issues.push(`H1 제목 ${h1Matches?.length}개 발견 (1개 권장)`);
    }

    // Word count (rough estimate)
    const textOnly = content.replace(/```[\s\S]*?```/g, '').replace(/[#*`\[\]()]/g, '');
    result.wordCount = textOnly.split(/\s+/).filter(w => w.length > 0).length;

    // Determine if preprocessing is recommended
    result.recommendPreprocess =
        result.hasObsidianImages ||
        result.hasObsidianLinks ||
        result.hasHighlights ||
        result.hasCallouts ||
        result.hasLongCodeLines ||
        result.hasComplexTables ||
        result.hasMultipleH1;

    // Recommend typography preset based on content analysis
    if (result.imageCount > 10) {
        result.recommendedPreset = 'image_heavy';
    } else if (result.tableCount > 5) {
        result.recommendedPreset = 'table_heavy';
    } else if (result.codeBlockCount > 10) {
        result.recommendedPreset = 'manual';
    } else if (result.wordCount > 10000) {
        result.recommendedPreset = 'text_heavy';
    } else {
        result.recommendedPreset = 'balanced';
    }

    return result;
}

/**
 * Display analysis result to console
 */
function displayAnalysisResult(result: MarkdownAnalysisResult): void {
    console.log(chalk.bold('📊 문서 분석 결과:\n'));

    // Statistics
    console.log(chalk.gray('  📝 단어 수:'), chalk.cyan(`약 ${result.wordCount.toLocaleString()}개`));
    console.log(chalk.gray('  🖼️  이미지:'), chalk.cyan(`${result.imageCount}개`));
    console.log(chalk.gray('  📊 표:'), chalk.cyan(`${result.tableCount}개`));
    console.log(chalk.gray('  💻 코드 블록:'), chalk.cyan(`${result.codeBlockCount}개`));
    console.log(chalk.gray('  📋 Frontmatter:'), result.hasFrontmatter ? chalk.green('있음') : chalk.yellow('없음'));

    // Issues found
    if (result.issues.length > 0) {
        console.log(chalk.yellow('\n⚠️  발견된 이슈:'));
        result.issues.forEach(issue => {
            console.log(chalk.yellow(`  • ${issue}`));
        });
    } else {
        console.log(chalk.green('\n✅ 특별한 이슈 없음 - 표준 Markdown'));
    }

    // Recommendation
    console.log(chalk.bold('\n💡 권장 사항:'));
    if (result.recommendPreprocess) {
        console.log(chalk.green('  → 문서 최적화가 필요하지만, 변환 과정에서 자동으로 적용됩니다.'));
    } else {
        console.log(chalk.blue('  → 바로 변환해도 안정적입니다.'));
    }
    console.log(chalk.gray(`  → 추천 프리셋: ${result.recommendedPreset}`));
}

/**
 * Get typography preset choices with recommended preset highlighted
 */
function getTypographyPresetChoices(analysisResult: MarkdownAnalysisResult) {
    const presetCategories = {
        'Basic': ['novel', 'presentation', 'review', 'ebook'],
        'Content-focused': ['text_heavy', 'table_heavy', 'image_heavy', 'balanced'],
        'Document Type': ['report', 'manual', 'magazine'],
    };

    const choices: any[] = [];

    for (const [category, presetIds] of Object.entries(presetCategories)) {
        choices.push(new inquirer.Separator(chalk.bold(`\n── ${category} ──`)));

        for (const presetId of presetIds) {
            const preset = TYPOGRAPHY_PRESETS[presetId];
            if (preset) {
                const isRecommended = presetId === analysisResult.recommendedPreset;
                const name = isRecommended
                    ? chalk.green(`★ ${preset.name}`) + chalk.gray(` - ${preset.description}`) + chalk.green(' (권장)')
                    : chalk.cyan(preset.name) + chalk.gray(` - ${preset.description}`);
                choices.push({ name, value: presetId });
            }
        }
    }

    return choices;
}

/**
 * Get cover theme choices grouped by category
 */
function getCoverThemeChoices() {
    const themeCategories: Record<string, string[]> = {
        'Basic': ['apple', 'modern_gradient', 'dark_tech', 'nature', 'classic_book', 'minimalist'],
        'Professional': ['corporate', 'academic', 'magazine'],
        'Creative': ['sunset', 'ocean', 'aurora', 'rose_gold'],
        'Seasonal': ['spring', 'autumn', 'winter'],
    };

    const choices: any[] = [];

    for (const [category, themeIds] of Object.entries(themeCategories)) {
        choices.push(new inquirer.Separator(chalk.bold(`\n── ${category} ──`)));

        for (const themeId of themeIds) {
            const theme = COVER_THEMES[themeId];
            if (theme) {
                choices.push({
                    name: chalk.cyan(theme.name) + chalk.gray(` - ${theme.description}`),
                    value: themeId,
                });
            }
        }
    }

    return choices;
}

// Configure CLI
program
    .name('markdown-to-document')
    .alias('m2d')
    .description('Professional-grade EPUB/PDF conversion tool for Markdown files')
    .version(getCliVersion())
    .argument('<input>', 'Input markdown file path')
    .option('--title <title>', 'Book title (defaults to frontmatter title or filename)')
    .option('--author <author>', 'Author name (defaults to frontmatter author)')
    .option('-o, --output <path>', 'Output directory')
    .option('-f, --format <format>', 'Output format (epub, pdf, both)', 'both')
    .option('-t, --typography <preset>', 'Typography preset (auto, novel, presentation, review, ebook, text_heavy, table_heavy, image_heavy, balanced, report, manual, magazine)', 'auto')
    .option('-c, --cover <theme>', 'Cover theme')
    .option('--no-validate', 'Skip content validation')
    .option('--no-auto-fix', 'Disable auto-fix')
    .option('--toc-depth <number>', 'Table of contents depth', '2')
    .option('--no-toc', 'Disable table of contents')
    .option('--pdf-engine <engine>', 'PDF engine (auto, pdflatex, xelatex, weasyprint)', 'auto')
    .option('--paper-size <size>', 'Paper size (a4, letter)', 'a4')
    .option('--font-subsetting', 'Enable font subsetting')
    .option('--css <path>', 'Custom CSS file path')
    .option('--pandoc-path <path>', 'Custom Pandoc executable path')
    .option('-v, --verbose', 'Verbose output')
    .action(async (input, options) => {
        try {
            // Enable verbose logging if requested
            if (options.verbose) {
                Logger.setEnabled(true);
                process.env.DEBUG = 'true';
            }

            // Validate and normalize input path
            const pathValidation = PathValidator.validatePath(input);

            if (!pathValidation.valid) {
                PathValidator.displayValidationError(pathValidation);
                process.exit(1);
            }

            const inputPath = pathValidation.normalizedPath!;

            const fileContent = fs.readFileSync(inputPath, 'utf-8');
            const analysisResult = analyzeMarkdownContent(fileContent);
            const metadata = extractMetadata(fileContent);

            const inferredTitle = metadata.title || path.basename(inputPath, '.md');
            const inferredAuthor = metadata.author || '';
            const customTitle = ((options.title as string | undefined) || inferredTitle).trim();
            const customAuthor = ((options.author as string | undefined) || inferredAuthor).trim();

            const typographyOption = String(options.typography || 'auto');
            const typographyPreset = typographyOption === 'auto' ? analysisResult.recommendedPreset : typographyOption;

            console.log(chalk.cyan.bold('\n📚 Markdown to Document CLI\n'));

            // Prepare conversion options
            const conversionOptions = {
                inputPath,
                outputPath: options.output ? path.resolve(options.output) : undefined,
                format: options.format as 'epub' | 'pdf' | 'both',
                typographyPreset: typographyPreset as any,
                coverTheme: options.cover,
                validateContent: options.validate !== false,
                autoFix: options.autoFix !== false,
                tocDepth: parseInt(options.tocDepth, 10),
                includeToc: options.toc !== false,
                pdfEngine: options.pdfEngine as any,
                paperSize: options.paperSize as any,
                enableFontSubsetting: options.fontSubsetting,
                cssPath: options.css ? path.resolve(options.css) : undefined,
                customTitle,
                customAuthor: customAuthor || undefined,
            };

            // Check dependencies proactively
            const depChecker = new DependencyChecker();
            const isReady = await depChecker.quickCheck(conversionOptions.format);

            if (!isReady) {
                await depChecker.displayDependencyReport();
                console.log(chalk.red('\n❌ 필수 의존성을 먼저 설치해 주세요.\n'));
                process.exit(1);
            }

            // Initialize converter
            const spinner = ora('Initializing...').start();
            const converter = new MarkdownToDocument(options.pandocPath);

            const initResult = await converter.initialize();
            if (!initResult.success) {
                spinner.fail('Initialization failed');
                console.error(chalk.red(`❌ ${initResult.error}`));
                console.log(chalk.yellow('\n' + MarkdownToDocument.getInstallInstructions()));
                process.exit(1);
            }

            spinner.succeed('Initialized successfully');

            // Show conversion info
            console.log(chalk.gray('─'.repeat(50)));
            console.log(chalk.bold('📄 Input:'), chalk.cyan(inputPath));
            console.log(chalk.bold('📤 Format:'), chalk.cyan(conversionOptions.format.toUpperCase()));
            console.log(chalk.bold('🎨 Typography:'), chalk.cyan(TYPOGRAPHY_PRESETS[conversionOptions.typographyPreset]?.name || conversionOptions.typographyPreset));
            console.log(chalk.bold('📖 Title:'), chalk.cyan(customTitle));
            if (customAuthor) console.log(chalk.bold('✍️  Author:'), chalk.cyan(customAuthor));
            if (conversionOptions.coverTheme) {
                console.log(chalk.bold('🖼️  Cover:'), chalk.cyan(COVER_THEMES[conversionOptions.coverTheme]?.name || conversionOptions.coverTheme));
            }
            console.log(chalk.gray('─'.repeat(50)) + '\n');

            // Start conversion
            const convertSpinner = ora('Converting document...').start();

            const result = await converter.convert(conversionOptions);

            if (result.success) {
                convertSpinner.succeed('Conversion completed!');

                // Show validation report if available
                if (result.validationReport) {
                    const report = result.validationReport;
                    console.log(chalk.gray('\n📊 Validation Report:'));

                    if (report.fixedIssues > 0) {
                        console.log(chalk.green(`  ✅ Fixed: ${report.fixedIssues} issues`));
                    }
                    if (report.warnings > 0) {
                        console.log(chalk.yellow(`  ⚠️  Warnings: ${report.warnings}`));
                    }
                    if (report.errors > 0) {
                        console.log(chalk.red(`  ❌ Errors: ${report.errors}`));
                    }
                }

                // Show warnings
                if (result.warnings.length > 0) {
                    console.log(chalk.yellow('\n⚠️  Warnings:'));
                    result.warnings.forEach(warning => {
                        console.log(chalk.yellow(`  • ${warning}`));
                    });
                }

                // Show output files
                console.log(chalk.green('\n✅ Output files:'));
                if (result.epubPath) {
                    console.log(chalk.green(`  📖 EPUB:  ${result.epubPath}`));
                }
                if (result.pdfPath) {
                    console.log(chalk.green(`  📄 PDF:   ${result.pdfPath}`));
                }

                console.log(chalk.green('\n🎉 Conversion successful!\n'));
            } else {
                convertSpinner.fail('Conversion failed');

                console.log(chalk.red('\n❌ Errors:'));
                result.errors.forEach(error => {
                    console.log(chalk.red(`  • ${error}`));
                });

                if (result.warnings.length > 0) {
                    console.log(chalk.yellow('\n⚠️  Warnings:'));
                    result.warnings.forEach(warning => {
                        console.log(chalk.yellow(`  • ${warning}`));
                    });
                }

                console.log(chalk.red('\n❌ Conversion failed!\n'));
                process.exit(1);
            }
        } catch (error) {
            console.error(chalk.red('\n❌ Unexpected error:'));
            console.error(chalk.red(error instanceof Error ? error.message : String(error)));

            if (options.verbose) {
                console.error(chalk.red('\nStack trace:'));
                console.error(error);
            }

            process.exit(1);
        }
    });

/**
 * Extract metadata from frontmatter
 */
function extractMetadata(content: string): { title?: string; author?: string } {
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!frontmatterMatch) return {};

    const frontmatter = frontmatterMatch[1];
    const titleMatch = frontmatter.match(/^title:\s*["']?(.+?)["']?\s*$/m);
    const authorMatch = frontmatter.match(/^author:\s*["']?(.+?)["']?\s*$/m);

    return {
        title: titleMatch?.[1]?.trim(),
        author: authorMatch?.[1]?.trim(),
    };
}

/**
 * Get simplified preset choices (top 6 most useful)
 */
function getSimplifiedPresetChoices(recommendedPreset: string) {
    const topPresets = ['ebook', 'novel', 'report', 'presentation', 'table_heavy', 'image_heavy'];

    return topPresets.map(presetId => {
        const preset = TYPOGRAPHY_PRESETS[presetId];
        if (!preset) return null;

        const isRecommended = presetId === recommendedPreset;
        const name = isRecommended
            ? chalk.green(`★ ${preset.name}`) + chalk.gray(` - ${preset.description}`)
            : chalk.cyan(preset.name) + chalk.gray(` - ${preset.description}`);
        return { name, value: presetId };
    }).filter(Boolean);
}

/**
 * Get simplified cover theme choices (top 6)
 */
function getSimplifiedThemeChoices() {
    const topThemes = ['apple', 'modern_gradient', 'academic', 'corporate', 'minimalist', 'classic_book'];

    return topThemes.map(themeId => {
        const theme = COVER_THEMES[themeId];
        if (!theme) return null;
        return {
            name: chalk.cyan(theme.name) + chalk.gray(` - ${theme.description}`),
            value: themeId,
        };
    }).filter(Boolean);
}

// Interactive mode - Refactored for better UX
program
    .command('interactive')
    .alias('i')
    .description('Interactive mode with streamlined workflow')
    .action(async () => {
        console.log(chalk.cyan.bold('\n' + '═'.repeat(60)));
        console.log(chalk.cyan.bold('  📚 Markdown to Document - Interactive Mode'));
        console.log(chalk.cyan.bold('═'.repeat(60) + '\n'));

        // ============ STEP 1: 파일 선택 ============
        console.log(chalk.gray('  Step 1/3: 파일 선택\n'));

        const fileAnswer = await inquirer.prompt([
            {
                type: 'input',
                name: 'inputPath',
                message: chalk.yellow('📄 마크다운 파일 경로:'),
                validate: (input: string) => {
                    const validation = PathValidator.validatePath(input);
                    if (!validation.valid) {
                        // Return first error and suggestion
                        let errorMsg = validation.error || '잘못된 경로입니다.';
                        if (validation.suggestions && validation.suggestions.length > 0) {
                            errorMsg += '\n' + chalk.gray('   💡 ' + validation.suggestions[0]);
                        }
                        return errorMsg;
                    }
                    return true;
                },
                transformer: (input: string) => PathValidator.normalizePath(input),
            },
        ]);

        const pathValidation = PathValidator.validatePath(fileAnswer.inputPath);
        if (!pathValidation.valid || !pathValidation.normalizedPath) {
            PathValidator.displayValidationError(pathValidation);
            process.exit(1);
        }

        const resolvedInputPath = pathValidation.normalizedPath;
        const fileContent = fs.readFileSync(resolvedInputPath, 'utf-8');

        // 문서 분석 (자동)
        const analysisResult = analyzeMarkdownContent(fileContent);
        const metadata = extractMetadata(fileContent);

        // 제목/저자: 반드시 사용자 입력을 받으며, 입력값을 항상 변환에 반영
        const metaAnswers = await inquirer.prompt([
            {
                type: 'input',
                name: 'customTitle',
                message: chalk.yellow('📖 책 제목 (Enter=자동):'),
                default: metadata.title || path.basename(resolvedInputPath, '.md'),
                validate: () => true,
                transformer: (input: string) => input,
            },
            {
                type: 'input',
                name: 'customAuthor',
                message: chalk.yellow('✍️  저자 (Enter=자동):'),
                default: metadata.author || '',
                validate: () => true,
                transformer: (input: string) => input,
            },
        ]);

        // ============ STEP 2: 모드 선택 및 설정 ============
        console.log(chalk.gray('\n' + '─'.repeat(60)));
        console.log(chalk.gray('  Step 2/3: 변환 설정\n'));

        // 분석 결과 요약 (간략하게)
        console.log(chalk.bold('📊 문서 분석:'));
        const statsLine = [
            `${analysisResult.wordCount.toLocaleString()}단어`,
            `이미지 ${analysisResult.imageCount}개`,
            `표 ${analysisResult.tableCount}개`,
        ].join(' | ');
        console.log(chalk.gray(`   ${statsLine}`));

        if (analysisResult.issues.length > 0) {
            console.log(chalk.yellow(`   ⚠️  ${analysisResult.issues.length}개 이슈 감지 → 자동 최적화 적용됨`));
        } else {
            console.log(chalk.green('   ✅ 표준 Markdown - 바로 변환 가능'));
        }

        if (metadata.title) {
            console.log(chalk.gray(`   📖 제목: ${metadata.title}`));
        }
        console.log();

        // 모드 선택
        const modeAnswer = await inquirer.prompt([
            {
                type: 'list',
                name: 'mode',
                message: chalk.yellow('🚀 변환 모드 선택:'),
                choices: [
                    {
                        name: chalk.green('⚡ 빠른 변환') + chalk.gray(' - 스마트 기본값으로 바로 변환 (권장)'),
                        value: 'quick',
                    },
                    {
                        name: chalk.blue('⚙️  상세 설정') + chalk.gray(' - 모든 옵션을 직접 선택'),
                        value: 'custom',
                    },
                ],
                default: 'quick',
            },
        ]);

        const mode: InteractiveMode = modeAnswer.mode;

        // 변환 설정 수집
        let format: OutputFormat = 'both';
        let typographyPreset = analysisResult.recommendedPreset;
        let coverTheme = 'apple';
        const inferredTitle = metadata.title || path.basename(resolvedInputPath, '.md');
        const inferredAuthor = metadata.author || '';
        let customTitle = (metaAnswers.customTitle as string).trim() || inferredTitle;
        let customAuthor = (metaAnswers.customAuthor as string).trim() || inferredAuthor;
        let outputPath = '';

        if (mode === 'quick') {
            // 빠른 모드: 출력 형식만 선택
            const quickAnswers = await inquirer.prompt([
                {
                    type: 'list',
                    name: 'format',
                    message: chalk.yellow('📤 출력 형식:'),
                    choices: [
                        { name: chalk.magenta('📚 EPUB + PDF'), value: 'both' },
                        { name: chalk.green('📖 EPUB만'), value: 'epub' },
                        { name: chalk.blue('📄 PDF만'), value: 'pdf' },
                    ],
                    default: 'both',
                },
            ]);
            format = quickAnswers.format;

            // 스마트 기본값 적용
            console.log(chalk.gray('\n   📋 적용될 설정:'));
            console.log(chalk.gray(`      프리셋: ${TYPOGRAPHY_PRESETS[typographyPreset]?.name || typographyPreset}`));
            console.log(chalk.gray(`      표지: ${COVER_THEMES[coverTheme]?.name || coverTheme}`));
            if (analysisResult.recommendPreprocess) {
                console.log(chalk.gray('      Obsidian 최적화: 자동 적용'));
            }

        } else if (mode === 'custom') {
            // 상세 모드: 모든 옵션 선택
            const customAnswers = await inquirer.prompt([
                {
                    type: 'list',
                    name: 'format',
                    message: chalk.yellow('📤 출력 형식:'),
                    choices: [
                        { name: chalk.magenta('📚 EPUB + PDF'), value: 'both' },
                        { name: chalk.green('📖 EPUB만'), value: 'epub' },
                        { name: chalk.blue('📄 PDF만'), value: 'pdf' },
                    ],
                    default: 'both',
                },
                {
                    type: 'list',
                    name: 'typographyPreset',
                    message: chalk.yellow('🎨 타이포그래피 프리셋:'),
                    choices: [
                        ...getSimplifiedPresetChoices(analysisResult.recommendedPreset),
                        new inquirer.Separator(),
                        { name: chalk.gray('더 많은 프리셋 보기...'), value: '_more' },
                    ],
                    default: analysisResult.recommendedPreset,
                },
                {
                    type: 'list',
                    name: 'coverTheme',
                    message: chalk.yellow('🖼️  표지 테마:'),
                    choices: [
                        ...getSimplifiedThemeChoices(),
                        new inquirer.Separator(),
                        { name: chalk.gray('더 많은 테마 보기...'), value: '_more' },
                    ],
                    default: 'apple',
                },
            ]);

            format = customAnswers.format;
            typographyPreset = customAnswers.typographyPreset;
            coverTheme = customAnswers.coverTheme;

            // "더 보기" 선택 시 전체 목록 표시
            if (typographyPreset === '_more') {
                const morePresetAnswer = await inquirer.prompt([
                    {
                        type: 'list',
                        name: 'typographyPreset',
                        message: chalk.yellow('🎨 타이포그래피 프리셋 (전체):'),
                        choices: getTypographyPresetChoices(analysisResult),
                        default: analysisResult.recommendedPreset,
                    },
                ]);
                typographyPreset = morePresetAnswer.typographyPreset;
            }

            if (coverTheme === '_more') {
                const moreThemeAnswer = await inquirer.prompt([
                    {
                        type: 'list',
                        name: 'coverTheme',
                        message: chalk.yellow('🖼️  표지 테마 (전체):'),
                        choices: getCoverThemeChoices(),
                        default: 'apple',
                    },
                ]);
                coverTheme = moreThemeAnswer.coverTheme;
            }

        }

        // ============ STEP 3: 변환 실행 ============
        console.log(chalk.gray('\n' + '─'.repeat(60)));
        console.log(chalk.gray('  Step 3/3: 변환 실행\n'));

        try {
            // Check dependencies proactively
            const depChecker = new DependencyChecker();
            const isReady = await depChecker.quickCheck(format);

            if (!isReady) {
                await depChecker.displayDependencyReport();
                console.log(chalk.red('\n❌ 필수 의존성을 먼저 설치해 주세요.\n'));
                process.exit(1);
            }

            const spinner = ora(chalk.cyan('⚙️  초기화 중...')).start();

            const converter = new MarkdownToDocument();
            const initResult = await converter.initialize();

            if (!initResult.success) {
                spinner.fail(chalk.red('초기화 실패'));
                console.error(chalk.red(`\n❌ ${initResult.error}`));
                console.log(chalk.yellow('\n' + MarkdownToDocument.getInstallInstructions()));
                process.exit(1);
            }

            // 변환 실행
            spinner.text = chalk.cyan('🔄 문서 변환 중...');

            const conversionOptions = {
                inputPath: resolvedInputPath,
                outputPath: outputPath ? path.resolve(outputPath) : undefined,
                format: format,
                typographyPreset: typographyPreset as any,
                coverTheme: coverTheme,
                validateContent: true,
                autoFix: true,
                tocDepth: 2,
                includeToc: true,
                customTitle: customTitle || undefined,
                customAuthor: customAuthor || undefined,
            };

            const result = await converter.convert(conversionOptions);

            if (result.success) {
                spinner.succeed(chalk.green('변환 완료!'));

                console.log(chalk.green.bold('\n📦 생성된 파일:\n'));
                if (result.epubPath) {
                    console.log(chalk.green(`   📖 ${result.epubPath}`));
                }
                if (result.pdfPath) {
                    console.log(chalk.blue(`   📄 ${result.pdfPath}`));
                }

                console.log(chalk.gray('\n' + '═'.repeat(60)));
                console.log(chalk.green.bold('🎉 변환이 완료되었습니다!\n'));
            } else {
                spinner.fail(chalk.red('변환 실패'));
                console.log(chalk.red('\n❌ 오류:'));
                result.errors.forEach(error => {
                    console.log(chalk.red(`   • ${error}`));
                });
                process.exit(1);
            }
        } catch (error) {
            console.error(chalk.red('\n❌ Error:'), error instanceof Error ? error.message : String(error));
            process.exit(1);
        }
    });

// List presets command
program
    .command('list-presets')
    .description('List available typography presets')
    .action(() => {
        console.log(chalk.cyan.bold('\n📝 Available Typography Presets:\n'));

        Object.values(TYPOGRAPHY_PRESETS).forEach(preset => {
            console.log(chalk.bold(`  ${preset.id}:`), chalk.cyan(preset.name));
            console.log(chalk.gray(`    ${preset.description}`));
            console.log(chalk.gray(`    Font size: ${preset.fontSize}pt | Line height: ${preset.lineHeight}`));
            console.log();
        });
    });

// List themes command
program
    .command('list-themes')
    .description('List available cover themes')
    .action(() => {
        console.log(chalk.cyan.bold('\n🎨 Available Cover Themes:\n'));

        const categories = {
            basic: 'Basic Themes',
            extended: 'Extended Themes',
        };

        Object.entries(categories).forEach(([category, title]) => {
            console.log(chalk.bold(`\n  ${title}:`));
            const themes = Object.values(COVER_THEMES).filter(t => t.category === category);
            themes.forEach(theme => {
                console.log(chalk.gray(`    • ${theme.id}: ${theme.description}`));
            });
        });
        console.log();
    });

// Check dependencies command
program
    .command('check')
    .description('Check if required dependencies are installed')
    .action(async () => {
        const depChecker = new DependencyChecker();
        const isReady = await depChecker.displayDependencyReport();

        if (isReady) {
            console.log(chalk.green('🚀 준비 완료! 지금 바로 문서 변환을 시작할 수 있습니다.\n'));
            console.log(chalk.cyan('사용 예시:'));
            console.log(chalk.gray('  m2d document.md'));
            console.log(chalk.gray('  m2d interactive\n'));
        } else {
            process.exit(1);
        }
    });

// Parse arguments
program.parse(process.argv);

// Show help if no arguments provided
if (!process.argv.slice(2).length) {
    program.outputHelp();
}
