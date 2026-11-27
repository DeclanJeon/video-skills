# WO-06 — audience-reaction-qa (QA1)

**Goal:** 각본 초안의 수요·반응을 벤치마크 대조(관측)와 가상 시청자 패널(가설)로 검수하고 ID 색인 수정 지시를 낸다.
**Spec:** DES-04 전체 · **의존:** WO-05

## Files
- Create: `audience-reaction-qa/SKILL.md`, `references/lanes.md`(레인 A/B/C 절차), `references/rubric.md`(R1–R8 앵커), `references/verdict-rules.md`, `references/persona-panel.md`(BRF에서 3–5 페르소나 도출법, 플랫폼별 기본 페르소나 예), `references/calibration.md`(출시 후 보정 루프)
- Create: `audience-reaction-qa/assets/QAR-1-template.md`
- Create: `evals/qa1/E-21..E-26.md`, `evals/qa1/fixtures/`(좋은 각본 1, 훅 늦은 각본 1, 벤치마크 복제 각본 1, 수요 반대 각본 1)

## 핵심 계약
- 레인 A와 B는 별도 표, 합산 점수 없음. 레인 B 모든 행 `hypothesis`.
- 작가와 독립: 서브에이전트가 가능하면 서브에이전트, 아니면 인라인 새로 읽기 규칙과 `reviewer_mode` 기록(DES-01 §9).
- 숫자 성과 예측 금지(조회수·유지율 %·확률).
- 수정 지시는 DES-01 §3.3 형식, 대상은 SCR ID. 고쳐 쓴 대사를 제시하지 않는다(작가 소유) — 단, `instruction`에 수락 기준은 쓴다.
- 직행 호출(벤치마크 없음): 레인 A를 `unknown`으로 두고 B·C만 수행, 판정 문구에 한계 명시.

## Steps
- [ ] **1. 평가 케이스**
  - E-21 좋은 각본 → `PASS`, 2–3점 항목은 비차단 메모
  - E-22 훅 6초 각본(쇼츠) → `REVISE`, R1 ≤2, fix target이 첫 씬 대사 ID
  - E-23 벤치마크 비트 시간표 ±10% 복제 + 고유 요소 없음 → `copy_risk`, R4 ≤2, `REVISE`
  - E-24 BMK는 "공감·위로"인데 각본 약속이 "조롱" → `RETHINK`
  - E-25 직행, 벤치마크 없음 → 레인 A `unknown`, 판정 진행
  - E-26 출력에 "예상 조회수", "%" 성과 예측이 없음 (정규식 검사: `조회수\s*\d|\d+\s*%\s*(유지|이탈)`)
- [ ] **2. 작성** — SKILL.md ≤120줄
- [ ] **3. 평가 실행** — `qa/wo-06/run-1/`. 판정 안정성: E-22·E-24를 각 3회 반복해 판정 일치 여부 기록
- [ ] **4. 수정·재실행 (최대 2회), 커밋** — `feat(v2): audience-reaction-qa`

## Acceptance
- E-21–E-26 PASS, 반복 판정 3/3 일치(불일치 시 verdict-rules 모호성 수정).
