---
name: continuity-reviewer
description: "Use when checking multi-clip continuity, reappearing assets, reference drift, edit boundaries, or whole-sequence flow."
disable-model-invocation: true
---
# continuity-reviewer

## 입력
현재 원본 자산·장면 상태, 채택 테이크와 ranges/revisions, 편집 관계와 참조 DAG. [참조 계약](../docs/design/02-reference-continuity.md)과 [QA 계약](../docs/design/04-qa-handoff.md)을 읽는다.

## 절차
1. 캐릭터 원본/현재 에셋 핀과도 대조한다. 이전 결과만 기준으로 삼아 누적 drift를 용인하지 않는다.
2. 앞 마지막 포함 프레임과 뒤 첫 프레임을 실제 전후 구간과 함께 연속 재생한다. 방향·시선·축·동작 위상·손/소품·지리·빛·음향·공개를 검사한다.
3. 극중 인과와 관객 공개 순서를 구분한다. 승인된 reaction-first, 시간 점프, 새 앵글에 이전 끝 프레임을 강제하지 않는다.
4. join 보고서를 정확한 take/range/acceptance revision에 결속한다. 같은 clip 이름만 같다고 재사용하지 않는다.
5. 검수용 러프 연결본을 승인된 순서로 끝까지 보고 전체 속도·감정/위협·중복/누락·재등장 상태를 검사한다. 후보·누락을 완성본으로 표시하지 않는다.

## 납품·완료
JoinReview와 FlowReview, 수정 영향 목록을 총괄에게 반환한다. flow-hash는 검수할 선택 스냅샷이며 전체 재생 자체가 아니다. 파일 교체는 관련 경계·연결본을 다시 검수한다.
