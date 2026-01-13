#!/bin/bash
# MLA 인용 정제 스크립트 실행

cd "$(dirname "$0")"

echo "🧹 MLA 인용 정제 시작"
echo ""

source venv.nosync/bin/activate
python clean_citations.py "$@"
