/**
 * Constants and Configuration
 */

import type { TypographyPreset, CoverTheme } from '../types/index.js';

export const WORDS_PER_MINUTE = 200;

export const COVER_THEMES: Record<string, CoverTheme> = {
    // === Basic Themes ===
    apple: {
        id: 'apple',
        name: 'Apple Style',
        category: 'basic',
        description: 'Minimalist design inspired by Apple',
        colors: {
            primary: '#ffffff',
            secondary: '#f5f5f7',
            accent: '#0071e3',
            background: '#000000',
            text: '#ffffff'
        },
        style: 'minimal'
    },
    modern_gradient: {
        id: 'modern_gradient',
        name: 'Modern Gradient',
        category: 'basic',
        description: 'Contemporary gradient design',
        colors: {
            primary: '#667eea',
            secondary: '#764ba2',
            accent: '#f093fb',
            background: '#1a1a2e',
            text: '#ffffff'
        },
        style: 'gradient'
    },
    dark_tech: {
        id: 'dark_tech',
        name: 'Dark Tech',
        category: 'basic',
        description: 'Dark technology style',
        colors: {
            primary: '#0a0a0a',
            secondary: '#1a1a1a',
            accent: '#00ff88',
            background: '#000000',
            text: '#ffffff'
        },
        style: 'dark'
    },
    nature: {
        id: 'nature',
        name: 'Nature',
        category: 'basic',
        description: 'Nature-friendly design',
        colors: {
            primary: '#2d5016',
            secondary: '#4a7c23',
            accent: '#8bc34a',
            background: '#1b2e0d',
            text: '#ffffff'
        },
        style: 'modern'
    },
    classic_book: {
        id: 'classic_book',
        name: 'Classic Book',
        category: 'basic',
        description: 'Classic book style',
        colors: {
            primary: '#8b4513',
            secondary: '#d2691e',
            accent: '#f4a460',
            background: '#2f1810',
            text: '#f5deb3'
        },
        style: 'minimal'
    },
    minimalist: {
        id: 'minimalist',
        name: 'Minimalist',
        category: 'basic',
        description: 'Extremely simple design',
        colors: {
            primary: '#ffffff',
            secondary: '#f8f8f8',
            accent: '#333333',
            background: '#ffffff',
            text: '#000000'
        },
        style: 'minimal'
    },

    // === Professional Themes ===
    corporate: {
        id: 'corporate',
        name: 'Corporate Blue',
        category: 'professional',
        description: '비즈니스 문서용 전문적인 블루 톤',
        colors: {
            primary: '#1e3a5f',
            secondary: '#2c5282',
            accent: '#63b3ed',
            background: '#1a365d',
            text: '#ffffff'
        },
        style: 'modern'
    },
    academic: {
        id: 'academic',
        name: 'Academic',
        category: 'professional',
        description: '학술 논문 및 연구 보고서용',
        colors: {
            primary: '#2d3748',
            secondary: '#4a5568',
            accent: '#805ad5',
            background: '#1a202c',
            text: '#e2e8f0'
        },
        style: 'minimal'
    },
    magazine: {
        id: 'magazine',
        name: 'Magazine',
        category: 'professional',
        description: '잡지 스타일의 세련된 디자인',
        colors: {
            primary: '#c53030',
            secondary: '#9b2c2c',
            accent: '#fed7d7',
            background: '#1a1a1a',
            text: '#ffffff'
        },
        style: 'modern'
    },

    // === Creative Themes ===
    sunset: {
        id: 'sunset',
        name: 'Sunset',
        category: 'creative',
        description: '따뜻한 석양 그라데이션',
        colors: {
            primary: '#f6ad55',
            secondary: '#ed64a6',
            accent: '#fbd38d',
            background: '#2d1b4e',
            text: '#ffffff'
        },
        style: 'gradient'
    },
    ocean: {
        id: 'ocean',
        name: 'Ocean',
        category: 'creative',
        description: '시원한 바다 블루 그라데이션',
        colors: {
            primary: '#0bc5ea',
            secondary: '#3182ce',
            accent: '#90cdf4',
            background: '#0d1b2a',
            text: '#ffffff'
        },
        style: 'gradient'
    },
    aurora: {
        id: 'aurora',
        name: 'Aurora',
        category: 'creative',
        description: '오로라 컬러 그라데이션',
        colors: {
            primary: '#38b2ac',
            secondary: '#805ad5',
            accent: '#68d391',
            background: '#0f0f1a',
            text: '#ffffff'
        },
        style: 'gradient'
    },
    rose_gold: {
        id: 'rose_gold',
        name: 'Rose Gold',
        category: 'creative',
        description: '우아한 로즈골드 톤',
        colors: {
            primary: '#b88b8b',
            secondary: '#8b6b6b',
            accent: '#d4a5a5',
            background: '#2d1f1f',
            text: '#ffeaea'
        },
        style: 'modern'
    },

    // === Seasonal Themes ===
    spring: {
        id: 'spring',
        name: 'Spring',
        category: 'seasonal',
        description: '봄의 생동감 있는 파스텔 톤',
        colors: {
            primary: '#f687b3',
            secondary: '#9ae6b4',
            accent: '#fbb6ce',
            background: '#1a1a2e',
            text: '#ffffff'
        },
        style: 'gradient'
    },
    autumn: {
        id: 'autumn',
        name: 'Autumn',
        category: 'seasonal',
        description: '가을의 따뜻한 단풍 컬러',
        colors: {
            primary: '#dd6b20',
            secondary: '#c05621',
            accent: '#fbd38d',
            background: '#1a0f0a',
            text: '#fffaf0'
        },
        style: 'modern'
    },
    winter: {
        id: 'winter',
        name: 'Winter',
        category: 'seasonal',
        description: '겨울의 차가운 블루/화이트 톤',
        colors: {
            primary: '#a0aec0',
            secondary: '#e2e8f0',
            accent: '#bee3f8',
            background: '#1a202c',
            text: '#ffffff'
        },
        style: 'minimal'
    }
};

export const TYPOGRAPHY_PRESETS: Record<string, TypographyPreset> = {
    // === Basic Presets ===
    novel: {
        id: 'novel',
        name: '소설',
        description: '장편 소설, 에세이용 - 16pt, 들여쓰기, 양쪽 정렬',
        fontSize: 16,
        lineHeight: 1.8,
        fontFamily: 'Noto Serif CJK KR, serif',
        textAlign: 'justify',
        paragraphSpacing: 0,
        features: ['indentation', 'widow-orphan-control', 'hyphenation']
    },
    presentation: {
        id: 'presentation',
        name: '발표',
        description: '프레젠테이션, 강의용 - 18pt, 큰 글씨, 넓은 여백',
        fontSize: 18,
        lineHeight: 1.6,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 12,
        features: ['large-headings', 'clear-structure', 'readable']
    },
    review: {
        id: 'review',
        name: '리뷰',
        description: '검토용 문서 - 11pt, 촘촘한 레이아웃',
        fontSize: 11,
        lineHeight: 1.4,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 6,
        features: ['compact', 'information-dense', 'printable']
    },
    ebook: {
        id: 'ebook',
        name: '전자책',
        description: '일반 전자책용 - 14pt, 균형잡힌 레이아웃',
        fontSize: 14,
        lineHeight: 1.6,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'justify',
        paragraphSpacing: 8,
        features: ['balanced', 'readable', 'responsive']
    },

    // === Content-focused Presets ===
    text_heavy: {
        id: 'text_heavy',
        name: '텍스트 중심',
        description: '긴 글 위주 문서용 - 12pt, 촘촘한 줄간격, 좁은 여백',
        fontSize: 12,
        lineHeight: 1.5,
        fontFamily: 'Noto Serif CJK KR, serif',
        textAlign: 'justify',
        paragraphSpacing: 3,
        features: ['compact-text', 'indentation', 'hyphenation']
    },
    table_heavy: {
        id: 'table_heavy',
        name: '테이블 중심',
        description: '표가 많은 문서용 - 11pt, 넓은 표 영역, 작은 폰트',
        fontSize: 11,
        lineHeight: 1.4,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 5,
        features: ['wide-tables', 'compact-margins', 'structured']
    },
    image_heavy: {
        id: 'image_heavy',
        name: '이미지 중심',
        description: '이미지가 많은 문서용 - 13pt, 이미지 최대화, 캡션 강조',
        fontSize: 13,
        lineHeight: 1.5,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 8,
        features: ['large-images', 'captions', 'visual-focus']
    },
    balanced: {
        id: 'balanced',
        name: '균형 레이아웃',
        description: '텍스트/테이블/이미지 균형 배치 - 12pt, 최적화된 가독성',
        fontSize: 12,
        lineHeight: 1.55,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 6,
        features: ['balanced', 'adaptive', 'professional']
    },

    // === Document Type Presets ===
    report: {
        id: 'report',
        name: '보고서',
        description: '비즈니스 보고서용 - 11pt, 공식적, 구조화된 레이아웃',
        fontSize: 11,
        lineHeight: 1.5,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'justify',
        paragraphSpacing: 7,
        features: ['formal', 'structured', 'toc-friendly']
    },
    manual: {
        id: 'manual',
        name: '매뉴얼',
        description: '기술 문서/매뉴얼용 - 11pt, 코드 블록, 단계별 설명 강조',
        fontSize: 11,
        lineHeight: 1.6,
        fontFamily: 'Noto Sans CJK KR, sans-serif',
        textAlign: 'left',
        paragraphSpacing: 8,
        features: ['code-blocks', 'numbered-steps', 'callouts']
    },
    magazine: {
        id: 'magazine',
        name: '매거진',
        description: '잡지 스타일 - 11pt, 드롭캡, 시각적 강조, 세련된 디자인',
        fontSize: 11,
        lineHeight: 1.5,
        fontFamily: 'Noto Serif CJK KR, serif',
        textAlign: 'justify',
        paragraphSpacing: 5,
        features: ['drop-cap', 'pull-quotes', 'visual-emphasis']
    }
};

export const CALLOUT_TYPES = [
    'note', 'abstract', 'summary', 'tip', 'info', 'todo', 'success', 'question',
    'warning', 'failure', 'danger', 'bug', 'example', 'quote'
];

export const ATTACHMENT_FOLDERS = ['attachments', 'images', 'assets', 'media'];

export const DEFAULT_CONFIG = {
    format: 'epub' as const,
    typographyPreset: 'ebook' as const,
    coverTheme: 'apple',
    tocDepth: 2,
    includeToc: true,
    enableFontSubsetting: false,
    validateContent: true,
    autoFix: true,
    generateCover: true,
    includeCopyright: false,
    paperSize: 'a4' as const,
    pdfEngine: 'weasyprint' as const
};
