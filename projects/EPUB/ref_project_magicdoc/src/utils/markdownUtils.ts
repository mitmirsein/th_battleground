/**
 * Markdown Utilities
 */

import * as path from 'path';
import type { DocumentMetadata } from '../types/index.js';

export function extractFrontmatter(content: string): {
    metadata: Partial<DocumentMetadata>;
    content: string;
    hasYamlFrontmatter: boolean;
} {
    const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n/;
    const match = content.match(frontmatterRegex);

    if (!match) {
        return { metadata: {}, content, hasYamlFrontmatter: false };
    }

    const yamlContent = match[1];
    const remainingContent = content.slice(match[0].length);

    const metadata: Partial<DocumentMetadata> = {};

    // Parse simple YAML key-value pairs
    const lines = yamlContent.split('\n');
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;

        const colonIndex = trimmed.indexOf(':');
        if (colonIndex > 0) {
            const key = trimmed.slice(0, colonIndex).trim();
            let value = trimmed.slice(colonIndex + 1).trim();

            // Remove quotes if present
            if ((value.startsWith('"') && value.endsWith('"')) ||
                (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1);
            }

            switch (key) {
                case 'title':
                    metadata.title = value;
                    break;
                case 'subtitle':
                    metadata.subtitle = value;
                    break;
                case 'author':
                    metadata.author = value;
                    break;
                case 'language':
                    metadata.language = value;
                    break;
                case 'date':
                    metadata.date = value;
                    break;
                case 'description':
                    metadata.description = value;
                    break;
                case 'isbn':
                    metadata.isbn = value;
                    break;
                case 'publisher':
                    metadata.publisher = value;
                    break;
            }
        }
    }

    return { metadata, content: remainingContent, hasYamlFrontmatter: true };
}

export function extractTitleFromContent(content: string): string {
    const h1Regex = /^#\s+(.+)$/m;
    const match = content.match(h1Regex);
    return match ? match[1].trim() : '';
}

export function splitTitle(title: string): { title: string; subtitle?: string } {
    const pipeIndex = title.indexOf('|');
    const colonIndex = title.indexOf(':');

    let splitIndex = -1;
    if (pipeIndex > 0) splitIndex = pipeIndex;
    if (colonIndex > 0 && (splitIndex === -1 || colonIndex < splitIndex)) {
        splitIndex = colonIndex;
    }

    if (splitIndex > 0) {
        return {
            title: title.slice(0, splitIndex).trim(),
            subtitle: title.slice(splitIndex + 1).trim()
        };
    }

    return { title: title.trim() };
}

export function convertObsidianLinks(content: string): string {
    // Convert [[link]] to [link](link.md)
    return content.replace(/\[\[([^\]]+)\]\]/g, (match, link) => {
        const parts = link.split('|');
        const text = parts[1] || parts[0];
        const target = parts[0];

        // Handle external links [[link|text]] -> [text](link)
        if (target.startsWith('http')) {
            return `[${text}](${target})`;
        }

        // Handle internal links [[link]] -> [link](link.md)
        return `[${text}](${target}.md)`;
    });
}

export function convertObsidianImageSyntax(content: string): {
    content: string;
    images: string[];
} {
    const images: string[] = [];

    const newContent = content.replace(/!\[\[([^\]]+)\]\]/g, (match, imageSpec) => {
        const parts = imageSpec.split('|');
        const imagePath = parts[0];
        const altText = parts[1] || '';

        images.push(imagePath);
        return `![${altText}](${imagePath})`;
    });

    return { content: newContent, images };
}

export function convertHighlights(content: string): string {
    // Convert ==highlight== to <mark>highlight</mark>
    return content.replace(/==([^=]+)==/g, '<mark>$1</mark>');
}

export function removeMediaEmbeds(content: string): string {
    // Remove audio/video embeds
    return content
        .replace(/\!\[\[.*?\.(mp3|wav|ogg|m4a|mp4|webm|mov|avi)\]\]/gi, '')
        .replace(/\{\{audio:.*?\}\}/gi, '')
        .replace(/\{\{video:.*?\}\}/gi, '');
}

export function countWords(content: string): number {
    const text = content
        .replace(/```[\s\S]*?```/g, '') // Remove code blocks
        .replace(/`[^`]+`/g, '') // Remove inline code
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove markdown links
        .replace(/[^\w\s\uAC00-\uD7AF\u3131-\u3163]/g, ' ') // Keep Korean, letters, numbers
        .replace(/\s+/g, ' ')
        .trim();

    if (!text) return 0;

    // Count words (space-separated for English, character-based for Korean)
    const koreanChars = (text.match(/[\uAC00-\uD7AF]/g) || []).length;
    const englishWords = text.replace(/[\uAC00-\uD7AF]/g, '').trim().split(/\s+/).filter(w => w).length;

    return koreanChars + englishWords;
}

export function countChapters(content: string): number {
    const h1Matches = content.match(/^#\s+.+$/gm);
    return h1Matches ? h1Matches.length : 0;
}

export function countImages(content: string): number {
    const imageMatches = content.match(/!\[.*?\]\(.*?\)/g);
    return imageMatches ? imageMatches.length : 0;
}

export function escapePipeCharacters(content: string): string {
    // Escape pipe characters that are not part of tables
    const lines = content.split('\n');
    const escapedLines: string[] = [];
    let inTable = false;

    for (const line of lines) {
        const trimmed = line.trim();

        // Detect table start/end
        if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
            inTable = true;
        } else if (inTable && !trimmed.startsWith('|')) {
            inTable = false;
        }

        if (inTable) {
            escapedLines.push(line);
        } else {
            escapedLines.push(line.replace(/\|/g, '\\|'));
        }
    }

    return escapedLines.join('\n');
}

export function extractStandardImagePaths(content: string): string[] {
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
    const paths: string[] = [];
    let match;

    while ((match = imageRegex.exec(content)) !== null) {
        paths.push(match[2]);
    }

    return paths;
}
