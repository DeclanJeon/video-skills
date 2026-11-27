---
name: video-postproduction-skills
description: Use when an explicitly selected video project needs local postproduction from approved production sources.
disable-model-invocation: true
---

# 로컬 후반작업

## 입력
실제 production Handoff와 고정 요구 snapshot/schema/brief/profile/권한, 승인 source/take/range, receiver가 필요하다. source deliverable은 최종 영상 완료가 아니다.

## 절차
1. [실행 계약](references/execution-contract.md)을 읽고 시스템·동일 프로그램을 점검한다. 새 설치가 필요하면 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후에만 설치한다. 기존 적합한 설치를 먼저 재사용한다.
2. [총괄](postproduction-supervisor/SKILL.md)이 현재 정본·단일 writer·작업 DAG를 소유한다. [picture](picture-editor/SKILL.md), [motion](motion-compositor/SKILL.md), [color](color-finisher/SKILL.md), [sound](sound-editor-mixer/SKILL.md), [caption](caption-editor/SKILL.md)은 승인 범위의 분야 변경안을 반환한다. 이 링크는 새 agent dispatch 권한이 아니다.
3. [finishing](finishing-operator/SKILL.md)의 실제 결과를 [QA](postproduction-qa/SKILL.md)가 최종 파일 기준으로 검수한다. 불완전/unknown/stale/미청취/조건 미해소는 완료로 세지 않는다.
4. 현재 PG와 필수 deliverables가 닫힐 때 로컬 납품한다. master-only/editable, fixture/reported, 가로/세로 branch를 구별한다. global 등록·업로드·게시를 수행하지 않는다.

## 반환
원장 revision, 실제 source→native→output 계보, 분야/coverage/fix/render/QA/delivery 별 진행, 열린 조치. 현재 CLI는 `python3 scripts/postproduction.py --help`, 외부 입력은 [schemas](schemas/)를 따른다.
