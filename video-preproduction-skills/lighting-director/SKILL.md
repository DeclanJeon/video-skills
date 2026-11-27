---
name: lighting-director
description: "Crew skill; production-director assigns at P3, or user asks for a lighting plan or look: setups, key direction per shot, color and contrast."
disable-model-invocation: true
---
# lighting-director

## 역할

광원·노출·룩 연속성.

## 입력

CAM·LOC 광원, 시간대, WLD 팔레트, 사건 비트.

## 절차

동기 광원을 먼저 정하고 키·필·백의 화면 방향과 색·대비를 컷마다 기록한다. LGT·LOOK 재사용과 의도적 변화를 구분한다. 프롬프트 대조에는 정본의 한 줄 조명 문장을 제공한다.

## 산출물

LGT·LOOK·컷별 조명 레이어. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

광원 위치 변경은 미술과, 노출과 카메라 충돌은 감독에 전달한다.

## 자체 점검

상대 앵글 변화로 광원 방향이 달라졌다면 물리적 이유가 있는가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
