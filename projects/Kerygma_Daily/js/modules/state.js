/**
 * State Management
 */

const SETTINGS_KEY = 'kerygma-daily-settings';

const DEFAULT_SETTINGS = {
    theme: 'auto',      // 'auto', 'light', 'dark'
    fontSize: 1.6       // rem value for original text
};

export const State = {
    dailyData: null,

    settings: { ...DEFAULT_SETTINGS },

    loadSettings() {
        try {
            const saved = localStorage.getItem(SETTINGS_KEY);
            this.settings = saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : { ...DEFAULT_SETTINGS };
        } catch {
            this.settings = { ...DEFAULT_SETTINGS };
        }
        return this.settings;
    },

    saveSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
        try {
            localStorage.setItem(SETTINGS_KEY, JSON.stringify(this.settings));
        } catch (e) {
            console.warn('설정 저장 실패:', e);
        }
    },

    // Setter for daily data
    setDailyData(data) {
        this.dailyData = data;
    },

    getDailyData() {
        return this.dailyData;
    }
};
