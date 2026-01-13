# 💻 MS_Dev Workspace Constitution

> **Core Role:** This is the unified **development environment** for theological research tools.
> **Key Principle:** Agent Skills First.

---

## 🛠️ Tech Stack

| Category | Preference |
| :--- | :--- |
| **Python** | 3.11 (via `shared_venv`) |
| **Architecture** | **Agent Skills Protocol** (Folder-based Modules) |
| **Search Engine** | **msn_th_db** (JSONL + MCP + grep) |

---

## 📁 Key Directories

| Path | Purpose |
| :--- | :--- |
| **`.skills/`** | **Agent Skills Registry** (Standardized Capabilities) |
| **`agents/`** | Backend Scripts & Maintenance Tools |
| **`projects/`** | Active Development (e.g., `msn_th_db`) |
| **`data/`** | JSONL Archives & Resources |

---

## 🤖 Skills Overview

모든 작업은 `.skills/` 내의 스킬을 호출하여 수행합니다.

- **`bible-meditation`**: 묵상 프로토콜
- **`journal-collector`**: 저널 수집
- **`theology-translator`**: 신학 번역 및 검수
- **`theology-chunker`**: PDF 청킹 및 DB화
- **`theology-searcher`**: 3중 언어 RAG 검색

> **Developer Note**: 새로운 기능을 추가할 때는 `agents/`에 스크립트를 작성하고, `.skills/`에 `SKILL.md`를 만들어 등록하십시오.

---

## 🚀 Workflow Shortcuts (Deprecated)

기존의 `/vector-db`, `#arc` 등의 명령어는 모두 **Agent Skills**로 대체되었습니다.
사용자의 자연어 요청("번역해줘", "묵상해줘")이 곧 명령어입니다.


