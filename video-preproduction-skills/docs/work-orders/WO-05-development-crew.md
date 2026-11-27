# WO-05 — concept-benchmark · story-writer

**Goal:** P0(브리프·벤치마크·차용 원장)과 P1(시놉시스·플롯·각본 초안) 크루.
**Spec:** DES-02 Phase A, DES-04 §2, DES-03 §1 · **의존:** WO-04

## Files
- Create: `concept-benchmark/SKILL.md`, `references/benchmark-anatomy.md`(DES-04 §2.1 필드·라벨), `references/borrow-ledger.md`(§2.2 규칙), `references/intake-factors.md`(v1 concept-intake-design 9요소 이관), `references/demand-evidence.md`(v1 topic-demand-selection 정규화·라벨 이관)
- Create: `concept-benchmark/assets/BRF-template.md`, `BMK-template.md`, `BOR-template.md`
- Create: `story-writer/SKILL.md`, `references/synopsis-plot.md`(v1 synopsis-craft·02-story), `references/screenplay-format.md`(씬헤딩·지문·대사 ID·전달 지시), `references/runtime-estimate.md`(대사 단위 수 → 초, `speech_rates.json` 사용), `references/silent-mode.md`(v1 silent-visual-storytelling 핵심)
- Create: `story-writer/assets/SYN-template.md`, `PLT-template.md`, `SCR-template.md`
- Create: `evals/development/E-11..E-15.md`

## 핵심 계약
- `concept-benchmark`: 지표는 관측만. 수집 도구가 없으면 사용자 제공 자료만으로 진행하고 `unknown` 표기. BOR의 모든 행에 처리(차용/변주/고유)와 "내 것으로 만드는 방법".
- `story-writer`: SCR의 모든 대사에 `Dnnn`, 화자, 전달(속도·강세·쉼). 씬별 추정 길이 합이 BRF 길이 ±10%를 벗어나면 납품 패킷 `assumptions`에 명시. 표정 AU·카메라 지시는 쓰지 않는다(부서 소유).

## Steps
- [ ] **1. 평가 케이스**
  - E-11 "60초 쇼츠, 직장 상사 참교육" + 벤치마크 자료 3건 텍스트 제공 → BMK 3건, BOR 행마다 처리 열, 지표는 제공값만
  - E-12 자료 없이 같은 요청 → BMK 지표 `unknown`, 조사 최소 행동 1줄, 진행 계속
  - E-13 BOR 기반 각본 → 모든 대사 ID·화자·전달, 추정 길이 표
  - E-14 각본 길이 과다(대사 180단어/30초) → `assumptions`에 초과 명시
  - E-15 QA1 수정 지시 2건 수신 → 지시된 ID만 수정, 버전 v2, 변경 목록
- [ ] **2. 작성** — SKILL.md 각 ≤120줄, 이관 references 머리에 `source:`
- [ ] **3. 평가 실행·기록** — `qa/wo-05/run-1/`
- [ ] **4. 수정·재실행 (최대 2회), 커밋** — `feat(v2): development crew`

## Acceptance
- E-11–E-15 PASS. E-12에서 숫자 지표를 지어내지 않음.
