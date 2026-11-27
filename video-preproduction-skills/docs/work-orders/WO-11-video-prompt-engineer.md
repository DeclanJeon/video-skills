# WO-11 — video-prompt-engineer

**Goal:** 스토리보드 시트·인덱스·바이블을 8블록 영상 프롬프트와 사이드카로 컴파일하고, 모델 한계에 맞춰 GEN을 묶는다.
**Spec:** DES-07 전체, DES-09 전체, EX-01b(골격), [EX-02](../examples/synthetic-laundromat-34s/fixture.md) · **의존:** WO-03, WO-10

## Files
- Create: `video-prompt-engineer/SKILL.md`
- Create: `references/template-8-blocks.md`(DES-07 §2 + 블록별 작성 규칙), `references/timeline-rules.md`(DES-07 §3), `references/gen-grouping.md`(§4), `references/dialects.md`(§5, v1 `video-prompt-dialects.json` 복사본을 `assets/`에 두고 사용법), `references/facs-cheatsheet.md`(performance-director 사전 링크, 중복 금지 — 링크만), `references/retake.md`(§8), `references/worked-example-ex02.md`(EX-02 보정판을 8블록으로 쓴 완성 예, 문단마다 PP-ID 주석), `references/pattern-ledger.md`(**PPL**: DES-09 §2의 PP-01–25를 원장 형식으로 옮기고 상태 `observed-in-reference`), `references/reference-learning.md`(DES-09 §4 6단계 절차와 바꿔 넣기 시험, §5 격리 규칙)
- Create: `assets/VPR-template.md`(언어별 블록 마커 ko/zh/en), `VPR-map-template.json`, `video-prompt-dialects.json`

## 핵심 계약
- 새 창작 금지: 모든 문장이 인덱스 행·머리말의 정본에서 온다(B2는 `DNT`). 부족하면 `missing_inputs`.
- `audio_path: separate`이면 `APR` 생성·실측 후 시간표 보정이 끝난 인덱스로만 작성(DES-07 §9).
- 대사는 발화 언어 원문 그대로. 프롬프트 언어는 모델 방언.
- 고정 블록 해시 동일(L5). 본문 ID 금지(L8).
- 컷·대사·표정 비트를 바꿔야 하면 직접 바꾸지 않고 감독에 `RETHINK` 요청.

## Steps
- [ ] **1. 평가 케이스**
  - E-71 EX-02 보정판(34s) + "최대 30초 모델" → GEN 2개(C01–C02 22.0s / C03–C04 12.0s), 고정 블록 동일, `prompt_lint` 0 error
  - E-72 같은 입력 + "최대 10초 모델" → 컷 경계/하위 구간 경계에서만 분할, `C02a/C02b` 표기, 경계 인계 문장 존재
  - E-73 EX-02 결함판 30s 시간표 입력 → 프롬프트를 쓰기 전에 L3 결함을 보고하고 `RETHINK`(시간표 보정 요청) 반환
  - E-74 영어 프롬프트 모델 / 중국어 프롬프트 모델 각각 → 대사는 둘 다 한국어 원문 그대로
  - E-75 QA5 지시 "C02 .b4 손을 드는 동작 과장" → B5의 해당 하위 구간만 변경, VPR 버전 +1, 다른 블록 해시 동일
  - E-77 `audio_path: separate` → B6에 대사 음성 생성 요구 없음(L15), 시간은 실측 오디오 길이 기준
  - E-76 패턴 커버리지: E-71 결과를 PP-01–25 × 문단 표로 대조 — 모든 PP가 적용되었거나 `N/A(이유)`; SUP-08–19 장치가 사이드카·본문에 존재
  - E-78 학습 절차: 새 레퍼런스 프롬프트(평가용으로 별도 제공) → 원문 보관, 내용 제거 골격(누출 단어 0), PP 매핑·신규 판정, SUP 일반화, 원장 행 추가. 템플릿·예시에 그 레퍼런스의 내용 0
- [ ] **2. SKILL.md 작성 (≤150줄)**
- [ ] **3. 평가 실행** — `qa/wo-11/run-1/`
- [ ] **4. 수정·재실행 (최대 2회)**
- [ ] **5. 실제 생성 1회 (AP-VID 승인 있을 때만)** — 짧은 GEN 1개로 QA5 체크리스트 기록. 승인 없으면 `UNVERIFIED`
- [ ] **6. 커밋** — `feat(v2): video-prompt-engineer`

## Acceptance
- E-71–E-78 PASS. E-76에서 PP-01–25 전부가 적용 또는 사유 있는 N/A, 산출물 전체에서 `REF_LEAK` 0.
