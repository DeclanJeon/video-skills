# WO-02 — production-ledger · ID 파서 · index_lint · timeline_check

**Goal:** 원장 스킬과 인덱스·타임라인 기계 검사를 구현한다. 이후 모든 게이트의 🅼 검사가 여기에 의존한다.
**Spec:** DES-03 전체, DES-07 §3(말속도 표), DES-09 §5, [EX-02](../examples/synthetic-laundromat-34s/fixture.md) §3·§4 · **의존:** WO-01

## Files
- Create: `scripts/cp2/__init__.py`, `scripts/cp2/ids.py`, `scripts/cp2/speech.py`, `scripts/cp2/ledger.py`
- Create: `scripts/index_lint.py`, `scripts/timeline_check.py`, `scripts/ledger.py`(CLI)
- Create: `production-ledger/SKILL.md`, `production-ledger/references/ledger-schema.md`, `scripts/cp2/speech_rates.json`은 기존 정본 재사용(복제하지 않음)
- Create: `tests/test_ids.py`, `tests/test_speech.py`, `tests/test_index_lint.py`, `tests/test_timeline_check.py`, `tests/test_ledger.py`
- Create: `tests/fixtures/ex02-defect-30s/` (EX-02 §3 결함판 index.csv, SCR.md), `tests/fixtures/ex02-fixed-34s/` (EX-02 §4 보정판), `tests/fixtures/lcut-synthetic/` (컷을 넘는 대사 1개를 가진 최소 합성 인덱스). 레퍼런스 원문 내용은 픽스처에 쓰지 않는다

## Interfaces
- `cp2.ids.parse_ref(ref: str) -> Ref` — `Ref(prefix: str, number: str|None, suffix: str|None, version: int|None, anchor: str|None, item: str|None)`; 잘못된 문법은 `RefError`
- `cp2.ids.parse_cut(s: str) -> tuple[int, int, int|None]` — `S01-C02.b3` → `(1, 2, 3)`
- `cp2.speech.count_units(text: str, lang: str) -> tuple[int, bool]` — (단위 수, 신뢰 여부). en=단어, ko=한글 음절, zh=CJK 글자, ja=가나 수(한자 포함 시 신뢰 False)
- `cp2.speech.rate_verdict(units: int, seconds: float, lang: str, mode: Literal["normal","heated"], pauses: int = 0) -> Literal["ok","warn","block","unverified"]` — `seconds - 0.3*pauses`로 나눈다. 값은 `speech_rates.json`
- `cp2.ledger.Ledger.load(root) / register(artifact_id, path, version, consumes: list[str]) / mark_stale(changed_ref) -> list[str] / status(artifact_id)`
- CLI: `index_lint.py --project ROOT --stage {bible,board,sheet,prompt} [--json]`, 코드 `IX01` 빈 필수 열, `IX02` 미해결 참조, `IX03` stale 참조, `IX04` 고아 바이블 항목, `IX05` 대사 미배정/중복, `IX06` 대사 원문 불일치, `IX07` 인덱스 머리말(`index-header.json`) 누락·버전 핀 없음. `@draft` 참조는 `--stage` 밖에서 IX03
- CLI: `timeline_check.py --index index.csv --runtime SEC [--script SCR.md] [--json]`, 코드 `TL01` 빈틈, `TL02` 겹침, `TL03` 하위 구간이 컷을 덮지 않음, `TL04` 말속도 차단, `TL05` 말속도 경고/미확인

## Steps
- [ ] **1. ID 테스트** — `test_parse_full_ref`: `"CHR-01@v2#anchor"` → prefix `CHR`, number `01`, version 2, anchor `anchor`; `test_parse_wardrobe_suffix`: `"WRD-02a"` → suffix `a`; `test_parse_cut_segment`; `test_bad_ref_raises`
- [ ] **2. 말속도 테스트** — `test_en_fast_blocks`: 18단어/3.7s/heated → `block`; `test_en_normal_ok`: 15/5.0 → `ok`; `test_ko_ex02_D001_blocks`: 19음절/2.0s → `block`; `test_pause_subtracted`: 5단어/1.0s/pauses=1 → `block`; `test_ko_syllables`: "괜찮아, 난 괜찮다고" → 8; `test_mixed_language_rate_unverified`: ja 한자 포함 → `unverified`
- [ ] **3. 실패 확인 → `ids.py`, `speech.py` 구현 → 통과**
- [ ] **4. timeline 테스트** — `test_ex02_defect_flags_rate`: fixture ex02-defect-30s → TL04가 D001, D002, D009–D010 (3건), TL05 경고가 S01-C02.b3 (7.03 음절/초, 격앙 표시 없음); `test_ex02_fixed_passes`: ex02-fixed-34s → 0 error; `test_gap_TL01`; `test_overlap_TL02`; `test_overlap_notation_allows_TL02`: EX-03 `overlap:D004+D005@12.4-13.6` 허용, 표기 없으면 `TL02`; `test_silent_none_dialogue_ok`: EX-04 `none(무대사 작품)` 허용·말속도 검사 0건; `test_lcut_dialogue_not_duplicate`: lcut-synthetic의 대사가 두 컷에 걸쳐도 TL02·IX05 아님(인덱스에 `lcut:` 표기)
- [ ] **5. 실패 확인 → `timeline_check.py` 구현 → 통과**
- [ ] **6. ledger 테스트** — `test_register_and_consume`; `test_stale_propagation`: SCR v2 등록 → CNT@v1(SCR@v1 소비) stale; `test_anchor_scoped_stale`: `CHR-01#anchor` 변경 → `CHR-01#anchor` 참조 행만 stale, `CHR-01#persona` 참조 행은 유지
- [ ] **7. index_lint 테스트** — fixture에 빈칸 `camera` → `IX01`; `LOC-09` 참조 → `IX02`; 고아 `PRP-03` → `IX04`; 대사 원문 한 글자 다름 → `IX06`; 머리말에서 `SYN` 삭제 → `IX07`; `test_draft_ref_no_stale`: `CNT@draft` 변경이 stale을 전파하지 않음; `adopted_take`·`audio_prompt` 열은 해당 단계 전 빈칸 허용
- [ ] **8. 실패 확인 → `ledger.py`, `index_lint.py` 구현 → 통과**
- [ ] **9. `production-ledger/SKILL.md` 작성** — 역할: 루트 초기화·등록·stale·이력; 쓰기는 감독 요청으로만; v1 `recording-production-history`의 `.history` 형식 승계(`source:` 표기)
- [ ] **10. 전체 테스트** — `pytest -q` 통과, 커밋 `feat(v2): ledger, index_lint, timeline_check`

## Acceptance
- ex02-defect-30s의 말속도 결함 3건과 경고 1건을 정확히 잡고, ex02-fixed-34s는 통과한다. 픽스처에서 `REF_LEAK` 0건.
