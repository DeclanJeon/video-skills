# WO-09 — storyboard-artist · 시트 조립

**Goal:** 콘티를 패널과 인덱스 행으로 만들고(P4), 생성 이미지로 시트를 조립(P5)한다.
**Spec:** DES-03 §4, DES-06 §3, DES-02 storyboard-artist · **의존:** WO-08, WO-02

## Files
- Create: `storyboard-artist/SKILL.md`, `references/panels.md` (컷당 1–3패널: 시작/정점/끝, v1 storyboard-contract 커버리지 규칙 이관), `references/index-row.md` (DES-03 §4 열 정의), `references/sheet-layout.md`
- Create: `storyboard-artist/assets/STB-template.md`, `index-template.csv`, `index-header-template.json`
- Create: `scripts/assemble_sheet.py`, `tests/test_assemble_sheet.py`
- 장비: v1 `split_storyboard.py`는 사용하지 않는다(v2는 패널 개별 생성 → 조립 방향)

## Interfaces
- `assemble_sheet.py --index index.csv --images DIR --out SHT-01.png [--cols 4 --rows 2] [--caption {id,time,dialogue,camera}]` → 셀 순서 = 인덱스 패널 순서, 캡션은 조립 단계 텍스트 레이어, `SHT-01.cells.json`(셀→패널 ID) 출력. Pillow가 없으면 HTML 시트(`SHT-01.html`)로 대체하고 그 사실을 출력에 표기

## Steps
- [ ] **1. 실패 테스트** — `test_cell_order_matches_index`, `test_max_8_cells_paginates`(9패널 → SHT-01, SHT-02), `test_missing_image_marked_blocked`(셀에 `blocked` 표시, exit 0 + 경고), `test_html_fallback_without_pillow`
- [ ] **2. 실패 확인 → 구현 → 통과**
- [ ] **3. SKILL.md 작성 (≤120줄)** — P4: 패널 서술 + 인덱스 행 + `index_lint --stage board` 통과까지; P5: 시트 조립 + `SHT` 셀 ID를 인덱스 `sheet` 열에 기록
- [ ] **4. 평가** — E-51 EX-02 CNT → STB 패널 4컷×(1–3), 인덱스 머리말(BRF·SYN·PLT·SCR·DNT·WLD·SND·LOOK 버전 핀) 완비, 필수 열 빈칸 0; E-52 바이블에 있는데 어느 컷에도 없는 PRP → `unused(이유)` 또는 `IX04` 보고
- [ ] **5. 커밋** — `feat(v2): storyboard-artist and sheet assembly`

## Acceptance
- EX-02 STB가 `index_lint --stage board` 0 error. 시트 캡션이 이미지 모델이 아니라 스크립트로 들어간다.
