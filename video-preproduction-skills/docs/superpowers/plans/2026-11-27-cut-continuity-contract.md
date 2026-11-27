# Cut Continuity Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 CTY에서 컷 간 연결 근거를 작성하고 부서별 설계와 QA까지 소비한다.

**Architecture:** DES-05 §4가 연결 계약의 단일 정본이다. CTY 양식에 컷별 관계와 상태를 작성하며 기존 CNT/인덱스의 continuity 핀으로 소비한다. 기계적 구조 검사와 에이전트의 사례별 판단 증거를 분리한다.

**Tech Stack:** Markdown, YAML 양식, Python pytest (기존 의존성만).

**Spec:** `docs/design/10-cut-continuity-contract.md`

## Global Constraints

- 새로운 원장이나 필수 CSV 열을 만들지 않고 기존 `continuity` 참조를 통해 계약을 찾는다.
- 이미지가 아직 없어도 텍스트 설계는 진행한다.
- 공급자 호출, 이미지 생성·과금, 설치본 동기화, 커밋·푸시는 이 변경의 실행 범위가 아니다.
- 기존 미커밋 수정은 보존한다. 사용자 승인된 현재 프로젝트에서 직접 작업한다.
- 실행 기록은 `.ultragoal/goals/active/cut-continuity-contract/goal.md`를 사용한다.

## Review Focus

- 교차편집 복귀는 직전 다른 장소가 아닌 동일 서사의 상태를 계승한다.
- 회상·첫 컷은 상태 기준이 없을 때 SCR/DNT/바이블 초기 근거를 사용한다.
- 무근거 소품 손 변경은 설명 없이는 확정하지 않는다.
- 리버스숏은 공간 상태를 계승하되 구도·화면 좌우의 단순 복사를 요구하지 않는다.
- 이미지 미생성은 텍스트 작업을 막지 않고 시각 QA만 미검증이다.

---

### Task 1: 기준선과 실패 검사

**Files:** Create `tests/test_continuity_contracts.py`; baseline evidence in goal evidence directory.

**Interfaces:** Consumes existing templates/manual. Produces structural regression tests and a read-only agent baseline report.

- [x] 기존 219개 테스트의 기준선 결과를 보관한다.
- [x] 기존 지침으로 교차편집·손 변경·회상·이미지 미생성 과제를 fresh-context 에이전트에 적용한다. 정본 수정 전에 실제 출력과 누락을 확인한다.
- [x] 실제 CTY 양식의 컷 앵커를 index_lint가 해결하고 잘못된·초안·무버전·superseded 핀을 차단하는 테스트 5개를 작성한다. 6개 슬롯·부서 포인터·QA 문장은 행동 QA와 독립 검토로 검사한다(실행 중 Ruling 기록).
- [x] CTY 컷 앵커 누락 결함 주입 → `python3 -m pytest -q tests/test_continuity_contracts.py`에서 1 failed/4 passed(IX02), 복원 후 PASS를 확인한다.

### Task 2: 정본·양식·소비 부서 보완

**Files:** Modify `docs/design/05-conti-collaboration.md`, `assistant-director/assets/{CTY-template.md,CNT-template.md,conti-layers-template.yaml}`, `{assistant-director,performance-director,cinematographer,film-editor,storyboard-artist,image-prompt-engineer,production-qa}/SKILL.md`, `docs/design/{03-artifact-index.md,06-image-prompt-spec.md}`.

**Interfaces:** Consumes Task 1 tests. Produces DES-05 §4 계약, CTY cut anchor, 기존 continuity 핀 소비.

- [x] DES-05 §4에 필드 의미·조건·단계별 적용·확정 조건을 정의한다. R0/R7과 완료 기준에 포인터를 연결한다.
- [x] CTY에 컷별 anchor 및 선행/유형/기준/상태/변경/의도 슬롯을 둔다. CNT와 레이어 양식은 CTY 연결 계약 핀을 소비한다.
- [x] 각 부서는 계약을 읽고 자기 레이어를 채우며 충돌은 감독에게 반환한다.
- [x] QA2는 관계·상태 변화, QA3는 실제 연결 패널 비교를 판단한다. 이미지 명세는 선택적 시각 참조 및 텍스트 진행 경계를 명시한다.
- [x] `python3 -m pytest -q tests/test_artifact_templates.py tests/test_continuity_contracts.py` → PASS.

### Task 3: 사례 QA·회귀·독립 검증

**Files:** Create `docs/qa/cut-continuity-contract-qa.md`; Modify `CHANGELOG.md`, 설계 상태와 목표 기록.

**Interfaces:** Consumes final manuals/templates; produces actual task outputs, verification logs and read-only independent review.

- [x] 동일 과제를 보완된 지침으로 재실행하고 손 변경·연속 동작·리버스숏·교차편집·회상·시간 생략·첫 컷·이미지 미생성을 표로 판정한다. 단어 검사만을 행동 검증으로 주장하지 않는다.
- [x] 전체 `python3 -m pytest -q`, `python3 scripts/check_skills.py --json`, `python3 docs/qa/tools/consistency_check.py`, `git diff --check` → 종료 0.
- [x] 기준선 diff가 최종 변경에도 보존됐는지 검사하고 변경 이력·설계 상태를 갱신한다.
- [x] 최종 파일 해시 목록을 고정하고 fresh-context 검토자에게 목표/설계/실제 증거를 읽기 전용 검증시킨다. 차단 결함이 있으면 실패 재현 후 최소 수정하고 영향 검사를 재실행한다. 변경된 최종 revision에 대한 독립 검증이 필요하다.
- [x] 모든 기준과 제약의 실제 증거를 목표에 기록하고 7/7 및 status=done일 때만 100%를 보고한다.

## 실행 결정

사용자는 목표를 활성화하고 직접 구현 및 검증용 하위 에이전트를 승인했다. 추가 계획 승인 대기는 생략하며 별도 구현 위임·worktree 생성·커밋은 하지 않는다. 구현 순서는 Task 1 → Task 2 → Task 3이다.
