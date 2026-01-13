/**
 * Type Definitions for Markdown to Document CLI
 */

// ============ Enums for Type Safety ============

export enum CoverThemeCategory {
    Basic = 'basic',
    Professional = 'professional',
    Creative = 'creative',
    Seasonal = 'seasonal',
    Extended = 'extended'
}

export enum CoverThemeStyle {
    Minimal = 'minimal',
    Gradient = 'gradient',
    Dark = 'dark',
    Modern = 'modern'
}

export enum TypographyPresetCategory {
    Basic = 'basic',
    ContentFocused = 'content',
    DocumentType = 'document'
}

export enum OutputFormat {
    Epub = 'epub',
    Pdf = 'pdf',
    Both = 'both'
}

// ============ Interfaces ============

export interface ConversionOptions {
    inputPath: string;
    outputPath?: string;
    format: 'epub' | 'pdf' | 'both';
    coverTheme?: string;
    typographyPreset?: TypographyPresetId;
    enableFontSubsetting?: boolean;
    tocDepth?: number;
    includeToc?: boolean;
    paperSize?: 'a4' | 'letter';
    pdfEngine?: 'pdflatex' | 'xelatex' | 'weasyprint' | 'auto';
    validateContent?: boolean;
    autoFix?: boolean;
    generateCover?: boolean;
    includeCopyright?: boolean;
    cssPath?: string;
    customTitle?: string;
    customAuthor?: string;
}

export interface ConversionResult {
    success: boolean;
    epubPath?: string;
    pdfPath?: string;
    errors: string[];
    warnings: string[];
    validationReport?: ValidationReport;
}

export interface DocumentMetadata {
    title: string;
    subtitle?: string;
    author?: string;
    language?: string;
    date?: string;
    description?: string;
    isbn?: string;
    publisher?: string;
    chapterCount?: number;
    wordCount?: number;
    imageCount?: number;
}

export interface ValidationReport {
    totalIssues: number;
    fixedIssues: number;
    warnings: number;
    errors: number;
    details: ValidationIssue[];
}

export interface ValidationIssue {
    type: 'error' | 'warning' | 'info';
    category: 'frontmatter' | 'heading' | 'link' | 'image' | 'table' | 'syntax' | 'accessibility';
    message: string;
    line?: number;
    fixed?: boolean;
    suggestion?: string;
}

export interface ResolvedImage {
    originalSyntax: string;
    standardSyntax: string;
    absolutePath: string;
    found: boolean;
    alt?: string;
    width?: number;
    height?: number;
}

export type TypographyPresetId =
    | 'novel' | 'presentation' | 'review' | 'ebook'  // Basic
    | 'text_heavy' | 'table_heavy' | 'image_heavy' | 'balanced'  // Content-focused
    | 'report' | 'manual' | 'magazine';  // Document type

export interface TypographyPreset {
    id: TypographyPresetId;
    name: string;
    description: string;
    fontSize: number;
    lineHeight: number;
    fontFamily: string;
    textAlign: 'left' | 'justify' | 'center';
    paragraphSpacing: number;
    features: string[];
}

export interface PandocInfo {
    available: boolean;
    version?: string;
    majorVersion?: number;
    path?: string;
    error?: string;
}

export interface PreprocessResult {
    content: string;
    metadata: DocumentMetadata;
    resolvedImages: ResolvedImage[];
    warnings: string[];
}

export interface CoverThemeColors {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
}

export interface CoverTheme {
    id: string;
    name: string;
    category: CoverThemeCategory | 'basic' | 'professional' | 'creative' | 'seasonal' | 'extended';
    description: string;
    colors: CoverThemeColors;
    style: CoverThemeStyle | 'minimal' | 'gradient' | 'dark' | 'modern';
}

// ============ Utility Types ============

export type CoverThemeId = string;
export type PresetCategory = 'basic' | 'content' | 'document';
