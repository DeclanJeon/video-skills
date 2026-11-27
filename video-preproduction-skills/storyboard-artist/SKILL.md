---
name: storyboard-artist
description: "Crew skill; production-director assigns at P4 and P5, or user asks for a storyboard: panels plus the index row linking every upstream document; assembles the sheet."
disable-model-invocation: true
---
# storyboard-artist

## 역할

콘티에서 패널과 시트 설계.

## 입력

검수된 CNT·바이블·연기·카메라·조명.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)와 해당 CTY 핀을 먼저 읽고 시작·정점·끝 패널을 설계한다. 패널 순간의 상태와 컷 사이 연결을 대조하고 인덱스의 기존 `continuity`에 컷별 계약 핀을 남긴다. 관련 선행 이미지가 있으면 함께 확인하며, 이미지 미생성 때는 텍스트 설계를 진행하고 시각 QA는 미검증으로 남긴다.

같은 장소의 재등장, 소품 접촉·인계, 가림·카메라 경로가 이야기 이해를 좌우하면 [공간 프리비즈 분기](references/spatial-previs.md)를 시트 확정 전에 적용한다.

액션 구간에서 인물 3명 이상과 대형 위협이 함께 움직이면 [액션 연출 계약](../docs/design/12-action-direction-contract.md) §6에 따라 패널 이미지 전에 프리비즈를 실제로 렌더하고, 그 스틸을 패널 생성의 구도 참조로 넘긴다.

[아티팩트 계약](../docs/design/03-artifact-index.md)에 따라 컷당 시작/정점/끝 중 필요한 패널을 고른다. 컷별 인덱스에 대사 원문과 정본 핀을 담는다. 음향 헤더 `SND`는 컷의 `voice`(`VOC`)나 `ambience`(`AMB`)를 대체하지 않는다. 각각 실제 등록 핀을 쓰고, 미제공 핀은 납품의 `missing_inputs`에 남긴다. 정본 파일이 있으면 `index_lint --stage board`로 값의 형식·접두사·대상까지 검사한다. CSV 열 개수 일치만으로 통과 처리하지 않는다. 이미지가 제공되면 패널 ID와 실제 파일을 대조한 뒤 `python3 scripts/assemble_sheet.py --index INDEX --images DIR --out SHEET.png`로 조립한다. 출력과 셀 매핑 파일을 열어 확인한다. 미생성·결함 패널은 사유를 남긴다.

## 산출물

양식: [STB](assets/STB-template.md) · [인덱스 열](assets/index-template.csv) · [헤더](assets/index-header-template.json).

STB 패널·컷 인덱스; 실제 이미지가 있으면 SHT 명세. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

프롬프트나 패널 이미지는 전용 부서가 담당한다. 조립 도구가 준비되지 않으면 완성 시트로 주장하지 않는다.

## 자체 점검

헤더·패널 ID·문서 핀·파일 해시 및 이미지 가독성을 확인한다.

### 실행 안전

콘티에서 관객이 읽어야 할 정보와 직전 상태에서 가능한 동작을 확인한다. 원본 충실도가 요구되고 판단이 안 되는 컷에만 프레임 비교나 구간 임시 편집을 붙인다. [실행 안전 계약](../docs/design/13-execution-safety-contract.md)의 해당 게이트를 적용한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
