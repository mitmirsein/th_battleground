/**
 * Eden Gardener - Main Application
 * Prototype v1.0
 */

// ============================================
// State Management
// ============================================

const state = {
    avatar: null,  // 'adam' or 'eve'
    currentScreen: 'screen-intro',
    day: 1,
    currentTab: 'ot',
    plantCared: false,
    animalCared: false,
    prayerWritten: false,
    isFirstDay: true
};

// Avatar display names
const avatarData = {
    adam: {
        name: '아담',
        icon: '🧔',
        title: '흙의 아들'
    },
    eve: {
        name: '이브',
        icon: '👩',
        title: '생명의 딸'
    }
};

// ============================================
// Screen Navigation
// ============================================

function goToScreen(screenId) {
    // Remove active from current screen
    const currentScreen = document.querySelector('.screen.active');
    if (currentScreen) {
        currentScreen.classList.remove('active');
    }

    // Add active to new screen
    const newScreen = document.getElementById(screenId);
    if (newScreen) {
        // Small delay for transition effect
        setTimeout(() => {
            newScreen.classList.add('active');
            state.currentScreen = screenId;

            // Update avatar icons if needed
            updateAvatarDisplays();

            // Load daily content if on daily screen
            if (screenId === 'screen-daily') {
                loadDailyContent();
            }

            // Update garden view with SVG creatures
            if (screenId === 'screen-garden') {
                updateGardenView();
            }
        }, 50);
    }
}


// ============================================
// Avatar Selection
// ============================================

function selectAvatar(avatarType) {
    state.avatar = avatarType;

    // Update UI - remove selected from all cards
    document.querySelectorAll('.avatar-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selected to clicked card
    const target = event.currentTarget || event.target.closest('.avatar-card');
    if (target) target.classList.add('selected');

    // Enable the next button
    const nextBtn = document.getElementById('btn-avatar-next');
    if (nextBtn) nextBtn.classList.remove('btn-disabled');
}

async function completeAvatarSelection() {
    if (!state.avatar) return;

    // Save profile to DB
    if (window.EdenDB) {
        await window.EdenDB.saveProfile({
            avatar: state.avatar,
            startDate: window.EdenDB.getTodayDate()
        });
    }

    state.isFirstDay = true;
    goToScreen('screen-garment');
}

async function confirmPledge() {
    if (state.isFirstDay) {
        goToScreen('screen-seed');
    } else {
        goToScreen('screen-daily');
    }
}

function updateAvatarDisplays() {
    if (!state.avatar) return;

    const data = avatarData[state.avatar];

    // Update all avatar icon displays
    const iconElements = [
        'pledge-avatar-icon',
        'seed-avatar-icon',
        'complete-avatar-icon',
        'garden-avatar-icon'
    ];

    iconElements.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = data.icon;
    });

    // Update pledge name
    const pledgeName = document.getElementById('pledge-name');
    if (pledgeName) pledgeName.textContent = data.name;

    // Update pledge Josa (Subject particle)
    const pledgeJosa = document.getElementById('pledge-josa');
    if (pledgeJosa) {
        // '아담' ends with consonant -> '은'
        // '이브' ends with vowel -> '는'
        pledgeJosa.textContent = (state.avatar === 'adam') ? '은' : '는';
    }

    // Update gardener title
    const gardenerTitle = document.getElementById('gardener-title');
    if (gardenerTitle) gardenerTitle.textContent = data.title;
}

// ============================================
// Seed Planting Animation
// ============================================

function plantSeed() {
    const btn = event.currentTarget;
    btn.disabled = true;
    btn.textContent = '💧 물 주는 중...';

    // Simulate watering animation
    setTimeout(() => {
        goToScreen('screen-complete');

        // Animate progress bar after screen loads
        setTimeout(() => {
            const progressFill = document.querySelector('#screen-complete .progress-fill');
            if (progressFill) {
                progressFill.style.width = '0.3%';
            }
        }, 500);
    }, 1500);
}

// ============================================
// Daily Loop Functions
// ============================================

function loadDailyContent() {
    // Get today's devotional from data module
    const devotional = window.EdenData ? window.EdenData.getTodayDevotional() : null;
    if (!devotional) {
        console.warn('No devotional data available');
        return;
    }

    // Update day counter with date and weekday
    const dayCounter = document.getElementById('daily-day-counter');
    if (dayCounter) {
        const today = new Date();
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const month = today.getMonth() + 1;
        const date = today.getDate();
        const weekday = weekdays[today.getDay()];
        dayCounter.textContent = `Day ${state.day || 1} · ${month}/${date}(${weekday})`;
    }

    // Load OT by default
    loadScripture('ot', devotional);

    // Load meditation text (not question)
    const meditationEl = document.getElementById('meditation-question');
    if (meditationEl && devotional.meditation) {
        meditationEl.textContent = devotional.meditation.text || devotional.meditation.question || '';
    }

    // Reset care states for today (allows multiple waterings per day)
    state.plantCared = false;
    state.animalCared = false;

    // Preserve prayer state if prayer input already has content (cached or user-typed)
    const prayerInput = document.getElementById('prayer-input');
    if (prayerInput && prayerInput.value.length > 0) {
        state.prayerWritten = true;
    } else {
        state.prayerWritten = false;
    }

    updateCareUI();
}

function loadScripture(testament, devotional) {
    const data = devotional[testament];
    if (!data) return;

    state.currentTab = testament;

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event?.currentTarget?.classList.add('active') ||
        document.querySelector(`.tab-btn:${testament === 'ot' ? 'first' : 'last'}-child`)?.classList.add('active');

    // Update scripture content
    const refEl = document.getElementById('scripture-ref');
    const koreanEl = document.getElementById('scripture-korean');

    if (refEl) refEl.textContent = data.ref;
    if (koreanEl) koreanEl.textContent = data.kor_std;
}


function switchTab(testament) {
    const devotional = window.EdenData ? window.EdenData.getTodayDevotional() : null;
    if (devotional) {
        loadScripture(testament, devotional);
    }
}

function toggleParsing() {
    const panel = document.getElementById('parsing-panel');
    if (!panel) return;

    if (panel.classList.contains('hidden')) {
        // Show parsing
        panel.classList.remove('hidden');
        renderParsing(panel);
    } else {
        panel.classList.add('hidden');
    }
}

function renderParsing(panel) {
    if (!state.currentWords || state.currentWords.length === 0) {
        panel.innerHTML = '<p style="text-align:center;color:var(--color-text-muted);">분석 데이터가 없습니다.</p>';
        return;
    }

    const html = `
        <div class="word-parse">
            ${state.currentWords.map(word => `
                <div class="word-item">
                    <div class="word-text">${word.text}</div>
                    <div class="word-sound">${word.sound}</div>
                    <div class="word-lemma">${word.lemma} [${word.lemma_sound || ''}]</div>
                    <div class="word-gloss">${word.gloss}</div>
                </div>

            `).join('')}
        </div>
    `;
    panel.innerHTML = html;
}

// ============================================
// Prayer Input & Caching
// ============================================

function getTodayDateString() {
    const today = new Date();
    return `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
}

function setupPrayerInput() {
    const prayerInput = document.getElementById('prayer-input');
    const charCount = document.getElementById('prayer-char-count');

    if (prayerInput && charCount) {
        // 1. Restore cached prayer if it exists for today
        const todayKey = `eden_prayer_${getTodayDateString()}`;
        const cachedPrayer = localStorage.getItem(todayKey);

        if (cachedPrayer) {
            prayerInput.value = cachedPrayer;
            // Trigger input event logic manually
            const len = cachedPrayer.length;
            charCount.textContent = len;
            state.prayerWritten = len > 0;
            // We need to wait for DOM or call UI updates directly
            // Small timeout to ensure other UI elements are ready if called early
            setTimeout(() => {
                updateCareUI();
                updateCompleteButton();
            }, 0);
        }

        // 2. Add Input Listener with Auto-Save
        prayerInput.addEventListener('input', () => {
            const len = prayerInput.value.length;
            charCount.textContent = len;

            state.prayerWritten = len > 0;

            // Save to localStorage
            localStorage.setItem(todayKey, prayerInput.value);

            updateCareUI();  // Update care button lock state
            updateCompleteButton();
        });
    }
}

// ============================================
// Care Actions
// ============================================

// ============================================
// Sound Effects
// ============================================

const sounds = {
    water: new Audio('assets/sounds/watering.mp3'),
    success: new Audio('assets/sounds/success.mp3')
};

function playSound(name) {
    const audio = sounds[name];
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(e => console.log('Audio play failed (user interaction needed):', e));
    }
}

// ============================================
// Care Actions
// ============================================

function careForPlant() {
    // 1. Play Sound
    playSound('water');

    // 2. Create Visual Effects
    createWaterDroplets();

    // 3. Add Shake Animation to Care Card
    const card = document.getElementById('care-plant');
    if (card) {
        card.classList.add('shake-animation');
        setTimeout(() => card.classList.remove('shake-animation'), 500);
    }

    if (state.plantCared) return;

    state.plantCared = true;

    const btn = card.querySelector('.btn-care');

    if (card && btn) {
        card.classList.add('cared');
        btn.innerHTML = '✓';
        btn.classList.add('done');

        // Success sound on first care
        setTimeout(() => playSound('success'), 800);
    }

    updateCompleteButton();
}

// Water droplet animation
function createWaterDroplets() {
    const container = document.body;
    const dropletCount = 5 + Math.floor(Math.random() * 5); // More droplets (5-10)

    for (let i = 0; i < dropletCount; i++) {
        setTimeout(() => {
            const droplet = document.createElement('div');
            droplet.className = 'water-droplet';
            droplet.textContent = '💧';

            // Random position near center
            const randomX = 40 + (Math.random() * 20);
            droplet.style.left = `${randomX}%`;
            droplet.style.top = '40%'; // Start from middle

            droplet.style.animationDelay = '0s';
            container.appendChild(droplet);

            // Remove after animation
            setTimeout(() => droplet.remove(), 1200);
        }, i * 150);
    }
}

function careForAnimal() {
    // Create food animation on every click
    createFoodParticles();

    if (state.animalCared) return;

    state.animalCared = true;

    const careCard = document.getElementById('care-animal');
    const btn = careCard.querySelector('.btn-care');

    if (careCard && btn) {
        careCard.classList.add('cared');
        btn.innerHTML = '✓';
        btn.classList.add('done');

        // Success sound on first care
        setTimeout(() => playSound('success'), 800);
    }

    updateCompleteButton();
}

// Food particle animation
function createFoodParticles() {
    const container = document.body;
    const foods = ['🌾', '🌿', '🍃', '✨'];
    const particleCount = 3 + Math.floor(Math.random() * 3); // 3-5 particles

    for (let i = 0; i < particleCount; i++) {
        setTimeout(() => {
            const particle = document.createElement('div');
            particle.className = 'food-particle';
            particle.textContent = foods[Math.floor(Math.random() * foods.length)];
            particle.style.left = `${20 + Math.random() * 60}%`;
            particle.style.animationDelay = `${Math.random() * 0.2}s`;
            container.appendChild(particle);

            // Remove after animation
            setTimeout(() => particle.remove(), 1200);
        }, i * 100);
    }
}

async function updateCareUI() {
    const container = document.getElementById('today-creature-container');
    if (!container) return;

    const { creatures, getCreatureEmoji } = window.EdenCreatures || {};
    if (!creatures) return;

    // Get completion count (entries count)
    const entryCount = await window.EdenDB.getEntryCount();
    console.log('📊 Entry count for unlock check:', entryCount);
    state.day = entryCount || 1; // Sync global state

    // Check if today is already completed
    const today = window.EdenDB.getTodayDate();
    const todayEntry = await window.EdenDB.getEntry(today);
    const completedToday = !!todayEntry;
    console.log('📅 Today:', today, '| Completed:', completedToday);

    // Find next creature to unlock (key is creature_N)
    // If entryCount is 0, next unlock is creature_1
    // If entryCount is 1, creature_1 is unlocked, next is creature_2
    const nextCreatureKey = `creature_${entryCount + 1}`;
    const nextCreature = creatures[nextCreatureKey];
    console.log('🔓 Next creature to unlock:', nextCreatureKey, nextCreature?.nameKo);

    // Get all unlocked creatures (those with unlockOrder <= entryCount)
    const unlockedCreatures = Object.values(creatures)
        .filter(c => c.unlockOrder <= entryCount)
        .sort((a, b) => a.unlockOrder - b.unlockOrder);
    console.log('🌱 Unlocked creatures count:', unlockedCreatures.length);

    if (!completedToday && nextCreature) {
        // Before completion: Show mystery icon (no name, no scripture)
        const mysteryIcon = nextCreature.type === 'plant' ? '🌰' : '🥚';
        container.innerHTML = `
            <div class="creature-display mystery">
                <div class="creature-emoji-large">${mysteryIcon}</div>
                <div class="creature-hint">오늘의 묵상을 완료하면 해금됩니다</div>
            </div>
        `;
    } else if (completedToday && unlockedCreatures.length > 0) {
        // After completion: Reveal the creature!
        const lastCreature = unlockedCreatures[unlockedCreatures.length - 1];
        const emoji = getCreatureEmoji ? getCreatureEmoji(lastCreature, 2) : '🌱';
        console.log('🎉 Revealing creature:', lastCreature.nameKo);
        container.innerHTML = `
            <div class="new-creature-reveal">
                <div class="creature-emoji-large">${emoji}</div>
                <div class="creature-name">${lastCreature.nameKo}</div>
                <div class="creature-scripture">${lastCreature.scriptureRef}</div>
            </div>
        `;
    } else if (unlockedCreatures.length > 0) {
        // Already have creatures but no new one today (or already viewed)
        const lastCreature = unlockedCreatures[unlockedCreatures.length - 1];
        const emoji = getCreatureEmoji ? getCreatureEmoji(lastCreature, 2) : '🌱';
        container.innerHTML = `
            <div class="creature-display">
                <div class="creature-emoji-large">${emoji}</div>
                <div class="creature-name">${lastCreature.nameKo}</div>
            </div>
        `;
    } else {
        // First time ever - show mystery
        container.innerHTML = `
            <div class="creature-display mystery">
                <div class="creature-emoji-large">🌰</div>
                <div class="creature-hint">오늘의 묵상을 완료하면 해금됩니다</div>
            </div>
        `;
    }

    updateCompleteButton();
}



function updateCompleteButton() {
    const btn = document.getElementById('btn-complete-day');
    if (!btn) return;

    // Always enable (no more watering requirement)
    btn.classList.add('ready');
    btn.disabled = false;
}

async function completeDailyLoop() {
    console.log('🙏 Starting completeDailyLoop...');
    
    // Save prayer if written
    const prayerInput = document.getElementById('prayer-input');
    const prayer = prayerInput ? prayerInput.value : '';

    // Save to Database
    if (window.EdenDB) {
        const today = window.EdenDB.getTodayDate();
        console.log('📅 Today date:', today);

        // Check if today's entry already exists
        const existingEntry = await window.EdenDB.getEntry(today);
        const isFirstCareToday = !existingEntry;
        console.log('🔍 Is first care today?', isFirstCareToday);

        // Save entry (this now waits for transaction complete)
        await window.EdenDB.saveEntry({
            date: today,
            prayer: prayer,
            wordRead: true,
            completed: true
        });
        console.log('✅ Entry saved successfully');

        // Verify the save worked
        const newEntryCount = await window.EdenDB.getEntryCount();
        console.log('📊 New entry count after save:', newEntryCount);

        // On first completion, update care UI to reveal new creature
        if (isFirstCareToday) {
            console.log('🎉 First care today! Playing success sound...');
            playSound('success');
        }

        // Always refresh UI to ensure unlock state is shown
        await updateCareUI();
    }

    // Stay on daily screen (shows revealed creature)
}

// ============================================
// Demo Reset
// ============================================

async function resetDemo() {
    if (!confirm('동산을 초기화하고 처음부터 다시 시작할까요?')) return;

    // Clear Database
    if (window.EdenDB) {
        await window.EdenDB.clearAllData();
    }

    // Reset local state
    state.avatar = null;
    state.day = 1;
    state.plantCared = false;
    state.animalCared = false;
    state.prayerWritten = false;
    state.isFirstDay = true;

    // Reset UI
    document.querySelectorAll('.avatar-card').forEach(card => {
        card.classList.remove('selected');
    });

    const nextBtn = document.getElementById('btn-avatar-next');
    if (nextBtn) nextBtn.classList.add('btn-disabled');

    // Reset prayer input
    const prayerInput = document.getElementById('prayer-input');
    if (prayerInput) prayerInput.value = '';

    const charCount = document.getElementById('prayer-char-count');
    if (charCount) charCount.textContent = '0';

    // Go to intro
    goToScreen('screen-intro');
}

// ============================================
// Touch Feedback
// ============================================

function addTouchFeedback() {
    document.querySelectorAll('button, .avatar-card').forEach(el => {
        el.addEventListener('touchstart', () => {
            el.style.transform = 'scale(0.98)';
        });
        el.addEventListener('touchend', () => {
            el.style.transform = '';
        });
    });
}

// ============================================
// Prevent Pull-to-Refresh (PWA feel)
// ============================================

function preventPullToRefresh() {
    let lastTouchY = 0;

    document.addEventListener('touchstart', (e) => {
        lastTouchY = e.touches[0].clientY;
    }, { passive: true });

    document.addEventListener('touchmove', (e) => {
        const touchY = e.touches[0].clientY;
        const touchYDelta = touchY - lastTouchY;

        // Prevent pull-to-refresh at top of page
        if (window.scrollY === 0 && touchYDelta > 0) {
            e.preventDefault();
        }
    }, { passive: false });
}

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🌿 Eden Gardener - Prototype v1.2 - Prayer Cache Fix');

    // Initialize touch and input handlers for ALL users (new and returning)
    addTouchFeedback();
    preventPullToRefresh();
    setupPrayerInput();

    // Initialize database
    if (window.EdenDB) {
        try {
            await window.EdenDB.init();
            console.log('✅ Database initialized');

            // Check for existing profile
            const profile = await window.EdenDB.getProfile();
            if (profile) {
                console.log('👋 Welcome back,', profile.avatar);
                state.avatar = profile.avatar;
                state.day = window.EdenDB.getDayNumber(profile.startDate);
                state.isFirstDay = false;

                // Bypass onboarding - Go straight to Daily Ritual (Garment)
                updateAvatarDisplays();
                goToScreen('screen-garment');
                return;
            }
        } catch (e) {
            console.warn('⚠️ Database init or profile load failed:', e);
        }
    }

    // Ensure intro screen is active for new users
    goToScreen('screen-intro');
});

// ============================================
// Garden View with SVG Creatures
// ============================================

async function updateGardenView() {
    if (!window.EdenCreatures) {
        console.warn('Creatures module not loaded');
        return;
    }

    const { creatures, getStageInfo, getCreatureEmoji } = window.EdenCreatures;

    // Get real data from DB
    let currentDay = state.day || 1;
    let mustardStreak = 0;

    if (window.EdenDB) {
        const dbCreatures = await window.EdenDB.getAllCreatures();
        const mustard = dbCreatures.find(c => c.id === 'mustard');
        if (mustard) {
            mustardStreak = mustard.careStreak || 0;
        }
    }

    // Update mustard seed display
    const mustardCard = document.getElementById('garden-mustard');
    if (mustardCard) {
        const stageInfo = getStageInfo(creatures.mustard, mustardStreak);

        // Try to load SVG, fallback to emoji
        const iconSpan = mustardCard.querySelector('span');
        if (iconSpan) {
            const img = document.createElement('img');
            img.src = stageInfo.assetPath;
            img.alt = creatures.mustard.nameKo;
            img.className = 'creature-svg-small';
            img.onerror = () => {
                iconSpan.textContent = getCreatureEmoji('mustard', stageInfo.number);
            };
            img.onload = () => {
                iconSpan.textContent = '';
                iconSpan.appendChild(img);
            };
        }

        // Update status text
        const statusEl = document.getElementById('mustard-status');
        if (statusEl) {
            statusEl.textContent = stageInfo.name;
        }
    }

    // Update progress display
    const progressPercent = ((currentDay / 365) * 100).toFixed(1);
    const progressFill = document.getElementById('garden-progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progressPercent}%`;
    }

    const progressText = document.getElementById('garden-progress-percent');
    if (progressText) {
        progressText.textContent = `진행률: ${progressPercent}%`;
    }

    const dayCounterBadge = document.getElementById('garden-day-counter');
    if (dayCounterBadge) {
        dayCounterBadge.textContent = `Day ${currentDay} / 365`;
    }

    // Update next unlock preview
    updateNextUnlockPreview(currentDay);
}

function updateNextUnlockPreview(currentDay) {
    if (!window.EdenCreatures) return;

    const nextCreature = window.EdenCreatures.getNextUnlock(currentDay);
    if (!nextCreature) return;

    const doveCard = document.getElementById('garden-dove');
    if (doveCard && nextCreature.id === 'dove') {
        const unlockDayEl = doveCard.querySelector('.unlock-day');
        if (unlockDayEl) {
            const daysLeft = nextCreature.unlockDay - currentDay;
            unlockDayEl.textContent = daysLeft > 0 ? `${daysLeft}일 후` : '오늘!';
        }
    }
}

// ============================================
// Prayer Log Modal with Month Navigation
// ============================================

// Prayer log state
let prayerLogState = {
    entries: [],
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1  // 1-12
};

async function openPrayerLog() {
    const modal = document.getElementById('prayer-log-modal');
    const listContainer = document.getElementById('prayer-log-list');

    if (!modal || !listContainer) return;

    // Show loading state
    listContainer.innerHTML = '<p class="prayer-empty">불러오는 중...</p>';
    modal.classList.remove('hidden');

    // Reset to current month
    prayerLogState.currentYear = new Date().getFullYear();
    prayerLogState.currentMonth = new Date().getMonth() + 1;

    // Fetch all entries from database
    if (window.EdenDB) {
        try {
            prayerLogState.entries = await window.EdenDB.getAllEntries();
            renderPrayerLogMonth();
        } catch (e) {
            console.error('Failed to load prayer log:', e);
            listContainer.innerHTML = '<p class="prayer-empty">기도 일지를 불러오는데 실패했습니다.</p>';
        }
    }
}

function navigatePrayerMonth(delta) {
    prayerLogState.currentMonth += delta;

    // Handle year rollover
    if (prayerLogState.currentMonth > 12) {
        prayerLogState.currentMonth = 1;
        prayerLogState.currentYear++;
    } else if (prayerLogState.currentMonth < 1) {
        prayerLogState.currentMonth = 12;
        prayerLogState.currentYear--;
    }

    renderPrayerLogMonth();
}

function renderPrayerLogMonth() {
    const listContainer = document.getElementById('prayer-log-list');
    const monthLabel = document.getElementById('prayer-month-label');

    if (!listContainer) return;

    // Update month label
    if (monthLabel) {
        monthLabel.textContent = `${prayerLogState.currentYear}년 ${prayerLogState.currentMonth}월`;
    }

    // Filter entries for current month
    const filteredEntries = prayerLogState.entries.filter(entry => {
        const date = new Date(entry.date);
        return date.getFullYear() === prayerLogState.currentYear &&
            (date.getMonth() + 1) === prayerLogState.currentMonth;
    });

    if (filteredEntries.length === 0) {
        listContainer.innerHTML = '<p class="prayer-empty">이 달에는 기록된 기도가 없습니다. 🍂</p>';
        return;
    }

    // Sort by date descending within the month
    filteredEntries.sort((a, b) => new Date(b.date) - new Date(a.date));

    // Render entries
    const html = filteredEntries.map(entry => {
        const date = new Date(entry.date);
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const dateStr = `${date.getDate()}일 (${weekdays[date.getDay()]})`;
        const prayerText = entry.prayer || '(기도문 없음)';

        return `
            <div class="prayer-entry">
                <div class="prayer-date">${dateStr}</div>
                <div class="prayer-text">${escapeHtml(prayerText)}</div>
            </div>
        `;
    }).join('');

    listContainer.innerHTML = html;
}

function closePrayerLog() {
    const modal = document.getElementById('prayer-log-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Debug / Development
// ============================================

// Quick jump to any screen (for dev)
window.skipTo = function (screenId) {
    // Set a default avatar if not selected
    if (!state.avatar) {
        state.avatar = 'adam';
    }
    goToScreen(screenId);
};

// Dev: Simulate days passing
window.simulateDays = function (days) {
    state.day = Math.min(365, (state.day || 1) + days);
    state.careStreaks = state.careStreaks || {};
    state.careStreaks.mustard = (state.careStreaks.mustard || 0) + days;
    console.log(`📅 Simulated ${days} days. Now at Day ${state.day}`);
    updateGardenView();
};

console.log('💡 Dev tips:');
console.log('  - skipTo("screen-garden") to jump to garden');
console.log('  - simulateDays(30) to test growth stages');
