"""
MCP Server for msn_th_db - Theology Archive

A stateless MCP server providing keyword-based search over JSONL archive.
Semantic filtering is delegated to Antigravity (LLM).

Tools:
    - search: 3-language expanded keyword search
    - get_chunk: Retrieve full chunk by global_chunk_id
    - list_sources: List available sources in archive
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from models import SearchResponse, SourceInfo
from searcher import ArchiveSearcher
from translator import glossary_manager, translation_archive

# Configuration
ARCHIVE_PATH = Path.home() / "Desktop" / "MS_Dev.nosync" / "data" / "msn_th_archive"
GLOSSARY_PATH = Path(__file__).parent.parent / "config" / "glossary.json"

# Initialize server and searcher
app = Server("msn_th_db")
searcher = ArchiveSearcher(ARCHIVE_PATH, GLOSSARY_PATH)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search",
            description="""신학 아카이브에서 3중 언어(한국어/영어/독일어) 확장 검색을 수행합니다.
            
키워드 검색 결과를 반환하며, 시맨틱 필터링은 Antigravity가 담당합니다.
검색 결과에는 snippet, citation, match_terms가 포함됩니다.

예시: query="칭의" → [칭의, Justification, Rechtfertigung]으로 확장 검색""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색어 (한국어/영어/독일어)"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["ko", "en", "de"],
                        "description": "확장 검색 대상 언어"
                    },
                    "source": {
                        "type": "string",
                        "description": "소스 필터 (doc_id 접두사, 예: RGG, TRE, EKL)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "최대 결과 수 (기본 10)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_chunk",
            description="""global_chunk_id로 특정 청크의 전체 내용을 조회합니다.

청크 ID 형식: {doc_id}:{chunk_id} (예: RGG_4_4:0235_001)
반환값에는 전체 텍스트, citation, 문서 메타데이터가 포함됩니다.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "global_chunk_id": {
                        "type": "string",
                        "description": "전역 청크 ID (예: RGG_4_4:0235_001)"
                    }
                },
                "required": ["global_chunk_id"]
            }
        ),
        Tool(
            name="list_sources",
            description="""아카이브에서 사용 가능한 모든 소스(문서) 목록을 반환합니다.

각 소스에 대해 doc_id, 제목, 언어, 문서 유형, 총 청크 수 정보를 제공합니다.""",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="lookup_term",
            description="""Glossary(v2.0) 용어 조회. TRE Lemma 기반의 신학 용어 데이터를 반환합니다.
            
canonical(표준 번역), definition(정의) 등을 반환합니다.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "조회할 용어 (한국어/독일어/영어)"
                    },
                    "lang": {
                        "type": "string",
                        "default": "de",
                        "description": "대상 언어 (기본: de)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="save_translation",
            description="""번역된 청크를 저장합니다.
            
JSONL 포맷으로 _KR.jsonl 파일에 아카이빙합니다.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "문서 ID"
                    },
                    "chunk_id": {
                        "type": "string",
                        "description": "청크 ID"
                    },
                    "original_text": {
                        "type": "string",
                        "description": "원본 텍스트"
                    },
                    "translated_text": {
                        "type": "string",
                        "description": "번역된 텍스트"
                    }
                },
                "required": ["doc_id", "chunk_id", "original_text", "translated_text"]
            }
        ),
        Tool(
            name="fetch_translation_batch",
            description="번역할 청크 배치(기본 5개)를 가져옵니다. status='todo'인 항목만 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "size": {"type": "integer", "default": 5}
                },
                "required": ["doc_id"]
            }
        ),
        Tool(
            name="submit_translation_batch",
            description="번역된 청크 배치를 일괄 저장합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "translations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chunk_id": {"type": "string"},
                                "translation": {"type": "string"}
                            },
                            "required": ["chunk_id", "translation"]
                        }
                    }
                },
                "required": ["doc_id", "translations"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "search":
        query = arguments.get("query", "")
        languages = arguments.get("languages", ["ko", "en", "de"])
        source = arguments.get("source")
        limit = arguments.get("limit", 10)
        
        response = searcher.search(
            query=query,
            languages=languages,
            source=source,
            limit=limit
        )
        
        # Format response
        result_text = f"## 검색 결과\n\n"
        result_text += f"**쿼리**: {query}\n"
        result_text += f"**확장 검색어**: {', '.join(response.expanded_queries)}\n"
        result_text += f"**총 결과**: {response.total_matches}개\n\n"
        
        for i, r in enumerate(response.results, 1):
            result_text += f"### [{i}] {r.citation}\n"
            result_text += f"- **ID**: `{r.global_chunk_id}`\n"
            result_text += f"- **페이지**: {r.printed_page}\n"
            result_text += f"- **매칭**: {', '.join(r.match_terms)} ({r.match_count}회)\n"
            result_text += f"- **발췌**:\n> {r.snippet}\n\n"
        
        return [TextContent(type="text", text=result_text)]
    
    elif name == "get_chunk":
        global_chunk_id = arguments.get("global_chunk_id", "")
        
        chunk = searcher.get_chunk(global_chunk_id)
        
        if not chunk:
            return [TextContent(
                type="text",
                text=f"❌ 청크를 찾을 수 없습니다: `{global_chunk_id}`"
            )]
        
        result_text = f"## 청크 상세\n\n"
        result_text += f"**ID**: `{chunk['global_chunk_id']}`\n"
        result_text += f"**문서**: {chunk['doc_id']}\n"
        result_text += f"**PDF 페이지**: {chunk['pdf_page']}\n"
        result_text += f"**인쇄 페이지**: {chunk['printed_page']}\n"
        result_text += f"**인용**: {chunk['citation']}\n\n"
        result_text += f"### 내용\n\n{chunk['content']}\n"
        
        if chunk.get('themes'):
            result_text += f"\n### 테마\n{', '.join(chunk['themes'])}\n"
        
        return [TextContent(type="text", text=result_text)]
    
    elif name == "list_sources":
        sources = searcher.list_sources()
        
        if not sources:
            return [TextContent(
                type="text",
                text="📭 아카이브에 소스가 없습니다.\n\n청킹 파이프라인을 실행하여 문서를 추가하세요."
            )]
        
        result_text = f"## 사용 가능한 소스\n\n"
        result_text += f"총 **{len(sources)}**개 문서\n\n"
        
        for s in sources:
            result_text += f"### {s.abbr}"
            if s.volume:
                result_text += f" Vol. {s.volume}"
            if s.edition:
                result_text += f" ({s.edition}판)"
            result_text += "\n"
            result_text += f"- **ID**: `{s.doc_id}`\n"
            result_text += f"- **제목**: {s.title}\n"
            result_text += f"- **언어**: {s.language}\n"
            result_text += f"- **유형**: {s.doc_type}\n"
            result_text += f"- **청크 수**: {s.total_chunks}\n\n"
        
        return [TextContent(type="text", text=result_text)]
    
    elif name == "lookup_term":
        query = arguments.get("query", "")
        lang = arguments.get("lang", "de")
        
        results = glossary_manager.lookup(query, lang)
        
        if not results:
             return [TextContent(type="text", text=f"🔍 용어 '{query}'를 찾을 수 없습니다.")]
             
        # Format output (take top 3 matching)
        out = f"## 용어 조회: {query}\n\n"
        for idx, item in enumerate(results[:3]):
            canonical = item.get("canonical", {})
            out += f"### {canonical.get('de', query)}\n"
            out += f"- **KO**: {canonical.get('ko', '-')}\n"
            out += f"- **EN**: {canonical.get('en', '-')}\n"
            out += f"- **FR**: {canonical.get('fr', '-')}\n"
            
            definitions = item.get("definitions", {})
            if "ko" in definitions:
                 out += f"- **정의(KO)**: {definitions['ko']}\n"
            
            out += "\n"
            
        return [TextContent(type="text", text=out)]
        
    elif name == "save_translation":
        doc_id = arguments.get("doc_id")
        chunk_id = arguments.get("chunk_id")
        original = arguments.get("original_text")
        translated = arguments.get("translated_text")
        
        path = translation_archive.save_translation(doc_id, chunk_id, original, translated)
        
        return [TextContent(type="text", text=f"✅ 번역 저장 완료: `{path}`")]
        
    elif name == "fetch_translation_batch":
        doc_id = arguments.get("doc_id")
        size = arguments.get("size", 5)
        
        batch = translation_archive.get_next_batch(doc_id, size)
        
        if not batch:
            return [TextContent(type="text", text="🎉 모든 번역이 완료되었습니다! (또는 파일이 없습니다)")]
            
        # Serialize batch to JSON string for the agent to parse
        import json
        return [TextContent(type="text", text=json.dumps(batch, ensure_ascii=False, indent=2))]
        
    elif name == "submit_translation_batch":
        doc_id = arguments.get("doc_id")
        translations = arguments.get("translations", [])
        
        count = translation_archive.save_batch(doc_id, translations)
        
        return [TextContent(type="text", text=f"✅ {count}개 청크 일괄 저장 완료.")]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ 알 수 없는 도구: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
