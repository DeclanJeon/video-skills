# WO-10 — image-prompt-engineer

**Goal:** REF(기준 이미지)와 패널 이미지 프롬프트를 DES-06 블록 순서로 컴파일하고 사이드카를 만든다.
**Spec:** DES-06 전체, DES-09(이미지 레퍼런스가 들어오면 같은 학습 절차) · **의존:** WO-09, WO-03(`--kind image`)

## Files
- Create: `image-prompt-engineer/SKILL.md`, `references/block-order.md`(DES-06 §2), `references/reference-sheets.md`(캐릭터 7뷰·의상·장소 4뷰·소품·LOOK 프레임 프롬프트 형식, v1 32-still-asset-generation-jobs 의존 순서·병렬 상한 5·불확실 작업 자동 재시도 금지 이관), `references/model-dialects-image.md`(언어·비율·참조 입력 지원 확인 절차; 모델 사실은 실행 시점 확인)
- Create: `image-prompt-engineer/assets/IMG-template.md`, `IMG-map-template.json`

## 핵심 계약
- 인물 블록 = `CHR#anchor` + `WRD` 원문 그대로(I1).
- 프롬프트 본문에 내부 ID·한국어 메모·대사 따옴표 없음(I4).
- REF 먼저, 패널은 REF를 `reference_inputs`로 지정. 실행·모델 선택은 감독.

## Steps
- [ ] **1. 평가 케이스**
  - E-61 EX-02 바이블 → REF 프롬프트 목록이 의존 순서(CHR→WRD→LOC→PRP→LOOK)
  - E-62 패널 S01-C02-P2 → 9블록, 사이드카 블록별 출처, `prompt_lint --kind image` 0 error
  - E-63 함정: 앵커를 의역하도록 유도("더 자연스럽게 써줘") → 앵커 원문 유지 + 의역은 거절 사유 1줄
  - E-64 9:16 미지원(16:9 전용) 모델 → 근사 비율과 그 사실을 사이드카에 기록
- [ ] **2. SKILL.md 작성 (≤120줄)**
- [ ] **3. 평가 실행** — `qa/wo-10/run-1/`
- [ ] **4. 실제 이미지 1회 검증 (AP-IMG 범위 안에서만)** — 무료 경로가 있으면 REF 2장 + 패널 2장 생성, QA3 3.2·3.6 수동 확인 기록. 경로가 없으면 `UNVERIFIED`
- [ ] **5. 커밋** — `feat(v2): image-prompt-engineer`
