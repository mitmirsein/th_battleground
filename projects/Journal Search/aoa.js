// Node.js v18+ (fetch 내장)

/**
 * ISSN 형식인지 확인합니다. (e.g., 1234-5678 or 1234567X)
 * @param {string} str - 확인할 문자열
 * @returns {boolean} ISSN 형식이면 true
 */
function isISSN(str) {
    if (!str) return false;
    return /^(\d{4}-?\d{3}[\dxX])$/.test(str.trim());
}

async function fetchArticles(issn, year) {
    const url = `https://api.crossref.org/journals/${issn}/works?filter=from-pub-date:${year}-01-01,until-pub-date:${year}-12-31&rows=100`;
    const response = await fetch(url);
    if (!response.ok) {
        console.error(`CrossRef API 오류: ${response.status} ${response.statusText}`);
        return [];
    }
    const data = await response.json();
    return data.message && data.message.items ? data.message.items : [];
}

function isOpenAccess(article) {
    // CrossRef의 license 필드가 있으면 OA로 간주
    return Array.isArray(article.license) && article.license.length > 0;
}

function getOAInfo(article) {
    if (!isOpenAccess(article)) return { oa: false };
    const license = article.license[0];
    return {
        oa: true,
        oa_url: license.URL || '',
        license_type: license['content-version'] || '',
        license_start: license.start ? license.start['date-parts'] : ''
    };
}

(async () => {
    const [issn, yearStr] = process.argv.slice(2);

    if (!issn || !yearStr) {
        console.log('사용법: node aoa.js <ISSN> <연도>');
        console.log('예시: node aoa.js 0044-2526 2023');
        return;
    }

    if (!isISSN(issn)) {
        console.error(`오류: 유효하지 않은 ISSN 형식입니다: ${issn}`);
        return;
    }

    const year = parseInt(yearStr, 10);
    if (isNaN(year) || yearStr.length !== 4) {
        console.error(`오류: 연도는 4자리 숫자로 입력해야 합니다: ${yearStr}`);
        return;
    }

    try {
        const articles = await fetchArticles(issn, year);
        if (articles.length === 0) {
            console.log(`'${issn}' 저널의 ${year}년도 논문 정보를 찾을 수 없습니다.`);
            return;
        }
        console.log(`'${issn}' 저널의 ${year}년도 논문 총 ${articles.length}편이 수집되었습니다. OA 정보:`);
        for (const art of articles) {
            const oaInfo = getOAInfo(art);
            console.log(`---`);
            console.log(`제목: ${art.title ? art.title[0] : "(제목없음)"}`);
            console.log(`DOI: ${art.DOI}`);
            console.log(`OA: ${oaInfo.oa ? "✅ Open Access" : "❌ No OA info"}`);
            if (oaInfo.oa) {
                console.log(`라이선스 URL: ${oaInfo.oa_url}`);
                console.log(`라이선스 타입: ${oaInfo.license_type}`);
                console.log(`라이선스 시작일: ${JSON.stringify(oaInfo.license_start)}`);
            }
        }
    } catch (error) {
        console.error("스크립트 실행 중 오류가 발생했습니다:", error.message);
    }
})();
