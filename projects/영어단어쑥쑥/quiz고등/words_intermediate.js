// words_intermediate.js

const DifficultyLevel = {
    BEGINNER: '초급',
    INTERMEDIATE: '중급',
    ADVANCED: '고급',
};

const LEVEL_ORDER = [
    DifficultyLevel.BEGINNER,
    DifficultyLevel.INTERMEDIATE,
    DifficultyLevel.ADVANCED,
];

const WORDS_DATA = [
    // --- 중급 (Intermediate) ---
    { id: 'i_1', english: 'left', korean: '왼쪽; 왼쪽의; 왼쪽으로', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_2', english: 'right', korean: '오른쪽; 오른쪽의; 오른쪽으로', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_3', english: 'truck', korean: '트럭', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_4', english: 'test', korean: '시험; 검사, 실험', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_5', english: 'student', korean: '학생', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_6', english: 'write', korean: '쓰다', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_7', english: 'minute', korean: '(시간 단위) 분', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_8', english: 'soon', korean: '곧, 머지않아', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_9', english: 'date', korean: '날짜', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_10', english: 'month', korean: '달, 월', level: DifficultyLevel.INTERMEDIATE },
    // (예시) 중급 단어 추가
    { id: 'i_11', english: 'language', korean: '언어', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_12', english: 'computer', korean: '컴퓨터', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_13', english: 'music', korean: '음악', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_14', english: 'picture', korean: '그림, 사진', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_15', english: 'travel', korean: '여행하다', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_16', english: 'important', korean: '중요한', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_17', english: 'beautiful', korean: '아름다운', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_18', english: 'difficult', korean: '어려운', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_19', english: 'easy', korean: '쉬운', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_20', english: 'always', korean: '항상', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_21', english: 'sometimes', korean: '때때로', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_22', english: 'never', korean: '결코 ~않다', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_23', english: 'understand', korean: '이해하다', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_24', english: 'question', korean: '질문', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_25', english: 'answer', korean: '대답', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_26', english: 'morning', korean: '아침', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_27', english: 'afternoon', korean: '오후', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_28', english: 'evening', korean: '저녁', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_29', english: 'night', korean: '밤', level: DifficultyLevel.INTERMEDIATE },
    { id: 'i_30', english: 'family', korean: '가족', level: DifficultyLevel.INTERMEDIATE },
    // 중급 단어를 QUESTIONS_PER_QUIZ 개수(50개)에 가깝게 추가하거나, QUESTIONS_PER_QUIZ 값을 조정해야 합니다.
    // 현재는 30개 단어만 있습니다.
];

// 퀴즈 설정 상수 (모든 단어 파일에서 일관되게 유지)
const QUESTIONS_PER_QUIZ = 50;
const OPTIONS_COUNT = 4;
const LEVEL_UP_THRESHOLD_PERCENTAGE = 70;

console.log('[words_intermediate.js] 중급 단어장 로드됨:', WORDS_DATA.length, '개 단어');