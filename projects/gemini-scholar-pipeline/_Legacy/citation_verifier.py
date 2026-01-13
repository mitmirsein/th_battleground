#!/usr/bin/env python3
"""
Citation Verifier (Phase 5)
- 리포트 내의 인용구 (Source: [ID])를 스캔
- SQLite DB (scholar_kb.db)의 Facts 테이블과 대조하여 유효성 검증
- 검증 결과 리포트 (JSON) 생성
"""

import sys
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict

class CitationVerifier:
    DB_NAME = "scholar_kb.db"
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = Path(__file__).parent / self.DB_NAME
        else:
            self.db_path = Path(db_path)
            
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def verify_file(self, file_path: str) -> Dict:
        """Markdown 파일 내 인용 검증"""
        path = Path(file_path)
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return {}
            
        content = path.read_text(encoding='utf-8')
        
        # Regex for citations: (Source: [ID]) or (Source: ID)
        # We target the specific format used in prompts: (Source: [abcdef12])
        pattern = r"\(Source: \[?([a-zA-Z0-9]+)\]?\)"
        
        matches = re.findall(pattern, content)
        unique_ids = list(set(matches))
        
        print(f"🔍 Found {len(matches)} citations ({len(unique_ids)} unique) in {path.name}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        valid_ids = []
        invalid_ids = []
        
        for cit_id in unique_ids:
            # Check if exists in facts table (id or paper_id could be used depending on citation strategy)
            # Currently Fact ID is 8 chars, Paper ID is larger UUID but often truncated.
            # We assume the prompt uses Fact IDs or Paper IDs.
            
            # Check exact match in Facts ID
            cursor.execute("SELECT id FROM facts WHERE id LIKE ?", (f"{cit_id}%",))
            res = cursor.fetchone()
            
            if not res:
                # Check Paper ID (if citation is paper-level)
                cursor.execute("SELECT id FROM papers WHERE id LIKE ?", (f"{cit_id}%",))
                res = cursor.fetchone()
                
            if res:
                valid_ids.append(cit_id)
            else:
                invalid_ids.append(cit_id)
                
        conn.close()
        
        report = {
            "file": str(path),
            "total_citations": len(matches),
            "unique_citations": len(unique_ids),
            "valid_count": len(valid_ids),
            "invalid_count": len(invalid_ids),
            "valid_ids": valid_ids,
            "invalid_ids": invalid_ids,
            "integrity_score": len(valid_ids) / len(unique_ids) if unique_ids else 1.0
        }
        
        self._print_report(report)
        return report

    def _print_report(self, report: Dict):
        print(f"\n📊 Verification Report for: {report['file']}")
        print(f"   • Score: {report['integrity_score']*100:.1f}%")
        print(f"   • Valid: {report['valid_count']}")
        print(f"   • Invalid: {report['invalid_count']}")
        
        if report['invalid_ids']:
            print(f"   ⚠️  Invalid/Missing IDs: {report['invalid_ids']}")
        else:
            print("   ✅ All citations valid.")

    def save_report(self, report: Dict, output_path: str = "verification_report.json"):
        Path(output_path).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"💾 Report saved to {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python citation_verifier.py [markdown_file_path]")
        return
        
    verifier = CitationVerifier()
    report = verifier.verify_file(sys.argv[1])
    verifier.save_report(report)

if __name__ == "__main__":
    main()
