#!/bin/bash
# Phase 2 전용: 질문 생성만 실행
# 사용법: ./run_query_gen.sh {주제명}
#
# 입력: reports/{주제명}_raw.md
# 출력: query.txt

set -e

if [ -z "$1" ]; then
    echo "사용법: ./run_query_gen.sh {주제명}"
    echo ""
    echo "📌 리포트 파일이 다음 위치에 있어야 합니다:"
    echo "   reports/{주제명}_raw.md"
    exit 1
fi

TOPIC=$1
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT_FILE="$SCRIPT_DIR/reports/${TOPIC}_raw.md"

if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ 리포트 파일을 찾을 수 없습니다: $REPORT_FILE"
    echo ""
    echo "📌 리포트를 다음 위치에 저장해주세요:"
    echo "   cp your_report.md reports/${TOPIC}_raw.md"
    exit 1
fi

echo "📄 입력 리포트: $REPORT_FILE"
echo ""

cd "$SCRIPT_DIR"
source venv.nosync/bin/activate
python query_gen_session.py "$TOPIC"
