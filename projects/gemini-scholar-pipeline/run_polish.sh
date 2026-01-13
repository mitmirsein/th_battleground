#!/bin/bash
# Phase 5: 문체 개선 실행
# 사용법: ./run_polish.sh <topic>

TOPIC=${1:-"research"}

echo "=================================="
echo "  Phase 5: 문체 개선"
echo "  Topic: $TOPIC"
echo "=================================="

# 입력 파일 확인
if [ ! -f "reports/${TOPIC}_annotated.md" ]; then
    echo "❌ 오류: reports/${TOPIC}_annotated.md 파일이 없습니다."
    echo "   먼저 Phase 4 (./run_integrate.sh $TOPIC)를 실행하세요."
    exit 1
fi

# 가상환경 활성화
source venv.nosync/bin/activate

# 실행
python polish_session.py "$TOPIC"

echo ""
echo "✅ 완료: reports/${TOPIC}_final.md"
