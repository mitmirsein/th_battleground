#!/bin/bash

# Phase 1.5: Academic Depth Enhancement
# 학술 깊이 강화 - Deep Research 출력의 약한 섹션 심화

set -e

PROFILE=$1
TOPIC=$2

if [ -z "$PROFILE" ] || [ -z "$TOPIC" ]; then
    echo "Usage: ./run_depth_enhance.sh <profile> <topic>"
    echo "Example: ./run_depth_enhance.sh account1 schechina"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Phase 1.5: Academic Depth Enhancement                    ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  프로필: $PROFILE"
echo "║  주제: $TOPIC"
echo "║  입력: reports/${TOPIC}_raw.md"
echo "║  출력: reports/${TOPIC}_enhanced.md"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 입력 파일 확인
if [ ! -f "reports/${TOPIC}_raw.md" ]; then
    echo "❌ 오류: reports/${TOPIC}_raw.md 파일이 없습니다."
    echo "먼저 Phase 1 (Deep Research)를 실행하세요."
    exit 1
fi

# 가상환경 활성화
source venv.nosync/bin/activate

# Phase 1.5 실행
python depth_enhance_session.py "$PROFILE" "$TOPIC"

echo ""
echo "✅ 완료: reports/${TOPIC}_enhanced.md"
echo ""
echo "💡 다음 단계: ./run_query_gen.sh $TOPIC"

