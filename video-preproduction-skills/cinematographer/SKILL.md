---
name: cinematographer
description: "Crew skill; production-director assigns at P3, or user asks for camera design: shot size, lens, axis, movement and transitions per cut."
disable-model-invocation: true
---
# cinematographer

## 역할

촬영 거리·축·구도·무빙.

## 입력

CNT·LOC 평면·DNT·연기 레이어.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)에서 상태 기준과 연결 의도를 먼저 읽고 카메라를 설계한다. 인물·소품의 세계 공간 상태를 계승하되 리버스숏의 화면 투영은 새 CAM에서 검토한다. 선행 구도 복제 대신 축·시선·동작 연결을 확인하고 충돌을 반환한다.

컷마다 앵글·렌즈·심도·프레임 크기·주제 위치·시선을 적고 무빙 이유 또는 고정 이유를 적는다. 화면 방향을 기준으로 CTY 축을 기록한다. 축 이탈은 동기와 리셋 컷을 제안한다. 컷별로 제안한 키 라이트의 화면 방향(좌·우·위·정면·후면)과 근거를 적는다. 확정되지 않은 리버스 투영이나 키 선택은 컷마다 `unverified`로 남겨 조명 부서에 넘기고, 공통 광원 설명으로 대신하지 않는다. 장면 정점이 지정되고 구도 고정 제약이 없으면, 같은 인물의 이전 컷보다 정점 컷을 한 단계 타이트하게 잡아 차이를 컷별 표에서 확인한다(PP-19). 반대로 고정 제약이 있으면 예외와 이유를 남긴다. 실제 프리비즈가 필요하면 감독에게 요청한다.

액션 구간은 [액션 연출 계약](../docs/design/12-action-direction-contract.md) §4 샷 팔레트로 크기·앵글·무빙·위협 노출을 배분한다. 정면 일렬 구도와 같은 룩 연속을 피하고, 위협 신체 일부를 전경에 둔 깊이 샷과 매크로 인서트로 동작을 운반한다.

## 산출물

CAM 셋업과 컷별 카메라 레이어. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

조명의 품질·방향은 조명 부서와 합의한다.

## 자체 점검

반대 쇼트의 시선이 만나고 카메라 위치·가시성이 공간에서 가능한가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
