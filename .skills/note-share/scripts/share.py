#!/usr/bin/env python3
"""
Just Share Please CLI - Antigravity Edition
============================================
Obsidian의 Just Share Please 플러그인 API를 호출하여 마크다운 노트를 공유합니다.

Usage:
    python jsp_share.py <파일경로>           # 새로 공유
    python jsp_share.py --update <파일경로>  # 기존 공유 업데이트
    python jsp_share.py --delete <파일경로>  # 공유 삭제
    python jsp_share.py --list               # 공유 목록

Author: Secretariat Tech Steward (스밀조)
"""

import argparse
import base64
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

import requests

# ============================================================================
# Configuration
# ============================================================================

OBSIDIAN_VAULT_PATH = Path("/Users/msn/Desktop/MS_Brain.nosync")
PLUGIN_DATA_PATH = OBSIDIAN_VAULT_PATH / ".obsidian/plugins/just-share-please/data.json"

DEFAULT_SERVER = "https://jsp.ellpeck.de"


def load_plugin_config() -> dict:
    """JSP 플러그인 설정을 로드합니다."""
    if PLUGIN_DATA_PATH.exists():
        with open(PLUGIN_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "url": DEFAULT_SERVER,
        "shared": [],
        "stripFrontmatter": True,
        "includeNoteName": True
    }


def save_plugin_config(config: dict) -> None:
    """JSP 플러그인 설정을 저장합니다."""
    with open(PLUGIN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_relative_path(file_path: Path) -> str:
    """볼트 기준 상대 경로를 반환합니다."""
    try:
        return str(file_path.relative_to(OBSIDIAN_VAULT_PATH))
    except ValueError:
        return str(file_path)


def preprocess_markdown(content: str, filename: str, config: dict) -> str:
    """마크다운을 전처리합니다 (플러그인과 동일한 로직)."""
    
    # 프론트매터 제거 옵션
    if config.get("stripFrontmatter", True):
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # 주석 제거 (%%...%%)
    content = re.sub(r'%%.*?%%', '', content, flags=re.DOTALL)
    
    # 노트 이름을 제목으로 추가
    if config.get("includeNoteName", True):
        # 이미 제목이 있는지 확인
        if not content.strip().startswith("# "):
            title = f"# {filename}\n\n"
            content = title + content
    
    return content


class JSPClient:
    """Just Share Please API 클라이언트"""
    
    def __init__(self, config: dict):
        self.server = config.get("url", DEFAULT_SERVER)
        self.config = config
    
    def share(self, content: str) -> Dict:
        """새 노트를 공유합니다."""
        response = requests.post(
            f"{self.server}/share.php",
            json={"content": content},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"공유 실패 ({response.status_code}): {response.text}")
        
        return response.json()
    
    def update(self, item_id: str, password: str, content: str) -> bool:
        """기존 공유를 업데이트합니다."""
        response = requests.patch(
            f"{self.server}/share.php?id={item_id}",
            headers={"Password": password},
            json={"content": content},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"업데이트 실패 ({response.status_code}): {response.text}")
        
        return True
    
    def delete(self, item_id: str, password: str) -> bool:
        """공유를 삭제합니다."""
        response = requests.delete(
            f"{self.server}/share.php?id={item_id}",
            headers={"Password": password},
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"삭제 실패 ({response.status_code}): {response.text}")
        
        return True
    
    def get_share_url(self, item_id: str) -> str:
        """공유 URL을 반환합니다."""
        return f"{self.server}#{item_id}"


def find_shared_item(config: dict, path: str) -> Optional[Dict]:
    """공유된 아이템을 찾습니다."""
    for item in config.get("shared", []):
        if item.get("path") == path:
            return item
    return None


def cmd_share(args, config: dict):
    """파일을 공유합니다."""
    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = OBSIDIAN_VAULT_PATH / file_path
    
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    rel_path = get_relative_path(file_path)
    
    # 이미 공유되었는지 확인
    existing = find_shared_item(config, rel_path)
    if existing and not args.force:
        print(f"⚠️  이미 공유된 파일입니다: {existing['id']}")
        print(f"   URL: {DEFAULT_SERVER}#{existing['id']}")
        print(f"   업데이트하려면 --update 옵션을 사용하세요.")
        return
    
    # 파일 읽기 및 전처리
    content = file_path.read_text(encoding="utf-8")
    processed = preprocess_markdown(content, file_path.stem, config)
    
    print(f"📄 파일: {file_path.name}")
    print(f"📝 크기: {len(content):,} bytes")
    print(f"🚀 공유 중...")
    
    client = JSPClient(config)
    result = client.share(processed)
    
    # 설정에 저장
    shared_item = {
        "id": result["id"],
        "password": result["password"],
        "path": rel_path
    }
    
    if "shared" not in config:
        config["shared"] = []
    
    # 기존 항목 제거 후 추가 (중복 방지)
    config["shared"] = [s for s in config["shared"] if s.get("path") != rel_path]
    config["shared"].append(shared_item)
    save_plugin_config(config)
    
    share_url = client.get_share_url(result["id"])
    
    print(f"\n✅ 공유 완료!")
    print(f"🔗 URL: {share_url}")
    print(f"🔑 ID: {result['id']}")
    
    # 클립보드에 복사 시도
    try:
        import subprocess
        subprocess.run(["pbcopy"], input=share_url.encode(), check=True)
        print(f"📋 클립보드에 복사됨!")
    except:
        pass
    
    # Frontmatter에 URL 추가
    update_frontmatter(file_path, share_url)


def update_frontmatter(file_path: Path, url: str) -> None:
    """마크다운 파일의 Frontmatter에 share_url을 추가/업데이트합니다."""
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # Frontmatter 패턴 확인
        fm_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.search(fm_pattern, content, re.DOTALL)
        
        if match:
            # 기존 Frontmatter가 있는 경우
            fm_content = match.group(1)
            # 이미 share_url이 있는지 확인
            if "share_url:" in fm_content:
                # 기존 URL 업데이트
                new_fm = re.sub(r'share_url:.*', f'share_url: {url}', fm_content)
            else:
                # 새 URL 추가
                new_fm = fm_content + f"\nshare_url: {url}"
            
            # 파일 내용 교체
            new_content = content.replace(f"---\n{fm_content}\n---", f"---\n{new_fm}\n---", 1)
        else:
            # Frontmatter가 없는 경우 새로 생성
            new_content = f"---\nshare_url: {url}\n---\n\n{content}"
            
        file_path.write_text(new_content, encoding="utf-8")
        print(f"📌 노트 속성(Frontmatter)에 URL이 기록되었습니다.")
        
    except Exception as e:
        print(f"⚠️ Frontmatter 업데이트 실패: {e}", file=sys.stderr)


def cmd_update(args, config: dict):
    """기존 공유를 업데이트합니다."""
    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = OBSIDIAN_VAULT_PATH / file_path
    
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    rel_path = get_relative_path(file_path)
    
    # 공유 정보 찾기
    existing = find_shared_item(config, rel_path)
    if not existing:
        print(f"❌ 공유되지 않은 파일입니다. 먼저 공유하세요.", file=sys.stderr)
        sys.exit(1)
    
    # 파일 읽기 및 전처리
    content = file_path.read_text(encoding="utf-8")
    processed = preprocess_markdown(content, file_path.stem, config)
    
    print(f"📄 파일: {file_path.name}")
    print(f"🔄 업데이트 중...")
    
    client = JSPClient(config)
    client.update(existing["id"], existing["password"], processed)
    
    print(f"\n✅ 업데이트 완료!")
    share_url = client.get_share_url(existing['id'])
    print(f"🔗 URL: {share_url}")
    
    # Frontmatter 업데이트
    update_frontmatter(file_path, share_url)


def cmd_delete(args, config: dict):
    """공유를 삭제합니다."""
    file_path = Path(args.file)
    if not file_path.is_absolute():
        file_path = OBSIDIAN_VAULT_PATH / file_path
    
    rel_path = get_relative_path(file_path)
    
    # 공유 정보 찾기
    existing = find_shared_item(config, rel_path)
    if not existing:
        print(f"❌ 공유되지 않은 파일입니다.", file=sys.stderr)
        sys.exit(1)
    
    print(f"🗑️  삭제 중: {existing['id']}")
    
    client = JSPClient(config)
    client.delete(existing["id"], existing["password"])
    
    # 설정에서 제거
    config["shared"] = [s for s in config["shared"] if s.get("id") != existing["id"]]
    save_plugin_config(config)
    
    print(f"\n✅ 삭제 완료!")


def cmd_list(args, config: dict):
    """공유 목록을 출력합니다."""
    shared = config.get("shared", [])
    
    if not shared:
        print("📭 공유된 파일이 없습니다.")
        return
    
    print(f"📚 공유된 파일 목록 ({len(shared)}개):\n")
    
    server = config.get("url", DEFAULT_SERVER)
    
    for item in shared:
        path = item.get("path", "Unknown")
        item_id = item.get("id", "???")
        url = f"{server}#{item_id}"
        
        # 파일 존재 여부 확인
        full_path = OBSIDIAN_VAULT_PATH / path
        exists = "✅" if full_path.exists() else "❌"
        
        print(f"{exists} {path}")
        print(f"   🔗 {url}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Just Share Please CLI - Obsidian 노트를 공유합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
    python jsp_share.py "010 Inbox/다이제스트.md"      # 새로 공유
    python jsp_share.py --update "010 Inbox/다이제스트.md"  # 업데이트
    python jsp_share.py --delete "010 Inbox/다이제스트.md"  # 삭제
    python jsp_share.py --list                         # 목록 보기
        """
    )
    
    parser.add_argument(
        "file",
        nargs="?",
        help="공유할 마크다운 파일 경로"
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="기존 공유를 업데이트합니다."
    )
    parser.add_argument(
        "--delete", "-d",
        action="store_true",
        help="공유를 삭제합니다."
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="공유된 파일 목록을 출력합니다."
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="이미 공유된 파일도 강제로 다시 공유합니다."
    )
    
    args = parser.parse_args()
    
    # 설정 로드
    config = load_plugin_config()
    print(f"📡 서버: {config.get('url', DEFAULT_SERVER)}")
    
    try:
        if args.list:
            cmd_list(args, config)
        elif args.file:
            if args.delete:
                cmd_delete(args, config)
            elif args.update:
                cmd_update(args, config)
            else:
                cmd_share(args, config)
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
