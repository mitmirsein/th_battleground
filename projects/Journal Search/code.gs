/* ==================================================================

## Theology Journal Analyzer v2.1 (Simplified Analysis)

+ 헤더 구조 변경 적용
+ OA 자동 체크 + Analysis 시트 정량 리포트

================================================================== */

/* -------------------- 설정 (Configuration) -------------------- */

class Config {
  static get SHEET_NAMES() {
    return {
      JOURNALS: 'Journals',
      ARTICLES: 'Articles',
      ANALYSIS: 'Analysis',
      SETTINGS: 'Settings'
    };
  }

  static get API_SETTINGS() {
    return {
      BASE_URL: 'https://api.crossref.org',
      ROWS_PER_REQUEST: 200,  // 증가: 한 번에 더 많은 데이터 요청
      MAX_ARTICLES_PER_JOURNAL: 1000,  // 증가: 더 많은 논문 수집 가능
      RATE_LIMIT_DELAY: 300,  // 감소: API 호출 간격 단축 (1000ms → 300ms)
      MAX_RETRIES: 3,
      INITIAL_RETRY_DELAY: 1000,  // 감소: 재시도 지연 시간 단축
      BATCH_SIZE: 5,  // 증가: 한 번에 처리하는 저널 수 증가
      TRIGGER_DELAY_MS: 10000,  // 감소: 트리거 간격 단축 (20s → 10s)
      YEAR_DELAY_MS: 500,  // 감소: 연도별 처리 간격 단축 (1500ms → 500ms)
      TRANSLATION_BATCH_SIZE: 20,  // 증가: 번역 배치 크기 증가
      CONCURRENT_REQUESTS: 3,  // 새로 추가: 동시 요청 수
      CACHE_DURATION: 300000  // 새로 추가: 캐시 지속 시간 (5분)
    };
  }

  static get HEADERS() {
    // 변경된 헤더 순서
    return [
      '저널명', '논문명', '저자', '볼륨', '이슈', '페이지',
      '출판일', '키워드', '초록', '초록 (번역)', 'OA', 'DOI/링크'
    ];
  }

  static get COLUMNS() {
    // 변경된 헤더 순서에 따른 컬럼 인덱스 (1-based)
    return {
      JOURNALS: { SELECT: 1, NAME: 3, SOURCE: 5, ID: 6 },
      ARTICLES: {
        JOURNAL: 1, TITLE: 2, AUTHORS: 3, VOLUME: 4, ISSUE: 5, PAGE: 6,
        DATE: 7, KEYWORDS: 8, ABSTRACT: 9, TRANSLATED: 10, OA: 11, DOI: 12
      }
    };
  }

  static get USER_AGENT() {
    return 'TheologyJournalAnalyzer/2.1 (https://github.com/yourusername/repo; mailto:your-email@example.com)';
  }

  static get STATE_PROPERTY_KEY() { return 'JOB_STATE'; }
  static get LAST_RESULT_KEY() { return 'LAST_JOB_RESULT'; }
  static get PROGRESS_KEY() { return 'COLLECTION_PROGRESS'; }
  static get DEBUG_KEY() { return 'DEBUG_LOG'; }
  static get STATS_KEY() { return 'COLLECTION_STATS'; }
}

/* -------------------- 불용어 목록 (Stopwords) - 분석 기능 제거로 미사용되나 유지 -------------------- */
class Stopwords {
  static get ENGLISH() {
    return new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'don', 'should', 'now', 'use', 'uses', 'used', 'using', 'make', 'makes', 'made', 'making', 'also', 'however', 'therefore', 'thus', 'hence', 'although', 'though', 'unless', 'until', 'while', 'whereas', 'whether', 'which', 'who', 'whom', 'whose', 'what', 'when', 'where', 'abstract', 'article', 'paper', 'study', 'research', 'analysis', 'approach', 'method']);
  }
  static get GERMAN() {
    return new Set(['der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines', 'und', 'oder', 'aber', 'von', 'zu', 'im', 'am', 'um', 'auf', 'aus', 'bei', 'mit', 'nach', 'seit', 'vor', 'für', 'als', 'ist', 'sind', 'war', 'waren', 'wird', 'werden', 'wurde', 'wurden', 'hat', 'haben', 'hatte', 'hatten', 'sein', 'seine', 'seiner', 'seinem', 'seinen', 'ihr', 'ihre', 'ihrer', 'ihrem', 'ihren', 'sich', 'nicht', 'es', 'sie', 'er', 'wir', 'ich', 'du', 'uns', 'kann', 'können', 'konnte', 'konnten', 'muss', 'müssen', 'musste', 'mussten', 'soll', 'sollen', 'sollte', 'sollten', 'will', 'wollen', 'wollte', 'wollten', 'darf', 'dürfen', 'durfte', 'durften', 'mag', 'mögen', 'mochte', 'mochten', 'durch', 'über', 'unter', 'zwischen', 'gegen', 'ohne', 'bis', 'noch', 'schon', 'sehr', 'nur', 'auch', 'dann', 'wenn', 'weil', 'dass', 'wie', 'was', 'wer', 'wen', 'wem', 'wo', 'wohin', 'woher', 'artikel', 'beitrag', 'untersuchung', 'forschung', 'analyse', 'ansatz', 'methode']);
  }
  static get KOREAN() {
    return new Set(['의', '를', '을', '에', '와', '과', '이', '가', '은', '는', '에서', '으로', '로', '부터', '까지', '에게', '한테', '께', '와', '과', '하고', '이고', '이며', '및', '또는', '혹은', '그리고', '그러나', '하지만', '그런데', '그래서', '따라서', '그러므로', '때문에', '위해', '위하여', '대해', '대하여', '관해', '관하여', '통해', '통하여', '의해', '의하여', '있다', '있는', '있고', '있으며', '있어', '있을', '없다', '없는', '없고', '없으며', '하다', '하는', '하고', '하며', '하여', '한', '할', '함', '되다', '되는', '되고', '되며', '이다', '이고', '이며', '이어', '일', '것', '들', '등', '중', '내', '속', '안', '밖']);
  }

  static isStopword(word) {
    if (!word) return true;
    const lowerWord = word.toLowerCase();
    return this.ENGLISH.has(lowerWord) || this.GERMAN.has(lowerWord) || this.KOREAN.has(lowerWord);
  }
}

/* -------------------- 텍스트 분석 유틸리티 - 분석 기능 제거로 미사용되나 유지 -------------------- */
class TextAnalyzer {
  static extractMeaningfulWords(text) {
    if (!text) return [];
    text = text.toLowerCase().replace(/[^a-zA-Z0-9가-힣\s\-]/g, ' ');
    const words = text.split(/\s+/);
    const meaningfulWords = [];
    words.forEach(word => {
      word = word.trim();
      if (/[가-힣]/.test(word)) { if (word.length < 2) return; }
      else { if (word.length < 4) return; }
      if (/^\d+$/.test(word)) return;
      if (Stopwords.isStopword(word)) return;
      meaningfulWords.push(word);
    });
    return meaningfulWords;
  }
}

/* -------------------- 디버깅 및 통계 (Debug & Stats) -------------------- */

class Debug {
  static log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}`;
    console.log(logMessage);
    Logger.log(logMessage);
    
    if (['ERROR', 'DEBUG', 'WARN', 'SUCCESS'].includes(level)) {
      this.appendDebugLog(logMessage);
    }
  }

  static appendDebugLog(message) {
    try {
      const prop = PropertiesService.getScriptProperties();
      let logs = prop.getProperty(Config.DEBUG_KEY) || '';
      const logLines = logs.split('\n');
      if (logLines.length > 200) logs = logLines.slice(-150).join('\n');
      logs += '\n' + message;
      prop.setProperty(Config.DEBUG_KEY, logs);
    } catch (e) {
      console.log('Failed to append debug log: ' + e.toString());
    }
  }

  static getDebugLogs() {
    return PropertiesService.getScriptProperties().getProperty(Config.DEBUG_KEY) || 'No debug logs available';
  }

  static clearDebugLogs() {
    PropertiesService.getScriptProperties().deleteProperty(Config.DEBUG_KEY);
  }

  static updateProgress(message) {
    PropertiesService.getScriptProperties().setProperty(Config.PROGRESS_KEY, message);
    this.log(message, 'SUCCESS');
  }

  static updateStats(stats) {
    PropertiesService.getScriptProperties().setProperty(Config.STATS_KEY, JSON.stringify(stats));
  }

  static getStats() {
    const js = PropertiesService.getScriptProperties().getProperty(Config.STATS_KEY);
    return js ? JSON.parse(js) : null;
  }
}

/* -------------------- URL Builder Utility -------------------- */

class URLBuilder {
  static buildQueryString(params) {
    const pairs = [];
    for (const key in params) {
      if (params.hasOwnProperty(key) && params[key] !== null && params[key] !== undefined) {
        pairs.push(encodeURIComponent(key) + '=' + encodeURIComponent(params[key]));
      }
    }
    return pairs.join('&');
  }
}

/* -------------------- API 클라이언트 -------------------- */

class CrossRefClient {
  constructor() {
    this.baseDelay = Config.API_SETTINGS.RATE_LIMIT_DELAY;
    this.requestCount = 0;
    this.cache = new Map();
    this.lastRequestTime = 0;
  }

  // 캐시 키 생성
  getCacheKey(url) {
    return Utilities.base64Encode(url).substring(0, 50);
  }

  // 캐시에서 데이터 조회
  getFromCache(url) {
    const key = this.getCacheKey(url);
    const cached = this.cache.get(key);
    
    if (cached && (Date.now() - cached.timestamp) < Config.API_SETTINGS.CACHE_DURATION) {
      Debug.log(`Cache hit for: ${url}`, 'DEBUG');
      return cached.data;
    }
    
    return null;
  }

  // 캐시에 데이터 저장
  setCache(url, data) {
    const key = this.getCacheKey(url);
    this.cache.set(key, {
      data: data,
      timestamp: Date.now()
    });
    
    // 캐시 크기 제한 (최대 100개)
    if (this.cache.size > 100) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
  }

  // 적응형 지연 시간 계산
  getAdaptiveDelay() {
    const timeSinceLastRequest = Date.now() - this.lastRequestTime;
    const minDelay = this.baseDelay;
    
    // 마지막 요청으로부터 충분한 시간이 지났으면 지연 시간 단축
    if (timeSinceLastRequest > minDelay * 2) {
      return Math.max(100, minDelay / 2);
    }
    
    return minDelay;
  }

  fetchJson(url, attempt = 1) {
    // 캐시 확인
    const cached = this.getFromCache(url);
    if (cached) return cached;

    this.requestCount++;
    Debug.log(`API Request #${this.requestCount} (attempt ${attempt}): ${url}`, 'DEBUG');
    
    try {
      // 적응형 지연 시간 적용
      const delay = this.getAdaptiveDelay();
      if (delay > 0) Utilities.sleep(delay);
      this.lastRequestTime = Date.now();
      
      const options = {
        method: 'get',
        headers: { 
          'User-Agent': Config.USER_AGENT, 
          'Accept': 'application/json',
          'Accept-Encoding': 'gzip'  // 압축 요청으로 전송 속도 향상
        },
        muteHttpExceptions: true,
        followRedirects: true
      };
      
      const res = UrlFetchApp.fetch(url, options);
      const code = res.getResponseCode();
      const content = res.getContentText();
      
      Debug.log(`Response code: ${code}`, 'DEBUG');
      
      if (code === 200) {
        try {
          const json = JSON.parse(content);
          if (json && json.message) {
            const itemCount = json.message.items?.length || 0;
            const totalResults = json.message['total-results'] || 0;
            Debug.log(`Success: Found ${itemCount} items, Total available: ${totalResults}`, 'INFO');
            
            // 성공한 응답을 캐시에 저장
            this.setCache(url, json);
          }
          return json;
        } catch (parseError) {
          Debug.log(`JSON parse error: ${parseError.toString()}`, 'ERROR');
          return null;
        }
      } else if (code === 500 && attempt < Config.API_SETTINGS.MAX_RETRIES) {
        Debug.log(`Server error 500, retrying...`, 'WARN');
        Utilities.sleep(Config.API_SETTINGS.INITIAL_RETRY_DELAY * attempt);
        return this.fetchJson(url, attempt + 1);
      } else if (code === 429) {
        Debug.log(`Rate limited, waiting longer...`, 'WARN');
        Utilities.sleep(Math.min(30000, 5000 * attempt)); // 최대 30초로 제한
        if (attempt < Config.API_SETTINGS.MAX_RETRIES) return this.fetchJson(url, attempt + 1);
      } else {
        Debug.log(`HTTP ${code} error`, 'ERROR');
      }
      return null;
    } catch (e) {
      Debug.log(`Fetch error: ${e.toString()}`, 'ERROR');
      return null;
    }
  }

  // 병렬 요청 처리 (여러 URL을 동시에 처리)
  fetchMultiple(urls) {
    const results = [];
    const batchSize = Config.API_SETTINGS.CONCURRENT_REQUESTS;
    
    for (let i = 0; i < urls.length; i += batchSize) {
      const batch = urls.slice(i, i + batchSize);
      const batchResults = batch.map(url => this.fetchJson(url));
      results.push(...batchResults);
      
      // 배치 간 짧은 지연
      if (i + batchSize < urls.length) {
        Utilities.sleep(200);
      }
    }
    
    return results;
  }

  buildYearUrl({ issn, year, rows, offset = 0, cursor = null }) {
    issn = issn.trim().replace(/[^\d\-X]/gi, '');
    
    const params = {
      rows: rows,
      filter: `from-pub-date:${year}-01-01,until-pub-date:${year}-12-31`,
      sort: 'published',
      order: 'desc'
    };
    
    if (cursor) params.cursor = cursor;
    else if (offset > 0) params.offset = offset;
    
    const qs = URLBuilder.buildQueryString(params);
    return `${Config.API_SETTINGS.BASE_URL}/journals/${issn}/works?${qs}`;
  }
}

/* -------------------- 데이터 처리 -------------------- */

class DataProcessor {
  static extractFromCrossRef(item, journalName) {
    try {
      const doi = item.DOI || null;
      
      let title = 'N/A';
      if (item.title) {
        if (Array.isArray(item.title) && item.title.length > 0) title = item.title[0];
        else if (typeof item.title === 'string') title = item.title;
      }
      
      let authors = 'N/A';
      if (item.author && Array.isArray(item.author)) {
        authors = item.author.map(a => `${a.given || ''} ${a.family || ''}`.trim()).filter(Boolean).join(', ');
      }
      
      let pubDate = 'N/A';
      if (item.published) {
        if (item.published['date-parts'] && item.published['date-parts'][0]) {
          pubDate = item.published['date-parts'][0].map(p => String(p).padStart(2, '0')).join('-');
        } else if (item.published['date-time']) {
          pubDate = item.published['date-time'].split('T')[0];
        }
      }
      
      let keywords = '';
      if (item.subject && Array.isArray(item.subject)) keywords = item.subject.join(', ');
      
      const abstract = item.abstract ? Utils.cleanAbstract(item.abstract) : '';
      const oa = (item.license && item.license.length > 0) ? 'TRUE' : 'FALSE';
      
      return {
        // 변경된 헤더 순서에 맞춰 데이터 배열 생성
        row: [
          journalName, title, authors,
          item.volume || 'N/A',
          item.issue || 'N/A',
          item.page || 'N/A',
          pubDate,
          keywords,
          abstract, 
          '', // 초록 (번역)
          oa,
          doi ? `https://doi.org/${doi}` : 'N/A'
        ],
        id: doi
      };
    } catch (e) {
      Debug.log(`Error extracting data: ${e.toString()}`, 'ERROR');
      return null;
    }
  }

  static getIdIndex(sheet) {
    const set = new Set();
    if (sheet.getLastRow() < 2) return set;
    
    try {
      const doiColumn = Config.COLUMNS.ARTICLES.DOI;
      const lastRow = sheet.getLastRow();
      const batchSize = 1000;
      
      for (let startRow = 2; startRow <= lastRow; startRow += batchSize) {
        const numRows = Math.min(batchSize, lastRow - startRow + 1);
        const range = sheet.getRange(startRow, doiColumn, numRows, 1);
        range.getValues().forEach(([doi]) => {
          if (doi && typeof doi === 'string' && doi.startsWith('https://doi.org/'))
            set.add(doi.substring(16));
        });
      }
      
      Debug.log(`Loaded ${set.size} existing DOIs from sheet`, 'DEBUG');
    } catch (e) {
      Debug.log(`Error building ID index: ${e.toString()}`, 'ERROR');
    }
    return set;
  }

  static appendBatch(sheet, rows) {
    if (!rows || rows.length === 0) return;
    
    try {
      // 대용량 데이터 처리를 위한 배치 크기 최적화
      const maxBatchSize = 1000;
      
      if (rows.length <= maxBatchSize) {
        // 작은 배치는 한 번에 처리
        const startRow = sheet.getLastRow() + 1;
        sheet.getRange(startRow, 1, rows.length, Config.HEADERS.length).setValues(rows);
        Debug.log(`Appended ${rows.length} rows to ${sheet.getName()}`, 'SUCCESS');
      } else {
        // 큰 배치는 분할 처리
        let totalAppended = 0;
        for (let i = 0; i < rows.length; i += maxBatchSize) {
          const batch = rows.slice(i, i + maxBatchSize);
          const startRow = sheet.getLastRow() + 1;
          sheet.getRange(startRow, 1, batch.length, Config.HEADERS.length).setValues(batch);
          totalAppended += batch.length;
          
          // 대용량 처리 시 중간 저장
          if (i > 0 && i % (maxBatchSize * 3) === 0) {
            SpreadsheetApp.flush(); // 강제 저장
            Utilities.sleep(100); // 짧은 휴식
          }
        }
        Debug.log(`Appended ${totalAppended} rows to ${sheet.getName()} in batches`, 'SUCCESS');
      }
    } catch (e) {
      Debug.log(`Error appending batch: ${e.toString()}`, 'ERROR');
    }
  }
}

/* -------------------- 유틸리티 -------------------- */

class Utils {
  static ui() { return SpreadsheetApp.getUi(); }
  
  static toast(msg, sec = 5) {
    try { SpreadsheetApp.getActiveSpreadsheet().toast(msg, '진행', sec); }
    catch (e) { Debug.log(`Toast: ${msg}`, 'DEBUG'); }
  }
  
  static showAlert(msg, title = '알림') { this.ui().alert(title, msg, this.ui().ButtonSet.OK); }
  
  static cleanAbstract(text = '') {
    if (!text) return '';
    return text.replace(/<jats:.*?>/g, '').replace(/<\/jats:.*?>/g, '').replace(/<[^>]+>/g, ' ').replace(/\s\s+/g, ' ').trim();
  }
  
  static parseYearRange(input) {
    if (!input) return null;
    input = input.trim();
    const single = input.match(/^(\d{4})$/);
    if (single) return { startYear: single[1], endYear: single[1] };
    const range = input.match(/^(\d{4})-(\d{4})$/);
    if (range) {
      const start = parseInt(range[1], 10);
      const end = parseInt(range[2], 10);
      if (start <= end) return { startYear: range[1], endYear: range[2] };
    }
    return null;
  }
}

/* -------------------- 메인 분석기 클래스 -------------------- */

class JournalAnalyzer {
  constructor() {
    this.ss = SpreadsheetApp.getActiveSpreadsheet();
    this.cr_api = new CrossRefClient();
    this.prop = PropertiesService.getScriptProperties();
  }

  status(msg) { Utils.toast(msg, 8); }

  getSelectedJournals() {
    const js = this.ss.getSheetByName(Config.SHEET_NAMES.JOURNALS);
    if (!js) { Utils.showAlert('Journals 시트를 찾을 수 없습니다.'); return []; }
    
    try {
      const lastRow = js.getLastRow();
      if (lastRow < 2) { Utils.showAlert('저널 데이터가 없습니다.'); return []; }
      
      const data = js.getRange(2, 1, lastRow - 1, 6).getValues();
      const journals = [];
      
      data.forEach(row => {
        const isSelected = row[Config.COLUMNS.JOURNALS.SELECT - 1] === true;
        const source = row[Config.COLUMNS.JOURNALS.SOURCE - 1]?.toString().trim().toLowerCase();
        const name = row[Config.COLUMNS.JOURNALS.NAME - 1]?.toString().trim();
        const id = row[Config.COLUMNS.JOURNALS.ID - 1]?.toString().trim();
        
        if (isSelected && source === 'crossref' && id) {
          journals.push({ name, id });
          Debug.log(`Selected journal: ${name} (ISSN: ${id})`, 'INFO');
        }
      });
      
      return journals;
    } catch (e) {
      Debug.log(`Error getting journals: ${e.toString()}`, 'ERROR');
      return [];
    }
  }

  startCollection({ startYear, endYear }) {
    Debug.clearDebugLogs();
    Debug.log(`Starting collection for period: ${startYear}-${endYear}`, 'INFO');
    
    const journals = this.getSelectedJournals();
    if (journals.length === 0) return;
    
    const period = startYear === endYear ? startYear : `${startYear}-${endYear}`;
    Utils.showAlert(`'${period}' 기간 데이터 수집을 시작합니다.\n\n선택된 저널: ${journals.length}개\n\n이 작업은 시간이 걸릴 수 있으며 백그라운드에서 진행됩니다.`, '🚀 작업 시작');
    
    deleteAllTriggers();
    this.prop.deleteProperty(Config.LAST_RESULT_KEY);
    this.prop.deleteProperty(Config.PROGRESS_KEY);
    this.prop.deleteProperty(Config.STATS_KEY);
    
    const sheet = this.prepareTargetSheet({ startYear, endYear });
    const actualSheetName = sheet.getName();
    
    const state = {
      startYear, endYear, journals,
      nextIndex: 0, total: journals.length, newRowsCount: 0,
      startTime: new Date().toISOString(), actualSheetName,
      stats: { totalArticles: 0, articlesWithAbstract: 0, articlesWithOA: 0, yearCounts: {}, journalCounts: {} }
    };
    
    this.prop.setProperty(Config.STATE_PROPERTY_KEY, JSON.stringify(state));
    createNextTrigger();
    this.status(`⏳ 수집 시작... (총 ${journals.length}개 저널)`);
  }

  prepareTargetSheet({ startYear, endYear }) {
    const baseName = `Articles_${startYear === endYear ? startYear : `${startYear}-${endYear}`}`;
    let sheetName = baseName;
    let sheet = this.ss.getSheetByName(sheetName);
    let counter = 2;
    
    while (sheet) {
      sheetName = `${baseName}_${counter++}`;
      sheet = this.ss.getSheetByName(sheetName);
    }
    
    sheet = this.ss.insertSheet(sheetName);
    Debug.log(`Created new sheet: ${sheetName}`, 'INFO');
    
    sheet.appendRow(Config.HEADERS);
    sheet.getRange(1, 1, 1, Config.HEADERS.length).setFontWeight('bold').setBackground('#f0f0f0');
    
    return sheet;
  }

  processBatch() {
    const stateJSON = this.prop.getProperty(Config.STATE_PROPERTY_KEY);
    if (!stateJSON) return;
    
    let state;
    try { state = JSON.parse(stateJSON); }
    catch (e) { Debug.log('Invalid job state', 'ERROR'); this.prop.deleteProperty(Config.STATE_PROPERTY_KEY); return; }
    
    const { startYear, endYear, journals, nextIndex, total, actualSheetName } = state;
    let { newRowsCount, stats } = state;
    
    Debug.log(`Processing batch: ${nextIndex}/${total}`, 'INFO');
    
    const startIdx = nextIndex;
    const endIdx = Math.min(startIdx + Config.API_SETTINGS.BATCH_SIZE, total);
    const batch = journals.slice(startIdx, endIdx);
    
    let sheet;
    try {
      sheet = actualSheetName ? this.ss.getSheetByName(actualSheetName) : this.getTargetSheet({ startYear, endYear });
      if (!sheet) throw new Error(`Sheet '${actualSheetName || 'target'}' not found`);
    } catch (e) {
      Debug.log(`Sheet error: ${e.toString()}`, 'ERROR');
      deleteAllTriggers();
      this.prop.deleteProperty(Config.STATE_PROPERTY_KEY);
      return;
    }
    
    const idSet = DataProcessor.getIdIndex(sheet);
    const newRowsInBatch = [];
    
    batch.forEach((journal, idx) => {
      try {
        const currentPos = startIdx + idx + 1;
        this.status(`처리 중 (${currentPos}/${total}): ${journal.name}`);
        Debug.log(`Processing journal ${currentPos}/${total}: ${journal.name} (ISSN: ${journal.id})`, 'INFO');
        
        const articles = this.fetchJournalArticlesEnhanced(journal, startYear, endYear);
        
        if (articles && articles.length > 0) {
          Debug.log(`Found total ${articles.length} articles from ${journal.name}`, 'SUCCESS');
          
          let journalNewCount = 0, duplicateCount = 0;
          articles.forEach(item => {
            const extracted = DataProcessor.extractFromCrossRef(item, journal.name);
            if (extracted) {
              if (extracted.id && !idSet.has(extracted.id)) {
                newRowsInBatch.push(extracted.row);
                idSet.add(extracted.id);
                journalNewCount++;
                
                const year = extracted.row[Config.COLUMNS.ARTICLES.DATE - 1].substring(0, 4);
                if (!stats.yearCounts[year]) stats.yearCounts[year] = 0;
                stats.yearCounts[year]++;
                
                stats.totalArticles++;
                if (extracted.row[Config.COLUMNS.ARTICLES.ABSTRACT - 1]) stats.articlesWithAbstract++;
                if (extracted.row[Config.COLUMNS.ARTICLES.OA - 1] === 'TRUE') stats.articlesWithOA++;
              } else if (extracted.id) duplicateCount++;
            }
          });
          
          stats.journalCounts[journal.name] = journalNewCount;
          Debug.log(`Added ${journalNewCount} new articles from ${journal.name} (${duplicateCount} duplicates skipped)`, 'SUCCESS');
          Debug.updateProgress(`Journal ${currentPos}/${total}: ${journal.name} - ${journalNewCount} new articles added`);
        } else {
          Debug.log(`No articles found for ${journal.name}`, 'WARN');
          stats.journalCounts[journal.name] = 0;
        }
      } catch (e) {
        Debug.log(`Error processing ${journal.name}: ${e.toString()}`, 'ERROR');
      }
    });
    
    if (newRowsInBatch.length > 0) {
      DataProcessor.appendBatch(sheet, newRowsInBatch);
      newRowsCount += newRowsInBatch.length;
    }
    
    Debug.updateStats(stats);
    
    if (endIdx < total) {
      state.nextIndex = endIdx;
      state.newRowsCount = newRowsCount;
      state.stats = stats;
      this.prop.setProperty(Config.STATE_PROPERTY_KEY, JSON.stringify(state));
      createNextTrigger();
    } else {
      this.completeCollection(state, newRowsCount, sheet);
    }
  }

  fetchJournalArticlesEnhanced(journal, startYear, endYear) {
    const allArticles = [];
    const startYearNum = parseInt(startYear);
    const endYearNum = parseInt(endYear);
    const rowsPerRequest = Config.API_SETTINGS.ROWS_PER_REQUEST;
    const maxArticles = Config.API_SETTINGS.MAX_ARTICLES_PER_JOURNAL;
    
    for (let year = endYearNum; year >= startYearNum && allArticles.length < maxArticles; year--) {
      try {
        Debug.log(`Fetching articles for ${journal.name} - Year ${year}`, 'DEBUG');
        
        let offset = 0, hasMore = true, yearArticleCount = 0, cursor = null;
        while (hasMore && yearArticleCount < 200 && allArticles.length < maxArticles) {
          const url = this.cr_api.buildYearUrl({ issn: journal.id, year, rows: rowsPerRequest, offset, cursor });
          const json = this.cr_api.fetchJson(url);
          
          if (json && json.message && json.message.items && json.message.items.length > 0) {
            const items = json.message.items;
            allArticles.push(...items);
            yearArticleCount += items.length;
            
            if (json.message['next-cursor']) {
              cursor = json.message['next-cursor'];
              offset = 0;
            } else {
              const totalResults = json.message['total-results'] || 0;
              offset += rowsPerRequest;
              if (offset >= totalResults || items.length < rowsPerRequest) hasMore = false;
            }
            // 동적 지연 시간 조정
            const dynamicDelay = items.length >= rowsPerRequest ? 200 : 100;
            Utilities.sleep(dynamicDelay);
          } else {
            hasMore = false;
          }
        }
        
        Debug.log(`Total ${yearArticleCount} articles collected for year ${year}`, 'INFO');
        // 연도 간 지연 시간 단축 및 동적 조정
        if (year > startYearNum) {
          const yearDelay = yearArticleCount > 50 ? Config.API_SETTINGS.YEAR_DELAY_MS : 200;
          Utilities.sleep(yearDelay);
        }
      } catch (e) {
        Debug.log(`Error fetching year ${year}: ${e.toString()}`, 'ERROR');
      }
    }
    
    return allArticles.slice(0, maxArticles);
  }

  completeCollection(state, newRowsCount, sheet) {
    deleteAllTriggers();
    this.prop.deleteProperty(Config.STATE_PROPERTY_KEY);
    
    const result = {
      sheetName: sheet.getName(),
      journalCount: state.total,
      newRows: newRowsCount,
      startTime: state.startTime,
      endTime: new Date().toISOString(),
      stats: state.stats
    };
    
    this.prop.setProperty(Config.LAST_RESULT_KEY, JSON.stringify(result));
    
    // 단순화된 Analysis 시트 생성
    createAnalysisSheet(sheet.getName(), 'Analysis');
    
    sendCompletionEmail(result);
    Debug.log(`Collection completed: ${newRowsCount} articles from ${state.total} journals`, 'SUCCESS');
    Debug.updateProgress(`Collection completed: ${newRowsCount} articles from ${state.total} journals`);
  }

  translateAbstracts() {
    const sheet = this.ss.getActiveSheet();
    if (!sheet.getName().includes('Articles')) { Utils.showAlert('Articles 시트에서 실행하세요.'); return; }
    
    const lastRow = sheet.getLastRow();
    if (lastRow < 2) { Utils.showAlert('번역할 데이터가 없습니다.'); return; }
    
    const absCol = Config.COLUMNS.ARTICLES.ABSTRACT;
    const trCol = Config.COLUMNS.ARTICLES.TRANSLATED;
    const batchSize = Config.API_SETTINGS.TRANSLATION_BATCH_SIZE;
    
    let translatedCount = 0;
    this.status('초록 번역을 시작합니다...');
    
    for (let row = 2; row <= lastRow; row += batchSize) {
      const numRows = Math.min(batchSize, lastRow - row + 1);
      const abstracts = sheet.getRange(row, absCol, numRows, 1).getValues();
      const translations = sheet.getRange(row, trCol, numRows, 1).getValues();
      const toTranslate = [], indices = [];
      
      abstracts.forEach((abs, idx) => { if (abs[0] && !translations[idx][0]) { toTranslate.push(abs[0]); indices.push(idx); } });
      
      if (toTranslate.length > 0) {
        this.status(`번역 중... (${row}-${row + numRows - 1}/${lastRow})`);
        const results = [];
        // 번역 배치 처리 최적화
        toTranslate.forEach((text, index) => {
          try {
            // 텍스트 길이에 따른 동적 지연
            const textLength = text.length;
            const delay = textLength > 1000 ? 300 : textLength > 500 ? 150 : 100;
            
            results.push([LanguageApp.translate(text, '', 'ko')]);
            translatedCount++;
            
            // 마지막 항목이 아닐 때만 지연
            if (index < toTranslate.length - 1) {
              Utilities.sleep(delay);
            }
          } catch (e) { 
            Debug.log(`Translation error: ${e.toString()}`, 'ERROR'); 
            results.push(['번역 오류']); 
          }
        });
        indices.forEach((idx, i) => { sheet.getRange(row + idx, trCol).setValue(results[i][0]); });
      }
    }
    Utils.showAlert(`${translatedCount}개의 초록이 번역되었습니다.`, '번역 완료');
  }
}

function getYearCell(dateCell) {
  if (typeof dateCell === 'string') return dateCell.substring(0, 4);
  if (dateCell instanceof Date) return String(dateCell.getFullYear());
  if (Array.isArray(dateCell)) {
    if (Array.isArray(dateCell[0])) return String(dateCell[0][0]);
    return String(dateCell[0]);
  }
  return '';
}

/* -------------------- 단순화된 분석 시트 생성 -------------------- */

function createAnalysisSheet(articlesSheetName, analysisSheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(articlesSheetName);
  if (!sheet) return;
  
  const data = sheet.getDataRange().getValues();
  const header = data[0];
  const rows = data.slice(1);
  
  // 지표 인덱스
  const idxAbstract = header.indexOf('초록');
  const idxOA = header.indexOf('OA');
  const idxDate = header.indexOf('출판일');
  const idxJournal = header.indexOf('저널명');
  
  // 통계 계산
  let total = 0, oaCount = 0, abstractCount = 0;
  const journalStats = {}, yearStats = {};
  
  rows.forEach(row => {
    total++;
    if (row[idxOA] === 'TRUE') oaCount++;
    if (row[idxAbstract] && String(row[idxAbstract]).length > 10) abstractCount++;
    
    const journalName = row[idxJournal] || 'N/A';
    const year = getYearCell(row[idxDate]) || 'N/A';
    
    // 저널별 통계
    if (!journalStats[journalName]) journalStats[journalName] = { total: 0, oa: 0 };
    journalStats[journalName].total++;
    if (row[idxOA] === 'TRUE') journalStats[journalName].oa++;
    
    // 연도별 통계
    if (!yearStats[year]) yearStats[year] = { total: 0, oa: 0 };
    yearStats[year].total++;
    if (row[idxOA] === 'TRUE') yearStats[year].oa++;
  });
  
  // Analysis 시트 초기화
  let analysis = ss.getSheetByName(analysisSheetName);
  if (!analysis) analysis = ss.insertSheet(analysisSheetName);
  else analysis.clear();
  
  // 통계 보고서 작성
  let r = 1;
  analysis.getRange(r++, 1, 1, 2).setValues([['수집 통계 분석', '']]).setFontWeight('bold').setFontSize(14);
  analysis.getRange(r++, 1, 1, 2).setValues([['', '']]);
  analysis.getRange(r++, 1, 1, 2).setValues([['데이터 저장 시트', articlesSheetName]]);
  analysis.getRange(r++, 1, 1, 2).setValues([['수집 시점', new Date().toLocaleString('ko-KR')]]);
  analysis.getRange(r++, 1, 1, 2).setValues([['', '']]);
  
  analysis.getRange(r, 1, 5, 2).setValues([
    ['총 저널 수', Object.keys(journalStats).length],
    ['총 논문 수', total],
    ['초록 있는 논문', abstractCount],
    ['OA 논문 수', oaCount],
    ['OA 비율', total > 0 ? (oaCount / total * 100).toFixed(1) + '%' : '0%']
  ]);
  r += 6;
  
  analysis.getRange(r++, 1).setValue('연도별 논문 수').setFontWeight('bold').setBackground('#e8f0fe');
  const yearRows = Object.keys(yearStats).sort().map(y => [y, yearStats[y].total, yearStats[y].oa]);
  analysis.getRange(r, 1, 1, 3).setValues([['연도', '총 논문', 'OA 논문']]).setFontWeight('bold');
  if (yearRows.length > 0) {
    analysis.getRange(r + 1, 1, yearRows.length, 3).setValues(yearRows);
    r += yearRows.length + 2;
  }
  
  analysis.getRange(r++, 1).setValue('저널별 논문 수').setFontWeight('bold').setBackground('#e8f0fe');
  const journalRows = Object.entries(journalStats)
    .sort((a, b) => b[1].total - a[1].total)
    .map(([j, c]) => [j, c.total, c.oa]);
  analysis.getRange(r, 1, 1, 3).setValues([['저널명', '총 논문', 'OA 논문']]).setFontWeight('bold');
  if (journalRows.length > 0) {
    analysis.getRange(r + 1, 1, journalRows.length, 3).setValues(journalRows);
  }
  
  analysis.getRange('A:A').setFontWeight('bold');
  analysis.autoResizeColumns(1, 3);
}

/* -------------------- 저널 검색 및 OA 조회 기능 -------------------- */

class JournalSearcher {
  constructor() {
    this.cr_api = new CrossRefClient();
  }

  /**
   * ISSN 형식인지 확인합니다.
   */
  isISSN(str) {
    if (!str) return false;
    return /^(\d{4}-?\d{3}[\dxX])$/.test(str.trim());
  }

  /**
   * ISSN으로 저널을 검색합니다.
   */
  searchByIssn(issn) {
    const apiUrl = `${Config.API_SETTINGS.BASE_URL}/journals/${issn}`;
    const json = this.cr_api.fetchJson(apiUrl);
    
    if (!json || !json.message) {
      return { success: false, message: `ISSN '${issn}'에 해당하는 저널을 찾을 수 없습니다.` };
    }
    
    const journal = json.message;
    const issnList = journal.ISSN ? journal.ISSN.join(", ") : issn;
    
    return {
      success: true,
      data: {
        title: journal.title,
        issn: issnList,
        publisher: journal.publisher || 'N/A'
      }
    };
  }

  /**
   * 저널 제목으로 저널을 검색합니다.
   */
  searchByTitle(query) {
    // 검색 쿼리 최적화
    const optimizedQuery = query.trim().replace(/\s+/g, '+');
    const apiUrl = `${Config.API_SETTINGS.BASE_URL}/journals?query=${encodeURIComponent(optimizedQuery)}&rows=15&sort=relevance`;
    
    const json = this.cr_api.fetchJson(apiUrl);
    
    if (!json || !json.message || !json.message.items || json.message.items.length === 0) {
      return { success: false, message: `'${query}'에 대한 검색 결과가 없습니다.` };
    }
    
    // 결과 처리 최적화 및 중복 제거
    const seenTitles = new Set();
    const results = json.message.items
      .filter(journal => {
        const title = journal.title?.toLowerCase();
        if (!title || seenTitles.has(title)) return false;
        seenTitles.add(title);
        return true;
      })
      .slice(0, 10) // 최대 10개로 제한
      .map(journal => ({
        title: journal.title,
        issn: (journal.ISSN && journal.ISSN.length > 0) ? journal.ISSN.join(", ") : "ISSN 정보 없음",
        publisher: journal.publisher || 'N/A',
        relevanceScore: this.calculateRelevance(query, journal.title) // 관련성 점수 추가
      }))
      .sort((a, b) => b.relevanceScore - a.relevanceScore); // 관련성 순 정렬
    
    return { success: true, data: results };
  }

  /**
   * 검색어와 저널 제목의 관련성 점수 계산
   */
  calculateRelevance(query, title) {
    if (!query || !title) return 0;
    
    const queryLower = query.toLowerCase();
    const titleLower = title.toLowerCase();
    
    // 완전 일치
    if (titleLower === queryLower) return 100;
    
    // 시작 일치
    if (titleLower.startsWith(queryLower)) return 90;
    
    // 포함 일치
    if (titleLower.includes(queryLower)) return 80;
    
    // 단어별 일치
    const queryWords = queryLower.split(/\s+/);
    const titleWords = titleLower.split(/\s+/);
    const matchCount = queryWords.filter(word => 
      titleWords.some(titleWord => titleWord.includes(word))
    ).length;
    
    return (matchCount / queryWords.length) * 70;
  }

  /**
   * 특정 저널의 OA 논문을 조회합니다.
   */
  checkOpenAccess(issn, year) {
    // 더 많은 데이터를 한 번에 가져오기 위해 rows 증가
    const url = `${Config.API_SETTINGS.BASE_URL}/journals/${issn}/works?filter=from-pub-date:${year}-01-01,until-pub-date:${year}-12-31&rows=200&sort=published&order=desc`;
    const json = this.cr_api.fetchJson(url);
    
    if (!json || !json.message || !json.message.items) {
      return { success: false, message: `'${issn}' 저널의 ${year}년도 논문 정보를 찾을 수 없습니다.` };
    }
    
    const articles = json.message.items;
    const oaArticles = [];
    const nonOaArticles = [];
    
    // 병렬 처리를 위한 배치 처리
    articles.forEach(article => {
      const isOA = Array.isArray(article.license) && article.license.length > 0;
      const title = article.title ? article.title[0] : "(제목없음)";
      const doi = article.DOI;
      const publishedDate = this.extractPublishedDate(article);
      
      const articleData = {
        title: title,
        doi: doi,
        publishedDate: publishedDate,
        isOA: isOA
      };
      
      if (isOA) {
        const license = article.license[0];
        articleData.licenseUrl = license.URL || '';
        articleData.licenseType = license['content-version'] || '';
        articleData.licenseStart = license.start ? license.start['date-parts'] : null;
        oaArticles.push(articleData);
      } else {
        nonOaArticles.push(articleData);
      }
    });
    
    // OA 논문을 날짜순으로 정렬 (최신순)
    oaArticles.sort((a, b) => {
      if (!a.publishedDate || !b.publishedDate) return 0;
      return new Date(b.publishedDate) - new Date(a.publishedDate);
    });
    
    return {
      success: true,
      data: {
        totalArticles: articles.length,
        oaArticles: oaArticles,
        nonOaArticles: nonOaArticles.slice(0, 10), // 비OA 논문도 일부 포함
        oaCount: oaArticles.length,
        oaRatio: articles.length > 0 ? (oaArticles.length / articles.length * 100).toFixed(1) : 0,
        hasMoreData: json.message['total-results'] > articles.length
      }
    };
  }

  /**
   * 논문의 출판일 추출
   */
  extractPublishedDate(article) {
    if (article.published && article.published['date-parts'] && article.published['date-parts'][0]) {
      const dateParts = article.published['date-parts'][0];
      return `${dateParts[0]}-${String(dateParts[1] || 1).padStart(2, '0')}-${String(dateParts[2] || 1).padStart(2, '0')}`;
    }
    return null;
  }
}

/* -------------------- 메뉴 함수들 -------------------- */

function menuSearchJournal() {
  const ui = SpreadsheetApp.getUi();
  
  // 사용자 입력 받기 (엔터 키 지원)
  let input = '';
  while (!input) {
    const response = ui.prompt('저널 검색', 
      '저널 제목 또는 ISSN을 입력하세요:\n\n' +
      '• 예시 1: Nature\n' +
      '• 예시 2: 0028-0836\n' +
      '• 예시 3: 00280836\n\n' +
      '입력 후 Enter 키를 누르거나 확인을 클릭하세요.', 
      ui.ButtonSet.OK_CANCEL);
    
    if (response.getSelectedButton() !== ui.Button.OK) return;
    
    input = response.getResponseText().trim();
    if (!input) {
      const retry = ui.alert('입력 오류', '검색어를 입력해주세요.', ui.ButtonSet.OK_CANCEL);
      if (retry !== ui.Button.OK) return;
    }
  }
  
  // 검색 진행 표시
  Utils.toast('저널 정보를 검색하고 있습니다...', 5);
  
  const searcher = new JournalSearcher();
  let result;
  
  if (searcher.isISSN(input)) {
    // ISSN 검색
    const issn = input.length === 8 && !input.includes('-') ? `${input.slice(0, 4)}-${input.slice(4)}` : input;
    result = searcher.searchByIssn(issn.toUpperCase());
    
    if (result.success) {
      const continueSearch = ui.alert('검색 결과', 
        `✅ 저널을 찾았습니다!\n\n` +
        `제목: "${result.data.title}"\n` +
        `ISSN: ${result.data.issn}\n` +
        `출판사: ${result.data.publisher}\n\n` +
        `다른 저널을 더 검색하시겠습니까?`, 
        ui.ButtonSet.YES_NO);
      
      if (continueSearch === ui.Button.YES) {
        menuSearchJournal(); // 재귀 호출로 연속 검색
      }
    } else {
      const retry = ui.alert('검색 결과', 
        `❌ ${result.message}\n\n다시 검색하시겠습니까?`, 
        ui.ButtonSet.YES_NO);
      
      if (retry === ui.Button.YES) {
        menuSearchJournal(); // 재귀 호출로 재시도
      }
    }
  } else {
    // 제목 검색
    result = searcher.searchByTitle(input);
    
    if (result.success) {
      let message = `'${input}'에 대한 검색 결과 (최대 10개):\n\n`;
      result.data.forEach((journal, index) => {
        message += `${index + 1}. "${journal.title}"\n`;
        message += `   ISSN: ${journal.issn}\n`;
        message += `   출판사: ${journal.publisher}\n\n`;
      });
      
      const continueSearch = ui.alert('검색 결과', 
        message + '\n다른 저널을 더 검색하시겠습니까?', 
        ui.ButtonSet.YES_NO);
      
      if (continueSearch === ui.Button.YES) {
        menuSearchJournal(); // 재귀 호출로 연속 검색
      }
    } else {
      const retry = ui.alert('검색 결과', 
        `❌ ${result.message}\n\n다시 검색하시겠습니까?`, 
        ui.ButtonSet.YES_NO);
      
      if (retry === ui.Button.YES) {
        menuSearchJournal(); // 재귀 호출로 재시도
      }
    }
  }
}

function menuCheckOpenAccess() {
  const ui = SpreadsheetApp.getUi();
  
  // ISSN 입력 받기 (엔터 키 지원)
  let issn = '';
  while (!issn) {
    const issnResponse = ui.prompt('OA 논문 조회 - 1단계', 
      'ISSN을 입력하세요:\n\n' +
      '• 예시 1: 0028-0836\n' +
      '• 예시 2: 00280836\n' +
      '• 예시 3: 1234-567X\n\n' +
      '입력 후 Enter 키를 누르거나 확인을 클릭하세요.', 
      ui.ButtonSet.OK_CANCEL);
    
    if (issnResponse.getSelectedButton() !== ui.Button.OK) return;
    
    issn = issnResponse.getResponseText().trim();
    if (!issn) {
      const retry = ui.alert('입력 오류', 'ISSN을 입력해주세요.', ui.ButtonSet.OK_CANCEL);
      if (retry !== ui.Button.OK) return;
    }
  }
  
  // ISSN 유효성 검사
  const searcher = new JournalSearcher();
  if (!searcher.isISSN(issn)) {
    const retry = ui.alert('입력 오류', 
      '유효하지 않은 ISSN 형식입니다.\n\n' +
      'ISSN은 다음 형식이어야 합니다:\n' +
      '• 1234-5678\n' +
      '• 1234567X\n\n' +
      '다시 입력하시겠습니까?', 
      ui.ButtonSet.YES_NO);
    
    if (retry === ui.Button.YES) {
      menuCheckOpenAccess(); // 재귀 호출로 재시도
    }
    return;
  }
  
  // 연도 입력 받기 (엔터 키 지원)
  let year = null;
  while (!year) {
    const yearResponse = ui.prompt('OA 논문 조회 - 2단계', 
      '조회할 연도를 입력하세요:\n\n' +
      '• 예시: 2023\n' +
      '• 범위: 2000-2024\n\n' +
      '입력 후 Enter 키를 누르거나 확인을 클릭하세요.', 
      ui.ButtonSet.OK_CANCEL);
    
    if (yearResponse.getSelectedButton() !== ui.Button.OK) return;
    
    const yearStr = yearResponse.getResponseText().trim();
    const yearNum = parseInt(yearStr, 10);
    
    if (isNaN(yearNum) || yearStr.length !== 4 || yearNum < 2000 || yearNum > 2024) {
      const retry = ui.alert('입력 오류', 
        '연도는 2000-2024 사이의 4자리 숫자로 입력해야 합니다.\n\n' +
        '다시 입력하시겠습니까?', 
        ui.ButtonSet.OK_CANCEL);
      
      if (retry !== ui.Button.OK) return;
    } else {
      year = yearNum;
    }
  }
  
  // 조회 진행 표시
  Utils.toast(`${issn} 저널의 ${year}년도 OA 논문 정보를 조회하고 있습니다...`, 10);
  
  const result = searcher.checkOpenAccess(issn, year);
  
  if (result.success) {
    const data = result.data;
    let message = `📊 '${issn}' 저널의 ${year}년도 OA 분석 결과:\n\n`;
    message += `📚 총 논문 수: ${data.totalArticles}편\n`;
    message += `🔓 OA 논문 수: ${data.oaCount}편\n`;
    message += `📈 OA 비율: ${data.oaRatio}%\n\n`;
    
    if (data.oaArticles.length > 0) {
      message += '🔓 주요 OA 논문 목록 (최대 5편):\n\n';
      data.oaArticles.slice(0, 5).forEach((article, index) => {
        message += `${index + 1}. ${article.title.substring(0, 80)}${article.title.length > 80 ? '...' : ''}\n`;
        message += `   📄 DOI: ${article.doi}\n`;
        if (article.licenseUrl) {
          message += `   📜 라이선스: ${article.licenseUrl}\n`;
        }
        message += '\n';
      });
      
      if (data.oaArticles.length > 5) {
        message += `... 외 ${data.oaArticles.length - 5}편의 OA 논문이 더 있습니다.\n\n`;
      }
    } else {
      message += '❌ 해당 연도에 OA 논문이 없습니다.\n\n';
    }
    
    const continueSearch = ui.alert('OA 조회 결과', 
      message + '다른 저널이나 연도를 더 조회하시겠습니까?', 
      ui.ButtonSet.YES_NO);
    
    if (continueSearch === ui.Button.YES) {
      menuCheckOpenAccess(); // 재귀 호출로 연속 조회
    }
  } else {
    const retry = ui.alert('OA 조회 결과', 
      `❌ ${result.message}\n\n다시 조회하시겠습니까?`, 
      ui.ButtonSet.YES_NO);
    
    if (retry === ui.Button.YES) {
      menuCheckOpenAccess(); // 재귀 호출로 재시도
    }
  }
}

/* -------------------- 트리거 및 메뉴 -------------------- */

function onOpen() { createAppMenu(); }

function createAppMenu() {
  const ui = SpreadsheetApp.getUi();
  const menu = ui.createMenu('신학 저널 분석 (v2.1)');
  
  menu.addItem('📥 논문 수집 (기간별)', 'menuStartCollection')
    .addItem('📥 논문 수집 (대규모: 2020-2024)', 'menuLargeCollection')
    .addSeparator()
    .addItem('🔍 저널 검색 (제목/ISSN)', 'menuSearchJournal')
    .addItem('📖 OA 논문 조회', 'menuCheckOpenAccess')
    .addSeparator()
    .addItem('🌐 선택 초록 번역', 'menuTranslateSelected')
    .addItem('🌐 모든 초록 번역', 'menuTranslateAll')
    .addSeparator()
    .addItem('📊 분석 리포트 생성/갱신', 'menuAnalysisReport')
    .addItem('📊 수집 통계 보기', 'menuShowStats')
    .addItem('� 디마지막 작업 결과', 'menuShowLastResult')
    .addItem('� 현버재 진행 상황', 'menuShowProgress')
    .addSeparator()
    .addItem('� 디버그 로그  보기', 'menuShowDebugLogs')
    .addItem('🔧 디버그 로그 초기화', 'menuClearDebugLogs')
    .addSeparator()
    .addItem('🛑 작업 중단', 'menuCancelOperation')
    .addSeparator()
    .addItem('ℹ️ 도움말', 'menuShowHelp')
    .addToUi();
}

function continueFetching() {
  try { new JournalAnalyzer().processBatch(); }
  catch (e) { Debug.log(`Continue error: ${e.toString()}`, 'ERROR'); deleteAllTriggers(); }
}

function createNextTrigger() {
  deleteAllTriggers();
  try {
    ScriptApp.newTrigger('continueFetching').timeBased().after(Config.API_SETTINGS.TRIGGER_DELAY_MS).create();
    Debug.log('Next trigger created', 'DEBUG');
  } catch (e) { Debug.log(`Trigger error: ${e.toString()}`, 'ERROR'); }
}

function deleteAllTriggers() {
  try {
    ScriptApp.getProjectTriggers().forEach(t => { 
      if (t.getHandlerFunction() === 'continueFetching') ScriptApp.deleteTrigger(t); 
    });
  } catch (e) { Debug.log(`Delete trigger error: ${e.toString()}`, 'ERROR'); }
}



function sendCompletionEmail(result) {
  try {
    const { sheetName, journalCount, newRows, startTime, endTime, stats } = result;
    const userEmail = Session.getActiveUser().getEmail();
    const spreadsheetName = SpreadsheetApp.getActiveSpreadsheet().getName();
    const durationMinutes = Math.round((new Date(endTime) - new Date(startTime)) / 60000);
    
    const subject = `[신학 저널 분석] 데이터 수집 완료`;
    const body = `안녕하세요.\n\n'${spreadsheetName}' 스프레드시트의 데이터 수집이 완료되었습니다.\n\n📊 수집 결과\n- 처리된 저널 수: ${journalCount}개\n- 새로 추가된 논문: ${newRows}개\n- 초록 있는 논문: ${stats.articlesWithAbstract}개\n- OA 논문: ${stats.articlesWithOA}개\n\n저장된 시트: '${sheetName}'\n소요 시간: ${durationMinutes}분\n\n📈 상세 분석은 'Analysis' 시트에서 확인하실 수 있습니다.\n\n스프레드시트 링크\n${SpreadsheetApp.getActiveSpreadsheet().getUrl()}\n\n감사합니다.`;
    
    MailApp.sendEmail(userEmail, subject, body);
    Debug.log(`Completion email sent to ${userEmail}`, 'SUCCESS');
  } catch (e) { Debug.log(`Email error: ${e.toString()}`, 'ERROR'); }
}

/* ----------- 메뉴 핸들러: 분석 리포트 수동 실행 ----------- */

function menuAnalysisReport() {
  const ui = SpreadsheetApp.getUi();
  const sheet = SpreadsheetApp.getActiveSheet();
  const sheetName = sheet.getName();
  
  if (!sheetName.startsWith('Articles')) {
    ui.alert('Articles 시트(논문 데이터 시트)에서만 실행 가능합니다!');
    return;
  }
  
  createAnalysisSheet(sheetName, 'Analysis');
  ui.alert('분석 리포트가 생성/갱신되었습니다!\n시트명: Analysis');
}

/* ----------- 메뉴: 수집, 번역, 통계, 로그, 도움말 ----------- */

function menuStartCollection() {
  const ui = SpreadsheetApp.getUi();
  const res = ui.prompt('수집 기간 입력', '수집할 기간을 입력하세요.\n\n예시:\n  단일 연도: 2023\n  기간: 2021-2023', ui.ButtonSet.OK_CANCEL);
  if (res.getSelectedButton() != ui.Button.OK) return;
  const yr = Utils.parseYearRange(res.getResponseText());
  if (yr) new JournalAnalyzer().startCollection(yr);
  else Utils.showAlert('올바른 형식으로 입력해주세요.\n예: 2023 또는 2021-2023');
}

function menuLargeCollection() {
  const ui = SpreadsheetApp.getUi();
  const resp = ui.alert('대규모 수집 확인', '2020-2024년 (5년간)의 모든 선택된 저널 데이터를 수집합니다.\n\n이 작업은 오랜 시간이 걸릴 수 있습니다.\n계속하시겠습니까?', ui.ButtonSet.YES_NO);
  if (resp === ui.Button.YES) new JournalAnalyzer().startCollection({ startYear: '2020', endYear: '2024' });
}

function menuTranslateSelected() {
  const sheet = SpreadsheetApp.getActiveSheet();
  if (!sheet.getName().includes('Articles')) { Utils.showAlert('Articles 시트에서 실행하세요.'); return; }
  const sel = SpreadsheetApp.getActiveRange();
  if (sel.getRow() < 2) { Utils.showAlert('데이터 행을 선택하세요.'); return; }
  
  const absCol = Config.COLUMNS.ARTICLES.ABSTRACT;
  const trCol = Config.COLUMNS.ARTICLES.TRANSLATED;
  const abstracts = sheet.getRange(sel.getRow(), absCol, sel.getNumRows(), 1).getValues();
  const translations = [];
  let cnt = 0;
  
  Utils.toast('번역 중...', 60);
  
  abstracts.forEach(([abs]) => {
    if (abs) {
      try { translations.push([LanguageApp.translate(abs, '', 'ko')]); cnt++; }
      catch (e) { translations.push(['번역 오류']); }
    } else translations.push(['']);
  });
  
  sheet.getRange(sel.getRow(), trCol, sel.getNumRows(), 1).setValues(translations);
  Utils.showAlert(`${cnt}개의 초록이 번역되었습니다.`, '번역 완료');
}

function menuTranslateAll() { new JournalAnalyzer().translateAbstracts(); }

function menuShowStats() {
  const s = Debug.getStats();
  if (s) {
    Utils.showAlert(`📊 수집 통계\n\n총 논문 수: ${s.totalArticles}\n초록 있는 논문: ${s.articlesWithAbstract}\nOA 논문: ${s.articlesWithOA}\n\n자세한 내용은 Analysis 시트를 확인하세요.`, '수집 통계');
  } else Utils.showAlert('아직 수집된 통계가 없습니다.', '통계 없음');
}

function menuShowLastResult() {
  const js = PropertiesService.getScriptProperties().getProperty(Config.LAST_RESULT_KEY);
  if (js) {
    const r = JSON.parse(js);
    const mins = Math.round((new Date(r.endTime) - new Date(r.startTime)) / 60000);
    Utils.showAlert(`📊 최근 작업 결과\n\n시트: ${r.sheetName}\n저널: ${r.journalCount}개\n논문: ${r.newRows}개\n소요시간: ${mins}분\n\n상세 통계는 Analysis 시트를 확인하세요.`, '작업 결과');
  } else Utils.showAlert('최근 작업 결과가 없습니다.', '결과 없음');
}

function menuShowProgress() {
  const p = PropertiesService.getScriptProperties().getProperty(Config.PROGRESS_KEY) || '진행 중인 작업이 없습니다.';
  Utils.showAlert(p, '현재 진행 상황');
}

function menuShowDebugLogs() {
  const logs = Debug.getDebugLogs();
  const html = HtmlService.createHtmlOutput(`<pre style="font-size:11px;white-space:pre-wrap;">${logs}</pre>`).setWidth(800).setHeight(500);
  SpreadsheetApp.getUi().showModalDialog(html, '디버그 로그');
}

function menuClearDebugLogs() {
  Debug.clearDebugLogs();
  PropertiesService.getScriptProperties().deleteProperty(Config.PROGRESS_KEY);
  PropertiesService.getScriptProperties().deleteProperty(Config.STATS_KEY);
  Utils.showAlert('디버그 로그가 초기화되었습니다.', '로그 초기화');
}

function menuCancelOperation() { 
  deleteAllTriggers();
  PropertiesService.getScriptProperties().deleteProperty(Config.STATE_PROPERTY_KEY);
  Utils.showAlert('진행 중인 작업이 중단되었습니다.');
}

function menuShowHelp() {
  Utils.showAlert(`📚 신학 저널 분석기 사용법 (v2.1)\n\n1. 논문 수집\n   - Journals 시트에서 원하는 저널 선택\n   - 메뉴 > 논문 수집 실행\n   - 기간 입력 (예: 2023 또는 2020-2023)\n\n2. 초록 번역\n   - Articles 시트에서 번역할 행 선택 후 '선택 초록 번역'\n   - 또는 '모든 초록 번역'으로 일괄 처리\n\n3. 통계 분석 확인\n   - Analysis 시트에서 정량 통계 확인\n   - 메뉴에서 '분석 리포트 생성'으로 수동 갱신 가능\n\n문의: your-email@example.com`, '도움말');
}

/* -------------------- 파일 끝 -------------------- */