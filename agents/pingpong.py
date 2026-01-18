import time
import json
import argparse
from pathlib import Path
import yaml
import sys

def load_config():
    """config.yaml에서 설정 로드 (~ 경로 자동 확장)"""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        print("❌ config.yaml을 찾을 수 없습니다.")
        sys.exit(1)
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # ~ (홈 디렉토리) 확장 - 양쪽 머신 호환성
    if 'paths' in config:
        for key, value in config['paths'].items():
            if isinstance(value, str) and value.startswith('~'):
                config['paths'][key] = str(Path(value).expanduser())
    
    return config

class PingPongAgent:
    def __init__(self, role: str):
        self.role = role.upper()  # PING or PONG
        self.opponent = "PONG" if self.role == "PING" else "PING"
        
        # Load Config & Memory Path
        config = load_config()
        memory_root = Path(config['paths']['memory_root'])
        
        if not memory_root.exists():
            print(f"❌ 메모리 경로를 찾을 수 없습니다: {memory_root}")
            print("   Syncthing이 제대로 설정되었는지 확인하세요.")
            sys.exit(1)
            
        self.game_file = memory_root / "pingpong.json"
        
    def read_state(self):
        """게임 상태 읽기"""
        if not self.game_file.exists():
            return None
        try:
            with open(self.game_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None  # 파일 쓰는 중일 수 있음
            
    def write_state(self, turn: str, count: int, message: str):
        """게임 상태 쓰기"""
        state = {
            "turn": turn,
            "count": count,
            "last_player": self.role,
            "message": message,
            "timestamp": time.time()
        }
        # Atomic wite (tmp 파일 쓰고 rename) 방식으로 충돌 방지
        tmp_file = self.game_file.with_suffix('.tmp')
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        tmp_file.rename(self.game_file)
        
    def play(self):
        print(f"🏓 [{self.role}] 선수 입장! (Memory: {self.game_file})")
        print(f"   상대방({self.opponent})의 서브를 기다립니다...")
        
        last_count = -1
        
        while True:
            state = self.read_state()
            
            # 1. 게임 초기화 (아무도 없으면 PING이 먼저 시작)
            if state is None:
                if self.role == "PING":
                    print("🚀 게임 시작! 서브 넣습니다!")
                    self.write_state("PONG", 1, "First Serve!")
                    time.sleep(1) # Syncthing 전파 대기
                    continue
                else:
                    time.sleep(1)
                    continue
            
            # 2. 내 차례인지 확인
            current_turn = state.get("turn")
            count = state.get("count", 0)
            
            if current_turn == self.role:
                # 이미 내가 처리한 턴인지 확인 (중복 방지)
                if count != last_count:
                    print(f"\n🎾 [Recv] 공을 받았습니다! (Count: {count})")
                    print(f"   Message: {state.get('message')}")
                    
                    # 처리 중... (3초 딜레이로 생각하는 척)
                    print("   Thinking...", end="", flush=True)
                    for _ in range(3):
                        time.sleep(0.5)
                        print(".", end="", flush=True)
                    print(" Smash! 💥")
                    
                    # 공 넘기기
                    self.write_state(self.opponent, count + 1, f"Hello from {self.role}!")
                    last_count = count + 1
                    print(f"   -> {self.opponent}에게 공을 넘겼습니다. (Count: {count + 1})")
            
            else:
                # 상대방 턴이면 대기
                # 터미널이 너무 조용하면 심심하니 5초마다 점 찍기
                pass
                
            time.sleep(1) # 폴링 간격

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Agent Ping Pong Test")
    parser.add_argument("--role", type=str, required=True, choices=["PING", "PONG"], help="Agent Role")
    args = parser.parse_args()
    
    try:
        agent = PingPongAgent(args.role)
        agent.play()
    except KeyboardInterrupt:
        print("\n\n🛑 게임 종료. 수고하셨습니다!")
