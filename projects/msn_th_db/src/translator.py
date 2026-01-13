
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import csv

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ARCHIVE_DIR = Path.home() / "Desktop" / "MS_Dev.nosync" / "data" / "msn_th_archive"
TRANSLATIONS_DIR = ARCHIVE_DIR / "translations"

logger = logging.getLogger("translator")

class JournalManager:
    """Manages theological journal abbreviations from CSV."""
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.journals = {}
        self.load_journals()
        
    def load_journals(self):
        if not self.csv_path.exists():
            return
            
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    abbr = row.get("약어", "").strip()
                    if abbr:
                        self.journals[abbr] = {
                            "full_title": row.get("전체 타이틀", ""),
                            "ko_title": row.get("한국어 이름", ""),
                            "description": row.get("설명", "")
                        }
        except Exception as e:
            logger.error(f"Error loading journals: {e}")
            
    def lookup(self, abbr: str) -> Optional[Dict]:
        return self.journals.get(abbr)


class GlossaryManager:
    def __init__(self, glossary_path: Path = CONFIG_DIR / "glossary.json"):
        self.glossary_path = glossary_path
        self.journal_path = PROJECT_ROOT.parent.parent / "data" / "tre_journal.csv" # /Users/msn/Desktop/MS_Dev.nosync/data/tre_journal.csv
        # Adjust path dynamically if needed, but hardcoding for user workspace is safer now
        if not self.journal_path.exists():
             # Fallback to absolute path provided by user
             self.journal_path = Path("/Users/msn/Desktop/MS_Dev.nosync/data/tre_journal.csv")
             
        self.terms = {}
        self.journal_manager = JournalManager(self.journal_path)
        self.load_glossary()

    def load_glossary(self):
        if not self.glossary_path.exists():
            logger.warning(f"Glossary not found at {self.glossary_path}")
            return

        with open(self.glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.terms = data.get("terms", {})
            self._meta = data.get("_meta", {})

    def lookup(self, query: str, lang: str = "de") -> List[Dict[str, Any]]:
        """
        Lookup term in glossary AND journals.
        """
        results = []
        query_norm = query.lower().strip()
        
        # 1. Journal Lookup (Exact match on abbreviation)
        # Check original case first, then upper
        journal_info = self.journal_manager.lookup(query.strip()) or self.journal_manager.lookup(query.strip().upper())
        
        if journal_info:
            results.append({
                "type": "journal",
                "canonical": {
                    "de": journal_info["full_title"],
                    "ko": journal_info["ko_title"],
                    "en": journal_info["full_title"]
                },
                "definitions": {
                    "ko": f"[저널] {journal_info['description']}"
                },
                "source": "TRE_Journal_CSV"
            })
        
        # 2. Glossary Term Lookup
        for term_key, term_data in self.terms.items():
            # Check canonical keys
            canonical = term_data.get("canonical", {})
            
            # Simple check: is query in canonical values?
            matched = False
            for l, val in canonical.items():
                if val and query_norm in val.lower():
                    matched = True
                    break
            
            if matched:
                results.append(term_data)
                
        return results

class TranslationArchive:
    def __init__(self, archive_dir: Path = TRANSLATIONS_DIR):
        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def save_translation(self, doc_id: str, chunk_id: str, original_text: str, navigation_text: str, metadata: Dict[str, Any] = None):
        """
        Append translation to the document's translation file.
        Format: JSONL
        """
        target_file = self.archive_dir / f"{doc_id}_KR.jsonl"
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "original": original_text,
            "translation": navigation_text,
            "metadata": metadata or {}
        }
        
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
        return str(target_file)

    def get_next_batch(self, doc_id: str, size: int = 5) -> List[Dict[str, Any]]:
        """Get next batch of chunks to translate (status='todo')."""
        target_file = self.archive_dir / f"{doc_id}_KR.jsonl"
        batch = []
        
        if not target_file.exists():
            return batch
            
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if record.get("metadata", {}).get("status") == "todo":
                            batch.append(record)
                            if len(batch) >= size:
                                break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error reading batch: {e}")
            
        return batch

    def save_batch(self, doc_id: str, updates: List[Dict[str, Any]]) -> int:
        """
        Update multiple records. 
        updates: List of {chunk_id, translation}
        """
        target_file = self.archive_dir / f"{doc_id}_KR.jsonl"
        if not target_file.exists():
            return 0
            
        # Create a lookup map for updates
        update_map = {u["chunk_id"]: u["translation"] for u in updates}
        all_records = []
        updated_count = 0
        
        # Read all
        with open(target_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    chunk_id = record["chunk_id"]
                    
                    if chunk_id in update_map:
                        record["translation"] = update_map[chunk_id]
                        record["metadata"]["status"] = "done"
                        record["timestamp"] = datetime.now().isoformat()
                        updated_count += 1
                        
                    all_records.append(record)
                except json.JSONDecodeError:
                    continue
                    
        # Write back all
        with open(target_file, "w", encoding="utf-8") as f:
            for record in all_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                
        return updated_count

# Singleton instances (can be used by MCP server)
glossary_manager = GlossaryManager()
translation_archive = TranslationArchive()
