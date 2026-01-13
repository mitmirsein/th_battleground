/**
 * Kerygma Daily - Application Entry Point
 * Refactored into Modules
 */

import { API } from './modules/api.js';
import { UI } from './modules/ui.js';
import { Utils } from './modules/utils.js';
import { State } from './modules/state.js';

// Global Event Handlers
async function init() {
    console.log('Initializing Kerygma Daily...');

    // 1. Init Settings (Theme, Font)
    UI.initSettingsUI();

    // 2. Update Date
    UI.updateDateDisplay();

    // 3. Register SW
    Utils.registerServiceWorker();

    // 4. Bind Global Events (Settings, Parsing Panel Close)
    bindGlobalEvents();

    // 5. Load Data
    await API.loadTodayData();
}

function bindGlobalEvents() {
    // Settings Toggle
    const settingsBtn = document.querySelector('.settings-toggle');
    if (settingsBtn) settingsBtn.addEventListener('click', () => UI.toggleSettings());

    const closeSettingsBtn = document.querySelector('.close-settings');
    if (closeSettingsBtn) closeSettingsBtn.addEventListener('click', () => UI.closeSettings());

    const settingsOverlay = document.getElementById('settings-overlay');
    if (settingsOverlay) settingsOverlay.addEventListener('click', () => UI.closeSettings());

    // Liturgical Modal Close
    const modal = document.getElementById('liturgical-modal');
    if (modal) modal.addEventListener('click', () => UI.closeLiturgicalModal());

    const closeModalBtn = document.querySelector('.close-modal');
    if (closeModalBtn) closeModalBtn.addEventListener('click', () => UI.closeLiturgicalModal());

    const modalContent = document.querySelector('.liturgical-modal-content');
    if (modalContent) modalContent.addEventListener('click', (e) => e.stopPropagation());

    // Parsing Panel Close
    const closePanelBtn = document.querySelector('.close-panel');
    if (closePanelBtn) closePanelBtn.addEventListener('click', () => UI.hideParsing());

    // Click Outside Parsing Panel
    document.addEventListener('click', (e) => {
        const panel = document.getElementById('parsing-panel');
        const isPanelVisible = panel.classList.contains('visible');
        if (isPanelVisible && !panel.contains(e.target) && !e.target.closest('.word-block')) {
            UI.hideParsing();
        }
    });

    // Keyboard ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            UI.hideParsing();
            UI.closeSettings();
            UI.closeLiturgicalModal();
        }
    });

    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => Utils.handleShare(State.getDailyData()));
    }
}

// Start App
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
