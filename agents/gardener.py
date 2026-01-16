from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import os

class GardenerAgent:
    """
    관리관 (Gardener)
    - 볼트 무결성 및 RAG 위생 관리
    - 메타데이터 검증
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        self.name = "Gardener"
        self.vault_path = vault_path or "/Users/msn/Desktop/MS_Brain.nosync"

    def check_vault_hygiene(self) -> Dict[str, Any]:
        """볼트 전체를 스캔하여 위생 상태 점검 (최적화 버전)"""
        print(f"🎋 [{self.name}] 볼트 지도 작성 중... (Indexing)")
        
        # 0. 파일 지도 작성 (캐싱)
        self.file_map = set()
        total_scan_count = 0
        
        # 제외할 디렉토리 패턴
        excludes = {".git", ".obsidian", ".trash", ".nosync", "Archive", "node_modules"}
        
        # os.walk로 한 번만 순회
        for root, dirs, files in os.walk(self.vault_path):
            # 제외 폴더 가지치기
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith(".")]
            
            for file in files:
                if file.endswith(".md") or file.endswith(".pdf"):
                    # 경로가 아닌 '파일명'만 저장 (Obsidian은 파일명 유일성 권장)
                    # 필요시 relative path 저장 등 전략 변경 가능
                    self.file_map.add(file)
                    # 확장자 없는 버전도 추가 (링크 매칭용)
                    if "." in file:
                        self.file_map.add(file.rsplit(".", 1)[0])
                total_scan_count += 1
                
        print(f"🎋 [{self.name}] {len(self.file_map)}개 노드 인덱싱 완료.")

        report = {
            "broken_links": [],
            "missing_metadata": [],
            "total_notes": 0
        }
        
        # 실제 검사
        md_files = list(Path(self.vault_path).rglob("*.md"))
        print(f"🎋 [{self.name}] 노트 {len(md_files)}개 정밀 검사 중...")

        for file in md_files:
            # 제외 폴더 필터링 (rglob은 폴더 제외가 까다로워 여기서 한 번 더 체크)
            if any(part.startswith(".") for part in file.parts):
                continue
                
            report["total_notes"] += 1
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # 1. 메타데이터 (YAML) 유무 확인
                    if not content.startswith("---"):
                        report["missing_metadata"].append(str(file.relative_to(self.vault_path)))
                    
                    # 2. 깨진 링크 탐지
                    # [[Target]] 또는 [[Target|Alias]]
                    links = re.findall(r"\[\[(.+?)\]\]", content)
                    for link in links:
                        link_target = link.split("|")[0].split("#")[0].strip() # 앵커(#) 제거
                        
                        if not link_target: continue
                        
                        # 캐시에서 검색 (O(1))
                        if link_target not in self.file_map:
                            report["broken_links"].append({
                                "file": str(file.relative_to(self.vault_path)),
                                "target": link_target
                            })
                            
            except Exception as e:
                # 인코딩 에러 등은 무시하고 진행
                pass
                
        return report

    def _check_link_exists(self, target: str) -> bool:
        """(Deprecated) 이제 self.file_map을 사용하므로 안 씀"""
        return target in self.file_map

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="ARC Secretariat - Gardener Agent")
    parser.add_argument("--check", action="store_true", help="Perform vault hygiene check")
    
    args = parser.parse_args()
    
    gardener = GardenerAgent()
    
    if args.check:
        result = gardener.check_vault_hygiene()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
