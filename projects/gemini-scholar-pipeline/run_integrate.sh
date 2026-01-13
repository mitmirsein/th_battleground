#!/bin/bash
# Footnote Integration Session (Phase 4)
# 브라우저 에이전틱 방식으로 각주 통합

cd "$(dirname "$0")"

TOPIC="${1:-research}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Footnote Integration Session (Phase 4)                    ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  주제: $TOPIC"
echo "║  입력: reports/${TOPIC}_raw.md + results/${TOPIC}.md"
echo "║  출력: reports/${TOPIC}_annotated.md"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 파일 존재 확인
if [ ! -f "reports/${TOPIC}_raw.md" ]; then
    echo "❌ 리포트 파일이 없습니다: reports/${TOPIC}_raw.md"
    exit 1
fi

if [ ! -f "results/${TOPIC}.md" ]; then
    echo "❌ Scholar 결과가 없습니다: results/${TOPIC}.md"
    exit 1
fi

source venv.nosync/bin/activate
python integration_session.py "$TOPIC"
