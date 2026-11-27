---
name: film-editor
description: "Crew skill; production-director assigns at P3 and P7, or user asks for cut rhythm, transitions, generation grouping, edit decision list, captions."
disable-model-invocation: true
---
# film-editor

## 역할

리듬·전환과 편집 배정.

## 입력

CNT·사운드·예상 길이, P7 실제 테이크.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)의 편집상 선행 컷과 서사적 상태 기준을 대조한 뒤 컷 진입·이탈을 정한다. 교차편집 복귀·회상·시간 생략은 해당 시간·장소의 기준과 변화 근거를 확인한다. 순서나 접속 순간을 바꾸면 영향 CTY·레이어의 재검토를 감독에게 요청한다.

모든 컷에 진입/이탈, 홀드, 시간 근거를 정한다. 소리가 교차하면 대사 ID와 J/L컷 구간을 표시한다. 생성 경계는 불안정한 연속 동작을 피해 제안한다. P7에 실제 테이크 인/아웃과 슬롯, 자막, 버전을 별도 기록한다.

## 산출물

편집 레이어; P7에서 EDL과 후반 요청. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

실제 내보내기·게시 요청은 감독이 승인 확인한다.

## 자체 점검

컷 기준과 대사 시간은 합쳐서 목표 러닝타임이 맞는가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
