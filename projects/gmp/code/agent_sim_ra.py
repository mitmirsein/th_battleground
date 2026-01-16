import os
import json
import sys

def search_rules(query, data_dir="data"):
    """
    Search specifically for regulations and product specs.
    """
    results = []
    # Broad search in the data directory
    keywords = query.replace("?", "").split()
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".jsonl"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        if any(k in line for k in keywords):
                            try:
                                doc = json.loads(line)
                                results.append(doc)
                            except:
                                continue
    return results

def generate_ra_advice(query, docs):
    print(f"🤖 [RA Agent] Analyzing Compliance for request: '{query}'")
    
    if not docs:
        return "관련 규정을 찾을 수 없습니다."
        
    print(f"📋 Found {len(docs)} reference documents.\n")
    
    response = []
    response.append(f"## 🏢 제품 허가 요건 분석 보고서")
    response.append(f"**분석 대상**: {query}\n")
    
    # Check for 'New Additive' scenario
    regs = [d for d in docs if "MFDS" in d.get('doc_id', '')]
    specs = [d for d in docs if "SPEC" in d.get('doc_id', '')]
    internal = [d for d in docs if "SOP" in d.get('doc_id', '')]
    
    response.append("### 1. 제품 특성 분석 (Specification)")
    if specs:
        for s in specs:
            response.append(f"- **제품명**: {s.get('product_name')}")
            response.append(f"- **특이사항**: {s.get('composition')} ({s.get('type')})")
            response.append(f"  -> 판단: '알로에 베라'는 기존에 없던 **새로운 첨가제**입니다.")
            
    response.append("\n### 2. 식약처(MFDS) 규제 요건")
    if regs:
        for r in regs:
            response.append(f"- **{r['doc_id']} ({r.get('article', '')})**:")
            response.append(f"  > {r.get('content')}")
            if "안전성" in r['content'] or "독성" in r['content']:
                response.append("  ⚠️ **Requirement**: 신규 첨가제이므로 독성/자극성 시험 자료 제출 필수.")
                
    response.append("\n### 3. 내부 준비 절차 (Action Plan)")
    if internal:
        for i in internal:
             response.append(f"- **{i['doc_id']} 따름**: {i.get('content')}")
    
    response.append("\n### ✅ 최종 허가용 필요 서류 리스트 (Checklist)")
    response.append("1. [필수] 단회투여독성시험 보고서 (GLP 기관)")
    response.append("2. [필수] 1차 피부자극시험 및 피부감작성시험 자료")
    response.append("3. [필수] 기준 및 시험방법 (점착력 등 이화학적 동등성 자료)")
    response.append("4. 첨가제(알로에)의 규격 설정 근거 자료")

    return "\n".join(response)

if __name__ == "__main__":
    query = "알로에 신제품 허가"
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
    chunks = search_rules(query)
    report = generate_ra_advice(query, chunks)
    print(report)
