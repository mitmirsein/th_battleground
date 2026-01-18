import time
import json
import os
import sys
import yaml
import glob
import re
from pathlib import Path
from datetime import datetime
import argparse

# Optional: Google GenAI (Worker만 사용)
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    try:
        import google.generativeai as genai
        HAS_GENAI = "LEGACY"
    except ImportError:
        HAS_GENAI = False

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_config():
    """config.yaml 로드 및 경로 확장"""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        print("❌ config.yaml을 찾을 수 없습니다.")
        sys.exit(1)
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if 'paths' in config:
        for key, value in config['paths'].items():
            if isinstance(value, str) and value.startswith('~'):
                config['paths'][key] = str(Path(value).expanduser())
    return config

class ConvoyAgent:
    def __init__(self, role: str):
        self.role = role.upper()
        self.config = load_config()
        
        memory_root = Path(self.config['paths']['memory_root'])
        self.convoy_dir = memory_root / "convoys"
        self.convoy_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.legacy_model = None
        if self.role == "WORKER":
            self._setup_llm()

    def _setup_llm(self):
        """GenAI 모델 초기화"""
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ [Warning] API Key가 없습니다.")
            return
            
        if not HAS_GENAI:
            print("⚠️ [Warning] google-genai 패키지가 없습니다.")
            return

        try:
            if HAS_GENAI == True:
                self.client = genai.Client(api_key=api_key)
                print("🤖 [LLM] Gemini (New SDK) 연결 완료!")
            else:
                genai.configure(api_key=api_key)
                self.legacy_model = genai.GenerativeModel('gemini-pro')
                print("🤖 [LLM] Gemini (Legacy SDK) 연결 완료!")
        except Exception as e:
            print(f"❌ LLM 연결 실패: {e}")

    # ==========================
    # FILE I/O Handlers
    # ==========================
    def _read_task(self, path: Path) -> dict:
        """JSON 또는 Markdown 파일 읽기"""
        if path.suffix == '.json':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return None
            
        elif path.suffix == '.md':
            return self._parse_markdown(path)
        return None

    def _write_task(self, path: Path, data: dict):
        """JSON 또는 Markdown 파일 쓰기"""
        if path.suffix == '.json':
            tmp = path.with_suffix('.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            tmp.rename(path)
            
        elif path.suffix == '.md':
            content = self._dump_markdown(data)
            tmp = path.with_suffix('.tmp')
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(content)
            tmp.rename(path)

    def _parse_markdown(self, path: Path) -> dict:
        """Markdown Frontmatter 파싱 (Split method)"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # --- 로 분리 (최대 2번 분리: Pre, Yaml, Body)
            parts = content.split('---', 2)
            
            # Frontmatter가 없는 경우 (parts 길이가 3 미만)
            if len(parts) < 3:
                return None
                
            # parts[0]은 첫 --- 앞이니까 비어있어야 함
            if parts[0].strip(): 
                return None
                
            yaml_text = parts[1]
            body = parts[2].strip()
            
            try:
                meta = yaml.safe_load(yaml_text) or {}
            except: meta = {}
            
            meta['content'] = body
            meta['file_type'] = 'md'
            if 'created_at' not in meta:
                 meta['created_at'] = datetime.fromtimestamp(path.stat().st_ctime).isoformat()
            
            if not meta['content']: return None
            return meta
            
        except Exception as e:
            print(f"Error parsing MD: {e}")
            return None

    def _dump_markdown(self, data: dict) -> str:
        """Dict -> Markdown 재조립 (Non-destructive & Append)"""
        body = data.get('content', '')
        # result가 있으면 무조건 추가
        result = data.get('result')
        if result:
            # 중복 방지를 위해 result 내용이 이미 끝부분에 있는지 체크할 수도 있지만,
            # 멀티턴을 위해 그냥 추가하는 게 맞음.
            if not body.strip().endswith(result.strip()):
                body += f"\n\n## 🤖 AI Result\n\n{result}\n"
            
        # 남은 data는 Frontmatter로 (content, result, file_type 제외)
        clean_meta = {k:v for k,v in data.items() if k not in ['content', 'result', 'file_type']}
        yaml_text = yaml.dump(clean_meta, allow_unicode=True, default_flow_style=False)
        return f"---\n{yaml_text}---\n{body}"

    # ==========================
    # Logic
    # ==========================
    def _update_dashboard(self):
        """대시보드 업데이트 (Multi-format & Robust)"""
        try:
            files = glob.glob(str(self.convoy_dir / "*.*"))
            tasks = []
            
            for f in files:
                try:
                    path = Path(f)
                    if path.name == 'index.html' or path.suffix not in ['.json', '.md']: continue
                    
                    data = self._read_task(path)
                    if data: 
                        data['filename'] = path.name
                        tasks.append(data)
                except Exception as inner_e:
                    print(f"⚠️ 파일 읽기 실패 ({path.name}): {inner_e}")
                
            # 최신순 정렬 (완료일 > 생성일)
            tasks.sort(key=lambda x: str(x.get('completed_at') or x.get('created_at', '')), reverse=True)
            
            html = """<!DOCTYPE html><html><head><meta charset="utf-8">
            <meta http-equiv="refresh" content="5">
            <style>
                body { background: #1e1e1e; color: #ddd; font-family: sans-serif; padding: 20px; }
                .card { background: #2d2d2d; padding: 15px; margin-bottom: 10px; border-left: 4px solid #555; border-radius: 4px;}
                .status-pending { border-color: #f1c40f; } .status-processing { border-color: #2ecc71; } .status-completed { border-color: #3498db; }
                .badge { background: #444; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
                .md-badge { color: #e83e8c; }
                .content { margin-top: 8px; font-weight: bold; }
                .time { color: #888; font-size: 0.8em; margin-left: 5px; }
            </style></head><body><h1>🛰️ Convoy Dashboard</h1>"""
            
            for t in tasks:
                status = t.get('status', 'unknown')
                ftype = "MD" if t.get('file_type') == 'md' else "JSON"
                
                # 표시 우선순위: 완료일 -> 생성일
                ts = str(t.get('completed_at') or t.get('created_at', ''))[:19]
                
                content_preview = str(t.get('content', ''))[:100].replace('<', '&lt;')
                
                html += f"""<div class="card status-{status}">
                    <div>
                        <span class="badge">{status.upper()}</span> 
                        <span class="badge md-badge">{ftype}</span> 
                        <span class="time">Last: {ts}</span> 
                        ({t.get('filename')})
                    </div>
                    <div class="content">{content_preview}...</div>
                </div>"""
            html += "</body></html>"
            
            with open(self.convoy_dir / "index.html", "w", encoding="utf-8") as f: f.write(html)
            
        except Exception as e:
            print(f"⚠️ 대시보드 전체 업데이트 실패: {e}")

    def process_task(self, task_file: Path, data: dict):
        print(f"⚙️ 작업 처리 중: {task_file.name}")
        
        data['status'] = 'processing'
        data['worker_id'] = 'iMac_Pro'
        self._write_task(task_file, data)
        self._update_dashboard()

        # LLM 호출
        result_text = ""
        try:
            prompt = f"다음 요청을 처리해주세요.\n[CONTEXT]: {data.get('content', '')}"
            # 모델 선택 (Frontmatter > Default)
            target_model = data.get('model', 'gemini-3-flash-preview') 
            
            if self.client:
                # New SDK
                res = self.client.models.generate_content(model=target_model, contents=prompt)
                result_text = res.text
            elif self.legacy_model:
                # Legacy (모델명 호환성 주의)
                res = self.legacy_model.generate_content(prompt)
                result_text = res.text
            else:
                result_text = "⚠️ LLM 미설정 Error"
        except Exception as e:
            result_text = f"Error: {e}"

        data['result'] = result_text
        data['status'] = 'completed'
        data['completed_at'] = datetime.now().isoformat()
        self._write_task(task_file, data)
        self._update_dashboard()
        print(f"✅ 완료: {task_file.name}")

    def run_loop(self):
        print(f"🚚 [Convoy] Worker Running (MD Support)... Monitor: {self.convoy_dir}")
        self._update_dashboard() # Boot Update
        
        while True:
            # JSON and MD scan
            files = list(self.convoy_dir.glob("*"))
            if self.role == "WORKER":
                for f in files:
                    if f.suffix not in ['.json', '.md']: continue
                    data = self._read_task(f)
                    if data and data.get('status') in ['pending', 'brainstorming', 'todo']:
                        self.process_task(f, data)
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", default="WORKER")
    args = parser.parse_args()
    ConvoyAgent(args.role).run_loop()
