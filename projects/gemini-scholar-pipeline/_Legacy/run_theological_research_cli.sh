#!/bin/bash
# Phase 0: Theological Research Session (Gemini CLI)
# Gemini CLI를 사용하여 theological_research v1.3 프로토콜 실행
# 페르소나 폴더를 컨텍스트로 포함
#
# 사용법: ./run_theological_research_cli.sh "셰키나"

set -e

cd "$(dirname "$0")"

TOPIC="${1:-}"

if [ -z "$TOPIC" ]; then
    echo "사용법: ./run_theological_research_cli.sh [주제]"
    echo "예시: ./run_theological_research_cli.sh 셰키나"
    exit 1
fi

# 경로 설정
PROMPT_FILE="prompts/theological_research.md"
PERSONAS_DIR="/Users/msn/Desktop/project/theological_research/personas"
OUTPUTS_DIR="/Users/msn/Desktop/project/theological_research/research_outputs"

# 출력 디렉토리 생성
mkdir -p "$OUTPUTS_DIR"

# 프롬프트 파일 확인
if [ ! -f "$PROMPT_FILE" ]; then
    echo "❌ 프롬프트 파일이 없습니다: $PROMPT_FILE"
    exit 1
fi

# 프롬프트 로드 및 주제 치환
PROMPT=$(cat "$PROMPT_FILE" | sed "s/{{.Input}}/$TOPIC/g")

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Phase 0: Theological Research Session (Gemini CLI)       ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Protocol: Adversarial Rationality v1.3                    ║"
echo "║  Topic: $TOPIC"
echo "║  Mode: Gemini CLI + Personas Context"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 페르소나 폴더: $PERSONAS_DIR"
echo "📄 프롬프트 크기: $(echo "$PROMPT" | wc -c | tr -d ' ') 문자"
echo ""

# 프롬프트를 클립보드에 복사
echo "$PROMPT" | pbcopy
echo "✅ 프롬프트가 클립보드에 복사되었습니다!"
echo ""

# Gemini CLI 실행 (프롬프트 없이 시작)
echo "🚀 Gemini CLI 실행..."
echo ""
echo "📝 작업 순서:"
echo "   1. /model 입력 → 원하는 모델 선택"
echo "   2. 붙여넣기 (Cmd+V) → Enter"
echo "   3. 각 단계 응답 후 진행"
echo ""

gemini --include-directories "$PERSONAS_DIR"

# 결과물 저장 안내
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Phase 0 Session Complete                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 결과물을 저장하려면:"
echo "   최종 결과를 복사하여 아래 파일에 저장하세요:"
echo "   $OUTPUTS_DIR/${TOPIC}_research.md"
echo ""
echo "다음 단계:"
echo "   Option A: ./run_depth_enhance.sh $TOPIC"
echo "   Option B: ./run.sh account3 $TOPIC"
