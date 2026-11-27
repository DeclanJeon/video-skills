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

식별해야 할 디테일이 있는 컷은 노출 목표를 그 대상에 붙인다. 예: 병 정면을 읽는 순간, 라벨의 흰 면에 반사가 걸려도 획이 사라지지 않고 손과 뚜껑의 접점이 암부에 묻히지 않는지 실제 패널에서 확인한다. 보드만 있다면 이를 다음 이미지의 수락 조건으로 남긴다.

## 산출물

LGT·LOOK·컷별 조명 레이어. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

광원 위치 변경은 미술과, 노출과 카메라 충돌은 감독에 전달한다.

## 자체 점검

상대 앵글 변화로 광원 방향이 달라졌다면 물리적 이유가 있는가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
