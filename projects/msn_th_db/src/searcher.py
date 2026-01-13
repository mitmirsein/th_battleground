"""
Archive Searcher for msn_th_db

Implements grep-based search over JSONL archive with 3-language expansion support.
"""

import json
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Optional

try:
    from .models import (
        ChunkRecord,
        DocumentMetadata,
        Manifest,
        SearchResult,
        SearchResponse,
        SourceInfo,
    )
except ImportError:
    from models import (
        ChunkRecord,
        DocumentMetadata,
        Manifest,
        SearchResult,
        SearchResponse,
        SourceInfo,
    )


class ArchiveSearcher:
    """
    Search engine for theology archive using grep/ripgrep.
    
    Stateless: performs keyword search only, semantic filtering delegated to Antigravity.
    """
    
    def __init__(self, archive_path: Path, glossary_path: Optional[Path] = None):
        """
        Initialize searcher with archive path.
        
        Args:
            archive_path: Path to msn_th_archive directory
            glossary_path: Optional path to glossary.json for query expansion
        """
        self.archive_path = Path(archive_path)
        self.chunks_dir = self.archive_path / "chunks"
        self.docs_dir = self.archive_path / "docs"
        self.manifest_path = self.archive_path / "manifest.json"
        
        self.glossary: dict[str, list[str]] = {}
        if glossary_path and glossary_path.exists():
            self._load_glossary(glossary_path)
        
        # Check for ripgrep availability
        self.use_ripgrep = self._check_ripgrep()
    
    def _check_ripgrep(self) -> bool:
        """Check if ripgrep is available."""
        try:
            subprocess.run(
                ["rg", "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _load_glossary(self, path: Path) -> None:
        """Load 3-language glossary for query expansion."""
        with open(path, "r", encoding="utf-8") as f:
            self.glossary = json.load(f)
    
    def normalize_text(self, text: str) -> str:
        """Apply NFC normalization for consistent matching."""
        return unicodedata.normalize("NFC", text)
    
    def expand_query(
        self, 
        query: str, 
        languages: list[str] = ["ko", "en", "de"]
    ) -> list[str]:
        """
        Expand query using glossary (3-language: ko, en, de).
        
        If term not in glossary, returns original only.
        LLM-based expansion is delegated to Antigravity.
        
        Args:
            query: Original search term
            languages: Target languages for expansion
            
        Returns:
            List of expanded terms including original
        """
        query = self.normalize_text(query)
        expanded = {query}
        
        # Check glossary for translations
        if query.lower() in self.glossary:
            translations = self.glossary[query.lower()]
            for term in translations:
                expanded.add(self.normalize_text(term))
        
        # Also check if query matches any translation
        for key, translations in self.glossary.items():
            normalized_translations = [
                self.normalize_text(t).lower() for t in translations
            ]
            if query.lower() in normalized_translations:
                expanded.add(self.normalize_text(key))
                for t in translations:
                    expanded.add(self.normalize_text(t))
        
        return list(expanded)
    
    def _grep_search(
        self,
        terms: list[str],
        source: Optional[str] = None,
        limit: int = 50
    ) -> list[tuple[Path, str]]:
        """
        Perform grep/ripgrep search on JSONL files.
        
        Args:
            terms: Search terms (OR logic)
            source: Optional doc_id prefix to filter
            limit: Maximum results
            
        Returns:
            List of (file_path, matching_line) tuples
        """
        results: list[tuple[Path, str]] = []
        
        # Build search pattern (OR logic)
        pattern = "|".join(re.escape(term) for term in terms)
        
        # Determine target directory/files
        if source:
            target_files = list(self.chunks_dir.glob(f"{source}*.jsonl"))
            if not target_files:
                return results
            target = [str(f) for f in target_files]
        else:
            target = [str(self.chunks_dir)]
        
        if self.use_ripgrep:
            # ripgrep: faster, handles large files better
            cmd = [
                "rg",
                "-i",  # case insensitive
                "-n",  # line numbers
                "--no-heading",
                "-e", pattern,
                *target
            ]
        else:
            # fallback to grep
            cmd = [
                "grep",
                "-r",
                "-i",
                "-n",
                "-E", pattern,
                *target
            ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                
                # Parse output: filename:line_number:content
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    file_path = Path(parts[0])
                    content = parts[2]
                    results.append((file_path, content))
                    
                    if len(results) >= limit:
                        break
                        
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        return results
    
    def _parse_jsonl_line(self, line: str) -> Optional[ChunkRecord]:
        """Parse a single JSONL line into ChunkRecord."""
        try:
            data = json.loads(line)
            return ChunkRecord(**data)
        except (json.JSONDecodeError, ValueError):
            return None
    
    def _create_snippet(
        self, 
        content: str, 
        terms: list[str], 
        max_length: int = 200
    ) -> str:
        """Create snippet around first match."""
        content = self.normalize_text(content)
        
        # Find first term occurrence
        first_pos = len(content)
        for term in terms:
            pos = content.lower().find(term.lower())
            if pos != -1 and pos < first_pos:
                first_pos = pos
        
        if first_pos == len(content):
            first_pos = 0
        
        # Extract centered window
        start = max(0, first_pos - max_length // 2)
        end = min(len(content), start + max_length)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def _count_matches(self, content: str, terms: list[str]) -> tuple[int, list[str]]:
        """Count term matches in content."""
        content_lower = self.normalize_text(content).lower()
        count = 0
        matched_terms = []
        
        for term in terms:
            term_lower = self.normalize_text(term).lower()
            term_count = content_lower.count(term_lower)
            if term_count > 0:
                count += term_count
                matched_terms.append(term)
        
        return count, matched_terms
    
    def search(
        self,
        query: str,
        languages: list[str] = ["ko", "en", "de"],
        source: Optional[str] = None,
        limit: int = 10
    ) -> SearchResponse:
        """
        Search archive with 3-language expansion.
        
        Args:
            query: Search query
            languages: Languages for expansion
            source: Optional source filter (doc_id prefix)
            limit: Maximum results
            
        Returns:
            SearchResponse with results and metadata
        """
        # Expand query
        expanded = self.expand_query(query, languages)
        
        # Perform grep search
        raw_results = self._grep_search(expanded, source, limit * 3)
        
        # Parse and rank results
        results: list[SearchResult] = []
        seen_chunks: set[str] = set()
        
        for file_path, line in raw_results:
            chunk = self._parse_jsonl_line(line)
            if not chunk:
                continue
            
            if chunk.global_chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk.global_chunk_id)
            
            match_count, match_terms = self._count_matches(chunk.content, expanded)
            snippet = self._create_snippet(chunk.content, expanded)
            
            results.append(SearchResult(
                global_chunk_id=chunk.global_chunk_id,
                doc_id=chunk.doc_id,
                chunk_id=chunk.chunk_id,
                printed_page=chunk.printed_page,
                citation=chunk.citation,
                snippet=snippet,
                match_terms=match_terms,
                match_count=match_count,
                match_field="content"
            ))
        
        # Sort by match count (desc)
        results.sort(key=lambda r: r.match_count, reverse=True)
        results = results[:limit]
        
        return SearchResponse(
            results=results,
            expanded_queries=expanded,
            total_matches=len(results)
        )
    
    def get_chunk(self, global_chunk_id: str) -> Optional[dict]:
        """
        Get full chunk by global_chunk_id.
        
        Args:
            global_chunk_id: Format {doc_id}:{chunk_id} (e.g., RGG_4_4:0235_001)
            
        Returns:
            Full chunk data with metadata, or None
        """
        if ":" not in global_chunk_id:
            return None
        
        doc_id, chunk_id = global_chunk_id.split(":", 1)
        jsonl_path = self.chunks_dir / f"{doc_id}.jsonl"
        
        if not jsonl_path.exists():
            return None
        
        # Search for chunk in JSONL
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("global_chunk_id") == global_chunk_id:
                        # Load document metadata
                        meta_path = self.docs_dir / f"{doc_id}.meta.json"
                        metadata = {}
                        if meta_path.exists():
                            with open(meta_path, "r", encoding="utf-8") as mf:
                                metadata = json.load(mf)
                        
                        return {
                            **data,
                            "metadata": {
                                "abbr": metadata.get("abbr", ""),
                                "volume": metadata.get("volume"),
                                "edition": metadata.get("edition"),
                            }
                        }
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def list_sources(self) -> list[SourceInfo]:
        """
        List all available sources in the archive.
        
        Returns:
            List of SourceInfo objects
        """
        sources: list[SourceInfo] = []
        
        # Iterate through all meta files
        for meta_file in self.docs_dir.glob("*.meta.json"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                doc_id = data.get("doc_id", meta_file.stem.replace(".meta", ""))
                chunks_path = f"chunks/{doc_id}.jsonl"
                
                sources.append(SourceInfo(
                    doc_id=doc_id,
                    abbr=data.get("abbr", ""),
                    title=data.get("title", ""),
                    volume=data.get("volume"),
                    edition=data.get("edition"),
                    language=data.get("language", "de"),
                    doc_type=data.get("doc_type", ""),
                    total_chunks=data.get("total_chunks", 0),
                    file_path=chunks_path
                ))
            except (json.JSONDecodeError, ValueError):
                continue
        
        return sources
    
    def get_manifest(self) -> Optional[Manifest]:
        """Load and return the archive manifest."""
        if not self.manifest_path.exists():
            return None
        
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Manifest(**data)
        except (json.JSONDecodeError, ValueError):
            return None
