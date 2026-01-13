/**
 * Dependency Checker - Proactive installation guidance
 * 
 * Checks for required dependencies and provides user-friendly installation instructions
 */

import { execFile } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';

const execFileAsync = promisify(execFile);

export interface DependencyStatus {
    name: string;
    required: boolean;
    installed: boolean;
    version?: string;
    installInstructions: InstallInstructions;
}

export interface InstallInstructions {
    description: string;
    macOS: string[];
    linux: string[];
    windows: string[];
    notes?: string;
}

export class DependencyChecker {
    /**
     * Check if a command is available
     */
    private async isCommandAvailable(command: string, args: string[] = ['--version']): Promise<{ available: boolean; version?: string }> {
        try {
            const { stdout } = await execFileAsync(command, args, { timeout: 3000 });
            const versionMatch = stdout.match(/(\d+\.\d+(?:\.\d+)?)/);
            return {
                available: true,
                version: versionMatch ? versionMatch[1] : 'installed'
            };
        } catch {
            return { available: false };
        }
    }

    /**
     * Check Node.js
     */
    private async checkNode(): Promise<DependencyStatus> {
        const result = await this.isCommandAvailable('node');
        return {
            name: 'Node.js',
            required: true,
            installed: result.available,
            version: result.version,
            installInstructions: {
                description: 'JavaScript 런타임 - CLI가 실행되는 기반',
                macOS: ['brew install node', '또는 https://nodejs.org 에서 다운로드'],
                linux: ['sudo apt-get install nodejs npm', '또는 https://nodejs.org 에서 다운로드'],
                windows: ['winget install OpenJS.NodeJS', '또는 https://nodejs.org 에서 다운로드'],
                notes: 'Node.js 18 이상 권장'
            }
        };
    }

    /**
     * Check Pandoc
     */
    private async checkPandoc(): Promise<DependencyStatus> {
        const result = await this.isCommandAvailable('pandoc');
        return {
            name: 'Pandoc',
            required: true,
            installed: result.available,
            version: result.version,
            installInstructions: {
                description: '문서 변환 엔진 - EPUB/PDF 생성의 핵심',
                macOS: ['brew install pandoc'],
                linux: ['sudo apt-get install pandoc'],
                windows: ['winget install --id JohnMacFarlane.Pandoc'],
                notes: 'Pandoc 2.19 이상 필요'
            }
        };
    }

    /**
     * Check PDF engines (at least one should be available)
     */
    private async checkPdfEngines(): Promise<DependencyStatus[]> {
        const engines = [
            {
                name: 'WeasyPrint',
                command: 'weasyprint',
                description: 'PDF 생성 엔진 (추천) - 가장 쉽고 한글 지원 우수',
                macOS: ['pip3 install weasyprint', '또는 pip install weasyprint'],
                linux: ['pip3 install weasyprint', '또는 pip install weasyprint'],
                windows: ['pip install weasyprint'],
                notes: 'Python이 필요합니다: https://python.org'
            },
            {
                name: 'XeLaTeX',
                command: 'xelatex',
                description: 'PDF 생성 엔진 (한글 최적화) - 전문 출판 품질',
                macOS: ['brew install --cask basictex', 'eval "$(/usr/libexec/path_helper)"'],
                linux: ['sudo apt-get install texlive-xetex texlive-fonts-recommended'],
                windows: ['https://www.tug.org/texlive/ 에서 설치'],
                notes: '설치 후 터미널 재시작 필요'
            },
            {
                name: 'PDFLaTeX',
                command: 'pdflatex',
                description: 'PDF 생성 엔진 (기본) - 표준 LaTeX',
                macOS: ['brew install --cask basictex'],
                linux: ['sudo apt-get install texlive-latex-base'],
                windows: ['https://www.tug.org/texlive/ 에서 설치'],
                notes: '설치 후 터미널 재시작 필요'
            }
        ];

        const results: DependencyStatus[] = [];
        for (const engine of engines) {
            const result = await this.isCommandAvailable(engine.command);
            results.push({
                name: engine.name,
                required: false,
                installed: result.available,
                version: result.version,
                installInstructions: {
                    description: engine.description,
                    macOS: engine.macOS,
                    linux: engine.linux,
                    windows: engine.windows,
                    notes: engine.notes
                }
            });
        }

        return results;
    }

    /**
     * Check Python (optional, for WeasyPrint)
     */
    private async checkPython(): Promise<DependencyStatus> {
        const result = await this.isCommandAvailable('python3', ['--version']);
        const result2 = !result.available ? await this.isCommandAvailable('python', ['--version']) : result;

        return {
            name: 'Python',
            required: false,
            installed: result.available || result2.available,
            version: result.version || result2.version,
            installInstructions: {
                description: 'WeasyPrint 설치에 필요 (선택사항)',
                macOS: ['brew install python3'],
                linux: ['sudo apt-get install python3 python3-pip'],
                windows: ['winget install Python.Python.3', '또는 https://python.org 에서 다운로드'],
                notes: 'WeasyPrint를 사용하려면 필요합니다'
            }
        };
    }

    /**
     * Check all dependencies
     */
    async checkAll(): Promise<{
        allRequired: boolean;
        hasPdfEngine: boolean;
        dependencies: DependencyStatus[];
        pdfEngines: DependencyStatus[];
    }> {
        const node = await this.checkNode();
        const pandoc = await this.checkPandoc();
        const python = await this.checkPython();
        const pdfEngines = await this.checkPdfEngines();

        const dependencies = [node, pandoc, python];
        const allRequired = node.installed && pandoc.installed;
        const hasPdfEngine = pdfEngines.some(engine => engine.installed);

        return {
            allRequired,
            hasPdfEngine,
            dependencies,
            pdfEngines
        };
    }

    /**
     * Display installation instructions for a dependency
     */
    displayInstallInstructions(dep: DependencyStatus): void {
        const platform = process.platform;
        const instructions = dep.installInstructions;

        console.log(chalk.yellow(`\n📦 ${dep.name} 설치 방법:`));
        console.log(chalk.gray(`   ${instructions.description}\n`));

        if (platform === 'darwin') {
            console.log(chalk.cyan('   macOS:'));
            instructions.macOS.forEach(cmd => {
                console.log(chalk.white(`   $ ${cmd}`));
            });
        } else if (platform === 'win32') {
            console.log(chalk.cyan('   Windows:'));
            instructions.windows.forEach(cmd => {
                console.log(chalk.white(`   > ${cmd}`));
            });
        } else {
            console.log(chalk.cyan('   Linux:'));
            instructions.linux.forEach(cmd => {
                console.log(chalk.white(`   $ ${cmd}`));
            });
        }

        if (instructions.notes) {
            console.log(chalk.gray(`\n   💡 ${instructions.notes}`));
        }
    }

    /**
     * Display comprehensive dependency report
     */
    async displayDependencyReport(): Promise<boolean> {
        console.log(chalk.cyan.bold('\n🔍 의존성 확인 중...\n'));

        const { allRequired, hasPdfEngine, dependencies, pdfEngines } = await this.checkAll();

        // Show required dependencies
        console.log(chalk.bold('필수 의존성:'));
        dependencies.filter(d => d.required).forEach(dep => {
            if (dep.installed) {
                console.log(chalk.green(`  ✅ ${dep.name} ${dep.version ? `(v${dep.version})` : ''}`));
            } else {
                console.log(chalk.red(`  ❌ ${dep.name} - 설치 필요`));
            }
        });

        // Show PDF engines
        console.log(chalk.bold('\nPDF 생성 엔진 (최소 1개 필요):'));
        pdfEngines.forEach(engine => {
            if (engine.installed) {
                console.log(chalk.green(`  ✅ ${engine.name} ${engine.version ? `(v${engine.version})` : ''}`));
            } else {
                console.log(chalk.gray(`  ⚪ ${engine.name} - 미설치`));
            }
        });

        // Show optional dependencies
        const optional = dependencies.filter(d => !d.required);
        if (optional.length > 0) {
            console.log(chalk.bold('\n선택 의존성:'));
            optional.forEach(dep => {
                if (dep.installed) {
                    console.log(chalk.green(`  ✅ ${dep.name} ${dep.version ? `(v${dep.version})` : ''}`));
                } else {
                    console.log(chalk.gray(`  ⚪ ${dep.name} - 미설치`));
                }
            });
        }

        // If missing required dependencies, show installation instructions
        if (!allRequired) {
            console.log(chalk.red.bold('\n⚠️  필수 의존성이 누락되었습니다!\n'));
            dependencies.filter(d => d.required && !d.installed).forEach(dep => {
                this.displayInstallInstructions(dep);
            });
            return false;
        }

        // If no PDF engine, show recommendations
        if (!hasPdfEngine) {
            console.log(chalk.yellow.bold('\n⚠️  PDF 생성 엔진이 없습니다!\n'));
            console.log(chalk.yellow('PDF 파일을 생성하려면 최소 1개의 PDF 엔진이 필요합니다.'));
            console.log(chalk.yellow('EPUB만 생성하려면 이 단계를 건너뛸 수 있습니다.\n'));

            // Show WeasyPrint first (recommended)
            const weasyprint = pdfEngines.find(e => e.name === 'WeasyPrint');
            if (weasyprint) {
                this.displayInstallInstructions(weasyprint);
            }

            console.log(chalk.gray('\n또는 다른 PDF 엔진을 선택하세요:'));
            pdfEngines.filter(e => e.name !== 'WeasyPrint').forEach(engine => {
                console.log(chalk.gray(`  • ${engine.name}: ${engine.installInstructions.description}`));
            });

            console.log(chalk.cyan('\n💡 전체 설치 가이드: https://github.com/goodlookingprokim/markdown-to-document-cli#-필수-요구사항\n'));
        }

        if (allRequired && hasPdfEngine) {
            console.log(chalk.green.bold('\n✅ 모든 의존성이 준비되었습니다!\n'));
        }

        return allRequired;
    }

    /**
     * Quick check - returns true if ready to convert
     */
    async quickCheck(format: 'epub' | 'pdf' | 'both'): Promise<boolean> {
        const { allRequired, hasPdfEngine } = await this.checkAll();

        if (!allRequired) {
            return false;
        }

        // If PDF is needed but no engine available
        if ((format === 'pdf' || format === 'both') && !hasPdfEngine) {
            return false;
        }

        return true;
    }
}
