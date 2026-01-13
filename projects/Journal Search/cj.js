// Node.js v18+ (fetch 내장)

/**
 * ISSN 형식인지 확인합니다. (e.g., 1234-5678 or 1234567X)
 * @param {string} str - 확인할 문자열
 * @returns {boolean} ISSN 형식이면 true
 */
function isISSN(str) {
    return /^(\d{4}-?\d{3}[\dxX])$/.test(str.trim());
}

/**
 * ISSN으로 저널을 검색합니다.
 * @param {string} issn - 검색할 ISSN
 */
async function searchByIssn(issn) {
    const apiUrl = `https://api.crossref.org/journals/${issn}`;
    const response = await fetch(apiUrl);

    if (response.status === 404) {
        console.log(`ISSN '${issn}'에 해당하는 저널을 찾을 수 없습니다.`);
        return;
    }
    if (!response.ok) {
        throw new Error(`CrossRef API 오류: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (data.message && data.message.title) {
        const issnList = data.message.ISSN ? data.message.ISSN.join(", ") : issn;
        console.log(`✅ "${data.message.title}"`);
        console.log(`   ISSN: ${issnList}`);
    } else {
        console.log(`ISSN '${issn}'에 대한 정보를 찾을 수 없습니다.`);
    }
}

/**
 * 저널 제목으로 저널을 검색합니다.
 * @param {string} query - 검색할 저널 제목
 */
async function searchByTitle(query) {
    const apiUrl = `https://api.crossref.org/journals?query=${encodeURIComponent(query)}&rows=5`;
    const response = await fetch(apiUrl);

    if (!response.ok) {
        throw new Error(`CrossRef API 오류: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    if (!data.message.items || data.message.items.length === 0) {
        console.log(`'${query}'에 대한 검색 결과가 없습니다.`);
        return;
    }

    console.log(`'${query}'에 대한 검색 결과 (최대 5개):`);
    data.message.items.forEach(journal => {
        const issnText = (journal.ISSN && journal.ISSN.length > 0) ? `ISSN: ${journal.ISSN.join(", ")}` : "ISSN 정보 없음";
        console.log(`- "${journal.title}" (${issnText})`);
    });
}

(async () => {
    const input = process.argv.slice(2).join(" ").trim();
    if (!input) {
        console.log('사용법: node cj.js "저널 제목" 또는 <ISSN>');
        console.log('예시 1: node cj.js "Nature"');
        console.log('예시 2: node cj.js 0028-0836');
        return;
    }

    try {
        if (isISSN(input)) {
            const issn = input.length === 8 && !input.includes('-') ? `${input.slice(0, 4)}-${input.slice(4)}` : input;
            await searchByIssn(issn.toUpperCase());
        } else {
            await searchByTitle(input);
        }
    } catch (error) {
        console.error("오류가 발생했습니다:", error.message);
    }
})();
