/**
 * Font Subsetter Service - 폰트 서브세팅으로 파일 크기 최적화
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const fontkit = require('fontkit');

export interface SubsetOptions {
    inputFontPath: string;
    outputFontPath: string;
    characters: Set<string>;
    format?: 'woff' | 'woff2' | 'ttf' | 'otf';
    preserveKerning?: boolean;
    preserveHinting?: boolean;
}

export interface FontAnalysis {
    totalGlyphs: number;
    usedGlyphs: number;
    originalSize: number;
    subsetSize: number;
    reductionPercent: number;
    missingCharacters: string[];
    coverage: number;
}

export interface FontMetadata {
    familyName: string;
    subfamilyName: string;
    fullName: string;
    postscriptName: string;
    version: string;
    copyright?: string;
    format: string;
    numGlyphs: number;
    unitsPerEm: number;
}

export interface SubsetResult {
    success: boolean;
    outputPath?: string;
    analysis?: FontAnalysis;
    error?: string;
}

export class FontSubsetter {
    private charCache: Map<string, Set<string>>;
    private fontCache: Map<string, any>;
    private cacheDir: string;
    private readonly MAX_CACHE_SIZE = 100;

    private baseCharacters = new Set([
        ...' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~',
        ...'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ',
        ...'、。「」『』〈〉《》【】〔〕\'\'""\…—·',
        ...'←↑→↓↔↕▲▼■□●○★☆♥♡',
    ]);

    constructor(cacheDir?: string) {
        this.charCache = new Map();
        this.fontCache = new Map();

        const baseDir = process.cwd();
        const defaultCacheDir = path.join(baseDir, '.font-cache');

        if (cacheDir) {
            this.cacheDir = path.resolve(cacheDir);
            if (!this.cacheDir.startsWith(baseDir)) {
                console.warn('Cache directory outside project directory, using default');
                this.cacheDir = defaultCacheDir;
            }
        } else {
            this.cacheDir = defaultCacheDir;
        }

        if (!fs.existsSync(this.cacheDir)) {
            fs.mkdirSync(this.cacheDir, { recursive: true });
        }
    }

    private evictCache(): void {
        if (this.fontCache.size > this.MAX_CACHE_SIZE) {
            const firstKey = this.fontCache.keys().next().value;
            if (firstKey !== undefined) {
                this.fontCache.delete(firstKey);
            }
        }
    }

    private getCacheKey(fontPath: string, chars: Set<string>): string {
        const charString = Array.from(chars).sort().join('');
        return crypto.createHash('md5').update(fontPath + charString).digest('hex');
    }

    private extractCharacters(content: string): Set<string> {
        const chars = new Set(this.baseCharacters);
        for (const char of content) {
            chars.add(char);
        }
        return chars;
    }

    async analyzeFont(fontPath: string, content?: string): Promise<FontAnalysis> {
        try {
            const font = fontkit.openSync(fontPath) as any;
            const characters = content ? this.extractCharacters(content) : this.baseCharacters;

            let usedGlyphs = 0;
            const missingCharacters: string[] = [];

            for (const char of characters) {
                const codePoint = char.codePointAt(0);
                if (codePoint !== undefined) {
                    try {
                        font.glyphForCodePoint(codePoint);
                        usedGlyphs++;
                    } catch {
                        missingCharacters.push(char);
                    }
                }
            }

            const originalSize = fs.statSync(fontPath).size;
            const coverage = (usedGlyphs / characters.size) * 100;

            return {
                totalGlyphs: font.numGlyphs || 0,
                usedGlyphs,
                originalSize,
                subsetSize: 0,
                reductionPercent: 0,
                missingCharacters,
                coverage,
            };
        } catch (error) {
            throw new Error(`Font analysis failed: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    async subsetFont(options: SubsetOptions): Promise<SubsetResult> {
        try {
            const { inputFontPath, outputFontPath, characters, format = 'woff2' } = options;

            if (!fs.existsSync(inputFontPath)) {
                return { success: false, error: `Input font not found: ${inputFontPath}` };
            }

            const cacheKey = this.getCacheKey(inputFontPath, characters);
            const cachedPath = path.join(this.cacheDir, `${cacheKey}.${format}`);

            if (fs.existsSync(cachedPath)) {
                const stats = fs.statSync(cachedPath);
                return {
                    success: true,
                    outputPath: cachedPath,
                    analysis: {
                        totalGlyphs: 0,
                        usedGlyphs: characters.size,
                        originalSize: fs.statSync(inputFontPath).size,
                        subsetSize: stats.size,
                        reductionPercent: 0,
                        missingCharacters: [],
                        coverage: 100,
                    },
                };
            }

            const font = fontkit.openSync(inputFontPath) as any;
            const subsetFont = font.createSubset();

            for (const char of characters) {
                const codePoint = char.codePointAt(0);
                if (codePoint !== undefined) {
                    try {
                        const glyph = font.glyphForCodePoint(codePoint);
                        subsetFont.includeGlyph(glyph);
                    } catch {
                        // Character not in font, skip
                    }
                }
            }

            const buffer = subsetFont.encode(format);
            fs.writeFileSync(outputFontPath, buffer);

            const originalSize = fs.statSync(inputFontPath).size;
            const subsetSize = buffer.length;
            const reductionPercent = ((originalSize - subsetSize) / originalSize) * 100;

            return {
                success: true,
                outputPath: outputFontPath,
                analysis: {
                    totalGlyphs: font.numGlyphs || 0,
                    usedGlyphs: characters.size,
                    originalSize,
                    subsetSize,
                    reductionPercent,
                    missingCharacters: [],
                    coverage: 100,
                },
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : String(error),
            };
        }
    }

    async subsetFontsInDirectory(
        inputDir: string,
        outputDir: string,
        content: string
    ): Promise<SubsetResult[]> {
        const results: SubsetResult[] = [];

        if (!fs.existsSync(inputDir)) {
            results.push({
                success: false,
                error: `Input directory not found: ${inputDir}`,
            });
            return results;
        }

        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const fontFiles = fs.readdirSync(inputDir).filter((file) =>
            /\.(ttf|otf|woff|woff2)$/i.test(file)
        );

        const characters = this.extractCharacters(content);

        for (const fontFile of fontFiles) {
            const inputPath = path.join(inputDir, fontFile);
            const outputPath = path.join(outputDir, fontFile.replace(/\.(ttf|otf|woff|woff2)$/i, '.woff2'));

            const result = await this.subsetFont({
                inputFontPath: inputPath,
                outputFontPath: outputPath,
                characters,
                format: 'woff2',
            });

            results.push(result);
        }

        return results;
    }

    clearCache(): void {
        if (fs.existsSync(this.cacheDir)) {
            const files = fs.readdirSync(this.cacheDir);
            for (const file of files) {
                fs.unlinkSync(path.join(this.cacheDir, file));
            }
        }
        this.charCache.clear();
        this.fontCache.clear();
    }
}
