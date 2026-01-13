/**
 * UI Rendering & DOM Manipulation
 */

import { State } from './state.js';
import { LITURGICAL_INFO, CONFIG } from './config.js';
import { Utils } from './utils.js';

export const UI = {
    // === Logic: Date & Liturgical ===

    updateDateDisplay() {
        const now = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        let dateStr = now.toLocaleDateString(CONFIG.DATE_LOCALE, options);
        dateStr = dateStr.replace('일요일', '주일');

        const el = document.getElementById('date-display');
        if (el) el.textContent = dateStr;
    },

    showLiturgicalInfo(liturgicalName) {
        const modal = document.getElementById('liturgical-modal');
        const title = document.getElementById('liturgical-modal-title');
        const desc = document.getElementById('liturgical-modal-desc');

        if (!modal || !title || !desc) return;

        title.textContent = liturgicalName;

        let description = LITURGICAL_INFO[liturgicalName];
        if (!description) {
            for (const key of Object.keys(LITURGICAL_INFO)) {
                if (liturgicalName.includes(key) || key.includes(liturgicalName)) {
                    description = LITURGICAL_INFO[key];
                    break;
                }
            }
        }

        desc.textContent = description || "이 절기에 대한 설명이 아직 준비되지 않았습니다.";
        modal.classList.add('visible');
    },

    closeLiturgicalModal() {
        const modal = document.getElementById('liturgical-modal');
        if (modal) modal.classList.remove('visible');
    },

    // === Logic: Rendering ===

    renderContent(data) {
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = '';

        // Liturgical Badge
        const liturgicalDisplay = document.getElementById('liturgical-display');
        if (data.liturgical && liturgicalDisplay) {
            // Event delegation handled in main.js or inline onclick removed
            // We'll reimplement onclick binding via direct element for safety OR standard events
            // Since we are module based, inline onclick="showLiturgicalInfo" won't work easily unless exposed global.
            // BETTER: Create element and add listener.

            liturgicalDisplay.innerHTML = '';
            const badge = document.createElement('span');
            badge.className = 'liturgical-badge';
            badge.textContent = data.liturgical;
            badge.addEventListener('click', () => this.showLiturgicalInfo(data.liturgical));

            liturgicalDisplay.appendChild(badge);
            liturgicalDisplay.classList.add('visible');
        }

        // Cards
        mainContent.appendChild(this.createVerseCard(data.ot, 'ot', '구약'));
        mainContent.appendChild(this.createVerseCard(data.nt, 'nt', '신약'));

        // Meditation
        if (data.meditation) {
            const medSection = document.getElementById('meditation-section');
            document.getElementById('meditation-content').textContent = data.meditation.content;
            document.getElementById('question-text').textContent = data.meditation.question;
            medSection.style.display = 'block';
        }
    },

    createVerseCard(verseData, cardId, label) {
        const template = document.getElementById('verse-card-template');
        const card = template.content.cloneNode(true);

        card.querySelector('.verse-ref').textContent = verseData.ref;
        card.querySelector('.verse-label').textContent = label;

        const originalText = card.querySelector('.original-text');
        originalText.classList.add(verseData.lang_class);
        originalText.setAttribute('dir', verseData.text_dir);

        verseData.words.forEach((word, idx) => {
            const wordBlock = document.createElement('div');
            wordBlock.className = 'word-block';
            wordBlock.addEventListener('click', () => this.showWordInfo(cardId, idx));
            wordBlock.innerHTML = `
                <span class="word-text">${word.text}</span>
                <span class="word-sound">${word.sound}</span>
            `;
            originalText.appendChild(wordBlock);
        });

        card.querySelector('.std-trans').textContent = verseData.kor_std;
        card.querySelector('.eng-text').textContent = verseData.eng_bsb;
        card.querySelector('.lit-text').textContent = verseData.kor_lit;

        return card;
    },

    // === Logic: Parsing Panel ===

    showWordInfo(cardId, wordIdx) {
        const data = State.getDailyData();
        if (!data) return;

        const verseData = cardId === 'ot' ? data.ot : data.nt;
        const word = verseData.words[wordIdx];

        document.getElementById('p-word').textContent = word.text;
        document.getElementById('p-sound').textContent = `[${word.sound}]`;
        const lemmaDisplay = word.lemma_sound ? `${word.lemma} [${word.lemma_sound}]` : word.lemma;
        document.getElementById('p-lemma').textContent = `기본형: ${lemmaDisplay}`;
        document.getElementById('p-morph').textContent = word.morph;
        document.getElementById('p-gloss').textContent = word.gloss;

        const wordEl = document.getElementById('p-word');
        const isHebrew = verseData.lang === 'hebrew';
        wordEl.style.fontFamily = isHebrew ? "'SBL Hebrew', serif" : "'SBL Greek', serif";
        wordEl.style.direction = isHebrew ? 'rtl' : 'ltr';

        document.getElementById('parsing-panel').classList.add('visible');
    },

    hideParsing() {
        document.getElementById('parsing-panel').classList.remove('visible');
    },

    showError() {
        document.getElementById('main-content').innerHTML = '';
        document.getElementById('error-state').style.display = 'block';
    },

    // === Logic: Settings & Theme ===

    setTheme(theme) {
        const root = document.documentElement;
        root.classList.remove('light-mode', 'dark-mode');

        if (theme === 'light') root.classList.add('light-mode');
        else if (theme === 'dark') root.classList.add('dark-mode');

        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });

        State.saveSettings({ theme });
    },

    setFontSize(size) {
        const sizeNum = parseFloat(size);
        document.documentElement.style.setProperty('--original-font-size', `${sizeNum}rem`);

        const valueDisplay = document.getElementById('font-size-value');
        if (valueDisplay) valueDisplay.textContent = `${sizeNum.toFixed(1)}rem`;

        const preview = document.getElementById('font-preview-text');
        if (preview) preview.style.fontSize = `${sizeNum}rem`;

        const slider = document.getElementById('font-size-slider');
        if (slider && slider.value != size) slider.value = sizeNum;

        State.saveSettings({ fontSize: sizeNum });
    },

    toggleSettings() {
        const panel = document.getElementById('settings-panel');
        const overlay = document.getElementById('settings-overlay');
        const isVisible = panel.classList.contains('visible');

        if (isVisible) this.closeSettings();
        else {
            panel.classList.add('visible');
            overlay.classList.add('visible');
        }
    },

    closeSettings() {
        document.getElementById('settings-panel').classList.remove('visible');
        document.getElementById('settings-overlay').classList.remove('visible');
    },

    initSettingsUI() {
        const settings = State.loadSettings();
        this.setTheme(settings.theme);
        this.setFontSize(settings.fontSize);

        // Bind settings events
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', () => this.setTheme(btn.dataset.theme));
        });

        const slider = document.getElementById('font-size-slider');
        if (slider) slider.addEventListener('input', (e) => this.setFontSize(e.target.value));
    }
};
