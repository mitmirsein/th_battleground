/**
 * API & Data Fetching
 */

import { CONFIG } from './config.js';
import { State } from './state.js';
import { UI } from './ui.js';

// Sample Data Fallback
const SAMPLE_DATA = {
    date: new Date().toISOString().split('T')[0],
    ot: {
        ref: "이사야 25:8",
        lang: "hebrew",
        text_dir: "rtl",
        lang_class: "hebrew",
        kor_std: "사망을 영원히 멸하실 것이라 주 여호와께서 모든 얼굴에서 눈물을 씻기시며",
        kor_lit: "그분께서 죽음을 영원히 삼키셨다 그리고 주 여호와께서 모든 얼굴에서 눈물을 닦으셨다",
        eng_bsb: "He will swallow up death forever. The Lord GOD will wipe away the tears from every face.",
        words: [
            { text: "בִּלַּ֤ע", sound: "빌라", lemma: "בָּלַע", morph: "동사 피엘(강조) 완료 3남단", gloss: "삼키셨다" },
            { text: "הַמָּ֙וֶת֙", sound: "함마웻", lemma: "מָוֶת", morph: "관사 + 명사 남성 단수", gloss: "그 죽음을" },
            { text: "לָנֶ֔צַח", sound: "라네차흐", lemma: "נֶצַח", morph: "전치사 + 명사", gloss: "영원히" },
            { text: "וּמָחָה", sound: "우마하", lemma: "מָחָה", morph: "접속사 + 동사 칼 완료 3남단", gloss: "그리고 닦으실 것이다" }
        ]
    },
    nt: {
        ref: "요한1서 4:9",
        lang: "greek",
        text_dir: "ltr",
        lang_class: "greek",
        kor_std: "하나님의 사랑이 우리에게 이렇게 나타난 바 되었다",
        kor_lit: "이로써 하나님의 사랑이 우리에게 나타난 바 되었다",
        eng_bsb: "This is how God's love was revealed among us: God sent His one and only Son into the world, so that we might live through Him.",
        words: [
            { text: "ἐν", sound: "엔", lemma: "ἐν", morph: "전치사", gloss: "~안에" },
            { text: "τούτῳ", sound: "투토", lemma: "οὗτος", morph: "지시대명사", gloss: "이것에" },
            { text: "ἐφανερώθη", sound: "에파네로떼", lemma: "φανερόω", morph: "동사", gloss: "나타났다" }
        ]
    },
    meditation: {
        content: "죽음은 결코 우리 삶의 허무한 종착역이 아니며, 영원한 안식과 생명으로 들어가는 새로운 문입니다...",
        question: "오늘 당신의 삶에서 '죽음을 삼키는 생명'의 능력을 경험해야 할 영역은 무엇입니까?"
    }
};

export const API = {
    async loadTodayData() {
        // UI.renderSkeleton(); // Removed in rollback

        try {
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            const dateKey = `${year}-${month}-${day}`;

            let data = null;

            if (CONFIG.DATA_SOURCE === 'json') {
                const yearMonth = dateKey.substring(0, 7);
                const jsonUrl = `${CONFIG.DATA_PATH}/${yearMonth}.json`;

                try {
                    const response = await fetch(jsonUrl);
                    if (response.ok) {
                        const monthData = await response.json();
                        data = monthData[dateKey];
                    }
                } catch (e) {
                    console.warn('JSON fetch error:', e);
                }
            } else if (CONFIG.DATA_SOURCE === 'api' && CONFIG.SHEETS_API_URL) {
                try {
                    const response = await fetch(CONFIG.SHEETS_API_URL);
                    if (response.ok) data = await response.json();
                } catch (e) {
                    console.error('API fetch error:', e);
                }
            }

            // Fallback
            if (!data) {
                console.warn('Using Sample Data');
                data = SAMPLE_DATA;
            }

            State.setDailyData(data);
            UI.renderContent(data);

        } catch (error) {
            console.error('Data loading failed completely:', error);
            UI.showError();
        }
    }
};
