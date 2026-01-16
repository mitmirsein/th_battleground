#!/usr/bin/env python3
"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  deacon.py — The Watchdog (수석 부제)                                ┃
┃                                                                       ┃
┃  "Peppone 동지, 시스템 순찰 결과를 보고합니다."                        ┃
┃  Gas Town의 철학을 계승하여 볼트와 인프라의 위생을 책임집니다.        ┃
┃                                                                       ┃
┃  Usage:                                                               ┃
┃    python deacon.py --patrol             # 전체 순찰 (Patrol)         ┃
┃    python deacon.py --monitor            # 지속 감시 (Watchdog Mode)  ┃
┃                                                                       ┃
┃  Components:                                                          ┃
┃    - Tech Steward (인프라)                                            ┃
┃    - Gardener (데이터/링크)                                            ┃
┃                                                                       ┃
┃  Author: ARC Secretariat                                              ┃
┃  Version: 1.0.0 (Gas Town Inspired)                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 같은 디렉토리의 모듈 임포트
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

try:
    from steward import TechSteward
    from gardener import GardenerAgent
except ImportError as e:
    print(f"❌ [Deacon] 필수 컴포넌트 로드 실패: {e}")
    print("gardener.py와 steward.py가 같은 디렉토리에 있는지 확인하세요.")
    sys.exit(1)

class Deacon:
    def __init__(self):
        self.name = "Deacon"
        self.steward = TechSteward()
        
        # Steward가 감지한 projects_dir을 기준으로 Brain 경로 추정
        # ../Projects.nosync -> ../../MS_Brain 또는 동등 레벨의 MS_Brain 등 환경에 따라 다름
        # 사용자의 경우: /Users/msn/Desktop/MS_Brain (기본값)
        
        # 1. PATHS["projects_dir"] = .../MS_Dev.nosync/projects (가정)
        # 2. 일반적으로 MS_Brain은 데스크탑 루트에 있음
        
        self.vault_path = Path("/Users/msn/Desktop/MS_Brain")
        if not self.vault_path.exists():
            # 혹시 이름이 다를 경우를 대비해 steward 상위에서 탐색
            potential_path = self.steward.paths["project_root"].parent / "MS_Brain"
            if potential_path.exists():
                self.vault_path = potential_path
             
        self.gardener = GardenerAgent(vault_path=str(self.vault_path))
        
        # Report Card
        self.status = {
            "timestamp": "",
            "infrastructure": "UNKNOWN",
            "data_hygiene": "UNKNOWN",
            "issues": []
        }

    def patrol(self, full_scan: bool = True):
        """전체 순찰 수행"""
        print(f"\n🐶 [{self.name}] 순찰을 시작합니다... (Full Scan: {full_scan})")
        start_time = datetime.now()
        self.status["timestamp"] = start_time.isoformat()
        self.status["issues"] = [] # 초기화
        
        # ─────────────────────────────────────────────────────────────
        # 1. 인프라 점검 (Steward)
        # ─────────────────────────────────────────────────────────────
        print(f"\n🔧 [Phase 1] 인프라 점검 (Tech Steward)")
        pipeline_status = self.steward.check_pipeline()
        venv_status = self.steward.audit_venv()
        
        # 인프라 상태 판정
        infra_issues = []
        if pipeline_status["overall_status"] != "✅ 정상":
            infra_issues.append(f"파이프라인 경고: {', '.join([k for k, v in pipeline_status['checks'].items() if v.get('status') != 'ok'])}")
            
        if "warning" in venv_status.get("recommendation", "") or "크기" in venv_status.get("recommendation", ""):
             infra_issues.append(f"VENV 용량 경고 ({venv_status.get('total_size_gb')}GB)")
             
        if infra_issues:
            self.status["infrastructure"] = "⚠️ 주의"
            self.status["issues"].extend(infra_issues)
        else:
            self.status["infrastructure"] = "✅ 양호"

        # ─────────────────────────────────────────────────────────────
        # 2. 데이터 위생 점검 (Gardener)
        # ─────────────────────────────────────────────────────────────
        print(f"\n🎋 [Phase 2] 데이터 위생 점검 (Gardener)")
        
        if full_scan:
            try:
                data_hygiene = self.gardener.check_vault_hygiene()
                
                broken_count = len(data_hygiene.get("broken_links", []))
                missing_meta_count = len(data_hygiene.get("missing_metadata", []))
                
                if broken_count > 0 or missing_meta_count > 0:
                    self.status["data_hygiene"] = f"⚠️ 이슈 발견"
                    if broken_count > 0:
                        self.status["issues"].append(f"데이터 위생: 깨진 링크 {broken_count}개 발견")
                    if missing_meta_count > 0:
                        self.status["issues"].append(f"데이터 위생: 메타데이터 누락 {missing_meta_count}개 발견")
                else:
                    self.status["data_hygiene"] = "✅ 청결"
            except Exception as e:
                self.status["data_hygiene"] = "❌ 오류"
                self.status["issues"].append(f"Gardener 스캔 실패: {e}")
        else:
            print("   (Skipped: Use --full for deeper scan)")
            self.status["data_hygiene"] = "⏭️ 통과 (Skipped)"

        # 3. 종합 보고
        self._report(datetime.now() - start_time)

    def _report(self, duration):
        """순찰 결과 리포트 출력"""
        print("\n" + "="*60)
        print(f"📜 [Deacon's Patrol Report]")
        print(f"⏱️ 소요 시간: {duration}")
        print("-" * 60)
        print(f"🏗️ 인프라 상태: {self.status['infrastructure']}")
        print(f"📚 데이터 위생: {self.status['data_hygiene']}")
        print("-" * 60)
        
        if self.status["issues"]:
            print("🚨 발견된 이슈:")
            for issue in self.status["issues"]:
                print(f"   - {issue}")
            print("\n💡 조치 권고:")
            print("   > `python agents/steward.py --clean` 으로 정리 필요")
            print("   > `python agents/gardener.py --check` 로 상세 내역 확인")
        else:
            print("✨ 모든 시스템이 정상입니다. Peppone 동지.")
            print("   (System is clean. Ready for intense theological work.)")
        print("="*60 + "\n")

    def monitor(self, interval_minutes: int = 60):
        """지속 감시 모드"""
        print(f"📡 [{self.name}] 감시 모드 시작 (주기: {interval_minutes}분)")
        try:
            while True:
                self.patrol(full_scan=True)
                print(f"💤 [{self.name}] 대기 모드 진입... ({datetime.now().strftime('%H:%M:%S')})")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print(f"\n👋 [{self.name}] 감시 종료.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deacon - The System Watchdog")
    parser.add_argument("--patrol", action="store_true", help="1회성 전체 순찰")
    parser.add_argument("--full", action="store_true", default=True, help="전체 데이터 정밀 스캔 포함")
    parser.add_argument("--monitor", action="store_true", help="데몬 모드 (지속 감시)")
    parser.add_argument("--interval", type=int, default=60, help="감시 주기 (분)")
    
    args = parser.parse_args()
    
    deacon = Deacon()
    
    # 기본 동작: 인자가 없어도 순찰 수행
    if args.monitor:
        deacon.monitor(args.interval)
    else:
        deacon.patrol(full_scan=args.full)
