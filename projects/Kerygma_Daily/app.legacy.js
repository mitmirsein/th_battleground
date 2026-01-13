/**
 * Kerygma Daily - Application Logic
 * Google Sheets integration + Dynamic rendering
 */

// ============================================
// Configuration
// ============================================

const CONFIG = {
    // 데이터 소스: 'json' (정적 파일) 또는 'api' (Google Sheets)
    DATA_SOURCE: 'json',

    // JSON 데이터 경로 (월별 파일: data/YYYY-MM.json)
    DATA_PATH: 'data',

    // Google Apps Script Web App URL (DATA_SOURCE가 'api'일 때 사용)
    SHEETS_API_URL: '',

    // 날짜 형식
    DATE_LOCALE: 'ko-KR',
    TIMEZONE: 'Asia/Seoul'
};

// ============================================
// Liturgical Day Descriptions
// ============================================

const LITURGICAL_INFO = {
    // 성탄절기
    "성탄절": "예수 그리스도의 탄생을 기념하는 날입니다. 하나님이 인간의 몸을 입고 이 땅에 오신 성육신의 신비를 묵상합니다.",
    "성탄 후 제1주일": "성탄의 기쁨 안에서 보내는 첫 번째 주일입니다. 어린 아기 예수의 탄생이 주는 의미를 깊이 묵상합니다.",
    "성탄 후 제2주일": "성탄의 신비를 계속 묵상하는 시기입니다. 말씀이 육신이 되어 우리 가운데 거하신 은혜를 기억합니다.",
    "성탄절기": "성탄일부터 주현절까지의 기간으로, 그리스도의 성육신을 묵상하는 절기입니다.",
    "새해 첫날 (예수 이름의 날)": "새해 첫날은 전통적으로 예수님이 할례를 받고 이름을 받으신 날을 기념합니다. 예수라는 이름은 '구원하시는 분'을 의미합니다.",

    // 주현절
    "주현절 (Epiphany)": "동방박사들이 아기 예수님을 찾아와 경배한 사건을 기념합니다. 그리스도께서 모든 민족의 빛으로 나타나심을 축하하는 날입니다.",
    "주현절": "동방박사들이 아기 예수님을 찾아와 경배한 사건을 기념합니다. 그리스도께서 모든 민족의 빛으로 나타나심을 축하하는 날입니다.",
    "주현절 전": "주현절을 준비하는 기간입니다. 그리스도의 나타나심(현현)을 기다리며 묵상합니다.",
    "주현절 이브": "주현절 바로 전날로, 동방박사들의 여정과 별을 따라가는 믿음을 묵상합니다.",
    "주현절 후 제1주일": "주현절 이후 첫 주일로, 예수님의 세례를 기념하는 '주의 세례 주일'로도 불립니다.",
    "주현절 후 제2주일": "예수님의 공생애 사역이 시작되는 시기를 묵상합니다. 첫 기적인 가나의 혼인잔치가 본문으로 자주 읽힙니다.",
    "주현절 후": "주현절 이후의 연중시기로, 그리스도의 사역과 가르침을 묵상하는 기간입니다.",

    // 사순절
    "재의 수요일": "사순절의 시작일입니다. 재를 이마에 바르며 회개와 겸손, 우리의 유한함을 기억합니다.",
    "사순절 제1주일": "사순절 첫 주일로, 예수님의 광야 시험을 묵상합니다. 40일간의 회개와 준비의 여정이 시작됩니다.",
    "사순절 제2주일": "사순절의 두 번째 주일입니다. 믿음의 길을 걷는 우리의 여정을 돌아봅니다.",
    "사순절 제3주일": "사순절의 세 번째 주일입니다. 회개와 갱신의 필요성을 묵상합니다.",
    "사순절 제4주일": "사순절의 네 번째 주일입니다. 레타레(기뻐하라) 주일로도 불리며, 부활의 기쁨을 미리 맛봅니다.",
    "사순절 제5주일": "사순절의 다섯 번째 주일입니다. 고난주간을 앞두고 예수님의 수난을 깊이 묵상합니다.",
    "종려주일": "예수님이 예루살렘에 입성하신 날을 기념합니다. 군중이 종려나무 가지를 흔들며 환호했지만, 곧 고난이 시작됩니다.",
    "고난주간": "예수님의 수난과 십자가를 묵상하는 주간입니다. 겟세마네 동산에서 골고다까지의 여정을 따릅니다.",
    "성목요일": "예수님이 제자들과 최후의 만찬을 나누신 날입니다. 성찬의 제정과 섬김의 본을 보이신 세족식을 기억합니다.",
    "성금요일": "예수님이 십자가에서 돌아가신 날입니다. 우리를 위한 그리스도의 대속적 죽음을 묵상합니다.",
    "성토요일": "예수님이 무덤에 계셨던 날입니다. 어둠과 침묵 속에서 부활을 기다리는 시간입니다.",

    // 부활절
    "부활절": "예수 그리스도께서 죽음을 이기고 부활하신 날입니다. 기독교 신앙의 핵심이자 가장 중요한 절기입니다.",
    "부활절 제2주일": "부활절 이후 두 번째 주일입니다. 도마의 고백을 통해 부활 신앙을 확인합니다.",
    "부활절 제3주일": "부활하신 주님과의 만남을 계속 묵상합니다. 엠마오 도상의 제자들 이야기가 자주 읽힙니다.",
    "부활절 제4주일": "선한 목자 주일로, 예수님을 우리의 목자로 고백합니다.",
    "부활절 제5주일": "부활하신 그리스도 안에서 사는 삶을 묵상합니다.",
    "부활절 제6주일": "승천을 앞두고 부활의 의미를 더 깊이 묵상합니다.",
    "승천일": "예수님이 하늘로 올라가신 날입니다. 부활 후 40일째 되는 날에 승천하셨습니다.",
    "부활절 제7주일": "승천과 오순절 사이의 주일입니다. 성령 강림을 기다리며 기도합니다.",

    // 성령강림절
    "성령강림절": "성령이 제자들에게 임하신 날입니다. 오순절이라고도 하며, 교회의 탄생일로 기념됩니다.",
    "삼위일체주일": "성령강림절 다음 주일로, 성부 성자 성령 삼위일체 하나님을 고백합니다.",
    "성령강림절 후": "성령강림절 이후의 연중시기로, 교회의 선교와 성장, 그리스도인의 삶을 묵상합니다.",

    // 기타
    "연중시기": "특별한 절기가 아닌 일반 주일입니다. 예수님의 가르침과 사역을 체계적으로 묵상합니다.",
    "추수감사주일": "하나님의 은혜와 공급하심에 감사드리는 주일입니다.",
    "대림절 제1주일": "새로운 교회력의 시작입니다. 그리스도의 오심을 준비하며 기다리는 시기입니다.",
    "대림절 제2주일": "그리스도의 재림을 기다리며 회개와 준비의 메시지를 듣습니다.",
    "대림절 제3주일": "가우데테(기뻐하라) 주일이라고도 합니다. 주님의 오심이 가까워졌음을 기뻐합니다.",
    "대림절 제4주일": "성탄을 바로 앞둔 주일입니다. 마리아의 순종과 요셉의 믿음을 묵상합니다."
};

// ============================================
// Liturgical Modal Functions
// ============================================

/**
 * 절기 설명 모달 표시
 */
function showLiturgicalInfo(liturgicalName) {
    const modal = document.getElementById('liturgical-modal');
    const title = document.getElementById('liturgical-modal-title');
    const desc = document.getElementById('liturgical-modal-desc');

    if (!modal || !title || !desc) return;

    title.textContent = liturgicalName;

    // 정확히 일치하는 설명 찾기 또는 부분 일치
    let description = LITURGICAL_INFO[liturgicalName];
    if (!description) {
        // 부분 일치 시도
        for (const key of Object.keys(LITURGICAL_INFO)) {
            if (liturgicalName.includes(key) || key.includes(liturgicalName)) {
                description = LITURGICAL_INFO[key];
                break;
            }
        }
    }

    desc.textContent = description || "이 절기에 대한 설명이 아직 준비되지 않았습니다.";
    modal.classList.add('visible');
}

/**
 * 절기 설명 모달 닫기
 */
function closeLiturgicalModal() {
    const modal = document.getElementById('liturgical-modal');
    if (modal) {
        modal.classList.remove('visible');
    }
}

// ============================================
// Sample Data (Fallback)
// ============================================

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
            { text: "וּמָחָה", sound: "우마하", lemma: "מָחָה", morph: "접속사 + 동사 칼 완료 3남단", gloss: "그리고 닦으실 것이다" },
            { text: "אֲדֹנָי", sound: "아도나이", lemma: "אֲדֹנָי", morph: "고유명사", gloss: "주" },
            { text: "יְהוִה", sound: "야훼", lemma: "יהוה", morph: "고유명사", gloss: "여호와" },
            { text: "דִּמְעָה", sound: "딤아", lemma: "דִּמְעָה", morph: "명사 여성 단수", gloss: "눈물을" },
            { text: "מֵעַל", sound: "메알", lemma: "עַל", morph: "전치사", gloss: "~위로부터" },
            { text: "כָּל־פָּנִים", sound: "콜-파님", lemma: "פָּנִים", morph: "명사 남성 복수", gloss: "모든 얼굴" }
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
            { text: "ἐν", sound: "엔", lemma: "ἐν", morph: "전치사 (여격 지배)", gloss: "~안에" },
            { text: "τούτῳ", sound: "투토", lemma: "οὗτος", morph: "지시대명사 여격 중성 단수", gloss: "이것에/이로써" },
            { text: "ἐφανερώθη", sound: "에파네로떼", lemma: "φανερόω", morph: "동사 부정과거 수동태 3단", gloss: "나타났다" },
            { text: "ἡ", sound: "헤", lemma: "ὁ", morph: "관사 주격 여성 단수", gloss: "그" },
            { text: "ἀγάπη", sound: "아가페", lemma: "ἀγάπη", morph: "명사 주격 여성 단수", gloss: "사랑이" },
            { text: "τοῦ", sound: "투", lemma: "ὁ", morph: "관사 소유격 남성 단수", gloss: "그" },
            { text: "θεοῦ", sound: "테우", lemma: "θεός", morph: "명사 소유격 남성 단수", gloss: "하나님의" },
            { text: "ἐν", sound: "엔", lemma: "ἐν", morph: "전치사", gloss: "~안에/에게" },
            { text: "ἡμῖν", sound: "헤민", lemma: "ἐγώ", morph: "인칭대명사 여격 1복수", gloss: "우리" }
        ]
    },
    meditation: {
        content: "죽음은 결코 우리 삶의 허무한 종착역이 아니며, 영원한 안식과 생명으로 들어가는 새로운 문입니다. 주님께서 친히 우리의 모든 눈물을 닦아주실 때, 우리가 흘렸던 슬픔은 영원한 찬송이 되고, 깊은 절망의 밤은 찬란한 부활의 소망으로 변화됩니다. 이 거룩한 생명의 약속은 오늘 우리가 마주한 고난과 시련을 넉넉히 이길 힘을 주며, 유한하고 덧없는 세상 속에서도 변치 않는 영원의 가치를 발견하게 합니다.",
        question: "오늘 당신의 삶에서 '죽음을 삼키는 생명'의 능력을 경험해야 할 영역은 무엇입니까?"
    }
};

// ============================================
// State
// ============================================

let dailyData = null;

// ============================================
// User Preferences (Settings)
// ============================================

const SETTINGS_KEY = 'kerygma-daily-settings';

// Default settings
const DEFAULT_SETTINGS = {
    theme: 'auto',      // 'auto', 'light', 'dark'
    fontSize: 1.6       // rem value for original text
};

/**
 * 설정 로드 (localStorage)
 */
function loadSettings() {
    try {
        const saved = localStorage.getItem(SETTINGS_KEY);
        return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch {
        return DEFAULT_SETTINGS;
    }
}

/**
 * 설정 저장 (localStorage)
 */
function saveSettings(settings) {
    try {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    } catch (e) {
        console.warn('설정 저장 실패:', e);
    }
}

/**
 * 테마 설정
 */
function setTheme(theme) {
    const root = document.documentElement;

    // Remove existing theme classes
    root.classList.remove('light-mode', 'dark-mode');

    // Apply new theme
    if (theme === 'light') {
        root.classList.add('light-mode');
    } else if (theme === 'dark') {
        root.classList.add('dark-mode');
    }
    // 'auto' = no class, system preference applies

    // Update button states
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });

    // Save setting
    const settings = loadSettings();
    settings.theme = theme;
    saveSettings(settings);
}

/**
 * 폰트 크기 설정
 */
function setFontSize(size) {
    const sizeNum = parseFloat(size);

    // Apply to CSS variable
    document.documentElement.style.setProperty('--original-font-size', `${sizeNum}rem`);

    // Update display
    const valueDisplay = document.getElementById('font-size-value');
    if (valueDisplay) {
        valueDisplay.textContent = `${sizeNum.toFixed(1)}rem`;
    }

    // Update preview
    const preview = document.getElementById('font-preview-text');
    if (preview) {
        preview.style.fontSize = `${sizeNum}rem`;
    }

    // Update slider
    const slider = document.getElementById('font-size-slider');
    if (slider && slider.value !== size) {
        slider.value = sizeNum;
    }

    // Save setting
    const settings = loadSettings();
    settings.fontSize = sizeNum;
    saveSettings(settings);
}

/**
 * 설정 패널 열기/닫기
 */
function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    const overlay = document.getElementById('settings-overlay');
    const isVisible = panel.classList.contains('visible');

    if (isVisible) {
        closeSettings();
    } else {
        panel.classList.add('visible');
        overlay.classList.add('visible');
    }
}

function closeSettings() {
    document.getElementById('settings-panel').classList.remove('visible');
    document.getElementById('settings-overlay').classList.remove('visible');
}

/**
 * 설정 초기화 (앱 시작 시)
 */
function initSettings() {
    const settings = loadSettings();

    // Apply theme
    setTheme(settings.theme);

    // Apply font size
    setFontSize(settings.fontSize);

    // Update slider value
    const slider = document.getElementById('font-size-slider');
    if (slider) {
        slider.value = settings.fontSize;
    }
}

// ============================================
// Main Functions
// ============================================

/**
 * 앱 초기화
 */
async function init() {
    initSettings();
    updateDateDisplay();
    await loadTodayData();
    registerServiceWorker();
}

/**
 * 날짜 표시 업데이트
 */
function updateDateDisplay() {
    const now = new Date();
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    };
    let dateStr = now.toLocaleDateString(CONFIG.DATE_LOCALE, options);
    // User Request: Improve display from '일요일' to '주일'
    dateStr = dateStr.replace('일요일', '주일');
    document.getElementById('date-display').textContent = dateStr;
}

/**
 * 오늘의 데이터 로드
 */
async function loadTodayData() {
    const mainContent = document.getElementById('main-content');

    // 1. Show Skeleton Loading
    mainContent.innerHTML = '';
    const skeletonTemplate = document.getElementById('skeleton-template');
    if (skeletonTemplate) {
        mainContent.appendChild(skeletonTemplate.content.cloneNode(true));
    }

    try {
        const today = new Date();
        // Fix: toISOString() uses UTC. We need local date (KST).
        // Construct YYYY-MM-DD using local components.
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const dateKey = `${year}-${month}-${day}`;

        if (CONFIG.DATA_SOURCE === 'json') {
            // JSON 파일에서 로드
            const yearMonth = dateKey.substring(0, 7); // YYYY-MM
            const jsonUrl = `${CONFIG.DATA_PATH}/${yearMonth}.json`;

            const response = await fetch(jsonUrl);
            if (!response.ok) {
                console.warn(`${yearMonth}.json 없음, 샘플 데이터 사용`);
                dailyData = SAMPLE_DATA;
            } else {
                const monthData = await response.json();
                // 날짜 키로 오늘 데이터 찾기
                dailyData = monthData[dateKey] || SAMPLE_DATA;

                if (!monthData[dateKey]) {
                    console.warn(`${dateKey} 데이터 없음, 샘플 데이터 사용`);
                }
            }
        } else if (CONFIG.DATA_SOURCE === 'api' && CONFIG.SHEETS_API_URL) {
            // Google Sheets API에서 데이터 가져오기
            const response = await fetch(CONFIG.SHEETS_API_URL);
            if (!response.ok) throw new Error('API 응답 오류');
            dailyData = await response.json();
        } else {
            // Fallback: 샘플 데이터
            dailyData = SAMPLE_DATA;
        }

        renderContent(dailyData);

    } catch (error) {
        console.error('데이터 로딩 실패:', error);
        showError();
    }
}

/**
 * 콘텐츠 렌더링
 */
function renderContent(data) {
    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = '';

    // Liturgical Day Display (separated with pipe)
    const liturgicalDisplay = document.getElementById('liturgical-display');
    if (data.liturgical && liturgicalDisplay) {
        liturgicalDisplay.innerHTML = `<span class="liturgical-badge" onclick="showLiturgicalInfo('${data.liturgical}')">${data.liturgical}</span>`;
        liturgicalDisplay.classList.add('visible');
    }

    // OT 카드
    const otCard = createVerseCard(data.ot, 'ot', '구약');
    mainContent.appendChild(otCard);

    // NT 카드
    const ntCard = createVerseCard(data.nt, 'nt', '신약');
    mainContent.appendChild(ntCard);

    // 묵상 섹션
    if (data.meditation) {
        const medSection = document.getElementById('meditation-section');
        document.getElementById('meditation-content').textContent = data.meditation.content;
        document.getElementById('question-text').textContent = data.meditation.question;
        medSection.style.display = 'block';
    }
}

/**
 * 성경 카드 생성
 */
function createVerseCard(verseData, cardId, label) {
    const template = document.getElementById('verse-card-template');
    const card = template.content.cloneNode(true);

    // 헤더
    card.querySelector('.verse-ref').textContent = verseData.ref;
    card.querySelector('.verse-label').textContent = label;

    // 원어 텍스트
    const originalText = card.querySelector('.original-text');
    originalText.classList.add(verseData.lang_class);
    originalText.setAttribute('dir', verseData.text_dir);

    verseData.words.forEach((word, idx) => {
        const wordBlock = document.createElement('div');
        wordBlock.className = 'word-block';
        wordBlock.onclick = () => showWordInfo(cardId, idx);
        wordBlock.innerHTML = `
            <span class="word-text">${word.text}</span>
            <span class="word-sound">${word.sound}</span>
        `;
        originalText.appendChild(wordBlock);
    });

    // 번역
    card.querySelector('.std-trans').textContent = verseData.kor_std;
    card.querySelector('.eng-text').textContent = verseData.eng_bsb;
    card.querySelector('.lit-text').textContent = verseData.kor_lit;

    return card;
}

/**
 * 단어 정보 표시
 */
function showWordInfo(cardId, wordIdx) {
    const verseData = cardId === 'ot' ? dailyData.ot : dailyData.nt;
    const word = verseData.words[wordIdx];

    document.getElementById('p-word').textContent = word.text;
    document.getElementById('p-sound').textContent = `[${word.sound}]`;
    document.getElementById('p-lemma').textContent = `기본형: ${word.lemma}`;
    document.getElementById('p-morph').textContent = word.morph;
    document.getElementById('p-gloss').textContent = word.gloss;

    // 폰트 설정
    const wordEl = document.getElementById('p-word');
    const isHebrew = verseData.lang === 'hebrew';
    wordEl.style.fontFamily = isHebrew ? "'SBL Hebrew', serif" : "'SBL Greek', serif";
    wordEl.style.direction = isHebrew ? 'rtl' : 'ltr';

    document.getElementById('parsing-panel').classList.add('visible');
}

/**
 * 파싱 패널 숨기기
 */
function hideParsing() {
    document.getElementById('parsing-panel').classList.remove('visible');
}

/**
 * 에러 표시
 */
function showError() {
    document.getElementById('main-content').innerHTML = '';
    document.getElementById('error-state').style.display = 'block';
}

// ============================================
// Share Feature
// ============================================

/**
 * 묵상 공유하기
 * Web Share API (Mobile) -> Clipboard (Desktop) Fallback
 */
async function handleShare() {
    if (!dailyData || !dailyData.meditation) return;

    const date = document.getElementById('date-display').textContent;
    const title = dailyData.meditation.title || "오늘의 묵상";
    const content = dailyData.meditation.content;
    const question = dailyData.meditation.question;
    const url = "https://kdbm.netlify.app/";

    const shareText = `[케리그마 매일 묵상] ${date}\n\n<${title}>\n\n${content}\n\n<성찰 질문>\n${question}\n\n${url}`;

    // 1. Web Share API (Mobile)
    if (navigator.share) {
        try {
            await navigator.share({
                title: '케리그마 매일 묵상',
                text: shareText,
                url: url
            });
            console.log('공유 성공');
        } catch (err) {
            console.log('공유 취소 또는 에러:', err);
        }
    }
    // 2. Clipboard Fallback (Desktop / Unsupported)
    else {
        try {
            await navigator.clipboard.writeText(shareText);
            showToast("클립보드에 복사되었습니다");
        } catch (err) {
            console.error('클립보드 복사 실패:', err);
            showToast("복사에 실패했습니다");
        }
    }
}

/**
 * 토스트 메시지 표시
 */
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('visible');

    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

/**
 * Service Worker 등록 (PWA)
 */
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js')
            .then(reg => console.log('SW registered'))
            .catch(err => console.log('SW registration failed:', err));
    }
}

// ============================================
// Event Listeners
// ============================================

// 배경 클릭 시 파싱 패널 닫기 (이벤트 위임 최적화)
document.addEventListener('click', (e) => {
    const panel = document.getElementById('parsing-panel');
    const isPanelVisible = panel.classList.contains('visible');

    // 패널이 열려있고, 패널 외부를 클릭했고, 워드 블록을 클릭한 게 아니라면 닫기
    if (isPanelVisible &&
        !panel.contains(e.target) &&
        !e.target.closest('.word-block')) {
        hideParsing();
    }
});

// 키보드 ESC로 패널 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        hideParsing();
        closeSettings();
        closeLiturgicalModal();
    }
});

// ============================================
// Swipe Gesture (Mobile)
// ============================================

let touchStartY = 0;
let touchEndY = 0;
const parsingPanel = document.getElementById('parsing-panel');

if (parsingPanel) {
    // 핸들 바 추가 (시각적 힌트)
    const handleBar = document.createElement('div');
    handleBar.style.cssText = `
        width: 40px;
        height: 5px;
        background: rgba(0,0,0,0.2);
        border-radius: 3px;
        margin: -10px auto 20px;
        cursor: grab;
    `;
    parsingPanel.insertBefore(handleBar, parsingPanel.firstChild);

    parsingPanel.addEventListener('touchstart', (e) => {
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    parsingPanel.addEventListener('touchend', (e) => {
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }, { passive: true });
}

function handleSwipe() {
    const swipeThreshold = 50; // 50px 이상 아래로 스와이프 시 닫기
    const swipeDistance = touchEndY - touchStartY;

    if (swipeDistance > swipeThreshold) {
        hideParsing();
    }
}

// 앱 시작
document.addEventListener('DOMContentLoaded', init);
