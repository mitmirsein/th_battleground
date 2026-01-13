// app.js

// --- HTML 요소 참조 ---
const appContainer = document.getElementById('app-container');
const levelSelectorContainer = document.getElementById('level-selector-container');
const levelButtonsWrapper = document.getElementById('level-buttons-wrapper');
const quizViewContainer = document.getElementById('quiz-view-container');
const resultScreenContainer = document.getElementById('result-screen-container');
const resetProgressButton = document.getElementById('reset-progress-button');

const quizModeSelector = document.getElementById('quiz-mode-selector');
const selectedLevelQuizModeText = document.getElementById('selected-level-quiz-mode-text');
const startRandomQuizButton = document.getElementById('start-random-quiz-button');
const startIncorrectQuizButton = document.getElementById('start-incorrect-quiz-button');
const backToLevelSelectButton = document.getElementById('back-to-level-select-button');

// NEW: 단어장 선택 관련 UI 요소
const wordSetSelectorContainer = document.getElementById('word-set-selector-container');
const wordSetButtons = document.querySelectorAll('.word-set-button'); // NodeList
const wordSetLoadingMessage = document.getElementById('word-set-loading-message');
const wordSetErrorMessage = document.getElementById('word-set-error-message');
const quizArea = document.getElementById('quiz-area');
const appFooter = document.getElementById('app-footer');


let currentLevelDisplay;
let scoreDisplay;
let progressBar;
let questionNumberDisplay;
let questionTextElement;
let optionsGrid;
let feedbackMessageElement;
let nextQuestionButton;

const resultTitle = document.getElementById('result-title');
const resultLevel = document.getElementById('result-level');
const resultDetails = document.getElementById('result-details');
const resultPercentage = document.getElementById('result-percentage');
const resultScore = document.getElementById('result-score');
const resultMessage = document.getElementById('result-message');
const resultMessageIcon = document.getElementById('result-message-icon');
const resultMessageText = document.getElementById('result-message-text');
const retryQuizButton = document.getElementById('retry-quiz-button');
const proceedNextLevelButton = document.getElementById('proceed-next-level-button');
const backToLevelsButton = document.getElementById('back-to-levels-button');

let currentQuizLevel = null;
let currentQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let unlockedLevels = new Set();
let answeredCorrectlyWordIdsByLevel = {};
let incorrectWordIdsByLevel = {};
let isAnswered = false;

const QuizMode = {
    RANDOM: 'random',
    INCORRECT_ONLY: 'incorrect_only'
};
let currentQuizMode = QuizMode.RANDOM;
let selectedLevelForQuizMode = null;

const svgIconCheck = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" /></svg>`;
const svgIconX = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" /></svg>`;
const svgIconCheckCircleLarge = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8"><path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" /></svg>`;
const svgIconXCircleLarge = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-8 h-8"><path fill-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zm-1.72 6.97a.75.75 0 10-1.06 1.06L10.94 12l-1.72 1.72a.75.75 0 101.06 1.06L12 13.06l1.72 1.72a.75.75 0 101.06-1.06L13.06 12l1.72-1.72a.75.75 0 10-1.06-1.06L12 10.94l-1.72-1.72z" clip-rule="evenodd" /></svg>`;

let initialQuizViewHTML = '';

// --- 유틸리티 함수 ---
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

// --- 화면 전환 함수 ---
function showScreen(screenToShow) {
    levelSelectorContainer.style.display = 'none';
    quizViewContainer.style.display = 'none';
    resultScreenContainer.style.display = 'none';
    quizModeSelector.style.display = 'none';

    screenToShow.style.display = 'block';
}

// --- 레벨 선택 화면 ---
function renderLevelSelector() {
    showScreen(levelSelectorContainer);
    levelButtonsWrapper.innerHTML = '';
    levelButtonsWrapper.style.display = 'flex';

    if (typeof LEVEL_ORDER === 'undefined' || !Array.isArray(LEVEL_ORDER)) {
        console.error("[DEBUG] LEVEL_ORDER is not defined or not an array. Cannot render level buttons.");
        levelButtonsWrapper.innerHTML = `<p class="text-red-300">레벨 정보를 불러올 수 없습니다. 선택한 단어장 파일을 확인해주세요.</p>`;
        return;
    }
    
    LEVEL_ORDER.forEach(levelName => {
        const button = document.createElement('button');
        let levelText = '';
        let levelClass = ''; 
        
        if (typeof DifficultyLevel === 'undefined') {
            console.warn("[DEBUG] DifficultyLevel is not defined. Using levelName as text.");
            levelText = levelName;
            levelClass = 'btn-primary';
        } else {
            if (levelName === DifficultyLevel.BEGINNER) {
                levelText = '🌟 초급 (Level 1)';
                levelClass = 'btn-primary'; 
            } else if (levelName === DifficultyLevel.INTERMEDIATE) {
                levelText = '⚡ 중급 (Level 2)';
                levelClass = 'btn-secondary'; 
            } else if (levelName === DifficultyLevel.ADVANCED) {
                levelText = '🔥 고급 (Level 3)';
                levelClass = 'btn-success'; 
            } else {
                levelText = levelName; 
                levelClass = 'btn-primary'; 
            }
        }

        button.innerHTML = levelText;
        button.classList.add('level-button', levelClass, 'text-white', 'font-bold', 'py-4', 'px-8', 'rounded-2xl', 'text-xl', 'shadow-xl'); 
        
        // 해당 레벨의 단어가 WORDS_DATA에 있는지 확인하여 버튼 활성화/비활성화
        const wordsForLevel = WORDS_DATA.filter(word => word.level === levelName);
        if (wordsForLevel.length === 0) {
            button.disabled = true;
            button.classList.add('opacity-50', 'cursor-not-allowed');
            button.title = `선택된 단어장에 '${levelName}' 레벨의 단어가 없습니다.`;
        } else {
            button.onclick = () => showQuizModeSelector(levelName); 
        }
        levelButtonsWrapper.appendChild(button);
    });
}

function showQuizModeSelector(level) {
    selectedLevelForQuizMode = level;
    levelButtonsWrapper.style.display = 'none'; 
    quizModeSelector.style.display = 'block';
    selectedLevelQuizModeText.textContent = `'${level}' 레벨 퀴즈 모드 선택`;

    const incorrectWordsCount = incorrectWordIdsByLevel[level] ? incorrectWordIdsByLevel[level].size : 0;
    startIncorrectQuizButton.textContent = `📝 오답 노트 풀기 (${incorrectWordsCount}개)`;
    startIncorrectQuizButton.disabled = incorrectWordsCount === 0;
    if (incorrectWordsCount === 0) {
        startIncorrectQuizButton.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        startIncorrectQuizButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    startRandomQuizButton.onclick = () => {
        currentQuizMode = QuizMode.RANDOM;
        selectLevel(selectedLevelForQuizMode);
    };
    startIncorrectQuizButton.onclick = () => {
        currentQuizMode = QuizMode.INCORRECT_ONLY;
        selectLevel(selectedLevelForQuizMode);
    };
    backToLevelSelectButton.onclick = () => {
        levelButtonsWrapper.style.display = 'flex';
        quizModeSelector.style.display = 'none';
    };
}

function reassignQuizViewElements() {
    currentLevelDisplay = document.getElementById('current-level-display');
    scoreDisplay = document.getElementById('score-display');
    progressBar = document.getElementById('progress-bar');
    questionNumberDisplay = document.getElementById('question-number-display');
    questionTextElement = document.getElementById('question-text');
    optionsGrid = document.getElementById('options-grid');
    feedbackMessageElement = document.getElementById('feedback-message');
    nextQuestionButton = document.getElementById('next-question-button');
    console.log("[DEBUG] Quiz view elements reassigned.");
}

function ensureQuizViewStructure() {
    if (!document.getElementById('question-text')) {
        console.warn("[DEBUG] Quiz view structure seems missing or incomplete. Restoring from initial HTML.");
        if (initialQuizViewHTML) {
            quizViewContainer.innerHTML = initialQuizViewHTML;
            reassignQuizViewElements(); 
        } else {
            console.error("[DEBUG] initialQuizViewHTML is not set. Cannot restore quiz view structure.");
            quizViewContainer.innerHTML = `
                <div class="text-center p-4 text-white">
                    <p class="text-red-300">퀴즈 화면 로드 오류. 레벨을 다시 선택해주세요.</p>
                    <button onclick="renderLevelSelector()" class="btn-primary text-white font-bold py-3 px-6 rounded-xl shadow-md">레벨 선택</button>
                </div>`;
            return false;
        }
    } else {
        reassignQuizViewElements();
    }
    return true;
}

function selectLevel(level) {
    currentQuizLevel = level;
    startQuiz();
}

function startQuiz() {
    showScreen(quizViewContainer);

    if (!ensureQuizViewStructure()) {
        return; 
    }
    
    let wordsToChooseFrom = [];
    // WORDS_DATA는 현재 로드된 단어 파일의 데이터를 사용
    const allLevelWords = WORDS_DATA.filter(word => word.level === currentQuizLevel);

    if (currentQuizMode === QuizMode.INCORRECT_ONLY) {
        const currentIncorrectIds = incorrectWordIdsByLevel[currentQuizLevel] || new Set();
        wordsToChooseFrom = Array.from(currentIncorrectIds)
                               .map(id => WORDS_DATA.find(word => word.id === id)) 
                               .filter(word => word !== undefined && word.level === currentQuizLevel); 
        
        console.log(`[DEBUG] Incorrect words for ${currentQuizLevel}:`, wordsToChooseFrom.length);

        if (wordsToChooseFrom.length === 0) {
            quizViewContainer.innerHTML = `
                <div class="text-center p-4 text-white">
                    <p class="mb-4">이 레벨(${currentQuizLevel})에는 현재 틀린 문제가 없습니다. <br/>랜덤 퀴즈에서 문제를 풀거나 다른 레벨을 선택해주세요.</p>
                    <button onclick="currentQuizMode = QuizMode.RANDOM; selectLevel('${currentQuizLevel}')" class="btn-primary text-white font-bold py-3 px-6 rounded-xl shadow-md">랜덤 퀴즈 시작</button>
                    <button onclick="renderLevelSelector()" class="glass text-white font-bold py-3 px-6 rounded-xl shadow-md mt-2">레벨 선택으로</button>
                </div>`;
            return;
        }
    } else {
        const currentAnsweredCorrectlyIds = answeredCorrectlyWordIdsByLevel[currentQuizLevel] || new Set();
        let newWords = allLevelWords.filter(word => !currentAnsweredCorrectlyIds.has(word.id));

        console.log(`[DEBUG] All words for ${currentQuizLevel}: ${allLevelWords.length}`);
        console.log(`[DEBUG] Answered correctly for ${currentQuizLevel}: ${currentAnsweredCorrectlyIds.size}`);
        console.log(`[DEBUG] New words available: ${newWords.length}`);
        
        if (newWords.length < QUESTIONS_PER_QUIZ && newWords.length < allLevelWords.length) { // 새로운 단어가 부족하고, 전체 단어보다는 적을 때
            console.warn(`[DEBUG] Not enough new words (${newWords.length}) for ${QUESTIONS_PER_QUIZ} questions. Reusing answered words.`);
            wordsToChooseFrom = allLevelWords; // 모든 단어 포함 (이전에 맞춘 단어 포함)
        } else if (newWords.length === 0 && allLevelWords.length > 0) { // 새로운 단어가 없고, 맞춘 단어만 있을 때
             console.warn(`[DEBUG] No new words. Using already answered words for ${currentQuizLevel}.`);
            wordsToChooseFrom = allLevelWords;
        }
        else { // 새로운 단어가 충분하거나, 아예 단어가 없을 경우 (이 경우 아래에서 처리)
            wordsToChooseFrom = newWords;
        }
    }
    
    // 실제 출제할 문제 수는 QUESTIONS_PER_QUIZ와 선택된 단어 수 중 작은 값으로 제한
    const numQuestionsToAsk = Math.min(QUESTIONS_PER_QUIZ, wordsToChooseFrom.length);
    currentQuestions = shuffleArray(wordsToChooseFrom).slice(0, numQuestionsToAsk);
    
    console.log(`[DEBUG] Final questions for quiz (max ${numQuestionsToAsk}): ${currentQuestions.length}`);

    if (currentQuestions.length === 0) {
        let message = `선택하신 '${currentQuizLevel}' 레벨에 출제할 문제가 현재 없습니다.`;
        if(allLevelWords.length > 0 && currentQuizMode === QuizMode.RANDOM) {
            message = `선택하신 '${currentQuizLevel}' 레벨의 모든 문제를 다 푸셨습니다! <br/>진행 상황을 초기화하거나 다른 레벨/단어장을 선택해보세요.`;
        } else if (allLevelWords.length === 0) {
             message = `선택하신 '${currentQuizLevel}' 레벨에 단어가 전혀 없습니다. <br/>다른 레벨을 선택하시거나, 단어장 파일을 확인해주세요.`;
        }

        quizViewContainer.innerHTML = `
            <div class="text-center p-4 text-white">
                <p class="text-red-300 mb-4">${message}</p>
                <button onclick="renderLevelSelector()" class="btn-primary text-white font-bold py-3 px-6 rounded-xl shadow-md">레벨 선택으로 돌아가기</button>
            </div>`;
        return;
    }
    
    currentQuestionIndex = 0;
    score = 0;
    renderQuestion();
}

function renderQuestion() {
    isAnswered = false;

    if (currentQuestionIndex >= currentQuestions.length) {
        renderResultScreen();
        return;
    }

    feedbackMessageElement.style.display = 'none';
    feedbackMessageElement.className = 'text-white p-4 rounded-2xl text-center font-bold text-lg shadow-xl'; 
    feedbackMessageElement.innerHTML = '';
    nextQuestionButton.style.display = 'none';
    optionsGrid.innerHTML = '';

    const questionData = currentQuestions[currentQuestionIndex];
    questionTextElement.textContent = `${questionData.english}`;
    currentLevelDisplay.textContent = `${currentQuizLevel} 퀴즈`;
    scoreDisplay.textContent = `점수: ${score} / ${currentQuestions.length}`;
    
    const progressPercent = ((currentQuestionIndex) / currentQuestions.length) * 100;
    progressBar.style.width = `${progressPercent}%`;
    questionNumberDisplay.textContent = `문제 ${currentQuestionIndex + 1} / ${currentQuestions.length}`;

    const options = generateOptions(questionData);
    options.forEach(optionText => {
        const optionButton = document.createElement('button');
        optionButton.innerHTML = `<span>${optionText}</span>`; 
        optionButton.classList.add('quiz-option-button', 'default'); 
        optionButton.onclick = (event) => handleAnswer(event.currentTarget, optionText, questionData.korean);
        optionsGrid.appendChild(optionButton);
    });
}

function generateOptions(correctWord) {
    const numOptions = (typeof OPTIONS_COUNT !== 'undefined') ? OPTIONS_COUNT : 4;
    const correctAnswer = correctWord.korean;

    // 현재 로드된 WORDS_DATA에서만 오답 후보를 찾음
    let distractors = WORDS_DATA
        .filter(word => word.korean !== correctAnswer && word.level === correctWord.level) // 같은 레벨에서 우선 찾기
        .map(word => word.korean);

    if (distractors.length < numOptions - 1) {
        // 같은 레벨에서 부족하면, 전체 WORDS_DATA에서 다른 레벨 단어도 포함 (단, 현재 정답과 중복되지 않게)
        const globalDistractors = WORDS_DATA
            .filter(word => word.korean !== correctAnswer && !distractors.includes(word.korean))
            .map(word => word.korean);
        distractors = [...new Set([...distractors, ...shuffleArray(globalDistractors)])]; // 섞어서 추가
    }

    distractors = shuffleArray(distractors).slice(0, numOptions - 1);

    let tempDistractorCount = 1;
    while (distractors.length < numOptions - 1) {
        const tempDist = `오답${tempDistractorCount++}`; // 임시 오답
        if (tempDist !== correctAnswer && !distractors.includes(tempDist)) {
            distractors.push(tempDist);
        } else if (tempDistractorCount > 200) { // 무한 루프 방지
            console.warn("Could not generate enough unique distractors. Using generic fallbacks.");
            for (let i = distractors.length; i < numOptions - 1; i++) {
                distractors.push(`선택지 ${i + 2}`);
            }
            break; 
        }
    }

    const finalOptions = shuffleArray([correctAnswer, ...distractors]);
    return finalOptions.slice(0, numOptions); // 최종 옵션 개수 보장
}


function handleAnswer(selectedButton, selectedAnswer, correctAnswer) {
    if (isAnswered) return;
    isAnswered = true;
    
    const optionButtons = Array.from(optionsGrid.children);
    optionButtons.forEach(btn => {
        btn.classList.add('answered'); 
        btn.onclick = null;
        btn.classList.remove('default'); 

        const textSpan = btn.querySelector('span'); 
        const originalText = textSpan ? textSpan.textContent : btn.textContent; 
        let iconToShow = '';

        if (originalText === correctAnswer) { 
            btn.classList.add('correct'); 
            iconToShow = `<span class="absolute right-3 top-1/2 -translate-y-1/2 text-white">${svgIconCheck}</span>`;
        } else if (btn === selectedButton) { 
            btn.classList.add('incorrect'); 
            iconToShow = `<span class="absolute right-3 top-1/2 -translate-y-1/2 text-white">${svgIconX}</span>`;
        } else { 
            btn.classList.add('unselected-after-reveal');
        }
        btn.innerHTML = `<span>${originalText}</span>${iconToShow}`; 
    });

    const currentQuestionId = currentQuestions[currentQuestionIndex].id;
    let feedbackIconHTML = '';

    if (selectedAnswer === correctAnswer) {
        score++;
        feedbackIconHTML = `<span class="text-2xl mr-3">${svgIconCheckCircleLarge}</span>`;
        feedbackMessageElement.innerHTML = `<div class="flex items-center justify-center">${feedbackIconHTML}<span>정답입니다! 훌륭해요!</span></div>`;
        feedbackMessageElement.classList.add('feedback-success'); 
        feedbackMessageElement.classList.remove('feedback-error');

        if (!answeredCorrectlyWordIdsByLevel[currentQuizLevel]) {
            answeredCorrectlyWordIdsByLevel[currentQuizLevel] = new Set();
        }
        answeredCorrectlyWordIdsByLevel[currentQuizLevel].add(currentQuestionId);

        if (incorrectWordIdsByLevel[currentQuizLevel] && incorrectWordIdsByLevel[currentQuizLevel].has(currentQuestionId)) {
            incorrectWordIdsByLevel[currentQuizLevel].delete(currentQuestionId);
        }
    } else {
        feedbackIconHTML = `<span class="text-2xl mr-3">${svgIconXCircleLarge}</span>`;
        feedbackMessageElement.innerHTML = `<div class="flex items-center justify-center">${feedbackIconHTML}<span>틀렸습니다. 정답: "${correctAnswer}"</span></div>`;
        feedbackMessageElement.classList.add('feedback-error');
        feedbackMessageElement.classList.remove('feedback-success');

        if (!incorrectWordIdsByLevel[currentQuizLevel]) {
            incorrectWordIdsByLevel[currentQuizLevel] = new Set();
        }
        incorrectWordIdsByLevel[currentQuizLevel].add(currentQuestionId);
    }
    feedbackMessageElement.style.display = 'block'; 
    nextQuestionButton.style.display = 'block';

    const nextButtonTextSpan = nextQuestionButton.querySelector('span'); // nextQuestionButton 내부의 span을 직접 찾도록 수정
    const nextButtonSvg = nextQuestionButton.querySelector('svg'); // nextQuestionButton 내부의 svg를 직접 찾도록 수정

    if (currentQuestionIndex >= currentQuestions.length - 1) {
        if(nextButtonTextSpan) nextButtonTextSpan.textContent = '결과 보기';
        if(nextButtonSvg) nextButtonSvg.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.25 4.5l7.5 7.5-7.5 7.5m-6-15l7.5 7.5-7.5 7.5" />`; 
    } else {
        if(nextButtonTextSpan) nextButtonTextSpan.textContent = '다음 문제로';
        if(nextButtonSvg) nextButtonSvg.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>`; 
    }
    saveProgress();
}

function renderResultScreen() {
    showScreen(resultScreenContainer);
    const threshold = (typeof LEVEL_UP_THRESHOLD_PERCENTAGE !== 'undefined') ? LEVEL_UP_THRESHOLD_PERCENTAGE : 70;
    const percentage = currentQuestions.length > 0 ? (score / currentQuestions.length) * 100 : 0;
    const passed = percentage >= threshold;

    resultLevel.textContent = `${currentQuizLevel} 결과`;
    resultPercentage.textContent = `${percentage.toFixed(0)}%`;
    resultScore.textContent = `${score} / ${currentQuestions.length} 문제 정답`;

    resultDetails.classList.remove('feedback-success', 'feedback-error', 'glass'); 
    resultDetails.classList.add('glass'); 
    if (passed) {
        resultDetails.classList.add('feedback-success');
    } else {
        resultDetails.classList.add('feedback-error');
    }
    resultPercentage.classList.add('text-white'); 
    resultScore.classList.add('text-white/80');

    resultMessageIcon.innerHTML = passed ? svgIconCheckCircleLarge : svgIconXCircleLarge;
    resultMessage.classList.remove('text-green-700', 'text-red-700'); 
    resultMessage.classList.add('text-white'); 
    resultMessageText.textContent = passed ? '축하합니다! 레벨을 통과했습니다.' : `아쉬워요! (${threshold}% 이상 필요)`;
    
    const currentLevelIdx = LEVEL_ORDER.indexOf(currentQuizLevel);
    if (passed && currentLevelIdx < LEVEL_ORDER.length - 1) {
        const nextLevel = LEVEL_ORDER[currentLevelIdx + 1];
        
        // 다음 레벨 버튼을 표시하기 전에, 해당 레벨의 단어가 WORDS_DATA에 실제로 있는지 확인
        const wordsForNextLevel = WORDS_DATA.filter(word => word.level === nextLevel);
        if (wordsForNextLevel.length > 0) {
            unlockedLevels.add(nextLevel); 
            saveProgress(); 
            resultMessageText.textContent += ` 다음 '${nextLevel}' 레벨로 도전해보세요!`;
            proceedNextLevelButton.style.display = 'inline-flex';
            
            proceedNextLevelButton.classList.add('btn-success');
            proceedNextLevelButton.classList.remove('btn-primary', 'glass');
            proceedNextLevelButton.innerHTML = `<span class="flex items-center justify-center">
                                                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                                                    </svg>
                                                    다음 레벨 (${nextLevel})
                                                </span>`;
            proceedNextLevelButton.onclick = () => {
                currentQuizMode = QuizMode.RANDOM;
                selectLevel(nextLevel);
            };
        } else {
             resultMessageText.textContent += ` 다음 '${nextLevel}' 레벨의 단어가 현재 단어장에 없습니다.`;
             proceedNextLevelButton.style.display = 'none';
        }
    } else if (passed && currentLevelIdx === LEVEL_ORDER.length - 1) {
        resultMessageText.textContent = '모든 레벨을 통과했습니다! 대단해요!';
        proceedNextLevelButton.style.display = 'none';
    } else {
        proceedNextLevelButton.style.display = 'none';
    }

    retryQuizButton.onclick = () => startQuiz(); 
    backToLevelsButton.onclick = renderLevelSelector; 

    retryQuizButton.classList.add('btn-primary');
    retryQuizButton.classList.remove('btn-success', 'glass');
    backToLevelsButton.classList.add('glass');
    backToLevelsButton.classList.remove('btn-primary', 'btn-success');
}

function loadProgress() {
    try {
        const storedLevels = localStorage.getItem('simpleQuizUnlockedLevels');
        if (storedLevels) {
            unlockedLevels = new Set(JSON.parse(storedLevels));
            console.log("[DEBUG] Loaded unlocked levels:", Array.from(unlockedLevels));
        } else {
            if (typeof LEVEL_ORDER !== 'undefined' && LEVEL_ORDER.length > 0) {
                // 현재 로드된 단어장에 실제로 데이터가 있는 첫 번째 레벨만 잠금 해제
                // 또는 모든 레벨을 기본으로 열어두려면 new Set(LEVEL_ORDER)
                let firstAvailableLevel = null;
                for (const level of LEVEL_ORDER) {
                    if (WORDS_DATA && WORDS_DATA.some(word => word.level === level)) {
                        firstAvailableLevel = level;
                        break;
                    }
                }
                if (firstAvailableLevel) {
                    unlockedLevels = new Set([firstAvailableLevel]);
                } else { // 사용 가능한 레벨이 없으면 빈 Set
                    unlockedLevels = new Set();
                }
                console.log("[DEBUG] No saved progress found. Unlocking default available levels:", Array.from(unlockedLevels));
            } else {
                unlockedLevels = new Set();
                console.log("[DEBUG] No saved progress and LEVEL_ORDER is not available. Initializing with empty unlocked levels.");
            }
        }

        const storedAnsweredCorrectlyWords = localStorage.getItem('simpleQuizAnsweredCorrectlyWords');
        if (storedAnsweredCorrectlyWords) {
            const parsedData = JSON.parse(storedAnsweredCorrectlyWords);
            for (const level in parsedData) {
                answeredCorrectlyWordIdsByLevel[level] = new Set(parsedData[level]);
            }
            console.log("[DEBUG] Loaded answered correctly word IDs:", answeredCorrectlyWordIdsByLevel);
        } else {
            answeredCorrectlyWordIdsByLevel = {};
        }

        const storedIncorrectWords = localStorage.getItem('simpleQuizIncorrectWords');
        if (storedIncorrectWords) {
            const parsedData = JSON.parse(storedIncorrectWords);
            for (const level in parsedData) {
                incorrectWordIdsByLevel[level] = new Set(parsedData[level]);
            }
            console.log("[DEBUG] Loaded incorrect word IDs:", incorrectWordIdsByLevel);
        } else {
            incorrectWordIdsByLevel = {};
        }

    } catch (e) {
        console.error("Failed to load progress from localStorage:", e);
        if (typeof LEVEL_ORDER !== 'undefined' && LEVEL_ORDER.length > 0 && WORDS_DATA && WORDS_DATA.some(word => word.level === LEVEL_ORDER[0])) {
            unlockedLevels.add(LEVEL_ORDER[0]);
        }
        answeredCorrectlyWordIdsByLevel = {}; 
        incorrectWordIdsByLevel = {};         
    }
}

function saveProgress() {
    localStorage.setItem('simpleQuizUnlockedLevels', JSON.stringify(Array.from(unlockedLevels)));
    console.log("[DEBUG] Saved unlocked levels:", Array.from(unlockedLevels));

    const serializableAnsweredCorrectly = {};
    for (const level in answeredCorrectlyWordIdsByLevel) {
        serializableAnsweredCorrectly[level] = Array.from(answeredCorrectlyWordIdsByLevel[level]);
    }
    localStorage.setItem('simpleQuizAnsweredCorrectlyWords', JSON.stringify(serializableAnsweredCorrectly));
    console.log("[DEBUG] Saved answered correctly word IDs:", answeredCorrectlyWordIdsByLevel);

    const serializableIncorrect = {};
    for (const level in incorrectWordIdsByLevel) {
        serializableIncorrect[level] = Array.from(incorrectWordIdsByLevel[level]);
    }
    localStorage.setItem('simpleQuizIncorrectWords', JSON.stringify(serializableIncorrect));
    console.log("[DEBUG] Saved incorrect word IDs:", serializableIncorrect);
}


// --- 단어장 동적 로드 함수 ---
let currentWordSetFile = null; // 현재 로드된 단어 파일명 저장

function loadWordSet(fileName, callback, errorCallback) {
    wordSetLoadingMessage.style.display = 'block';
    wordSetErrorMessage.style.display = 'none';
    wordSetErrorMessage.textContent = '';

    const existingScript = document.querySelector('script[data-wordset="true"]');
    if (existingScript) {
        console.log(`[DEBUG] Removing existing word set script: ${existingScript.src}`);
        existingScript.remove();
        window.WORDS_DATA = undefined;
        window.LEVEL_ORDER = undefined;
        window.DifficultyLevel = undefined;
        window.QUESTIONS_PER_QUIZ = undefined;
        window.OPTIONS_COUNT = undefined;
        window.LEVEL_UP_THRESHOLD_PERCENTAGE = undefined;
        console.log("[DEBUG] Cleared global word set variables.");
    }

    const script = document.createElement('script');
    script.src = fileName;
    script.setAttribute('data-wordset', 'true');
    script.async = true;

    script.onload = () => {
        console.log(`[DEBUG] ${fileName} loaded successfully.`);
        wordSetLoadingMessage.style.display = 'none';
        currentWordSetFile = fileName; // 현재 로드된 파일명 업데이트
        
        if (typeof WORDS_DATA !== 'undefined' && 
            typeof LEVEL_ORDER !== 'undefined' &&
            typeof DifficultyLevel !== 'undefined' &&
            typeof QUESTIONS_PER_QUIZ !== 'undefined' &&
            typeof OPTIONS_COUNT !== 'undefined' &&
            typeof LEVEL_UP_THRESHOLD_PERCENTAGE !== 'undefined'
            ) {
            callback();
        } else {
            const errorMsg = `${fileName} 파일은 로드되었으나, 필수 변수(WORDS_DATA, LEVEL_ORDER, 등)가 없습니다. 파일 내용을 확인해주세요.`;
            console.error(errorMsg);
            if(errorCallback) errorCallback(errorMsg);
        }
    };

    script.onerror = (event) => {
        const errorMsg = `오류: ${fileName} 파일을 로드할 수 없습니다. 파일 경로 및 네트워크를 확인해주세요. (경로: ${event.target.src})`;
        console.error(errorMsg, event);
        wordSetLoadingMessage.style.display = 'none';
        if(errorCallback) errorCallback(errorMsg);
    };

    document.head.appendChild(script);
}

// --- 앱 시작 로직 (단어장 선택부터) ---
function startApplication() {
    wordSetButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            if (e.currentTarget.disabled) return;

            const fileName = e.currentTarget.dataset.wordsfile;
            if (fileName) {
                // 만약 동일한 단어장을 다시 클릭하면, 초기화 후 다시 로드할지 결정 (여기서는 항상 새로 로드)
                // if (fileName === currentWordSetFile && typeof WORDS_DATA !== 'undefined') {
                //     console.log(`[DEBUG] Word set ${fileName} is already loaded. Proceeding to initializeApp.`);
                //     wordSetSelectorContainer.style.display = 'none';
                //     quizArea.style.display = 'block';
                //     if(appFooter) appFooter.style.display = 'block';
                //     initializeApp();
                //     return;
                // }

                loadWordSet(
                    fileName,
                    () => { 
                        wordSetSelectorContainer.style.display = 'none';
                        quizArea.style.display = 'block';
                        if(appFooter) appFooter.style.display = 'block';
                        initializeApp();
                    },
                    (errorMsg) => { 
                        wordSetErrorMessage.textContent = errorMsg;
                        wordSetErrorMessage.style.display = 'block';
                    }
                );
            }
        });
    });

    if (wordSetSelectorContainer) wordSetSelectorContainer.style.display = 'block';
    if (quizArea) quizArea.style.display = 'none';
    if (appFooter) appFooter.style.display = 'none';
}


// --- 앱 초기화 (단어장 로드 후 호출) ---
function initializeApp() {
    if (typeof WORDS_DATA === 'undefined' || typeof LEVEL_ORDER === 'undefined' || 
        typeof DifficultyLevel === 'undefined' || typeof QUESTIONS_PER_QUIZ === 'undefined' || 
        typeof OPTIONS_COUNT === 'undefined' || typeof LEVEL_UP_THRESHOLD_PERCENTAGE === 'undefined') {
        
        const criticalErrorMsg = `오류: 선택된 단어장 파일에서 필수 설정값을 읽어올 수 없습니다. 단어장 파일 내용을 확인하거나 다른 단어장을 선택해주세요.`;
        
        if (quizArea) {
            quizArea.innerHTML = `
                <div class="text-center p-4 text-white">
                    <p class="text-red-300 text-lg">${criticalErrorMsg}</p>
                    <button onclick="window.location.reload()" class="mt-6 btn-primary text-white font-bold py-3 px-6 rounded-xl shadow-md">
                        페이지 새로고침
                    </button>
                </div>`;
            quizArea.style.display = 'block';
        } else {
            document.body.innerHTML = `<div class="min-h-screen flex flex-col items-center justify-center p-4 text-white"><p class="text-red-300 text-lg">${criticalErrorMsg}</p></div>`;
        }
        console.error("Critical variables from the loaded word set are missing. Initialization aborted.");
        return;
    }
    
    const tempQuizViewContainer = document.getElementById('quiz-view-container');
    if (tempQuizViewContainer) {
        // quizViewContainer의 내용을 바꾸기 전에 초기 HTML을 저장해야 함.
        // 만약 이미 저장되어 있고, 단어장만 바뀐다면 다시 저장할 필요는 없음.
        if (!initialQuizViewHTML) {
            initialQuizViewHTML = tempQuizViewContainer.innerHTML;
            console.log("[DEBUG] Initial quiz view HTML saved.");
        } else {
             // 단어장이 바뀌면, quizViewContainer를 초기 상태로 되돌릴 필요가 있을 수 있음.
             // 여기서는 ensureQuizViewStructure 함수가 이 역할을 하므로, initialQuizViewHTML을 다시 설정할 필요는 없음.
             console.log("[DEBUG] Initial quiz view HTML already exists.");
        }
    } else {
        console.error("[DEBUG] initializeApp: quiz-view-container not found. Cannot save initial HTML.");
        if(quizArea) {
            quizArea.innerHTML = `<p class="text-red-300 text-center text-lg">퀴즈 UI(#quiz-view-container)를 찾을 수 없습니다. HTML 구조를 확인해주세요.</p>`;
            quizArea.style.display = 'block';
        }
        return;
    }
    
    reassignQuizViewElements(); 

    if (nextQuestionButton) {
        const newNextButton = nextQuestionButton.cloneNode(true); // Clean event listeners
        nextQuestionButton.parentNode.replaceChild(newNextButton, nextQuestionButton);
        nextQuestionButton = newNextButton;

        nextQuestionButton.addEventListener('click', function() {
            console.log("[DEBUG] Next question button clicked.");
            currentQuestionIndex++;
            renderQuestion();
        });
    } else {
        console.error("[DEBUG] nextQuestionButton not found during initializeApp.");
    }
    
    if (resetProgressButton) {
        resetProgressButton.onclick = () => {
            if (confirm("정말로 모든 진행 상황을 초기화하시겠습니까? (레벨 잠금 해제, 정답/오답 문제 기록이 모두 초기화됩니다)")) {
                localStorage.removeItem('simpleQuizUnlockedLevels'); 
                localStorage.removeItem('simpleQuizAnsweredCorrectlyWords');
                localStorage.removeItem('simpleQuizIncorrectWords');
                
                unlockedLevels = new Set();
                answeredCorrectlyWordIdsByLevel = {};
                incorrectWordIdsByLevel = {};

                loadProgress(); // 로드하면 WORDS_DATA를 기반으로 기본 잠금 해제 진행
                renderLevelSelector(); 
                const notification = document.createElement('div');
                notification.textContent = '진행 상황이 초기화되었습니다.';
                notification.className = 'fixed bottom-4 right-4 glass text-white p-3 rounded-lg shadow-md animate-pulse z-50';
                document.body.appendChild(notification);
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
        };
    } else {
        console.error("[DEBUG] resetProgressButton not found during initializeApp.");
    }

    loadProgress(); 
    renderLevelSelector();
}

document.addEventListener('DOMContentLoaded', startApplication);