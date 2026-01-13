/**
 * Common Utilities
 */

export function escapeRegex(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

export function truncateString(str: string, maxLength: number): string {
    if (str.length <= maxLength) return str;
    return `${str.slice(0, maxLength - 3)}...`;
}

export function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export class Logger {
    private static enabled = true;

    static setEnabled(enabled: boolean): void {
        this.enabled = enabled;
    }

    static info(message: string, ...args: any[]): void {
        if (this.enabled) {
            console.log(`[INFO] ${message}`, ...args);
        }
    }

    static warn(message: string, ...args: any[]): void {
        if (this.enabled) {
            console.warn(`[WARN] ${message}`, ...args);
        }
    }

    static error(message: string, ...args: any[]): void {
        if (this.enabled) {
            console.error(`[ERROR] ${message}`, ...args);
        }
    }

    static debug(message: string, ...args: any[]): void {
        if (this.enabled && process.env.DEBUG === 'true') {
            console.debug(`[DEBUG] ${message}`, ...args);
        }
    }
}

export function getTempDir(): string {
    const tempDir = (process.env.TMPDIR || '/tmp') + '/markdown-to-document';
    if (!import('fs').then(fs => fs.existsSync(tempDir))) {
        import('fs').then(fs => fs.mkdirSync(tempDir, { recursive: true }));
    }
    return tempDir;
}
