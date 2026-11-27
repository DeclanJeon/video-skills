# WO-04 — production-director (감독)

**Goal:** 단계 판정 → 콜시트 → 납품 수령 → 게이트 소집 → 판정 → 승인 대기만 하는 오케스트레이터.
**Spec:** DES-01 전체, DES-02 §3 감독, DES-05 §2(충돌 판정) · **의존:** WO-01, WO-02

## Files
- Create: `production-director/SKILL.md`
- Create: `production-director/references/phase-table.md` (DES-01 §2 표의 실행본), `call-sheet.md` (콜시트·납품 패킷 스키마), `rulings.md` (충돌 우선순위·RUL 형식), `approvals.md` (v1 policy.md에서 승인 분리만 이관, `source:` 표기), `direct-routes.md` (DES-01 §6), `equipment.md` (공급자 어댑터 목록과 호출 조건 — v1 `explicit-video-execution.md`, `workspace-integration.md` 요약)
- Create: `production-director/references/execution-modes.md` (DES-01 §9 인라인/서브에이전트, 새로 읽기 규칙), `production-director/references/director-notes.md` (DNT 5항목 작성법)
- Create: `production-director/assets/CALL-template.yaml`, `DLV-template.yaml`, `RUL-template.yaml`, `DNT-template.md`
- Evaluation: [감독 사례 E-01–E-10](../../evals/director/cases.md) (정의됨, 실행 미검증)
- QA4 제출 경로: [배치·제출 규약](../../production-director/references/qa4-submit.md)

## SKILL.md 본문 요구 (≤150줄)
1. **역할**: "비전을 주고 시킨다" — 직접 쓰는 창작물은 `DNT` 하나. 인라인 실행 시 `acting_as:` 표기(DES-01 §9).
2. **단계표**: phase-table 링크 + 단계 판정 규칙 3줄(원장 우선, 파일 존재로 추론 금지, 직행 판정).
3. **콜시트**: 발행 전 `index_lint`로 입력 stale 여부 확인. inputs는 버전 핀.
4. **게이트**: 납품 수령 시 해당 단계의 🅼 검사 실행 → 게이트 단계면 QA 크루 배정 → 판정 처리(DES-01 §3).
5. **승인**: AP-IMG/AP-VID/권리/게시만 대기. 그 외 자동 진행.
6. **직행**: direct-routes 표.
7. **마감**: DES-01 §8 두 형식.

## Steps
- [ ] **1. 평가 케이스 작성 (먼저)** — 각 케이스 = 사용자 입력 + 관찰 가능한 합격 조건
  - E-01 "문 닫는 세탁소를 두고 다투는 남매, 35초 세로 드라마 만들어줘": P0 콜시트가 `concept-benchmark`에, 같은 턴에 P1·QA1까지 진행, 마지막 줄 `다음: … — 자동 진행`
  - E-02 "이 대본 반응 어떨지만 봐줘 (대본 첨부)": 직행 `audience-reaction-qa`, 원장·폴더 생성 없음, ID `tmp:`
  - E-03 재개: 원장에 P3 완료·P4 미완 → P4 콜시트부터, P0 재인터뷰 없음
  - E-04 cinematographer와 lighting-director 충돌 납품 → `RUL` 기록, 우선순위 문구 인용
  - E-05 QA4 PASS, 승인 없음 → `대기: AP-VID 영상 실행·비용 승인 — 필요: 모델·예산 승인`
  - E-06 사용자 "QA1 결과 보여주고 멈춰" → QA1 후 대기, 이유는 사용자 지정 정지
  - E-07 서브에이전트 도구 없음 → QA 게이트를 인라인으로 수행하되 QAR에 `reviewer_mode: inline`과 "독립 검수 아님" 잔여 위험 기록; 도구·위임 승인 있음 → QA를 서브에이전트로 보내고 콜시트에 파일 경로만 전달
  - E-08 P2 완료 → P3 콘티 콜시트보다 먼저 `DNT`가 작성되고, 모든 씬에 5항목
- [ ] **2. 기준선 실행** — v1 `creative-production`으로 E-01·E-04를 실행해 결과 저장 `qa/wo-04/baseline/` (비교용)
- [ ] **3. SKILL.md·references·assets 작성**
- [ ] **4. 평가 실행** — 깨끗한 세션에서 E-01–E-06, 결과 `qa/wo-04/run-1/`, 케이스별 PASS/FAIL 표
- [ ] **5. FAIL 수정 후 실패 케이스만 재실행** (최대 2회)
- [ ] **6. `check_skills.py` 통과, 커밋** — `feat(v2): production-director`

## Acceptance
- E-01–E-06 PASS. 특히 E-01에서 감독이 각본을 직접 쓰지 않고 `story-writer`를 배정했는지 출력에서 확인 가능.
