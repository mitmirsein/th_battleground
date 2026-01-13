#!/bin/bash
# Theological Research Visualization
# research_outputs/*.md → Interactive HTML 변환
#
# Usage: ./run_visualize.sh {topic}
# Example: ./run_visualize.sh Schechina

set -e

TOPIC="${1:-}"

if [ -z "$TOPIC" ]; then
    echo "Usage: ./run_visualize.sh {topic}"
    echo "Example: ./run_visualize.sh Schechina"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# venv 활성화 (심볼릭 링크)
source venv.nosync/bin/activate

# reports 폴더 생성 (visualize_session.py 기본 경로)
mkdir -p reports

echo "================================"
echo "Theological Research Visualization"
echo "Topic: $TOPIC"
echo "================================"

# 입력 파일 확인
INPUT_FILE="research_outputs/${TOPIC}_research.md"
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

# reports 폴더로 복사 (visualize_session.py 기대 경로)
cp "$INPUT_FILE" "reports/${TOPIC}_final.md"

# 시각화 실행
python visualize_session.py --topic "$TOPIC" --mode both

# 결과물을 research_outputs로 이동
mv "reports/${TOPIC}_report.html" "research_outputs/${TOPIC}_report.html" 2>/dev/null || true
mv "reports/${TOPIC}_brief.html" "research_outputs/${TOPIC}_brief.html" 2>/dev/null || true

echo ""
echo "✅ 시각화 완료!"
echo ""
echo "Output:"
echo "  research_outputs/${TOPIC}_report.html"
echo "  research_outputs/${TOPIC}_brief.html"
echo ""
echo "To view:"
echo "  open research_outputs/${TOPIC}_report.html"
