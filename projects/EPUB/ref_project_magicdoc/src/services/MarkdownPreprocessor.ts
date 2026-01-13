/**
 * Markdown Preprocessor - Markdown Syntax Conversion
 */

import * as path from 'path';
import type { DocumentMetadata, PreprocessResult, ResolvedImage } from '../types/index.js';
import {
    extractFrontmatter,
    countWords,
    countChapters,
    countImages,
    extractTitleFromContent,
    splitTitle,
    convertObsidianImageSyntax,
    convertObsidianLinks,
    convertHighlights,
    removeMediaEmbeds,
    escapePipeCharacters,
    extractStandardImagePaths,
} from '../utils/markdownUtils.js';
import { findImageInVault, ensureDirectory } from '../utils/fileUtils.js';
import { ATTACHMENT_FOLDERS } from '../utils/constants.js';
import { Logger } from '../utils/common.js';

export class MarkdownPreprocessor {
    private basePath: string;

    constructor(basePath: string = '.') {
        this.basePath = path.resolve(basePath);
    }

    /**
     * Main preprocessing pipeline
     */
    async preprocess(
        content: string,
        sourcePath: string,
        outputFormat: 'epub' | 'pdf' = 'epub'
    ): Promise<PreprocessResult> {
        const warnings: string[] = [];
        const resolvedImages: ResolvedImage[] = [];

        Logger.info('Starting markdown preprocessing...');

        // Step 1: Extract YAML frontmatter
        const { metadata: frontmatterMeta, content: contentWithoutYaml } =
            extractFrontmatter(content);

        // Step 2: Remove audio/video embeds
        let processedContent = removeMediaEmbeds(contentWithoutYaml);

        // Step 3: Convert Obsidian image syntax
        const { content: contentWithImages, images: obsidianImages } =
            convertObsidianImageSyntax(processedContent);
        processedContent = contentWithImages;

        // Step 4: Resolve image paths
        const sourceDir = path.dirname(sourcePath);
        const searchDirs = ATTACHMENT_FOLDERS.map(folder => path.join(this.basePath, folder));

        // Resolve Obsidian images
        const obsidianImagePromises = obsidianImages.map(imageName =>
            this.resolveImage(imageName, sourceDir, searchDirs)
        );
        const obsidianResolvedImages = await Promise.all(obsidianImagePromises);

        for (const resolvedImage of obsidianResolvedImages) {
            resolvedImages.push(resolvedImage);
            if (!resolvedImage.found) {
                warnings.push(`Image not found: ${resolvedImage.originalSyntax}`);
            }
        }

        // Step 5: Process standard markdown images
        const standardImagePaths = extractStandardImagePaths(processedContent);
        const standardImagePromises: Promise<ResolvedImage>[] = [];

        for (const imagePath of standardImagePaths) {
            const existing = resolvedImages.find((r) => r.originalSyntax === imagePath);
            if (!existing) {
                standardImagePromises.push(this.resolveImage(imagePath, sourceDir, searchDirs));
            }
        }

        if (standardImagePromises.length > 0) {
            const standardResolvedImages = await Promise.all(standardImagePromises);
            for (const resolvedImage of standardResolvedImages) {
                resolvedImages.push(resolvedImage);
                if (!resolvedImage.found) {
                    warnings.push(`Image not found: ${resolvedImage.originalSyntax}`);
                }
            }
        }

        // Step 6: Replace image paths with absolute paths
        processedContent = this.replaceImagePaths(processedContent, resolvedImages);

        // Step 7: Convert Obsidian internal links
        processedContent = convertObsidianLinks(processedContent);

        // Step 8: Convert highlights
        processedContent = convertHighlights(processedContent);

        // Step 9: Replace '---' horizontal rules with '***' to avoid YAML confusion
        // Pandoc interprets '---' as YAML frontmatter delimiter
        processedContent = processedContent.replace(/^---$/gm, '***');

        // Step 10: Escape pipe characters for EPUB
        if (outputFormat === 'epub') {
            processedContent = escapePipeCharacters(processedContent);
        }

        // Step 10: Build metadata
        const extractedTitle =
            frontmatterMeta.title || extractTitleFromContent(contentWithoutYaml);
        const { title, subtitle } = splitTitle(extractedTitle || path.basename(sourcePath, '.md'));

        const metadata: DocumentMetadata = {
            title,
            subtitle: frontmatterMeta.subtitle || subtitle,
            author: frontmatterMeta.author,
            language: frontmatterMeta.language || 'ko',
            date: frontmatterMeta.date || new Date().toISOString().slice(0, 10),
            description: frontmatterMeta.description,
            isbn: frontmatterMeta.isbn,
            publisher: frontmatterMeta.publisher,
            chapterCount: countChapters(contentWithoutYaml),
            wordCount: countWords(contentWithoutYaml),
            imageCount: countImages(content),
        };

        Logger.info('Preprocessing completed', {
            title: metadata.title,
            chapters: metadata.chapterCount,
            words: metadata.wordCount,
            images: metadata.imageCount,
        });

        return {
            content: processedContent,
            metadata,
            resolvedImages,
            warnings,
        };
    }

    /**
     * Resolve image path to absolute path
     */
    private async resolveImage(
        imageName: string,
        basePath: string,
        searchDirs: string[]
    ): Promise<ResolvedImage> {
        const result: ResolvedImage = {
            originalSyntax: imageName,
            standardSyntax: '',
            absolutePath: '',
            found: false,
        };

        try {
            const resolvedPath = await findImageInVault(imageName, basePath, searchDirs);

            if (resolvedPath) {
                result.found = true;
                result.absolutePath = resolvedPath;
                result.standardSyntax = resolvedPath;
            }
        } catch (error) {
            Logger.warn(`Failed to resolve image: ${imageName}`, error);
        }

        return result;
    }

    /**
     * Replace image paths with absolute paths
     */
    private replaceImagePaths(content: string, resolvedImages: ResolvedImage[]): string {
        let newContent = content;

        for (const image of resolvedImages) {
            if (image.found) {
                // Replace both Obsidian and standard markdown image syntax
                newContent = newContent.replace(
                    new RegExp(`!\\[\\[${this.escapeRegex(image.originalSyntax)}\\]\\]`, 'g'),
                    `![${image.alt || ''}](${image.absolutePath})`
                );

                newContent = newContent.replace(
                    new RegExp(`!\\[[^\\]]*\\]\\(${this.escapeRegex(image.originalSyntax)}\\)`, 'g'),
                    `![${image.alt || ''}](${image.absolutePath})`
                );
            }
        }

        return newContent;
    }

    /**
     * Escape regex special characters
     */
    private escapeRegex(string: string): string {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Escape YAML string value using single quotes - simpler and more robust
     * Single quotes in YAML only need single quotes doubled, no other escaping needed
     */
    private escapeYamlString(value: string): string {
        // In single-quoted YAML strings, only single quotes need escaping (by doubling them)
        return value.replace(/'/g, "''");
    }

    /**
     * Generate clean markdown with YAML frontmatter
     */
    generateCleanMarkdown(
        preprocessResult: PreprocessResult,
        outputFormat: 'epub' | 'pdf' = 'epub',
        overrides?: { title?: string; author?: string }
    ): string {
        const { content, metadata } = preprocessResult;

        // Build YAML frontmatter using single quotes (safer for special characters)
        const yamlLines: string[] = ['---'];

        const finalTitle = overrides?.title || metadata.title;
        const finalAuthor = overrides?.author || metadata.author;

        if (finalTitle) yamlLines.push(`title: '${this.escapeYamlString(finalTitle)}'`);
        if (metadata.subtitle) yamlLines.push(`subtitle: '${this.escapeYamlString(metadata.subtitle)}'`);
        if (finalAuthor) yamlLines.push(`author: '${this.escapeYamlString(finalAuthor)}'`);
        if (metadata.language) yamlLines.push(`language: ${metadata.language}`);
        if (metadata.date) yamlLines.push(`date: ${metadata.date}`);
        if (metadata.description) yamlLines.push(`description: '${this.escapeYamlString(metadata.description)}'`);
        if (metadata.isbn) yamlLines.push(`isbn: ${metadata.isbn}`);
        if (metadata.publisher) yamlLines.push(`publisher: '${this.escapeYamlString(metadata.publisher)}'`);

        yamlLines.push('---');
        yamlLines.push('');

        return yamlLines.join('\n') + content;
    }
}
