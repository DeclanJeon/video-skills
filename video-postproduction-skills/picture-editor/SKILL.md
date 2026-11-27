---
name: picture-editor
description: Use when approved source takes need assembly, cut-order, range or branch edit decisions.
disable-model-invocation: true
---

# 픽처 편집

## 입력
실제 승인 source/take/range, 전체 요구·대사/사건 anchor, 편집 의도/권한과 profile. [공통 실행 계약](../references/execution-contract.md)을 먼저 읽는다.

## 절차
1. 시스템·동일 프로그램/필수 dependency를 먼저 점검해 적합한 설치를 재사용한다. 새 설정·폰트·프로그램이 필요하면 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후 설치한다. 동의 전 download/installer를 실행하지 않는다.
2. 총괄 정본의 현재 핀/검수/stream/timebase와 원본 구간을 수령한다. 분야 변경안은 총괄 commit으로만 반영한다. anchor가 없으면 채택 구간 전체를 보호하고 certified exterior handle은0으로 둔다.
3. `EditProposal`의 순서/trim/overlap/branch를 승인 범위와 전체 요구 분모로 검사한다. 지원되지 않는 retime/VFR/conform은 명시된 verified route를 요청한다.
4. FilmCraft의 실제 item/clip IDs와 source→master ticks를 투영하고 saved native readback/export/full decode를 대조한다. field 지원을 추측하거나 다른 도구를 native 편집 성공으로 바꾸지 않는다.
5. 변경된 구간·접합·공개 순서·가시성에 필요한 전구간 QA를 반환한다. historical succeeded는 현재 마스터 채택이 아니다.

## 반환
현재 branch/edit map·원본/목표 구간, 승인 대조, 실제 native IDs/파일·decode 증거, 누락·가림·의미 변경 위험과 QA 요청.
