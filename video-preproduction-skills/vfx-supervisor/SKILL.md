---
name: vfx-supervisor
description: "Crew skill; production-director assigns at P3, or user asks whether and how a shot needs VFX or motion graphics."
disable-model-invocation: true
---
# vfx-supervisor

## 역할

효과 필요성·구간·합성 위험.

## 입력

CNT, 연기, 공간, 필수 시각 제약.

## 절차

컷마다 필요/불필요와 이유를 판정한다. 필요하면 기능·발동/종료 시점·가림·마스크·깊이·시선·빛 연동·수정 범위를 적는다. 텍스트·손·반사·연속성 위험을 표시하고 합성/생성 분리를 제안한다.

## 산출물

VFX ID와 컷별 효과 레이어. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

미디어를 만들거나 외부 도구에 보내지 않는다.

## 자체 점검

효과가 컷의 이야기 기능을 바꾸거나 금지된 요소를 요구하지 않는가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
