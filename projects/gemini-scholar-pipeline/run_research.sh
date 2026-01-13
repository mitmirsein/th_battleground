#!/bin/bash
# Gemini Research Session (Phase 1 + 2 통합)
# 하나의 브라우저에서 Deep Research + Query Generation 수행

cd "$(dirname "$0")"

TOPIC="${1:-research}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Gemini Research Session (Phase 1 + 2)                     ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  주제: $TOPIC"
echo "║  프로필: account1 (유료 계정)"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

source venv.nosync/bin/activate
python gemini_research_session.py "$TOPIC"
