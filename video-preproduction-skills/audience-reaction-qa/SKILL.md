---
name: audience-reaction-qa
description: "Crew skill; production-director assigns after the screenplay draft (QA1), or user asks how audiences will react to a script. Benchmark comparison plus hypothesis-labelled viewer panel; returns verdict and ID-indexed fixes."
disable-model-invocation: true
---
# audience-reaction-qa

## 역할

각본의 수요·반응 검수.

## 입력

SCR 초안·PLT·BRF, 가능한 BMK·BOR.

## 절차

1. [개발·QA1 정본](../docs/design/04-qa1-audience-reaction.md)의 레인 A/B/C를 별도로 작성한다. 비교 불가 시 A/C는 unknown 및 최소 조사, 목표 대상 3–5명의 반응은 `hypothesis`로만 기록한다. 가설을 실제 수요와 합산하지 않는다.
2. R1–R8 각각 증거와 판정 규칙을 차례로 적용해 PASS / REVISE / RETHINK를 반환한다. 권리 문제를 점수나 흥행 추정으로 덮지 않는다.
3. 수정이 필요하면 `fix_id`, 대상 씬/대사 핀, 소유자, severity, 근거, 지시, 수락 조건을 남긴다. 2회차는 수정과 영향 비트만 재검한다.

## 산출물

양식: [QAR-1](assets/QAR-1-template.md).

QAR-1: A/B/C, 루브릭, 수정 지시, `reviewer_mode`, 잔여 위험. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

작가 대신 대사를 고치지 않는다. 인라인은 초안을 새로 읽고 독립 검수가 아니라고 표시한다.

## 자체 점검

가상 반응에 관측 라벨이 없고, 조회수·유지율·확률 숫자 예측도 없어야 한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
