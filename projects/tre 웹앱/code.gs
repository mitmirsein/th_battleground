// Code.gs - 구글 앱스 스크립트 서버 코드

/**
 * 웹앱의 기본 HTML 페이지를 렌더링합니다.
 */
function doGet() {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('신학용어 & 저널 검색');
}

/**
 * [신학용어 검색] Th_terms 시트에서 데이터를 검색합니다.
 */
function searchThTerms(query, page = 1) {
  return searchSheet_({
    sheetName: 'Th_terms',
    query: query,
    page: page,
    pageSize: 50, // 한 페이지에 50개씩 표시
    sortLogic: null // 특별한 정렬 없음
  });
}

/**
 * [저널 검색] Journals 시트에서 데이터를 검색합니다.
 */
function searchJournals(query, page = 1) {
  return searchSheet_({
    sheetName: 'Journals',
    query: query,
    page: page,
    pageSize: 50,
    // 저널 약어(첫 열)가 정확히 일치하는 결과를 최상단으로 올리는 정렬 로직
    sortLogic: (results, searchQuery) => {
      results.sort((a, b) => {
        const aExactMatch = a[0] && a[0].toString().toLowerCase() === searchQuery;
        const bExactMatch = b[0] && b[0].toString().toLowerCase() === searchQuery;
        if (aExactMatch && !bExactMatch) return -1;
        if (!aExactMatch && bExactMatch) return 1;
        return 0;
      });
    }
  });
}

/**
 * [공통 로직] 실제 시트를 검색하는 핵심 함수
 * @param {object} options - 검색 옵션 객체
 */
function searchSheet_(options) {
  const { sheetName, query, page, pageSize, sortLogic } = options;

  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
    if (!sheet) {
      return { success: false, error: `${sheetName} 시트를 찾을 수 없습니다.` };
    }

    const startTime = new Date().getTime();
    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const totalRows = Math.max(0, sheet.getLastRow() - 1);

    // 검색어가 없는 경우, 최신 데이터 50개만 반환
    if (!query || query.trim() === '') {
      const startRow = Math.max(2, totalRows - 49);
      const numRows = Math.min(50, totalRows);
      const data = numRows > 0 ? sheet.getRange(startRow, 1, numRows, sheet.getLastColumn()).getValues() : [];
      return { success: true, headers, results: data, foundCount: data.length, currentPage: 1, totalPages: 1 };
    }

    // 검색어가 있는 경우, 배치 처리로 검색
    const searchQuery = query.toLowerCase().trim();
    const results = [];
    const batchSize = 1000; // 1000행씩 끊어서 처리
    const maxResults = 300; // 최대 300개까지만 찾음

    for (let startRow = 2; startRow <= sheet.getLastRow() && results.length < maxResults; startRow += batchSize) {
      if (new Date().getTime() - startTime > 25000) break; // 25초 이상 실행되면 중단

      const range = sheet.getRange(startRow, 1, Math.min(batchSize, sheet.getLastRow() - startRow + 1), sheet.getLastColumn());
      const batchValues = range.getValues();
      
      const batchResults = batchValues.filter(row => 
        row.some(cell => cell && cell.toString().toLowerCase().includes(searchQuery))
      );
      results.push(...batchResults);
    }

    // 제공된 정렬 로직이 있으면 실행
    if (sortLogic) {
      sortLogic(results, searchQuery);
    }
    
    // 페이징 처리
    const totalFound = results.length;
    const totalPages = Math.ceil(totalFound / pageSize);
    const startIndex = (page - 1) * pageSize;
    const pagedResults = results.slice(startIndex, startIndex + pageSize);

    return { success: true, headers, results: pagedResults, foundCount: totalFound, currentPage: page, totalPages };

  } catch (e) {
    Logger.log(e);
    return { success: false, error: '검색 중 오류가 발생했습니다: ' + e.message };
  }
}