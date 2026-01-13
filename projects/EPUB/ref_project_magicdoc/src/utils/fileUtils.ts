/**
 * File Utilities
 */

import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

export function sanitizeFilename(filename: string): string {
    return filename
        .replace(/[<>:"/\\|?*]/g, '_')
        .replace(/\s+/g, '_')
        .replace(/^\.+/, '')
        .slice(0, 200);
}

export function ensureDirectory(dirPath: string): void {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

export async function findImageInVault(
    imageName: string,
    basePath: string,
    searchDirs: string[] = []
): Promise<string | null> {
    const possiblePaths = [
        path.join(basePath, imageName),
        path.join(basePath, 'images', imageName),
        path.join(basePath, 'attachments', imageName),
        ...searchDirs.map(dir => path.join(dir, imageName))
    ];

    for (const possiblePath of possiblePaths) {
        if (fs.existsSync(possiblePath)) {
            return path.resolve(possiblePath);
        }
    }

    // Try glob search
    const pattern = `**/${path.basename(imageName)}`;
    const matches = await glob(pattern, { cwd: basePath, absolute: true });

    if (matches.length > 0) {
        return matches[0];
    }

    return null;
}

export function getFileExtension(filePath: string): string {
    return path.extname(filePath).toLowerCase();
}

export function getFileStats(filePath: string): { size: number; exists: boolean } {
    try {
        const stats = fs.statSync(filePath);
        return { size: stats.size, exists: true };
    } catch {
        return { size: 0, exists: false };
    }
}

export function readFileSync(filePath: string): string {
    return fs.readFileSync(filePath, 'utf-8');
}

export function writeFileSync(filePath: string, content: string): void {
    ensureDirectory(path.dirname(filePath));
    fs.writeFileSync(filePath, content, 'utf-8');
}

export async function readFileAsync(filePath: string): Promise<string> {
    return fs.promises.readFile(filePath, 'utf-8');
}

export async function writeFileAsync(filePath: string, content: string): Promise<void> {
    ensureDirectory(path.dirname(filePath));
    await fs.promises.writeFile(filePath, content, 'utf-8');
}

export function getTempDir(): string {
    const tempDir = path.join(process.env.TMPDIR || '/tmp', 'markdown-to-document');
    ensureDirectory(tempDir);
    return tempDir;
}
