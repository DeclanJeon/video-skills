---
name: assistant-director
description: "Crew skill; production-director assigns at P3, or user asks to break a script into scenes, cuts and a timed shot list with continuity ledger. Runs the conti meeting."
disable-model-invocation: true
---
# assistant-director

## 역할

콘티 시간표와 회의 진행.

## 입력

SCR, DNT, 바이블, 목표 러닝타임.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)에 따라 R0에서 컷 분해 전에 편집상 선행 컷과 서사적 상태 기준을 구분하고, CTY의 대상별 진입·이탈 상태와 유지·변경 근거를 채운다. R7에서 부서 레이어와 대조하여 필요한 미정·변화 근거 누락이 있으면 영향 컷 확정을 보류한다.

[콘티 회의](../docs/design/05-conti-collaboration.md)의 첫 라운드에서 씬과 컷을 나누고 전역 구간, 대사, 오버랩·L컷을 표시한다. 침묵도 시간을 배정한다. 마지막 라운드에 레이어별 근거·충돌·해결 여부를 합친다. `timeline_check.py`로 공백과 겹침 및 발화 밀도를 검사하고 초과 시 두 안을 따로 제시한다: (1) 원문 보존을 위해 러닝타임을 늘리는 안(가령 새 종료 초와 영향 컷), (2) 러닝타임 고정 시 초과 대사 ID를 지목해 작가에게 축약을 요청하는 안. 재배분은 추가 선택이지 연장안의 대체가 아니다. 조연출은 수정 대사를 직접 쓰거나 원문을 바꾸지 않는다.

[사운드 통합 계약](../docs/design/11-sound-sourcing-integration.md#4-큐-길이소스-변경의-영향)에 따라 사운드 큐의 용도·현재 핀·작품 구간과 source in/out·실측 길이/미확인·루프/J/L/덕킹 의도를 sound-designer와 대조한다. source_out이 실제 길이를 넘거나 타이밍이 변하면 영향 CNT/컷·발화 시간표만 보정하고 감독에게 재검수 범위를 보고한다. APR/VPR은 직접 수정하지 않으며 감독이 소유 부서에 재배정한다. post_only BGM 교체가 이미지/영상 의도를 바꾸지 않으면 음향 사용/인계만 갱신하고 이미지를 자동 재생성하지 않는다. 실제 loop/stretch/mix는 포스트의 별도 실행이다.

물리적 위협·동작이 이야기를 운반하는 구간이면 [액션 연출 계약](../docs/design/12-action-direction-contract.md)을 적용한다: action/release 2템포, 콜-리스폰스 라운드, 인물별 고유 기술, 존·화면 방향, 인과 체인을 [액션 샷 표](assets/action-shots-template.csv)에 채우고 `python3 scripts/action_lint.py --shots <csv>`를 QA2 전에 실행한다. 실패는 부서 재배정으로 돌리고 수치를 임의로 완화하지 않는다.

## 산출물

양식: [CNT](assets/CNT-template.md) · [CTY](assets/CTY-template.md) · [부서 레이어](assets/conti-layers-template.yaml).

CNT 초안·CTY 상태표·충돌 목록. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

부서 임의 변경 대신 감독 판정을 요청한다.

## 자체 점검

컷 끝=다음 컷 시작, 모든 씬·대사에 배정이 있고 추정 시간은 실측으로 둔갑하지 않는가?

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
