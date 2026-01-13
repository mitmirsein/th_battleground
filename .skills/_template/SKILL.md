---
name: Template Skill
description: A template for creating new Agent Skills within the MS_Dev ecosystem.
version: 0.1.0
---

# Template Skill

## 1. Description
이 스킬은 새로운 Agent Skill을 생성하기 위한 **기본 템플릿**입니다. 이 폴더를 복사하여 새로운 스킬을 만드세요.

## 2. Context (언제 사용하나?)
- 사용자가 새로운 반복 작업(워크플로우)을 "스킬"로 정의하고 싶을 때.
- 특정 도구 사용 절차를 표준화하고 싶을 때.

## 3. Instructions (실행 절차)
1.  사용자의 요청을 분석하여 필요한 작업 단계를 파악한다.
2.  `scripts/` 폴더에 있는 도구가 필요하다면 실행한다.
    - 실행 예시: `python {skill_path}/scripts/main.py`
3.  작업 결과를 사용자에게 간결하게 보고한다.

## 4. Rules & Preferences
- 모든 스크립트는 `shared_venv` 환경에서 실행되어야 한다.
- 결과물은 항상 마크다운 형식을 준수한다.
