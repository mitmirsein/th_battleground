#!/bin/bash
# 전체 연구 파이프라인 오케스트레이터
#
# Phase 1+2: Gemini 통합 세션 (account1 유료 계정)
# Phase 3: Scholar Labs 검색 (유연한 계정)

set -e  # 오류 발생 시 중단

cd "$(dirname "$0")"

DEEP_MODE="false"
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --deep)
      DEEP_MODE="true"
      shift # past argument
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

TOPIC="${1:-research}"
SCHOLAR_ACCOUNT="${2:-account3}"  # Phase 3용 계정 (유연)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Theological Research Pipeline                             ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Topic: $TOPIC"
echo "║  Mode: $(if [ "$DEEP_MODE" = "true" ]; then echo "🔥 DEEP RESEARCH (API)"; else echo "Standard (Legacy)"; fi)"
echo "║  Phase 1+2 (Gemini): account1 (유료 고정)"
echo "║  Phase 3 (Scholar): $SCHOLAR_ACCOUNT"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Phase 1+2: Gemini Research Session (통합)
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  PHASE 1+2: Gemini Research Session                        │"
echo "│  (Deep Research → Query Generation)                        │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

if [ "$DEEP_MODE" = "true" ]; then
    echo "🚀 Executing via Gemini Deep Research API..."
    python3 deep_research_session.py "$TOPIC"
    
    # Create dummy query.txt to satisfy pipeline checks if not generated
    if [ ! -f "query.txt" ]; then
        echo "Auto-generated deep research query" > query.txt
    fi
else
    ./run_research.sh "$TOPIC"
fi

# 파일 확인
if [ ! -f "reports/${TOPIC}_raw.md" ]; then
    echo "❌ 리포트 파일이 생성되지 않았습니다."
    exit 1
fi

if [ ! -f "query.txt" ]; then
    echo "❌ query.txt 파일이 생성되지 않았습니다."
    exit 1
fi

Q_COUNT=$(grep -c "Q[0-9]" query.txt 2>/dev/null || echo "0")
echo ""
echo "✅ Phase 1+2 완료"
echo "   📄 리포트: reports/${TOPIC}_raw.md"
echo "   📄 질문: ${Q_COUNT}개"
echo ""

# Phase 3: Scholar Labs Search
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  PHASE 3: Scholar Labs Semantic Search                     │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

if [ "$DEEP_MODE" = "true" ]; then
    echo "🚀 Executing via Gemini Deep Scholar Agent (API)..."
    python3 scholar_deep_agent.py "$TOPIC"
else
    ./run.sh "$SCHOLAR_ACCOUNT" "$TOPIC"
fi

# 검색 결과 확인
if [ ! -f "results/${TOPIC}.md" ]; then
    echo "❌ 검색 결과 파일이 생성되지 않았습니다."
    exit 1
fi
echo "✅ Phase 3 완료: results/${TOPIC}.md"
echo ""

# MLA 정제
echo "🧹 MLA 인용 정제 중..."
./clean.sh "results/${TOPIC}.md"
echo ""

# Phase 4: Footnote Integration
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  PHASE 4: Footnote Integration                             │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
./run_integrate.sh "$TOPIC" "$TOPIC"

# 파일 확인
if [ ! -f "reports/${TOPIC}_annotated.md" ]; then
    echo "❌ 각주 통합 파일이 생성되지 않았습니다."
    exit 1
fi
echo "✅ Phase 4 완료: reports/${TOPIC}_annotated.md"
echo ""

# Phase 5: Academic Prose Polish
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  PHASE 5: Academic Prose Polish                            │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
./run_polish.sh "$TOPIC"

# 파일 확인
if [ ! -f "reports/${TOPIC}_final.md" ]; then
    echo "❌ 문체 개선 파일이 생성되지 않았습니다."
    exit 1
fi
echo "✅ Phase 5 완료: reports/${TOPIC}_final.md"
echo ""

# Phase 6: Report Visualization
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  PHASE 6: Report Visualization                             │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
./run_visualize.sh "$TOPIC"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ PIPELINE COMPLETE                                      ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Input:  Gemini Deep Research on '$TOPIC'"
echo "║  Output: reports/${TOPIC}_report.html"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📖 To view the report:"
echo "   open reports/${TOPIC}_report.html"

