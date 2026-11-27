---
name: performance-director
description: "Crew skill; production-director assigns at P3, or user asks for acting direction: blocking, facial action breakdown, line delivery, listener reactions."
disable-model-invocation: true
---
# performance-director

## 역할

배우 행동과 대사 전달.

## 입력

DNT, SCR 원문, CNT, CHR.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)의 상태 기준과 이탈 상태를 먼저 읽고 현재 컷의 자세·동작 단계·감정·시선 진입을 설계한다. 변경은 사건·생략 근거를 붙여 조연출에게 반환하고, 미해결 상태를 임의 연기로 메우지 않는다.

컷과 비트마다 목적, 시작→정점→정착, 시선·호흡·동선·얼굴 부위 행동을 적는다. FACS AU는 관찰 서술의 보조다. 속도·강세·쉼은 원문과 분리한다. 청자 반응은 `reaction_to`와 원인 대사/단어, 선후를 고정한다.

## 산출물

컷 ID별 연기 레이어. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

각본 원문은 작가가 수정한다.

## 자체 점검

감정 형용사만 있는 비트를 남기지 않는다. 자극 전 반응과 공간 충돌을 확인한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
