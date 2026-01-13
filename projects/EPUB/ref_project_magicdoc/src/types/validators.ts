/**
 * Validator Type Definitions
 */

export interface ValidationResult {
    isValid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    fixed?: boolean;
}

export interface ValidationError {
    type: 'frontmatter' | 'heading' | 'link' | 'image' | 'table' | 'syntax' | 'accessibility';
    message: string;
    line?: number;
    column?: number;
    context?: string;
}

export interface ValidationWarning {
    type: 'frontmatter' | 'heading' | 'link' | 'image' | 'table' | 'syntax' | 'accessibility';
    message: string;
    line?: number;
    suggestion?: string;
}

export interface ValidatorConfig {
    autoFix: boolean;
    strictMode: boolean;
    allowedImageFormats: string[];
    maxImageSize: number;
    requireAltText: boolean;
    checkExternalLinks: boolean;
}
