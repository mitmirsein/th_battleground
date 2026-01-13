/**
 * Theme and Preset Utility Functions
 * Centralized helpers for theme/preset filtering, validation, and listing
 */

import { COVER_THEMES, TYPOGRAPHY_PRESETS } from './constants.js';
import type { CoverTheme, TypographyPreset, TypographyPresetId } from '../types/index.js';
import { CoverThemeCategory } from '../types/index.js';

// ============ Cover Theme Utilities ============

/**
 * Get all available cover theme IDs
 */
export function getCoverThemeIds(): string[] {
    return Object.keys(COVER_THEMES);
}

/**
 * Get cover theme by ID
 */
export function getCoverTheme(id: string): CoverTheme | undefined {
    return COVER_THEMES[id];
}

/**
 * Check if a cover theme ID is valid
 */
export function isValidCoverTheme(id: string): boolean {
    return id in COVER_THEMES;
}

/**
 * Get cover themes filtered by category
 */
export function getCoverThemesByCategory(category: string): CoverTheme[] {
    return Object.values(COVER_THEMES).filter(theme => theme.category === category);
}

/**
 * Get cover themes grouped by category
 */
export function getCoverThemesGrouped(): Record<string, CoverTheme[]> {
    const groups: Record<string, CoverTheme[]> = {};

    for (const theme of Object.values(COVER_THEMES)) {
        const cat = theme.category;
        if (!groups[cat]) {
            groups[cat] = [];
        }
        groups[cat].push(theme);
    }

    return groups;
}

/**
 * Get cover theme categories with theme counts
 */
export function getCoverThemeCategorySummary(): { category: string; count: number; themes: string[] }[] {
    const grouped = getCoverThemesGrouped();
    return Object.entries(grouped).map(([category, themes]) => ({
        category,
        count: themes.length,
        themes: themes.map(t => t.id)
    }));
}

// ============ Typography Preset Utilities ============

/**
 * Get all available typography preset IDs
 */
export function getTypographyPresetIds(): TypographyPresetId[] {
    return Object.keys(TYPOGRAPHY_PRESETS) as TypographyPresetId[];
}

/**
 * Get typography preset by ID
 */
export function getTypographyPreset(id: string): TypographyPreset | undefined {
    return TYPOGRAPHY_PRESETS[id];
}

/**
 * Check if a typography preset ID is valid
 */
export function isValidTypographyPreset(id: string): boolean {
    return id in TYPOGRAPHY_PRESETS;
}

/**
 * Get typography presets by category (basic, content, document)
 */
export function getTypographyPresetsByCategory(category: 'basic' | 'content' | 'document'): TypographyPreset[] {
    const categoryMap: Record<string, TypographyPresetId[]> = {
        basic: ['novel', 'presentation', 'review', 'ebook'],
        content: ['text_heavy', 'table_heavy', 'image_heavy', 'balanced'],
        document: ['report', 'manual', 'magazine']
    };

    const ids = categoryMap[category] || [];
    return ids.map(id => TYPOGRAPHY_PRESETS[id]).filter(Boolean);
}

/**
 * Get typography presets grouped by category
 */
export function getTypographyPresetsGrouped(): Record<string, TypographyPreset[]> {
    return {
        basic: getTypographyPresetsByCategory('basic'),
        content: getTypographyPresetsByCategory('content'),
        document: getTypographyPresetsByCategory('document')
    };
}

// ============ CLI Help Utilities ============

/**
 * Generate help text for cover themes
 */
export function generateCoverThemeHelpText(): string {
    const grouped = getCoverThemesGrouped();
    const lines: string[] = [];

    for (const [category, themes] of Object.entries(grouped)) {
        const themeList = themes.map(t => t.id).join(', ');
        lines.push(`  ${category}: ${themeList}`);
    }

    return lines.join('\n');
}

/**
 * Generate help text for typography presets
 */
export function generateTypographyPresetHelpText(): string {
    const grouped = getTypographyPresetsGrouped();
    const lines: string[] = [];

    for (const [category, presets] of Object.entries(grouped)) {
        const presetList = presets.map(p => p.id).join(', ');
        lines.push(`  ${category}: ${presetList}`);
    }

    return lines.join('\n');
}

// ============ Validation Utilities ============

/**
 * Validate and return cover theme, with fallback to default
 */
export function validateCoverTheme(id: string | undefined, defaultId: string = 'apple'): CoverTheme {
    if (id && isValidCoverTheme(id)) {
        return COVER_THEMES[id];
    }
    return COVER_THEMES[defaultId];
}

/**
 * Validate and return typography preset ID, with fallback to default
 */
export function validateTypographyPreset(id: string | undefined, defaultId: TypographyPresetId = 'ebook'): TypographyPresetId {
    if (id && isValidTypographyPreset(id)) {
        return id as TypographyPresetId;
    }
    return defaultId;
}
