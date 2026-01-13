#!/bin/bash
# Google Scholar Labs Agent 간편 실행 스크립트

# 스크립트 위치로 이동
cd "$(dirname "$0")"

# 기본값 설정
PROFILE="${1:-account1}"
JOB="${2:-research}"
QUERY_FILE="${3:-query.txt}"

echo "🔍 Scholar Labs Agent 실행"
echo "   프로필: $PROFILE"
echo "   작업명: $JOB"
echo "   쿼리파일: $QUERY_FILE"
echo ""

# venv 활성화 후 실행
source venv.nosync/bin/activate
python scholar_labs_agent.py --query-file "$QUERY_FILE" --profile "$PROFILE" --job "$JOB"
