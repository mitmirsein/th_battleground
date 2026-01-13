/**
 * Eden Gardener - Creature System
 * Manages 365 creatures assets and unlock states
 */

// ============================================
// Creature Database (365 Species)
// ============================================

// Base list of defined creature types (from EMOJI_LIST.md)
const definedCreatures = [
    // 1-20
    { id: 'mustard', nameKo: '겨자씨', emoji: '🌱', ref: '마태복음 13:31' },
    { id: 'dove', nameKo: '비둘기', emoji: '🕊️', ref: '창세기 8:11' },
    { id: 'grape', nameKo: '포도나무', emoji: '🍇', ref: '요한복음 15:5' },
    { id: 'lamb', nameKo: '어린양', emoji: '🐑', ref: '요한복음 1:29' },
    { id: 'olive', nameKo: '올리브', emoji: '🫒', ref: '로마서 11:17' },
    { id: 'fish', nameKo: '물고기', emoji: '🐟', ref: '마태복음 4:19' },
    { id: 'fig', nameKo: '무화과', emoji: '🌳', ref: '마가복음 11:13' },
    { id: 'eagle', nameKo: '독수리', emoji: '🦅', ref: '이사야 40:31' },
    { id: 'lily', nameKo: '백합', emoji: '🌷', ref: '마태복음 6:28' },
    { id: 'lion', nameKo: '사자', emoji: '🦁', ref: '요한계시록 5:5' },
    { id: 'palm', nameKo: '종려나무', emoji: '🌴', ref: '요한복음 12:13' },
    { id: 'raven', nameKo: '까마귀', emoji: '🐦‍⬛', ref: '열왕기상 17:6' },
    { id: 'wheat', nameKo: '밀', emoji: '🌾', ref: '마태복음 13:24' },
    { id: 'donkey', nameKo: '나귀', emoji: '🫏', ref: '마태복음 21:5' },
    { id: 'hyssop', nameKo: '히솝', emoji: '🌿', ref: '출애굽기 12:22' },
    { id: 'camel', nameKo: '낙타', emoji: '🐪', ref: '마태복음 19:24' },
    { id: 'rose', nameKo: '장미', emoji: '🌹', ref: '아가서 2:1' },
    { id: 'chicken', nameKo: '닭', emoji: '🐔', ref: '마태복음 26:34' },
    { id: 'pomegranate', nameKo: '석류', emoji: '🍎', ref: '아가서 4:3' },
    { id: 'ox', nameKo: '소', emoji: '🐂', ref: '누가복음 14:19' },

    // 21-40
    { id: 'acacia', nameKo: '아카시아', emoji: '🌳', ref: '출애굽기 25:10' },
    { id: 'snake', nameKo: '뱀', emoji: '🐍', ref: '민수기 21:8' },
    { id: 'cedar', nameKo: '백향목', emoji: '🌲', ref: '시편 92:12' },
    { id: 'goat', nameKo: '염소', emoji: '🐐', ref: '마태복음 25:33' },
    { id: 'walnut', nameKo: '호두나무', emoji: '🌰', ref: '아가서 6:11' },
    { id: 'wolf', nameKo: '늑대', emoji: '🐺', ref: '마태복음 7:15' },
    { id: 'cherry_blossom', nameKo: '벚꽃', emoji: '🌸', ref: '' },
    { id: 'bear', nameKo: '곰', emoji: '🐻', ref: '열왕기하 2:24' },
    { id: 'sunflower', nameKo: '해바라기', emoji: '🌻', ref: '' },
    { id: 'fox', nameKo: '여우', emoji: '🦊', ref: '누가복음 13:32' },
    { id: 'tulip', nameKo: '튤립', emoji: '🌷', ref: '' },
    { id: 'whale', nameKo: '고래', emoji: '🐋', ref: '요나 1:17' },
    { id: 'hibiscus', nameKo: '무궁화', emoji: '🌺', ref: '대한민국 국화' },
    { id: 'locust', nameKo: '메뚜기', emoji: '🦗', ref: '마태복음 3:4' },
    { id: 'dandelion', nameKo: '민들레', emoji: '🌼', ref: '' },
    { id: 'frog', nameKo: '개구리', emoji: '🐸', ref: '출애굽기 8:3' },
    { id: 'lotus', nameKo: '연꽃', emoji: '🪷', ref: '' },
    { id: 'crocodile', nameKo: '악어', emoji: '🐊', ref: '에스겔 29:3' },
    { id: 'bamboo', nameKo: '대나무', emoji: '🎋', ref: '' },
    { id: 'monkey', nameKo: '원숭이', emoji: '🐵', ref: '열왕기상 10:22' },

    // 41-60
    { id: 'mushroom', nameKo: '버섯', emoji: '🍄', ref: '' },
    { id: 'dog', nameKo: '강아지', emoji: '🐕', ref: '' },
    { id: 'pine', nameKo: '소나무', emoji: '🌲', ref: '' },
    { id: 'cat', nameKo: '고양이', emoji: '🐈', ref: '' },
    { id: 'tangerine', nameKo: '귤', emoji: '🍊', ref: '' },
    { id: 'rabbit', nameKo: '토끼', emoji: '🐇', ref: '' },
    { id: 'lemon', nameKo: '레몬', emoji: '🍋', ref: '' },
    { id: 'hamster', nameKo: '햄스터', emoji: '🐹', ref: '' },
    { id: 'watermelon', nameKo: '수박', emoji: '🍉', ref: '' },
    { id: 'mouse', nameKo: '생쥐', emoji: '🐭', ref: '' },
    { id: 'strawberry', nameKo: '딸기', emoji: '🍓', ref: '' },
    { id: 'squirrel', nameKo: '다람쥐', emoji: '🐿️', ref: '' },
    { id: 'clover', nameKo: '클로버', emoji: '🍀', ref: '삼위일체' },
    { id: 'hedgehog', nameKo: '고슴도치', emoji: '🦔', ref: '' },
    { id: 'cactus', nameKo: '선인장', emoji: '🌵', ref: '' },
    { id: 'bat', nameKo: '박쥐', emoji: '🦇', ref: '' },
    { id: 'maple', nameKo: '단풍', emoji: '🍁', ref: '' },
    { id: 'polar_bear', nameKo: '북극곰', emoji: '🐻‍❄️', ref: '' },
    { id: 'life_tree', nameKo: '생명나무', emoji: '🌳✨', ref: '요한계시록 22:2' }, // Special ID placeholder
    { id: 'dragon', nameKo: '드래곤', emoji: '🐉', ref: '' }
];

// Generate full 365 creature list
const creatures = {};

for (let i = 1; i <= 365; i++) {
    const isPlant = i % 2 !== 0; // Odd = Plant, Even = Animal
    let creatureData;

    // Last day special: Tree of Life
    if (i === 365) {
        creatureData = { id: 'lifeTree', nameKo: '생명나무', emoji: '🌳✨', ref: '요한계시록 22:2' };
    } else {
        // Cycle through defined list provided we have enough, otherwise reuse generic
        // Adjust index to map 1..60 correctly, reusing if we go over (but keeping plant/animal parity is tricky if list isn't perfectly alternating)
        // For simplicity, we just use modulo of the defined list length
        const index = (i - 1) % definedCreatures.length;
        creatureData = definedCreatures[index];
    }

    // Safety: Ensure generic fallback if Types don't alternate perfectly in defined list
    // (In our list above, we tried to alternate, but let's enforce type based on order to keep the system robust)
    const type = isPlant ? 'plant' : 'animal';

    // Override emoji/name if data missing or type mismatch (simple fallback)
    const baseId = creatureData ? creatureData.id : (isPlant ? `plant_${i}` : `animal_${i}`);
    const nameKo = creatureData ? creatureData.nameKo : (isPlant ? `이름없는 꽃 ${i}` : `이름없는 동물 ${i}`);
    const unlockedEmoji = creatureData ? creatureData.emoji : (isPlant ? '🌿' : '🐾');
    const scriptureRef = creatureData ? creatureData.ref : '';

    const mysteryEmoji = isPlant ? '🌰' : '🥚';

    // Use unique ID for each order to prevent overwriting in the map
    const uniqueId = `creature_${i}`;

    // Store in map
    creatures[uniqueId] = {
        id: baseId, // Semantic ID (e.g. 'mustard')
        nameKo: nameKo,
        type: type,
        unlockOrder: i,
        scriptureRef: scriptureRef,
        defaultEmoji: unlockedEmoji,
        mysteryEmoji: mysteryEmoji
    };
}

// ============================================
// Helper Functions
// ============================================

// Get emoji based on unlock state (simplified logic)
// 1 = Locked/Mystery, 2 = Unlocked
function getCreatureEmoji(uniqueId, state) {
    const c = typeof uniqueId === 'object' ? uniqueId : creatures[uniqueId];
    if (!c) return '❓';

    if (state === 1) return c.mysteryEmoji; // Before completion (Mystery)
    return c.defaultEmoji;                  // After completion (Unlocked)
}

function getUnlockedCreatures(completionCount) {
    return Object.values(creatures)
        .filter(c => c.unlockOrder <= completionCount)
        .sort((a, b) => a.unlockOrder - b.unlockOrder);
}

// ============================================
// Export
// ============================================

window.EdenCreatures = {
    creatures,
    getCreatureEmoji,
    getUnlockedCreatures
};
