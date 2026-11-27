---
name: production-qa
description: "Crew skill; production-director assigns at QA2 to QA-F gates, or user asks to review storyboard, sheet, prompts, takes or final cut against checklists."
disable-model-invocation: true
---
# production-qa

## 역할

단계별 제작 검수.

## 입력

게이트, 검수 대상 핀, 기계 검사 결과 및 실제 미디어.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)를 기준으로 QA2에서 선행 컷/상태 기준·진입/이탈·변화 근거를 대조한다. QA3에서는 관련 연결 패널을 함께 열어 확인하고 파일·해시와 관찰된 상태를 기록한다. 계약 누락은 영향 컷 수정 대상으로, 이미지 미생성은 시각 QA 미검증으로 구분한다.

[아티팩트 계약](../docs/design/03-artifact-index.md)의 해당 QA 체크리스트를 읽는다. QA2는 인덱스·타임라인, QA3은 [시트 파일과 검수 기록](references/qa3-sheet.md)을 대조한 후 실제 패널 가독성·연속성, QA4는 프롬프트·배치·모델과 의도, QA5는 테이크를 본다. 파일이 없거나 재생하지 않으면 시각 확인을 미검증으로 표시한다. 수정 대상과 영향 범위만 다시 검사한다.

[사운드 통합 계약](../docs/design/11-sound-sourcing-integration.md)에 따라 QA2에서는 큐 설계/용도/필수성/탐색·확보 상태를, QA4에서는 실제 generation_input의 현재 파일·권리·청취·모델 입력/승인 근거를 대조한다. 소스 확보 포함 납품은 모든 required 큐의 실제 파일/해시·기술 검사·최종 청취·개별 권리/크레딧·Content ID 대응·원본 전달 조건을 별도 확인한다. 미확인 소스는 2회 상한 뒤에도 ready로 승격하지 않는다. post_only의 미확보는 관련 소스 납품을 막을 뿐 독립 시각 QA를 막지 않는다. index_lint는 직접 참조 파일만 검사하므로 소스 원장의 증빙/리뷰 핀과 현재 바이트도 대조하고, 법적 판정/청취 관측을 기계 검사라고 부르지 않는다.

액션 구간이 있으면 QA2에서 `action_lint.py` 결과를 확인하고, QA3에서 실제 패널을 열어 위협 노출·일렬 타블로·인서트·공간 존 일치를 판정한다. lint 종료 0을 박진감 합격으로 기록하지 않는다([액션 연출 계약](../docs/design/12-action-direction-contract.md)).

## 산출물

양식: [QAR](assets/QAR-template.md).

QAR: 증거, PASS/REVISE/RETHINK, 수정 지시, reviewer_mode. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

직접 수정하거나 승인·제출하지 않는다. 인라인은 독립 검수가 아니다.

## 자체 점검

기계 검사 통과와 제작 판정, 실행 승인, 실제 검수 증거를 분리한다.

### 실행 안전

계획 대응과 실제 재현을 분리한다. 시험이 필요한 구간은 검수 전 확장을, 최종 파일은 필요한 시청·청취 증거 없이 승격을 차단한다. [실행 안전 계약](../docs/design/13-execution-safety-contract.md)의 해당 게이트를 적용한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
