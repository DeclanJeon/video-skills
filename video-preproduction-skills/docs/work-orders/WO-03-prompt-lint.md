# WO-03 — prompt_lint (영상 L1–L20, 이미지 I1–I7)

**Goal:** 영상·이미지 프롬프트와 사이드카를 정본에 대조하는 차단 검사기 (영상 L1–L20).
**Spec:** DES-07 §3·§6–7, DES-06 §5, DES-09 §3, [EX-02](../examples/synthetic-laundromat-34s/fixture.md) · **의존:** WO-02

## Files
- Create: `scripts/prompt_lint.py`, `scripts/cp2/prompt_parse.py`
- Create: `tests/test_prompt_lint.py`, `tests/fixtures/ex02-defect-30s/VPR-01.md`(EX-02 결함판을 8블록으로, 결함 SUP-01–05를 그대로 포함), `VPR-01.map.json`; `tests/fixtures/ex02-fixed-34s/VPR-01.md`, `VPR-02.md`(GEN 2개 분할본) + map

## Interfaces
- `cp2.prompt_parse.split_blocks(text: str, markers: dict[str, str]) -> dict[str, str]` — 블록 마커는 사이드카 `block_markers`(예: `{"B3": "【人物一致性】"}`)에서 받는다. 언어 무관
- `cp2.prompt_parse.extract_quotes(text: str) -> list[str]` — `"…"`, `“…”`, `「…」` 모두
- `cp2.prompt_parse.normalized_hash(block: str) -> str` — 공백·줄바꿈 정규화 후 sha256
- CLI: `prompt_lint.py --kind {video,image} --prompt FILE --map FILE --project ROOT [--json]` → L1–L20 / I1–I7 코드

## 로컬 CLI 연결 상태

- 영상: L1–L5, L7–L8, L10, L12, L15, L18의 전부 또는 구조적 부분을 검사한다. L5는 `fixed_block_baseline: GEN-01@vN`을 원장에서 해결하고, 등록 해시가 일치하는 JSON의 `fixed_block_hash`를 공통 기준으로 사용한다. 기준 핀이 없으면 미검증이며 로컬 해시만으로 합격하지 않는다. L9는 `reaction_to` 또는 `stimulus`의 `dialogue`·`word`를 확인한다. 자극 큐 시작 전 반응은 차단하고, 같은 큐 내부는 `stimulus_source: CNT@vN`의 등록 JSON이 같은 `screenplay`·`gen`을 가리키고, `word_events`에 `dialogue`, `word`, 전역 `start_s`·`end_s`가 유일하게 있어야 판정한다. GEN 오프셋을 빼고 해당 큐 안에 드는 단어 끝보다 먼저 반응하면 차단한다. 근거 누락·중복·범위 이탈은 미검증이며 추정 단어 위치로 대신하지 않는다. L18은 sidecar의 화자 키를 비교하며 자유문 속 화자 표기는 아직 대조하지 않는다.
- 이미지: I1, I4의 내부 ID·인용부, I5의 기본 금지, I6의 영어 시간 연결 단서를 검사한다. I1은 `identity` 블록을 `identity_sources`의 순서대로 이어붙인 등록 원문(`CHR-01@vN#anchor`의 `## anchor`, `WRD-01a@vN#prompt`의 `## prompt`)과 대조한다. 누락된 정본 핀과 나머지 규칙은 미검증이다.
- sidecar 필수: `block_markers`; 영상은 `duration_s`, `shots[].t`, `shots[].segments[].t`, 발화가 있으면 원장으로 해결되는 `screenplay: SCR@vN`. B5의 인용문을 배정된 대사와 순서대로 비교한다. 시간은 GEN 로컬 기준이며 무언 구간도 시간창에 포함한다.
- 방향 대조(L6·L17): B5 내부에 컷 순서대로 `Shot 1`, `Shot 2` 등 독립 헤더를 둔다. `axis_source`와 각 샷의 `lighting`은 원장에 등록된 JSON 핀이다. 각각 `axis_by_cut`, `light_by_cut` 맵에서 컷 ID로 한 줄짜리 `Axis:`, `Light:` 문장을 찾아 해당 샷과 대조한다. 원장 근거가 없으면 미검증, 조명 문장 불일치는 경고다.
- 이미지 시트 대조(I2·I3·I7): `sheet_baseline`은 등록된 시트 JSON 핀이다. `visible_by_panel`의 인물 목록 길이를 `composition` 블록의 `Visible people: N`과 맞춘다. 공통 `style_hash`와 각 패널의 `style` 블록을 공백 정규화 후 대조한다. `axis_by_panel`이 있으면 `composition`의 `Axis:`도 비교한다. 이는 텍스트 계약 검사이며 실제 이미지나 임의 문장의 방향까지 판정하지 않는다.
- 자유 서술 검수: 샷 안에서 하위 구간마다 `Beat N` 헤더를 둔다. `Emotion:`만 있고 `Action:`이 없거나 `Props:`/`Hands:`가 빠지면 경고; 비트 대응 누락은 미검증이다. 일부 좌우·전역 상대시간 표현 및 동일 강도 반복도 경고한다. 보이는 표지판·봉투·라벨에 글자가 있다고 명시한 독립 영문 문장과 B7의 글자 금지는 차단한다. 각본과 일치한 인용 대사는 여기서 제외한다. 이 검사는 자유문 전체의 의미 판독이나 실제 렌더 검수를 대체하지 않는다.
- 생성 분할 로컬 회귀: 독립 GEN 입력 두 개가 같은 등록 기준과 GEN 로컬 타임라인을 사용하고, 한쪽이 고정 블록을 바꾼 뒤 자체 재해시해도 차단되는지 확인한다. EX-02의 22초+12초 합성 프롬프트와 전 구간 검증은 `test_ex02_full_prompt_batch_cli`로 재현한다. `python3 scripts/prompt_batch_check.py --project ROOT --manifest ROOT/batch.json --json`은 `index`, `runtime_s`, `packets`(각 `prompt`·`map` 경로)를 읽는다. PBG01은 전역 간격·중복 GEN, PBG02는 컷 순서·구간·누락, PBG03은 컷별 대사 배정, PBG04는 공통 원장 핀을 검사한다. 각 프롬프트 검사도 실행하며, 미확인 모델 지원은 종료 3으로 남긴다. 입력 인덱스는 호출자가 지정한 검수본이며 이 명령은 제작 모델 호출이나 미디어 검수를 하지 않는다.
- 등록 근거는 JSON 전체 또는 등록 Markdown의 단일 `prompt-evidence` 코드 블록 속 JSON 객체를 사용한다. 축·조명 맵은 보드가 핀한 동일 정본에 두고 일치 여부를 검토한다. 이미지 인물이 없는 컷은 빈 `identity_sources`, `identity_na_reason`, 등록 시트 기준의 빈 패널 인물 목록이 모두 필요하며 identity 본문은 없어야 한다. 이 시트 기준은 **텍스트 선검사**에 쓸 수 있으나 이미지 파일이나 QA3 증거가 아니다.
- 종료 코드: 0 검사 완료·오류 없음 / 1 차단 / 2 입력 오류 / 3 오류는 없으나 미검증 규칙 존재. **3은 제출 통과가 아니다.**
- EX-02의 CLI 테스트는 기존 대사와 시간표에서 8블록 검사 입력을 조립한다. 완성 제작 프롬프트나 GEN 분할 검증으로 세지 않는다.

## Steps
- [ ] **1. 실패 테스트** —
  - `test_L2_dialogue_verbatim`: 따옴표 대사 한 단어 변경 → `L2`
  - `test_L3_rate_from_map`: ex02-defect-30s → `L3` 3건 (D001, D002, D009–D010)
  - `test_L5_fixed_block_hash_mismatch`: VPR-02의 B3 한 단어 다름 → `L5`
  - `test_fixed_block_hash_normalized`: 줄바꿈만 다름 → `L5` 없음
  - `test_L8_internal_id_leak`: 본문에 `CHR-01` → `L8`
  - `test_L9_reaction_before_stimulus`: ex02-defect-30s의 `reaction_to: D009 "세탁소 아줌마"`가 21.0–24.5, D009 구간 24.5–28.0 → `L9`
  - `test_L10_model_duration_exceeded`: 확인된 최대 길이 초과 → `L10` 차단
  - `test_L11_missing_observable_action`: 감정 형용사만 있는 연기 구간 → `L11` 경고
  - `test_L12_missing_block`: B8 없음 → `L12`
  - `test_I1_anchor_paraphrased`, `test_I4_text_in_image_prompt`, `test_I7_axis_mismatch`
  - `test_L13_lr_without_reference`: "오른쪽 위로 시선을 피한다"(기준 없음) → `L13` 경고
  - `test_L14_global_relative_time_in_B6`: "마지막 1초에 갈라진다" → `L14` 경고 (ex02-defect-30s)
  - `test_L15_separate_audio_requests_voice`: header `audio_path: separate` + B6 "대사는 원생 생성한다" → `L15`
  - `test_L16_flat_intensity`, `test_L17_missing_light_direction`, `test_L18_unknown_speaker_label`("형"이 `labels`에 없음), `test_L19_missing_hand_state`
  - `test_L20_body_contradicts_prohibition`: EX-04 결함 주입(봉투 글자 묘사 + B7 글자 금지) → `L20`
  - `test_silent_skips_dialogue_rules`: EX-04 → L2·L3·L4·L9 미적용, 0 error
  - `test_ex02_fixed_split_passes`: 0 error
- [ ] **2. 실패 확인**
- [ ] **3. 구현** — L6·L7·L11은 사전 기반 문자열 검사(축: "left/左/좌" 사전), L10은 `model_facts` 비교·`UNVERIFIED`면 경고, L9는 사이드카 `reaction_to`의 단어 시점(해당 대사 구간 내 단어 위치 비례 추정)과 반응 구간 시작 비교
- [ ] **4. 통과 확인** — `pytest tests/test_prompt_lint.py -q`
- [ ] **5. 커밋** — `feat(v2): prompt_lint`

## Acceptance
- EX-01 결함 F1·F2·(F3는 L1/규칙3 위반으로)·F7(경고)이 원문 fixture에서 검출되고 보정안 fixture는 통과.
