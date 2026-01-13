/**
 * Eden Gardener - Database Module
 * IndexedDB wrapper for persistent storage
 */

const DB_NAME = 'EdenGardenerDB';
const DB_VERSION = 1;

let db = null;

// ============================================
// Database Initialization
// ============================================

function initDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => {
            console.error('❌ Failed to open database');
            reject(request.error);
        };

        request.onsuccess = () => {
            db = request.result;
            console.log('✅ Database opened successfully');
            resolve(db);
        };

        request.onupgradeneeded = (event) => {
            const database = event.target.result;

            // User profile store
            if (!database.objectStoreNames.contains('profile')) {
                const profileStore = database.createObjectStore('profile', { keyPath: 'id' });
                console.log('📦 Created profile store');
            }

            // Daily entries store
            if (!database.objectStoreNames.contains('entries')) {
                const entriesStore = database.createObjectStore('entries', { keyPath: 'date' });
                entriesStore.createIndex('by_date', 'date', { unique: true });
                console.log('📦 Created entries store');
            }

            // Creatures store (unlock status, states)
            if (!database.objectStoreNames.contains('creatures')) {
                const creaturesStore = database.createObjectStore('creatures', { keyPath: 'id' });
                console.log('📦 Created creatures store');
            }
        };
    });
}

// ============================================
// Profile Operations
// ============================================

async function saveProfile(profile) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['profile'], 'readwrite');
        const store = transaction.objectStore('profile');

        const data = {
            id: 'user',
            avatar: profile.avatar,
            startDate: profile.startDate || getTodayDate(),
            createdAt: profile.createdAt || new Date().toISOString()
        };

        const request = store.put(data);
        request.onsuccess = () => resolve(data);
        request.onerror = () => reject(request.error);
    });
}

async function getProfile() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['profile'], 'readonly');
        const store = transaction.objectStore('profile');
        const request = store.get('user');

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
}

// ============================================
// Entry Operations
// ============================================

async function saveEntry(entry) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['entries'], 'readwrite');
        const store = transaction.objectStore('entries');

        const data = {
            date: entry.date,
            prayer: entry.prayer || '',
            wordRead: entry.wordRead || false,
            plantWatered: entry.plantWatered || null,
            animalFed: entry.animalFed || null,
            completed: entry.completed || true,
            createdAt: new Date().toISOString()
        };

        store.put(data);

        // Wait for TRANSACTION complete, not just request success
        // This ensures data is fully committed to disk
        transaction.oncomplete = () => {
            console.log('✅ Entry saved and committed:', data.date);
            resolve(data);
        };
        transaction.onerror = () => reject(transaction.error);
    });
}

async function getEntry(date) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['entries'], 'readonly');
        const store = transaction.objectStore('entries');
        const request = store.get(date);

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
}

async function getAllEntries() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['entries'], 'readonly');
        const store = transaction.objectStore('entries');
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result || []);
        request.onerror = () => reject(request.error);
    });
}

async function getEntryCount() {
    const entries = await getAllEntries();
    return entries.length;
}

// ============================================
// Creature Operations
// ============================================

async function unlockCreature(creatureId, type) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['creatures'], 'readwrite');
        const store = transaction.objectStore('creatures');

        const data = {
            id: creatureId,
            type: type, // 'plant' or 'animal'
            state: 'seed', // seed, sprout, growing, flourishing, golden
            unlockedAt: new Date().toISOString(),
            lastCaredAt: null,
            careStreak: 0
        };

        const request = store.put(data);
        request.onsuccess = () => resolve(data);
        request.onerror = () => reject(request.error);
    });
}

async function updateCreatureState(creatureId, state, careStreak) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['creatures'], 'readwrite');
        const store = transaction.objectStore('creatures');
        const getRequest = store.get(creatureId);

        getRequest.onsuccess = () => {
            const creature = getRequest.result;
            if (creature) {
                creature.state = state;
                creature.careStreak = careStreak;
                creature.lastCaredAt = new Date().toISOString();

                const putRequest = store.put(creature);
                putRequest.onsuccess = () => resolve(creature);
                putRequest.onerror = () => reject(putRequest.error);
            } else {
                reject(new Error('Creature not found'));
            }
        };
        getRequest.onerror = () => reject(getRequest.error);
    });
}

async function getAllCreatures() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['creatures'], 'readonly');
        const store = transaction.objectStore('creatures');
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result || []);
        request.onerror = () => reject(request.error);
    });
}

// ============================================
// Utility Functions
// ============================================

function getTodayDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function getDayNumber(startDate, currentDate = getTodayDate()) {
    const start = new Date(startDate);
    const current = new Date(currentDate);
    const diffTime = Math.abs(current - start);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays + 1; // Day 1 is the start day
}

async function clearAllData() {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['profile', 'entries', 'creatures'], 'readwrite');

        transaction.objectStore('profile').clear();
        transaction.objectStore('entries').clear();
        transaction.objectStore('creatures').clear();

        transaction.oncomplete = () => {
            console.log('🗑️ All data cleared');
            resolve();
        };
        transaction.onerror = () => reject(transaction.error);
    });
}

// ============================================
// Export/Import for Backup
// ============================================

async function exportData() {
    const profile = await getProfile();
    const entries = await getAllEntries();
    const creatures = await getAllCreatures();

    return {
        version: 1,
        exportedAt: new Date().toISOString(),
        profile,
        entries,
        creatures
    };
}

async function downloadBackup() {
    const data = await exportData();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `eden-gardener-backup-${getTodayDate()}.json`;
    a.click();

    URL.revokeObjectURL(url);
}

// Export for use in app.js
window.EdenDB = {
    init: initDB,
    saveProfile,
    getProfile,
    saveEntry,
    getEntry,
    getAllEntries,
    getEntryCount,
    unlockCreature,
    updateCreatureState,
    getAllCreatures,
    getTodayDate,
    getDayNumber,
    clearAllData,
    exportData,
    downloadBackup
};
