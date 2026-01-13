#!/usr/bin/env python3
"""
Scholar Knowledge Base Manager (SQLite)
- Scholar Labs 검색 결과를 로컬 SQLite DB에 저장 및 관리
- Vector Search를 위한 기본 구조 포함
"""

import sqlite3
import re
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ScholarKnowledgeBase:
    DB_NAME = "scholar_kb.db"
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = Path(__file__).parent / self.DB_NAME
        else:
            self.db_path = Path(db_path)
            
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """데이터베이스 테이블 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Papers Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT,
            authors TEXT,
            year INTEGER,
            journal TEXT,
            abstract TEXT,
            url TEXT,
            citation_count INTEGER,
            created_at DATETIME,
            raw_markdown TEXT,
            query TEXT,
            UNIQUE(url),
            UNIQUE(title)
        )
        """)
        
        # Embeddings Table (Vector Search)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            paper_id TEXT,
            chunk_id INTEGER,
            content TEXT,
            embedding_json TEXT,
            FOREIGN KEY(paper_id) REFERENCES papers(id)
        )
        """)

        # Facts Table (Fact Extraction)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id TEXT PRIMARY KEY,
            paper_id TEXT,
            fact_type TEXT, -- claim, evidence, stat, quote
            content TEXT,
            context TEXT,
            created_at DATETIME,
            FOREIGN KEY(paper_id) REFERENCES papers(id)
        )
        """)
        
        # Migration: Add fact_extracted column to papers if not exists
        try:
            cursor.execute("ALTER TABLE papers ADD COLUMN fact_extracted INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Column likely already exists

        # Migration: Add source_type column
        try:
            cursor.execute("ALTER TABLE papers ADD COLUMN source_type TEXT DEFAULT 'scholar'")
        except sqlite3.OperationalError:
            pass

            
        conn.commit()
        conn.close()
        print(f"✅ Database initialized/updated: {self.db_path}")

    def ingest_markdown_file(self, file_path: Path) -> int:
        """Markdown 결과 파일을 파싱하여 DB에 저장"""
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 0
            
        content = file_path.read_text(encoding='utf-8')
        entries = self._parse_markdown(content)
        
        if not entries:
            print(f"⚠️ No entries found in {file_path.name}")
            return 0
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        skipped_count = 0
        
        for entry in entries:
            if self.insert_paper(entry):
                inserted_count += 1
            else:
                skipped_count += 1
                
        conn.close()
        
        print(f"📄 Processed {file_path.name}: {inserted_count} inserted, {skipped_count} skipped (duplicates)")
        return inserted_count

    def insert_paper(self, entry: Dict) -> bool:
        """단일 논문/웹페이지 정보 DB 저장"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO papers (
                id, title, authors, year, journal, abstract, url, 
                citation_count, created_at, raw_markdown, query, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                entry['title'],
                entry.get('authors', ''),
                entry.get('year'),
                entry.get('journal', ''),
                entry.get('snippet', ''),
                entry['url'],
                entry.get('citations', 0),
                datetime.now(),
                entry.get('raw_markdown', ''),
                entry.get('query', ''),
                entry.get('source_type', 'scholar')
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def _parse_markdown(self, content: str) -> List[Dict]:
        """마크다운 텍스트에서 논문 정보 추출"""
        entries = []
        
        # 쿼리별로 분리 (### Q1: ... 형식)
        # 쿼리 섹션 찾기
        query_sections = re.split(r'\n### (Q\d+:.+)', content)
        
        current_query = "Unknown"
        
        # 첫 번째 조각은 쿼리 전 헤더이므로 스킵할 수도 있음, 
        # 하지만 re.split 특성상 [preamble, query1_title, query1_body, query2_title, query2_body...] 순서
        
        start_idx = 1 if len(query_sections) > 1 else 0
        
        for i in range(start_idx, len(query_sections), 2):
            if i + 1 >= len(query_sections):
                break
                
            query_title = query_sections[i].strip()
            query_body = query_sections[i+1]
            
            # 쿼리 타이틀에서 Q넘버 등 정리
            current_query = query_title
            
            # 개별 논문 파싱
            # 패턴: **1. [Title](URL)** ... ---
            paper_blocks = query_body.split('\n---')
            
            for block in paper_blocks:
                block = block.strip()
                if not block or "검색 결과가 없습니다" in block:
                    continue
                    
                entry = self._parse_single_entry(block)
                if entry:
                    entry['query'] = current_query
                    entries.append(entry)
                    
        return entries

    def _parse_single_entry(self, block: str) -> Optional[Dict]:
        """단일 논문 블록 파싱"""
        lines = block.split('\n')
        if not lines:
            return None
            
        entry = {'raw_markdown': block}
        
        # 1. Title & URL
        # **1. [Title](URL)**
        title_line = lines[0]
        link_match = re.search(r'\[(.*?)\]\((.*?)\)', title_line)
        if link_match:
            entry['title'] = link_match.group(1)
            entry['url'] = link_match.group(2)
        else:
            # 링크 없는 경우
            text_match = re.search(r'\*\*(\d+\.\s)?(.*?)\*\*', title_line)
            if text_match:
                entry['title'] = text_match.group(2)
                entry['url'] = "" # URL 없음
            else:
                return None # 타이틀 인식 실패
                
        # 2. Meta Info (Authors, Journal, Year)
        # 예: TD Stegman - Theological studies, 2011 - journals.sagepub.com
        # 또는 두 번째 줄에 위치
        
        meta = ""
        snippet_lines = []
        citations = 0
        
        for line in lines[1:]:
            line = line.strip()
            if not line: continue
            
            # 인용 수
            if line.startswith('📚'):
                cit_match = re.search(r'(\d+)회', line)
                if cit_match:
                    citations = int(cit_match.group(1))
                continue
                
            # 인용문 (MLA)
            if line.startswith('>'):
                continue
                
            # 메타 정보 (연도 포함된 줄)
            if re.search(r'\d{4}', line) and ' - ' in line and len(line) < 150:
                 # 저자 - 저널, 연도 - 출판사
                 meta = line
                 parts = meta.split(' - ')
                 if parts:
                     entry['authors'] = parts[0]
                 if len(parts) > 1:
                     # "Journal, 2011" or "2011"
                     jy = parts[1]
                     yr = re.search(r'\d{4}', jy)
                     if yr:
                         entry['year'] = int(yr.group(0))
                         entry['journal'] = jy.replace(yr.group(0), '').strip(', ')
                 continue
            
            # 스니펫 (나머지)
            if line.startswith('•') or len(line) > 20:
                snippet_lines.append(line.lstrip('• '))

        entry['citations'] = citations
        entry['snippet'] = ' '.join(snippet_lines)
        
        return entry

    def get_stats(self):
        """DB 통계 출력"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT count(*) FROM papers")
        total_papers = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(DISTINCT query) FROM papers")
        total_queries = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n📊 Knowledge Base Stats:")
        print(f"   • Total Papers: {total_papers}")
        print(f"   • Unique Queries: {total_queries}")
        return total_papers


def main():
    if len(sys.argv) < 2:
        print("Usage: python kb_manager.py [init|ingest|stats] [file_path]")
        return

    cmd = sys.argv[1]
    kb = ScholarKnowledgeBase()

    if cmd == "init":
        kb.init_db()
    
    elif cmd == "ingest":
        if len(sys.argv) < 3:
            # Ingest all in results/ by default
            results_dir = Path(__file__).parent / "results"
            if results_dir.exists():
                print(f"📂 Scanning {results_dir}...")
                for f in results_dir.glob("*.md"):
                    kb.ingest_markdown_file(f)
            else:
                print("Usage: python kb_manager.py ingest <file_path>")
        else:
            kb.ingest_markdown_file(Path(sys.argv[2]))
            
        kb.get_stats()
        
    elif cmd == "stats":
        kb.get_stats()

if __name__ == "__main__":
    main()
