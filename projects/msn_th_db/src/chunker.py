"""
Main Chunker for msn_th_db

Processes PDF files into JSONL archive format with proper citation metadata.
Requires pre-chunk configuration from Antigravity HITL workflow.
"""

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import yaml

try:
    from .models import ChunkRecord, DocumentMetadata, Manifest, ManifestDocument, ChunkType
except ImportError:
    from models import ChunkRecord, DocumentMetadata, Manifest, ManifestDocument, ChunkType


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
TEMP_DIR = PROJECT_ROOT / "temp"
ARCHIVE_DIR = Path.home() / "Desktop" / "MS_Dev.nosync" / "data" / "msn_th_archive"


def load_known_sources() -> dict:
    """Load known sources database."""
    path = CONFIG_DIR / "known_sources.yaml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"sources": {}}


def load_chunking_presets() -> dict:
    """Load chunking presets."""
    path = CONFIG_DIR / "chunking_presets.yaml"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"presets": {"default": {"chunk_size": 4000, "overlap": 700}}}


def clean_ocr_text(text: str) -> str:
    """
    Minimal OCR text cleaning for search quality.
    
    - NFC normalization (macOS decomposed character fix)
    - CJK character removal (OCR errors like ß → 公)
    - Ligature conversion
    - Multiple whitespace normalization
    """
    # 1. NFC normalization
    text = unicodedata.normalize("NFC", text)
    
    # 2. CJK character removal (OCR errors)
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    
    # 3. Ligature conversion
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = text.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    
    # 4. Multiple whitespace normalization
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def generate_doc_id(abbr: str, edition: Optional[int], volume: Optional[int]) -> str:
    """Generate doc_id in format: {abbr}_{edition}_{volume}"""
    parts = [abbr]
    if edition:
        parts.append(str(edition))
    if volume:
        parts.append(str(volume))
    return "_".join(parts)


def generate_citation(
    abbr: str,
    volume: Optional[int],
    edition: Optional[int],
    printed_page: int,
    language: str,
    part: Optional[str] = None,
    author: Optional[str] = None
) -> str:
    """Generate citation string based on language and document type."""
    
    # Special case for monographs with author
    if author and part:
        return f"{author}, {abbr} {part}, {printed_page}"
    elif author:
        return f"{author}, {abbr}, {printed_page}"
    
    # Dictionary/Lexicon citations
    if language == "de":
        if edition and volume:
            return f"{abbr}, {edition}. Aufl., Bd. {_to_roman(volume)}, {printed_page}"
        elif volume:
            return f"{abbr}, Bd. {_to_roman(volume)}, {printed_page}"
        else:
            return f"{abbr}, {printed_page}"
    else:  # English
        if edition and volume:
            return f"{abbr}, {_ordinal(edition)} ed., Vol. {volume}, {printed_page}"
        elif volume:
            return f"{abbr}, Vol. {volume}, {printed_page}"
        else:
            return f"{abbr}, {printed_page}"


def _to_roman(num: int) -> str:
    """Convert integer to Roman numeral."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
    result = ''
    for i, v in enumerate(val):
        while num >= v:
            result += syms[i]
            num -= v
    return result


def _ordinal(n: int) -> str:
    """Convert integer to ordinal string."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def extract_pdf_text(pdf_path: Path) -> list[tuple[int, str]]:
    """
    Extract text from PDF using PyMuPDF.
    
    Returns:
        List of (pdf_page, text) tuples (0-based page numbers)
    """
    pages = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        text = clean_ocr_text(text)
        pages.append((page_num, text))
    
    doc.close()
    return pages


def chunk_text(
    pages: list[tuple[int, str]],
    chunk_size: int,
    overlap: int,
    page_offset: int
) -> list[dict]:
    """
    Split pages into overlapping chunks.
    
    Each chunk records its pdf_page and printed_page.
    """
    chunks = []
    current_chunk = ""
    current_pdf_page = 0
    chunk_seq = 0
    
    for pdf_page, text in pages:
        # Track the starting page of current chunk
        if not current_chunk:
            current_pdf_page = pdf_page
        
        current_chunk += text + "\n"
        
        # Check if chunk is large enough
        while len(current_chunk) >= chunk_size:
            # Find a good split point (paragraph or sentence boundary)
            split_point = chunk_size
            
            # Try to find paragraph break
            para_break = current_chunk.rfind("\n\n", 0, split_point + 200)
            if para_break > split_point - 500:
                split_point = para_break
            else:
                # Try sentence break
                sent_break = current_chunk.rfind(". ", 0, split_point + 100)
                if sent_break > split_point - 300:
                    split_point = sent_break + 1
            
            chunk_text_content = current_chunk[:split_point].strip()
            
            if chunk_text_content:
                printed_page = current_pdf_page + page_offset
                chunk_id = f"{printed_page:04d}_{chunk_seq:03d}"
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "pdf_page": current_pdf_page,
                    "printed_page": printed_page,
                    "content": chunk_text_content
                })
                chunk_seq += 1
            
            # Keep overlap for next chunk
            current_chunk = current_chunk[split_point - overlap:] if split_point > overlap else ""
            current_pdf_page = pdf_page
    
    # Handle remaining text
    if current_chunk.strip():
        printed_page = current_pdf_page + page_offset
        chunk_id = f"{printed_page:04d}_{chunk_seq:03d}"
        
        chunks.append({
            "chunk_id": chunk_id,
            "pdf_page": current_pdf_page,
            "printed_page": printed_page,
            "content": current_chunk.strip()
        })
    
    return chunks


def extract_footnotes(text: str) -> tuple[str, list[tuple[str, str]]]:
    """
    Extract footnotes from text.
    Returns cleaned text and list of (marker, content) tuples.
    Detects patterns like [1], (1), or starting with 1.
    """
    footnotes = []
    
    # Pattern for footnote definitions at end of text or isolated lines
    # Only detect [n] or (n) style to avoid mistaking numbered lists (1. Item) for footnotes
    fn_pattern = re.compile(r'(?:^|\n)(\[\d+\]|\(\d+\))\s+(.+)(?=$|\n)')
    
    matches = list(fn_pattern.finditer(text))
    
    # Reverse iterate to remove from text safely
    for match in reversed(matches):
        marker = match.group(1)
        content = match.group(2)
        footnotes.append((marker, content))
        
        # Remove from text? Or keep marker?
        # Strategy: Keep marker in text usually, but if it's a footnote section, remove it.
        # Ideally, we want to extract the definition.
        # For now, let's assuming we found definition lines.
        span = match.span()
        text = text[:span[0]] + text[span[1]:]
        
    return text.strip(), footnotes[::-1]  # Restore order


def chunk_by_paragraph(
    pages: list[tuple[int, str]],
    constraints: dict,
    page_offset: int
) -> tuple[list[dict], list[dict]]:
    """
    Chunk text by paragraphs with smart merging.
    
    Args:
        pages: List of (pdf_page, text)
        constraints: Dict with max_chars, min_chars
        page_offset: Page offset
        
    Returns:
        tuple(body_chunks, footnote_chunks)
    """
    max_chars = constraints.get("max_chars", 6000)
    min_chars = constraints.get("min_chars", 300)
    
    body_chunks = []
    footnote_chunks = []
    
    current_chunk_text = ""
    current_pdf_page = 0
    current_footnotes: list[tuple[str, str]] = []
    
    chunk_seq = 0
    
    # 1. Flatten pages into paragraphs
    all_paras = []
    for pdf_page, text in pages:
        # Split by double newline as primary separator
        paras = re.split(r'\n\s*\n', text)
        for para in paras:
            if not para.strip():
                continue
            all_paras.append({
                "text": para.strip(),
                "pdf_page": pdf_page
            })
            
    # 2. Merge paragraphs into chunks
    temp_chunk_paras = []
    temp_chunk_len = 0
    chunk_start_page = 0
    
    for i, para in enumerate(all_paras):
        para_text = para["text"]
        para_page = para["pdf_page"]
        
        # Extract footnotes from paragraph
        cleaned_text, footnotes = extract_footnotes(para_text)
        current_footnotes.extend(footnotes)
        
        # If adding this paragraph exceeds max_chars
        if temp_chunk_len + len(cleaned_text) > max_chars and temp_chunk_len >= min_chars:
            # Finalize current chunk
            printed_page = chunk_start_page + page_offset
            chunk_id = f"{printed_page:04d}_{chunk_seq:03d}"
            
            full_text = "\n\n".join([p["text"] for p in temp_chunk_paras])
            
            body_chunks.append({
                "chunk_id": chunk_id,
                "pdf_page": chunk_start_page,
                "printed_page": printed_page,
                "content": full_text,
                "chunk_type": ChunkType.BODY
            })
            
            # Process accumulated footnotes for this chunk
            for fn_marker, fn_content in current_footnotes:
                fn_chunk_id = f"{chunk_id}_fn_{fn_marker}"
                footnote_chunks.append({
                    "chunk_id": fn_chunk_id,
                    "pdf_page": chunk_start_page, # Approx
                    "printed_page": printed_page,
                    "content": fn_content,
                    "chunk_type": ChunkType.FOOTNOTE,
                    "parent_chunk_id": chunk_id,
                    "footnote_marker": fn_marker
                })
            
            # Reset
            chunk_seq += 1
            temp_chunk_paras = []
            temp_chunk_len = 0
            current_footnotes = []
            chunk_start_page = para_page
            
        if not temp_chunk_paras:
            chunk_start_page = para_page
            
        temp_chunk_paras.append({"text": cleaned_text, "pdf_page": para_page})
        temp_chunk_len += len(cleaned_text)
        
    # Handle remaining
    if temp_chunk_paras:
        printed_page = chunk_start_page + page_offset
        chunk_id = f"{printed_page:04d}_{chunk_seq:03d}"
        full_text = "\n\n".join([p["text"] for p in temp_chunk_paras])
        
        body_chunks.append({
            "chunk_id": chunk_id,
            "pdf_page": chunk_start_page,
            "printed_page": printed_page,
            "content": full_text,
            "chunk_type": ChunkType.BODY
        })
        
        for fn_marker, fn_content in current_footnotes:
            fn_chunk_id = f"{chunk_id}_fn_{fn_marker}"
            footnote_chunks.append({
                "chunk_id": fn_chunk_id,
                "pdf_page": chunk_start_page,
                "printed_page": printed_page,
                "content": fn_content,
                "chunk_type": ChunkType.FOOTNOTE,
                "parent_chunk_id": chunk_id,
                "footnote_marker": fn_marker
            })

    return body_chunks, footnote_chunks


def save_document(
    doc_id: str,
    metadata: DocumentMetadata,
    chunks: list[dict],
    archive_dir: Path
) -> None:
    """Save document metadata and chunks to archive."""
    
    docs_dir = archive_dir / "docs"
    chunks_dir = archive_dir / "chunks"
    docs_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    
    # Update metadata with chunk count
    metadata.total_chunks = len(chunks)
    metadata.indexed_at = datetime.now()
    
    # Save metadata
    meta_path = docs_dir / f"{doc_id}.meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
    
    # Save chunks as JSONL
    chunks_path = chunks_dir / f"{doc_id}.jsonl"
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            record = ChunkRecord(
                global_chunk_id=f"{doc_id}:{chunk['chunk_id']}",
                doc_id=doc_id,
                chunk_id=chunk["chunk_id"],
                pdf_page=chunk["pdf_page"],
                printed_page=chunk["printed_page"],
                content=chunk["content"],
                citation=generate_citation(
                    abbr=metadata.abbr,
                    volume=metadata.volume,
                    edition=metadata.edition,
                    printed_page=chunk["printed_page"],
                    language=metadata.language.value if hasattr(metadata.language, 'value') else metadata.language,
                    part=metadata.part
                ),
                themes=None  # Will inherit default_themes
            )
            # Add new fields if present
            if "chunk_type" in chunk:
                record.chunk_type = chunk["chunk_type"]
            if "parent_chunk_id" in chunk:
                record.parent_chunk_id = chunk["parent_chunk_id"]
            if "footnote_marker" in chunk:
                record.footnote_marker = chunk["footnote_marker"]
                
            f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
            
    # Create Translation Draft (If translation strategy is used)
    # This automatically prepares the document for the translation pipeline.
    if metadata.chunking.strategy == "paragraph":
        trans_dir = archive_dir / "translations"
        trans_dir.mkdir(parents=True, exist_ok=True)
        trans_path = trans_dir / f"{doc_id}_KR.jsonl"
        
        if not trans_path.exists():
            try:
                with open(trans_path, "w", encoding="utf-8") as f:
                    for chunk in chunks:
                        # Determine chunk type string
                        ct_val = chunk.get("chunk_type")
                        if hasattr(ct_val, "value"): # Enum
                            chunk_type_str = ct_val.value
                        else:
                            chunk_type_str = str(ct_val) if ct_val else "body"
                            
                        record_t = {
                            "chunk_id": chunk["chunk_id"],
                            "doc_id": doc_id,
                            "original": chunk["content"],
                            "translation": "(번역 대기)",
                            "metadata": {
                                "status": "todo",
                                "chunk_type": chunk_type_str,
                                "pdf_page": chunk["pdf_page"],
                                "printed_page": chunk["printed_page"]
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                        f.write(json.dumps(record_t, ensure_ascii=False) + "\n")
                print(f"✅ Created translation draft: {trans_path}")
            except Exception as e:
                print(f"⚠️ Failed to create translation draft: {e}")
        else:
            print(f"ℹ️ Translation file already exists: {trans_path}")
    
    # Update manifest
    manifest_path = archive_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    else:
        manifest_data = {"version": "1.0", "documents": {}}
    
    manifest_data["updated_at"] = datetime.now().isoformat()
    manifest_data["documents"][doc_id] = {
        "meta_path": f"docs/{doc_id}.meta.json",
        "chunks_path": f"chunks/{doc_id}.jsonl"
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(chunks)} chunks for {doc_id}")
    print(f"   - Metadata: {meta_path}")
    print(f"   - Chunks: {chunks_path}")


def load_pre_chunk_config(config_path: Path) -> dict:
    """Load pre-chunk configuration from temp directory."""
    if not config_path.exists():
        raise FileNotFoundError(f"Pre-chunk config not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_pdf(
    pdf_path: Path,
    config: dict,
    archive_dir: Path = ARCHIVE_DIR
) -> None:
    """
    Main processing function.
    
    Args:
        pdf_path: Path to PDF file
        config: Pre-chunk configuration dict
        archive_dir: Target archive directory
    """
    print(f"\n📖 Processing: {pdf_path.name}")
    
    # Extract configuration
    abbr = config["abbr"]
    volume = config.get("volume")
    edition = config.get("edition")
    page_offset = config.get("page_offset", 0)
    chunk_size = config.get("chunk_size", 4000)
    chunk_overlap = config.get("chunk_overlap", 700)
    
    doc_id = generate_doc_id(abbr, edition, volume)
    print(f"   doc_id: {doc_id}")
    
    # Extract text
    print("   Extracting text...")
    pages = extract_pdf_text(pdf_path)
    print(f"   Extracted {len(pages)} pages")
    
    # Chunk text
    print(f"   Created {len(chunks)} chunks")
    
    # Check for paragraph strategy
    strategy = config.get("strategy", "default")
    if strategy == "paragraph":
        print("   Using Paragraph Chunking Strategy...")
        constraints = config.get("constraints", {})
        body_chunks, fn_chunks = chunk_by_paragraph(pages, constraints, page_offset)
        chunks = body_chunks + fn_chunks
        print(f"   Created {len(body_chunks)} body chunks, {len(fn_chunks)} footnote chunks")
    else:
        # Default strategy
        print(f"   Chunking (size={chunk_size}, overlap={chunk_overlap})...")
        chunks = chunk_text(pages, chunk_size, chunk_overlap, page_offset)
        print(f"   Created {len(chunks)} chunks")
    
    # Create metadata
    metadata = DocumentMetadata(
        doc_id=doc_id,
        source=pdf_path.name,
        abbr=abbr,
        title=config.get("title", ""),
        volume=volume,
        edition=edition,
        part=config.get("part"),
        year=config.get("year"),
        language=config.get("language", "de"),
        doc_type=config.get("doc_type", "dictionary_small"),
        default_themes=config.get("default_themes", []),
        page_offset=page_offset,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Save to archive
    save_document(doc_id, metadata, chunks, archive_dir)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process PDF into JSONL archive"
    )
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to PDF file"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=TEMP_DIR / "pre_chunk_config.json",
        help="Path to pre-chunk config (default: temp/pre_chunk_config.json)"
    )
    parser.add_argument(
        "--archive",
        type=Path,
        default=ARCHIVE_DIR,
        help="Archive directory"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_pre_chunk_config(args.config)
    
    # Process PDF
    process_pdf(args.pdf_path, config, args.archive)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
