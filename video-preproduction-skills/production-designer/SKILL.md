---
name: production-designer
description: "Crew skill; production-director assigns at P2, or user asks for locations, buildings, environments, backgrounds or props with layouts and states."
disable-model-invocation: true
---
# production-designer

## 역할

장소·환경·세트·소품.

## 입력

SCR·WLD와 촬영 제약.

## 절차

1. 장소 LOC, 세트 SET, 환경 ENV, 소품 PRP를 구분한다.
2. 장소는 4뷰, plan에 출입·광원·동선, layers에 전·중·후경을 지정한다. 환경은 시간대·계절·날씨를 고정한다.
3. 소품은 초기 상태·손/소유자·이동·보이는 컷을 기록한다.

## 산출물

양식: [LOC](assets/LOC-template.md) · [SET](assets/SET-template.md) · [ENV](assets/ENV-template.md) · [PRP](assets/PRP-template.md).

LOC/SET/ENV/PRP와 미배정 대상 목록. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

빛의 실제 방향·노출은 조명감독, 공간 속 광원 위치는 미술.

## 자체 점검

4뷰에 모순 없는 출입구/광원 및 컷별 소품 추적을 확인한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
