"""
Pydantic Data Models for msn_th_db

Defines the schema for document metadata and chunks following the PRD specification.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocType(str, Enum):
    """Document type classification for chunking presets."""
    DICTIONARY_SMALL = "dictionary_small"
    DICTIONARY_LARGE = "dictionary_large"
    LEXICON = "lexicon"
    MONOGRAPH = "monograph"
    COMMENTARY = "commentary"
    TRANSLATION = "translation"


class Language(str, Enum):
    """Supported languages."""
    DE = "de"
    EN = "en"
    KO = "ko"


class ChunkType(str, Enum):
    """Type of content in the chunk."""
    BODY = "body"
    FOOTNOTE = "footnote"
    HEADING = "heading"


class DocumentMetadata(BaseModel):
    """
    Document-level metadata stored in docs/{doc_id}.meta.json
    
    Example doc_id: RGG_4_4 (abbr_edition_volume)
    """
    doc_id: str = Field(..., description="전역 문서 ID (예: RGG_4_4)")
    source: str = Field(..., description="원본 파일명")
    abbr: str = Field(..., description="약어 (예: RGG, TRE, EKL)")
    title: str = Field(..., description="전체 제목")
    volume: Optional[int] = Field(None, description="권 번호")
    edition: Optional[int] = Field(None, description="판본 번호")
    part: Optional[str] = Field(None, description="KD의 경우 I/1, I/2 등")
    year: Optional[int] = Field(None, description="출판 연도")
    language: Language = Field(..., description="주요 언어")
    doc_type: DocType = Field(..., description="문서 유형")
    default_themes: list[str] = Field(
        default_factory=list,
        description="문서 전체에 적용되는 기본 검색 키워드"
    )
    page_offset: int = Field(0, description="PDF 페이지 → 인쇄 페이지 오프셋")
    chunk_size: int = Field(4000, description="청크 크기 (문자)")
    chunk_overlap: int = Field(700, description="청크 오버랩 (문자)")
    total_chunks: int = Field(0, description="총 청크 수")
    indexed_at: Optional[datetime] = Field(None, description="인덱싱 시각")

    class Config:
        use_enum_values = True


class ChunkRecord(BaseModel):
    """
    Single chunk record stored in JSONL format.
    One line = one chunk in chunks/{doc_id}.jsonl
    
    Example global_chunk_id: RGG_4_4:0235_001
    """
    global_chunk_id: str = Field(
        ..., 
        description="전역 청크 ID (예: RGG_4_4:0235_001)"
    )
    doc_id: str = Field(..., description="문서 ID")
    chunk_id: str = Field(
        ..., 
        description="문서 내 로컬 ID (예: 0235_001 = page_seq)"
    )
    chunk_type: ChunkType = Field(
        ChunkType.BODY, 
        description="청크 유형 (body/footnote)"
    )
    parent_chunk_id: Optional[str] = Field(
        None, 
        description="각주인 경우 본문 청크 ID"
    )
    footnote_marker: Optional[str] = Field(
        None, 
        description="각주 마커 (예: [1])"
    )
    pdf_page: int = Field(..., description="원본 PDF 페이지 (0-based)")
    printed_page: int = Field(..., description="offset 적용 후 인쇄 페이지")
    content: str = Field(..., description="NFC 정규화된 청크 텍스트")
    citation: str = Field(
        ..., 
        description="인용 포맷 (예: RGG, 4. Aufl., Bd. IV, 235)"
    )
    themes: Optional[list[str]] = Field(
        None,
        description="null = default_themes 상속, [] = 명시적 비움"
    )


class SearchResult(BaseModel):
    """Single search result returned by the search tool."""
    global_chunk_id: str
    doc_id: str
    chunk_id: str
    printed_page: int
    citation: str
    snippet: str = Field(..., description="매칭 컨텍스트 (~200자)")
    match_terms: list[str] = Field(
        default_factory=list,
        description="매칭된 검색어들"
    )
    match_count: int = Field(0, description="매칭 횟수")
    match_field: str = Field("content", description="매칭 필드 (content/themes)")


class SearchResponse(BaseModel):
    """Response structure for the search tool."""
    results: list[SearchResult]
    expanded_queries: list[str] = Field(
        default_factory=list,
        description="3중 언어 확장된 쿼리들"
    )
    total_matches: int = Field(0, description="총 매칭 수")


class SourceInfo(BaseModel):
    """Source information for list_sources tool."""
    doc_id: str
    abbr: str
    title: str
    volume: Optional[int] = None
    edition: Optional[int] = None
    language: str
    doc_type: str
    total_chunks: int = 0
    file_path: str = Field(..., description="JSONL 파일 상대 경로")


class ManifestDocument(BaseModel):
    """Single document entry in manifest.json"""
    meta_path: str
    chunks_path: str


class Manifest(BaseModel):
    """Archive manifest structure."""
    version: str = "1.0"
    updated_at: datetime = Field(default_factory=datetime.now)
    documents: dict[str, ManifestDocument] = Field(default_factory=dict)
