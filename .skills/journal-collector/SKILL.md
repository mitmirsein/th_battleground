---
name: Journal Collector
description: Automates the collection of theological journal articles using the Librarian agent.
version: 1.0.0
---

# Journal Collector Skill

## 1. Description
이 스킬은 신학 저널(KuD, EvTh, ZNW 등)의 특정 권/호를 수집하여 로컬에 저장하고, 메타데이터를 정리하는 작업을 수행합니다. `agents/librarian.py`를 기반으로 작동합니다.

## 2. Trigger
- 사용자가 "저널 수집해줘", "KuD 85권 가져와" 등의 요청을 할 때.
- "#수집", "#스크래핑" 키워드가 감지될 때.

## 3. Workflow Steps

1.  **Parameter Extraction (정보 추출)**
    - 사용자 요청에서 다음 정보를 추출하십시오.
        - **Journal Code**: `kud` (Kerygma und Dogma), `evth` (Evangelische Theologie), `znw` (ZNW) 등.
        - **Band (권)**: 숫자.
        - **Heft (호)**: 숫자.
    - **Missing Info**: 정보가 부족하면 사용자에게 되물어 확인하십시오.

2.  **Execution (실행)**
    - 추출된 정보를 바탕으로 다음 명령어를 실행하십시오.
    - `python agents/librarian.py --journal {code} --band {band} --heft {heft}`
    - 일반 URL 스크래핑인 경우:
    - `python agents/librarian.py --url "{url}" --agent`

3.  **Verification (확인)**
    - 명령어가 성공적으로 종료되었는지 확인하십시오.
    - 수집된 파일의 위치와 요약 정보를 사용자에게 보고하십시오.

## 4. Tips
- **Cloudflare**: 스크래핑이 막힐 경우, 사용자에게 브라우저 모드를 제안하거나 수동 개입을 요청하십시오.
- **Backup**: 수집된 데이터는 기본적으로 `010 Inbox` 또는 지정된 프로젝트 폴더에 저장됩니다.
