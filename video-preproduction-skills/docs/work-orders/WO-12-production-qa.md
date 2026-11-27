# WO-12 — production-qa (QA2–QA5, QA-F)

**Goal:** 게이트별 체크리스트를 기계 검사 + 판단 검사로 실행하고 ID 색인 수정 지시와 판정을 낸다.
**Spec:** DES-03 §6, DES-01 §3 · **의존:** WO-02, WO-03

## Files
- Create: `production-qa/SKILL.md`, `references/qa2-preproduction.md`, `qa3-sheet.md`, `qa4-presubmit.md`(모의 낭독 절차 포함, v1 phase-review "실제 요청만 보고 예상 결과 기술" 이관), `qa5-takes.md`(v1 21-generated-video-qa-retry, 27-camera-motion-qa), `qaf-final.md`(v1 creative-qa), `impact-scope.md`(2회차 영향 범위 산정: ledger `mark_stale` 결과 사용)
- Create: `production-qa/assets/QAR-template.md`

## 핵심 계약
- 🅼 항목은 스크립트 결과만 인용(재판단 금지). 🅹 항목은 근거 ID 필수.
- 이미지·영상 검사(QA3·QA5·QA-F)는 실제 파일을 열어 본 경우만 판정, 아니면 `UNVERIFIED` — 시뮬레이션 금지.
- 직접 고치지 않음. 2회 상한, 잔여 위험 기록.
- QAR 머리에 `reviewer_mode: inline | subagent`. 인라인이면 산출물 파일을 새로 열어 그 내용만으로 판정(DES-01 §9)하고 "독립 검수 아님"을 잔여 위험에 기록.

## Steps
- [ ] **1. 평가 케이스**
  - E-81 QA2: EX-02 결함판 30s 시간표 STB → 2.5 차단(SUP-01), 수정 지시 owner `assistant-director`
  - E-82 QA2: 축 넘는 컷 사유 없음 → 2.6 REVISE, owner `cinematographer`
  - E-83 QA4: EX-02 결함판 VPR → L3·L9 차단, L13·L14 경고, 모의 낭독에서 SUP-03(18.5–24.5초 화면 밖 대사 공백) 발견
  - E-84 QA4 2회차: 수정된 블록만 재검, 고정 블록 재검 생략 근거 = 해시 동일
  - E-85 QA3/QA5: 이미지·영상 파일 없이 요청 → `UNVERIFIED`, PASS 아님
- [ ] **2. SKILL.md 작성 (≤150줄)**
- [ ] **3. 평가 실행·수정 (최대 2회), 커밋** — `feat(v2): production-qa`
