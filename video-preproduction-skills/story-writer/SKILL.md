---
name: story-writer
description: "Crew skill; production-director assigns at P1, or user asks for a synopsis, plot beats or screenplay draft with dialogue. Writes SYN, PLT, SCR."
disable-model-invocation: true
---
# story-writer

## 역할

시놉시스와 각본.

## 입력

BRF·BOR, 있으면 번호가 있는 QA1 수정 지시.

## 절차

1. SYN에 로그라인·인물 목표·충돌·결말의 대가를, PLT에는 `Bnn`별 기능·씬·시간·관측되는 결과를 적는다. 첫 약속과 마지막 보상이 이어져야 한다.
2. SCR은 씬별 지문과 대사 `- D001: 원문`을 분리한다. `Dnnn`마다 화자·속도·강세·쉼을 별도 메타에 둔다. 무대사는 시각 행동의 원인/결과와 의도된 침묵을 쓴다.
3. [발화 계약](../production-ledger/references/ledger-schema.md#타임라인-계산-입력)으로 추정 길이를 확인한다. BRF 대비 ±10% 이탈은 assumptions에 초과량과 축약/연장 선택으로 기록한다.
4. QA1 재작업은 fix 대상과 영향 비트만 수정하고 이전 ID를 보존한다. 새 버전과 바뀐 범위를 보고한다.

## 산출물

양식: [SYN](assets/SYN-template.md) · [PLT](assets/PLT-template.md) · [SCR](assets/SCR-template.md).

SYN·PLT·SCR 및 추정 시간표. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

촬영, FACS AU, 편집 선택은 콘티 부서에 남긴다.

## 자체 점검

대사 ID 중복 0; 원문과 전달 지시를 혼합하지 않는다. QA1 전 각본을 잠그지 않는다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
