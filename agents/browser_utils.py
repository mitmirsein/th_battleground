import subprocess
import json
from typing import Dict, List, Optional

class AgentBrowser:
    """
    Agent-Browser CLI wrapper for AI-friendly web automation.
    Extracted from legacy Librarian agent.
    """
    
    def __init__(self, session: str = "default_session"):
        self.session = session
        
    def _run(self, cmd: List[str], json_output: bool = False) -> Dict:
        """Execute agent-browser command"""
        full_cmd = ["agent-browser"] + cmd
        if json_output:
            full_cmd.append("--json")
        full_cmd.extend(["--session", self.session])
        
        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"success": False, "error": result.stderr}
            
            if json_output:
                try:
                    return json.loads(result.stdout)
                except:
                    return {"success": False, "raw": result.stdout}
            
            return {"success": True, "stdout": result.stdout}
        except FileNotFoundError:
             return {"success": False, "error": "agent-browser executable not found."}
    
    def open(self, url: str): return self._run(["open", url])
    def wait(self, ms: int): return self._run(["wait", str(ms)])
    def snapshot(self): return self._run(["snapshot", "-i"], json_output=True)
    def get_text(self, ref: str): return self._run(["get", "text", ref], json_output=True)
    def click(self, ref: str): return self._run(["click", ref])
    def screenshot(self, path: str): return self._run(["screenshot", path])
    def close(self): return self._run(["close"])
