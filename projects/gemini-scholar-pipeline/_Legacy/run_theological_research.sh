#!/bin/bash
# Phase 0: Theological Research Session
# theological_research v1.3 프롬프트를 Gemini에서 실행
#
# 사용법: ./run_theological_research.sh "셰키나"

set -e

cd "$(dirname "$0")"

TOPIC="${1:-}"

if [ -z "$TOPIC" ]; then
    echo "사용법: ./run_theological_research.sh [주제]"
    echo "예시: ./run_theological_research.sh 셰키나"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Phase 0: Theological Research Session                     ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Protocol: Adversarial Rationality v1.3                    ║"
echo "║  Topic: $TOPIC"
echo "║  Account: account1 (유료)"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 가상환경 활성화
if [ -d "venv" ]; then
    source venv.nosync/bin/activate
fi

# 프롬프트 파일 확인
if [ ! -f "prompts/theological_research.md" ]; then
    echo "❌ 프롬프트 파일이 없습니다: prompts/theological_research.md"
    exit 1
fi

# 출력 디렉토리 생성
mkdir -p theological_outputs

# 실행
python theological_research_session.py "$TOPIC"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Phase 0 Complete                                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📄 결과물: theological_outputs/${TOPIC}_research.md"
echo ""
echo "다음 단계:"
echo "   Option A: ./run_depth_enhance.sh $TOPIC"
echo "   Option B: ./run.sh account3 $TOPIC"
