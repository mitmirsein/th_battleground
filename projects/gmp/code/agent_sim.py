import os
import json
import subprocess
import sys

def search_archive(query, data_dir="data"):
    """
    Simulates the 'Grep Retrieval' process.
    It looks for specific keywords in the JSONL files.
    """
    print(f"🔎 Searching for keywords: '{query}' in {data_dir}...")
    
    # Simple grep (case insensitive) simulating the engine
    # In real world: rg -i "keyword" data/
    
    found_chunks = []
    
    # Keywords strategy: simple split
    keywords = query.split()
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".jsonl"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        # ALL keywords must be present for a 'strict' match, 
                        # or ANY for a 'loose' match. Let's use ANY for demo.
                        if any(k in line for k in keywords):
                            try:
                                doc = json.loads(line)
                                found_chunks.append(doc)
                            except:
                                pass
                                
    return found_chunks

def generate_response(query, context_chunks):
    """
    Simulates the 'LLM Generation' part.
    Since this is a script, we will use a simple rule-based template 
    to demonstrate how the 'Found Context' is used.
    """
    print("\n🤖 [AI Agent Logic] Generating Response based on Evidence...")
    
    if not context_chunks:
        return "죄송합니다. 관련 규정이나 과거 사례를 찾을 수 없습니다."
        
    response = []
    response.append(f"❓ 질문: {query}")
    response.append("\n✅ 분석 결과 및 대응 방안:")
    
    # Categorize findings
    sops = [c for c in context_chunks if "SOP" in c.get('doc_id', '') or "REG" in c.get('doc_id','')]
    devs = [c for c in context_chunks if "DEV" in c.get('doc_id', '')]
    
    if sops:
        response.append("\n[1. 관련 규정 및 SOP]")
        for i, doc in enumerate(sops, 1):
            response.append(f"  - ({doc['doc_id']}) {doc.get('content')[:100]}...")
            
    if devs:
        response.append("\n[2. 유사 과거 사례 (Lesson Learned)]")
        for i, doc in enumerate(devs, 1):
            response.append(f"  - ({doc['doc_id']}) {doc.get('content')}")
            
    response.append("\n💡 [권장 조치 (Action Item)]")
    if "점착력" in query:
        response.append("  1. SOP-QA-001에 의거, 즉시 생산을 중단하고 격리(Quarantine) 조치하십시오.")
        response.append("  2. SOP-MF-012에 의거, 건조기 온도가 80℃ 미만인지 점검하십시오.")
        response.append("  3. 과거 사례(DEV-230205)와 동일하게 히터 고장 가능성이 높습니다.")
        
    return "\n".join(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_sim.py 'search query'")
        sys.exit(1)
        
    query = sys.argv[1]
    
    # 1. Retrieve
    chunks = search_archive(query)
    
    # 2. Re-rank (Skipped for demo, simple list)
    print(f"📊 Found {len(chunks)} relevant documents.\n")
    
    # 3. Generate
    final_output = generate_response(query, chunks)
    print(final_output)
