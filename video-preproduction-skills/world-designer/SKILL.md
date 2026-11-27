---
name: world-designer
description: "Crew skill; production-director assigns at P2, or user asks for a worldbuilding or period bible: rules, forbidden on-screen elements, palette."
disable-model-invocation: true
---
# world-designer

## 역할

세계관 정본.

## 입력

잠긴 각본·BRF·장소/고증 제약.

## 절차

1. 씬에서 불변 세계 규칙과 예외, 시대가 바꾸는 도구·행동을 추출한다.
2. 사실·가정·허구를 구분하고 출처 없는 고증은 미확인으로 표시한다.
3. 규칙마다 적용 씬, 화면 금지와 색·질감 팔레트를 묶는다.

## 산출물

양식: [WLD](assets/WLD-template.md).

WLD: rules / forbidden / palette. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

공간 배치와 실제 소품은 미술 부서 소유.

## 자체 점검

모든 화면 금지와 필수 룩이 서로 모순되지 않는지 확인한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
