// words.js

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
    // --- 초급 (Beginner) ---
    { id: 'b_1', english: 'man', korean: '(성인) 남자, 남성', level: DifficultyLevel.BEGINNER },
    { id: 'b_2', english: 'woman', korean: '(성인) 여자, 여성', level: DifficultyLevel.BEGINNER },
    { id: 'b_3', english: 'age', korean: '나이', level: DifficultyLevel.BEGINNER },
    { id: 'b_4', english: 'dear', korean: '사랑하는, 소중한', level: DifficultyLevel.BEGINNER },
    { id: 'b_5', english: 'girl', korean: '소녀, 여자아이', level: DifficultyLevel.BEGINNER },
    { id: 'b_6', english: 'boy', korean: '소년, 남자아이', level: DifficultyLevel.BEGINNER },
    { id: 'b_7', english: 'baby', korean: '아기', level: DifficultyLevel.BEGINNER },
    { id: 'b_8', english: 'name', korean: '이름', level: DifficultyLevel.BEGINNER },
    { id: 'b_9', english: 'daughter', korean: '딸', level: DifficultyLevel.BEGINNER },
    { id: 'b_10', english: 'brother', korean: '형, 오빠, 남동생', level: DifficultyLevel.BEGINNER },

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
    
    // --- 고급 (Advanced) ---
    { id: 'a_1', english: 'friendship', korean: '우정', level: DifficultyLevel.ADVANCED },
    { id: 'a_2', english: 'strange', korean: '이상한, 낯선', level: DifficultyLevel.ADVANCED },
    { id: 'a_3', english: 'neighbor', korean: '이웃', level: DifficultyLevel.ADVANCED },
    { id: 'a_4', english: 'partner', korean: '파트너, 짝', level: DifficultyLevel.ADVANCED },
    { id: 'a_5', english: 'share', korean: '함께 쓰다/ 나누다', level: DifficultyLevel.ADVANCED },
    { id: 'a_6', english: 'together', korean: '함께, 같이', level: DifficultyLevel.ADVANCED },
    { id: 'a_7', english: 'alone', korean: '혼자', level: DifficultyLevel.ADVANCED },
    { id: 'a_8', english: 'welcome', korean: '환영하다', level: DifficultyLevel.ADVANCED },
    { id: 'a_9', english: 'grow up', korean: '성장하다, 자라다', level: DifficultyLevel.ADVANCED },
    { id: 'a_10', english: 'watch out', korean: '조심하다', level: DifficultyLevel.ADVANCED },
];

// 퀴즈 설정 상수
const QUESTIONS_PER_QUIZ = 5;
const OPTIONS_COUNT = 4;
const LEVEL_UP_THRESHOLD_PERCENTAGE = 70;