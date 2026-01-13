#!/usr/bin/env python3
"""
Agent-Browser Python Wrapper for Theology AI Lab
AI-friendly browser automation for journal scraping
"""
import subprocess
import json
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserAgent:
    """AI-friendly browser automation wrapper"""
    
    def __init__(self, session: Optional[str] = None):
        self.session = session or "theology_scraper"
        self.cmd_base = ["agent-browser"]
        
    def _run(self, cmd: List[str], json_output: bool = False) -> Dict:
        """Execute agent-browser command"""
        full_cmd = self.cmd_base + cmd
        if json_output:
            full_cmd.append("--json")
        full_cmd.extend(["--session", self.session])
        
        logger.debug(f"Running: {' '.join(full_cmd)}")
        
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            return {"success": False, "error": result.stderr}
        
        if json_output:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": False, "error": "Invalid JSON response"}
        
        return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
    
    def open(self, url: str):
        """Navigate to URL"""
        logger.info(f"Opening: {url}")
        return self._run(["open", url])
    
    def snapshot(self, interactive: bool = True) -> Dict:
        """Get accessibility tree with refs"""
        cmd = ["snapshot"]
        if interactive:
            cmd.append("-i")
        return self._run(cmd, json_output=True)
    
    def find_and_click(self, role: str, name: str):
        """Find by role and click"""
        return self._run(["find", "role", role, "click", "--name", name])
    
    def find_text_and_click(self, text: str):
        """Find by text and click"""
        return self._run(["find", "text", text, "click"])
    
    def find_and_fill(self, label: str, text: str):
        """Find input by label and fill"""
        return self._run(["find", "label", label, "fill", text])
    
    def get_text(self, ref: str) -> str:
        """Get text from element ref"""
        result = self._run(["get", "text", ref], json_output=True)
        return result.get("data", "") if result.get("success") else ""
    
    def get_html(self, ref: str = "body") -> str:
        """Get HTML content"""
        result = self._run(["get", "html", ref], json_output=True)
        return result.get("data", "") if result.get("success") else ""
    
    def wait(self, ms: int = 2000):
        """Wait for specified milliseconds"""
        return self._run(["wait", str(ms)])
    
    def wait_for_selector(self, selector: str):
        """Wait for element to appear"""
        return self._run(["wait", selector])
    
    def screenshot(self, path: str):
        """Take screenshot"""
        logger.info(f"Screenshot: {path}")
        return self._run(["screenshot", path])
    
    def close(self):
        """Close browser"""
        logger.info("Closing browser")
        return self._run(["close"])


# Quick test
if __name__ == "__main__":
    browser = BrowserAgent("test_session")
    browser.open("https://example.com")
    snapshot = browser.snapshot()
    print(json.dumps(snapshot, indent=2))
    browser.close()
