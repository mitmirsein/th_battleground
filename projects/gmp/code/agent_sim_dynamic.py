import os
import json
import sys

def search_dynamic(query, metadata, data_dir="data"):
    """
    Search scope is dynamically adjusted based on metadata.
    """
    results = []
    keywords = query.split()
    
    # 1. Dynamic Scope Filtering
    target_files = []
    market = metadata.get("market", "KR") # Default to Korean MFDS
    
    print(f"⚙️ [System] Configuring Search Scope for Market: {market}")
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if not file.endswith(".jsonl"): continue
            
            # Dynamic Filter Logic
            if market == "US" and "mfds" in file:
                continue # Skip KR regs if US market
            if market == "KR" and "fda" in file:
                continue # Skip US regs if KR market
                
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    # Simple keyword match
                    if any(k in line for k in keywords):
                        try:
                            doc = json.loads(line)
                            results.append(doc)
                        except:
                            continue
    return results

def generate_dynamic_response(query, docs, metadata):
    role = metadata.get("role", "General")
    intent = metadata.get("intent", "info")
    product_ctx = metadata.get("product_context", {})
    
    print(f"🎨 [LLM] Adapting Persona -> Role: {role}, Intent: {intent}")
    
    response = []
    
    # 2. Dynamic Tone & Format
    if role == "Operator":
        response.append("## 🚨 현장 작업자 긴급 대응 지침")
        response.append(f"**대상 설비**: {product_ctx.get('equipment', '설비 미지정')}")
        response.append(f"**관련 제품**: {product_ctx.get('product_name', '제품 미지정')}\n")
        
        response.append("### [즉시 행동 요령]")
        for doc in docs:
            if "SOP" in doc.get('doc_id', ''):
                response.append(f"✅ **{doc['doc_id']} 준수**: {doc['content'][:50]}... (즉시 확인하세요!)")
                
    elif role == "QA_Manager":
        response.append("## 📑 CAPA (시정 및 예방 조치) 보고서 초안")
        response.append(f"**Report ID**: GEN-{product_ctx.get('lot_no', 'N/A')}")
        response.append(f"**Regulatory Context**: {metadata.get('market', 'KR')} Market\n")
        
        response.append("### 1. Root Cause Analysis (Legal Basis)")
        for doc in docs:
            response.append(f"- **Reference**: {doc['doc_id']}")
            response.append(f"  - Summary: {doc.get('content')}")
            
        response.append("\n### 2. Risk Assessment")
        response.append("시스템 분석 결과, 본 건은 'Major Deviation'으로 분류될 가능성이 높습니다.")
        
    return "\n".join(response)

if __name__ == "__main__":
    # Example Usage: python sim.py "query" '{"json":"metadata"}'
    query = "점착력"
    if len(sys.argv) > 1: query = sys.argv[1]
    
    meta_str = '{"role": "QA_Manager", "market": "KR"}'
    if len(sys.argv) > 2: meta_str = sys.argv[2]
    
    metadata = json.loads(meta_str)
    
    hits = search_dynamic(query, metadata)
    output = generate_dynamic_response(query, hits, metadata)
    print("\n" + "="*30)
    print(output)
    print("="*30)
