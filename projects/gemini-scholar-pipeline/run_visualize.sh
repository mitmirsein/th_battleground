#!/bin/bash
# Phase 6: Report Visualization
# Markdown → Interactive HTML 변환
#
# Usage: ./run_visualize.sh {topic} [--mode full|condensed|both] [--suffix _research]
# Example: ./run_visualize.sh justification
#          ./run_visualize.sh justification --mode condensed
#          ./run_visualize.sh justification --suffix _research
#
# Input:
#   - reports/{topic}_final.md (또는 _annotated.md)
#   - reports/{topic}_footnotes.json
#
# Output:
#   - reports/{topic}[suffix]_report.html (full)
#   - reports/{topic}[suffix]_brief.html (condensed)

set -e

TOPIC=""
MODE_VALUE="both"
SUFFIX=""

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE_VALUE="$2"
            shift 2
            ;;
        --suffix)
            SUFFIX="$2"
            shift 2
            ;;
        *)
            if [ -z "$TOPIC" ]; then
                TOPIC="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$TOPIC" ]; then
    echo "Usage: ./run_visualize.sh {topic} [--mode full|condensed|both] [--suffix _research]"
    echo "Example: ./run_visualize.sh justification"
    echo "         ./run_visualize.sh justification --mode condensed"
    echo "         ./run_visualize.sh justification --suffix _research"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 가상환경 활성화
source venv.nosync/bin/activate

echo "================================"
echo "Phase 6: Report Visualization"
echo "Topic: $TOPIC"
echo "Mode: $MODE_VALUE"
if [ -n "$SUFFIX" ]; then
    echo "Suffix: $SUFFIX"
fi
echo "================================"

# 입력 파일 확인
if [ ! -f "reports/${TOPIC}_final.md" ] && [ ! -f "reports/${TOPIC}_annotated.md" ]; then
    echo "Error: No input file found."
    echo "Expected: reports/${TOPIC}_final.md or reports/${TOPIC}_annotated.md"
    exit 1
fi

# 실행
python visualize_session.py --topic "$TOPIC" --mode "$MODE_VALUE" --suffix "$SUFFIX"

echo ""
echo "Output files:"
if [[ "$MODE_VALUE" == "full" || "$MODE_VALUE" == "both" ]]; then
    echo "  Full: reports/${TOPIC}${SUFFIX}_report.html"
fi
if [[ "$MODE_VALUE" == "condensed" || "$MODE_VALUE" == "both" ]]; then
    echo "  Brief: reports/${TOPIC}${SUFFIX}_brief.html"
fi
echo ""
echo "To view, run:"
echo "  open reports/${TOPIC}${SUFFIX}_report.html"

