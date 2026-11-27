# 06 — 이미지 프롬프트 규격 (프리프로덕션 2차)

- 문서 ID: `DES-06` · 상태: `draft-r3`
- 소유 스킬: `image-prompt-engineer` · 시트 조립: `storyboard-artist`
- 입력: `STB`(인덱스 포함), 바이블 전체, `LOOK`. 출력: `IMG-*` 프롬프트 + 사이드카, 실행 후 `REF-*`, `SHT-nn`.

## 1. 두 층의 이미지

| 층 | 목적 | 대상 | 생성 순서 |
|---|---|---|---|
| **기준 이미지 (REF)** | 정체성·공간·룩을 고정해 이후 모든 패널과 영상의 참조로 쓴다 | 캐릭터 7뷰(정면·¾좌우·측면 좌우·후면·표정 3종), 의상 상태별 전신, 장소 4뷰, 주요 소품, LOOK 프레임 1장 | 먼저. 의존 순서: CHR → WRD → LOC → PRP → LOOK |
| **패널 이미지** | 컷의 시작/정점/끝 순간 시각화 | `STB` 패널 | REF 이후, 각 패널이 해당 REF를 참조 입력으로 받음 |

REF 없이 패널을 만들지 않는다(정체성 드리프트의 주원인). 공급자가 참조 입력을 지원하지 않으면 앵커 문장 재사용으로 대체하고 QA3에서 정체성 검사를 엄격히 한다.

## 1.1 기본 이미지 실행자와 완료 경계

- 사용자가 다른 경로를 지정하지 않으면 정지 기준 이미지·콘티 패널 생성은 설치된 `codex-imagen` 스킬을 읽고 그 도구로 실행한다. 지원 여부·인증은 실제 환경에서 확인한다. 이 문서는 CLI/API 설치, 다른 유료 공급자 대체, 영상 생성 또는 게시 권한을 주지 않는다.
- 승인된 로컬 인물/자료만 필요한 참조로 전달한다. 사용자 범위 밖 인물 전송·음성 복제는 별도 확인한다. 실제 요청문·참조 경로/해시·관찰된 출력·실행 이력을 프로젝트에 남긴다.
- 순서는 기존 CHR→WRD→LOC→PRP→LOOK→개별 패널→시트 조립→QA3이다. 동시 이미지 작업은 호스트 전체 최대5개. 불확실/타임아웃 작업은 기존 출력과 실행을 대조하기 전 자동 재시도하지 않는다. `codex-imagen` 기본 재시도가 이 원칙과 충돌하면 `--no-retry`로 호출한다.
- 이미지가 있는 프리프로덕션의 완료 근거는 실제 개별 PNG, 최대8셀 PNG 시트와 `.cells.json`, 현재 인덱스/참조 버전 및 실제 열린 이미지의 검수 기록이다. 프롬프트·빈 폴더·생성 예측·성공 응답만으로 완료라고 하지 않는다.
- 텍스트/프롬프트 전용 요청에서는 생성하지 않는다. 런타임·권한·필수 공간 증거가 없으면 그 의존 작업만 정확히 차단하고 독립 가능한 기준 이미지/패널 작업은 계속한다. 시트 조립 성공은 실제 정체성·연속성·접촉/물리 검증이나 QA4 승인이 아니다.

## 2. 패널 프롬프트 블록 순서

모델 중립 슬롯. 직렬화(언어·문법)는 선택 모델 방언에서 마지막에 적용한다.

| # | 블록 | 출처 ID | 작성 규칙 |
|---|---|---|---|
| 1 | 매체·스타일 잠금 | `LOOK`, `WLD#palette` | 전 패널 동일 문장. "realistic cinematic still, 35mm film grain, muted brown/grey-brown/desaturated green" 등 |
| 2 | 화면비·프레이밍 | `BRF`, `CAM-nn` | 영상과 같은 화면비(예: 20:9 → 모델 지원 비율로 근사 시 기록) |
| 3 | 샷 | `CAM-nn` | 사이즈·앵글·렌즈 감각·심도. "85mm portrait, chest-up close shot, very shallow depth of field" |
| 4 | 인물 | `CHR-nn#anchor`, `WRD-nnx` | **바이블 앵커 문장을 그대로** 붙여 넣는다. 의역 금지. 화면에 보이는 인물만 |
| 5 | 순간의 행동·표정 | `CNT#…perf` 의 해당 하위 구간 정점 | 관찰 가능한 부위 서술. 정지 이미지이므로 하나의 순간만 |
| 6 | 배치·축·시선 | `CTY.axis`, `CAM` | 화면 좌/우, 전경/배경, 시선 방향. "man on frame left facing right" |
| 7 | 장소·환경·빛 | `LOC`, `SET`, `ENV`, `LGT` | 배경 요소는 심도에 맞게 흐림 정도 명시 |
| 8 | 소품 | `PRP` | 상태와 손 위치 |
| 9 | 금지 | `WLD#forbidden`, 공통 | 글자·워터마크·로고·말풍선·패널 번호·제3인물·현대 물품 |

## 2.1 컷 간 상태를 패널로 옮기는 순서

[연결 계약 정본](05-conti-collaboration.md#4-연속성-원장-cty)을 읽고, 인덱스 `continuity`의 CTY 컷 계약에서 현재 패널 순간의 상태를 고른다. 진입·정점·이탈은 서로 다른 순간이다. 필요한 미정이나 변화 근거 누락은 영향 패널의 확정을 보류하고 감독에게 반환한다.

- 텍스트 출처는 기존 사이드카 `sources`에 `"continuity": ["CTY@vN#Snn-Cnn"]`처럼 기록한다(실제 버전·앵커 사용). 내부 핀은 프롬프트 본문에 노출하지 않는다.
- 선행 패널이 실제로 있고 손·소품·위치 등의 비교가 필요하면 관련 파일을 열고 확인한 파일·해시·관찰 상태를 납품 증거에 기록한다. 교차편집에서는 상태 기준 패널을 고른다.
- 모델에 첨부할 때만 기존 `references`에 해당 파일 참조를 추가하고 유지하려는 상태와 역할을 기록한다. 실제 지원·권한을 확인하며 직전 이미지의 무조건 첨부나 구도 복제를 요구하지 않는다. 확인만 한 이미지와 첨부한 이미지는 구분한다.
- 리버스숏은 같은 세계 공간의 상태를 새 CAM에 투영한다. 회상·시간 생략은 근거에 따라 달라진 상태를 사용한다.
- 이미지 미생성 때는 CTY·바이블로 텍스트 설계·프롬프트를 진행하고, 해당 시각 비교만 미검증으로 남긴다. 실제 이미지 납품·QA3 완료 기준은 §1.1 그대로 유지한다.

## 3. 시트 조립 규칙

- 패널은 **개별 이미지로 생성**하고 시트는 스크립트로 조립한다(`assemble_sheet`, WO-08). 패널 번호·시간·대사·카메라 표기는 조립 단계에서 텍스트 레이어로 넣는다. 이미지 모델에게 글자를 그리게 하지 않는다.
- 시트 한 장 최대 8패널, 읽는 순서 좌→우·상→하, 셀 ID를 `SHT-nn#cell-nn`으로 인덱스에 기록.
- 빠른 시안이 필요하면 다중 패널 한 장 생성도 허용하되 `draft_sheet`로 표시하고 QA3 정체성 검사 대상에서 제외(시안은 승인 근거가 아님).

## 4. 사이드카 (`IMG-….map.json`)

```json
{
  "id": "IMG-S01-C02-P2",
  "panel": "S01-C02-P2",
  "moment": "S01-C02.b3 peak (≈14.0s)",
  "blocks": {
    "style": ["LOOK-01@v1", "WLD@v1#palette"],
    "shot": ["CAM-02@v1"],
    "subject": ["CHR-02@v1#anchor", "WRD-02a@v1"],
    "action": ["CNT@v3#S01-C02.b3"],
    "blocking": ["CTY@v2#axis-01"],
    "setting": ["LOC-01@v1", "ENV-01@v1", "LGT-01@v1"],
    "negative": ["WLD@v1#forbidden", "common:no-text"]
  },
  "reference_inputs": ["REF-CHR-02-front", "REF-LOC-01-view-right"],
  "model": "<실행 시 기록>",
  "prompt_language": "en"
}
```

## 5. 이미지 프롬프트 점검 (I-규칙, `prompt_lint --kind image`)

| 규칙 | 내용 | 차단 |
|---|---|---|
| I1 | 인물 블록 문장이 `CHR#anchor`·`WRD` 원문과 문자 단위로 동일 | ● |
| I2 | 보이는 인물 수 = 인덱스 `characters_visible` | ● |
| I3 | 스타일 잠금 문장이 시트 내 모든 패널에서 동일 | ● |
| I4 | 프롬프트 본문에 내부 ID·한국어 메모·대사 원문 따옴표 없음(글자 렌더 위험) | ● |
| I5 | 금지 블록에 no-text/no-watermark 포함 | ● |
| I6 | 한 패널 = 한 순간 (동작 연쇄 "then" 없음) | ○ |
| I7 | 좌/우 배치가 CTY 축과 일치 | ● |

## 6. 완성 예 — 패널 `S01-C02-P3` (동생 어깨 너머 근접, `.b4` 정점 ≈ 16.5초)

내용은 [EX-02 합성 픽스처](../examples/synthetic-laundromat-34s/fixture.md)다. 줄바꿈은 블록 구분용이며 실제 제출 시 모델 방언에 맞춘다. 중괄호는 설명이며 제출문에 넣지 않는다.

```text
Realistic cinematic film still, faint digital noise, low saturation, contrast between cold green-white fluorescent light and warm orange streetlight.   {블록1 LOOK-01}
Vertical 9:16 frame.   {블록2 BRF aspect}
Over-the-shoulder medium close shot, 50mm lens look, chest-up, shallow depth of field.   {블록3 CAM-02}
A Korean woman in her mid-fifties, sturdy build, short bob hair tied back tightly, no makeup, an old iron burn scar on the back of her right hand; grey knit sweater under a navy apron, sleeves rolled up.   {블록4 CHR-02#anchor + WRD-02a, 원문 그대로}
She holds the back of her right hand up toward the man so the burn scar faces the camera; her eyes stay on his face, not on her hand; inner brows lifted, lower eyelids tense, rims of her eyes reddened but no tears, lips pressed together.   {블록5 CNT#S01-C02.b4 정점}
She stands center-right of frame facing frame left; the blurred grey shoulder and back of the head of a thin older man fill the lower-left fifth of the frame in the foreground; their eyelines meet across a laundry counter.   {블록6 CTY#axis-01, dist-01}
Background: a narrow old laundromat at night, rows of plastic-covered garments on hangers deep in the frame, a steam ironing board, a glass door with a streetlight outside; cold fluorescent light from above, warm orange streetlight rim from deep frame left on her left cheek (screen left).   {블록7 LOC-01#layers, ENV-01, LGT-01}
Nothing held in either hand; a closed ledger lies on the counter.   {블록8 PRP-01 state-closed}
No text, no captions, no signage lettering, no watermark, no logo, no panel numbers, no third person, no beauty retouching, no commercial lighting.   {블록9 WLD#forbidden + common}
```

이 수준이 "구체적·세밀"의 최소선이다: 한 순간, 보이는 인물과 화면 내 위치, 얼굴 부위별 상태, 배경 심도, 빛의 방향, 금지 목록이 모두 있다.
