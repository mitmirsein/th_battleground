import time
import shutil
import os
from pathlib import Path
import yaml
import sys
import datetime

def load_config():
    """config.yaml 로드 및 경로 ~ 확장"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'paths' in config:
        for key, value in config['paths'].items():
            if isinstance(value, str) and value.startswith('~'):
                config['paths'][key] = str(Path(value).expanduser())
    return config

class SorterAgent:
    def __init__(self):
        config = load_config()
        self.memory_root = Path(config['paths']['memory_root'])
        
        # 작업 공간 정의
        self.inbox_dir = self.memory_root / "inbox"
        self.library_dir = self.memory_root / "library"
        
        # 규칙 정의
        self.rules = {
            "pdf": "pdf_shelf",
            "epub": "ebooks",
            "png": "images",
            "jpg": "images",
            "jpeg": "images",
            "md": "notes",
            "txt": "notes",
            "json": "data"
        }
        self.default_folder = "misc"

        # 초기화
        self._init_folders()
        
    def _init_folders(self):
        """필요한 폴더 자동 생성"""
        if not self.memory_root.exists():
            print(f"❌ 메모리 경로 없음: {self.memory_root}")
            sys.exit(1)
            
        # Inbox 및 Library 하위 폴더 생성
        self.inbox_dir.mkdir(exist_ok=True)
        for folder in set(self.rules.values()):
            (self.library_dir / folder).mkdir(parents=True, exist_ok=True)
        (self.library_dir / self.default_folder).mkdir(parents=True, exist_ok=True)
        
        print(f"📂 [Sorter] 작업 환경 초기화 완료.")
        print(f"   감시 경로: {self.inbox_dir}")
        print(f"   대상 경로: {self.library_dir}")

    def sort_file(self, file_path: Path):
        """파일 분류 및 이동 로직"""
        # 1. 파일이 완전히 전송되었는지 확인 (Syncthing 중일 수 있음)
        # 간단한 방법: 크기가 변하지 않을 때까지 대기
        initial_size = -1
        try:
            while initial_size != file_path.stat().st_size:
                initial_size = file_path.stat().st_size
                time.sleep(0.5)
        except FileNotFoundError:
            return # 그새 사라졌으면 무시

        # 2. 분류 결정
        ext = file_path.suffix.lower().lstrip(".")
        target_subfolder = self.rules.get(ext, self.default_folder)
        target_dir = self.library_dir / target_subfolder
        
        # 3. 이동 (파일명 중복 시 타임스탬프 추가)
        destination = target_dir / file_path.name
        if destination.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            destination = target_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
            
        try:
            shutil.move(str(file_path), str(destination))
            print(f"🚚 [Moved] {file_path.name} -> {target_subfolder}/")
        except Exception as e:
            print(f"❌ [Error] 이동 실패 ({file_path.name}): {e}")

    def run(self):
        print("👀 [Sorter] Inbox 감시 시작... (Ctrl+C to stop)")
        try:
            while True:
                # Inbox 스캔
                files = [f for f in self.inbox_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
                
                if files:
                    print(f"✨ [Detected] {len(files)}개 파일 발견!")
                    for file in files:
                        self.sort_file(file)
                        
                time.sleep(2) # 2초마다 확인
        except KeyboardInterrupt:
            print("\n👋 Sorter 퇴근합니다.")

if __name__ == "__main__":
    agent = SorterAgent()
    agent.run()
