# 03 — 아티팩트·ID·인덱스 규약

- 문서 ID: `DES-03` · 상태: `draft-r2`
- 정본 범위: ID 문법, 아티팩트 목록, 폴더 구조, 스토리보드 인덱스 행, 검사 규칙, 변경 전파, 게이트 체크리스트.

## 1. 아티팩트 목록

| 접두사 | 이름 | 소유 크루 | 단계 | 하위 항목 ID |
|---|---|---|---|---|
| `BRF` | 브리프 | concept-benchmark | P0 | — |
| `BMK-nn` | 벤치마크 해부 1건 | concept-benchmark | P0 | `#hook`, `#beats`, `#curve` |
| `BOR` | 차용 원장 (Borrow ledger) | concept-benchmark | P0 | `BOR.Bnn` 행 |
| `SYN` | 시놉시스 | story-writer | P1 | — |
| `PLT` | 플롯/비트시트 | story-writer | P1 | `Bnn` 비트 |
| `SCR` | 각본 | story-writer | P1 | `Snn` 씬, `Dnnn` 대사 |
| `QAR-x` | QA 보고 (1,2,3,4,5,F) | audience-reaction-qa / production-qa | 게이트 | `Fnn` 수정 지시 |
| `WLD` | 세계관 바이블 | world-designer | P2 | `#rules`, `#forbidden`, `#palette` |
| `CHR-nn` | 캐릭터 (페르소나 포함) | character-designer | P2 | `#anchor`, `#persona`, `#voice-identity` |
| `WRD-nnx` | 의상 상태 (캐릭터 nn의 상태 x) | costume-designer | P2 | — |
| `LOC-nn` | 장소 | production-designer | P2 | `#view-front` 등 4뷰, `#plan`, `#layers`(배경: 전경/중경/원경) |
| `SET-nn` | 세트/건물 | production-designer | P2 | — |
| `ENV-nn` | 환경(시간대·날씨·계절) | production-designer | P2 | — |
| `PRP-nn` | 소품/도구 | production-designer | P2 | `#state-a` |
| `SND` | 사운드 바이블·큐 사용/확보 상태 | sound-designer | P2–납품 | `VOC-nn`, `AMB-nn`, `SFX-nn`, `MUS-nn`; 현재 소스·권리·리뷰 핀 |
| `DNT` | 연출 노트 | production-director | P3 전 | `#Snn` 씬별 5항목 |
| `CNT` | 콘티 | assistant-director + 부서 | P3 | `Snn-Cnn` 컷, `Snn-Cnn.bn` 하위 구간, `CAM-nn`, `LGT-nn`, `LOOK-nn`, `VFX-nn`, `CTY` 연속성 원장 |
| `STB` | 스토리보드 + 인덱스 | storyboard-artist | P4 | `Snn-Cnn-Pn` 패널 |
| `IMG-*` | 이미지 프롬프트 | image-prompt-engineer | P5 | `IMG-REF-CHR-01-front`, `IMG-Snn-Cnn-Pn` |
| `REF-*` | 기준 이미지 및 소스 참조/증빙 파일 | (작성/실행 결과) | 해당 단계 | 기존 tail 문법 재사용; 예: REF-MUS-01-rights/review, REF-SOUND-SOURCES/SEARCH. 이미지가 아닌 증빙을 이미지 입력으로 자동 전송하지 않음 |
| `SHT-nn` | 스토리보드 시트 이미지 | storyboard-artist | P5 | — |
| `GEN-nn` | 생성 작업 묶음 | video-prompt-engineer | P6 | 포함 컷 목록 |
| `VPR-nn` | 영상 프롬프트 (GEN과 1:1, 재시도 시 버전 증가) | video-prompt-engineer | P6 | 8블록 |
| `APR-nn` | 오디오 프롬프트 (separate 오디오 경로일 때만) | sound-designer | P6 | `#voice-Dnnn`, `#sfx`, `#music` |
| `TAK-nn-tk` | 테이크 파일 | (실행 결과) | 생성 | `tk` 테이크 번호 |
| `EDL` | 편집 결정 목록 | film-editor | P7 | — |
| `RUL-nn` | 감독 판정 기록 | production-director | 전 단계 | — |
| `CALL-…` / `DLV` | 콜시트 / 납품 패킷 ([01 §4](01-pipeline-and-gates.md#4-콜시트와-납품-패킷)) | director / 크루 | 전 단계 | 원장에만 보관, 산출물 아님 |

**대본과 각본.** v2에서 `SCR`(각본)이 정본이다: 씬헤딩·지문·대사·화자·전달 지시가 모두 들어간다. "대본"(대사·내레이션만 모은 낭독용 원고)은 `SCR`에서 `D` 항목만 추출한 **파생 보기**이며 따로 편집하지 않는다. 내레이션도 화자 `NAR`의 `D` 항목이다.

## 2. ID 문법

```
ref      := artifact [ "@v" version ] [ "#" anchor ] [ "." item ]
artifact := PREFIX [ "-" number [ suffix ] ]
cut      := "S" nn "-C" nn                 # 씬-컷  예: S01-C02
segment  := cut ".b" n                     # 컷 내부 하위 구간  예: S01-C02.b3
take     := "TAK-" nn "-" tk               # GEN 번호 - 테이크 번호
panel    := cut "-P" n                     # 예: S01-C02-P1
dialogue := "D" nnn                         # 프로젝트 전역 일련번호 (씬과 무관하게 유일)
```

- 번호는 0채움 2자리(대사는 3자리), 한번 부여한 ID는 삭제해도 재사용하지 않는다(`retired`).
- 버전 핀: 다른 산출물을 소비할 때 반드시 `@v`를 붙인다. 문서 본문 안의 같은 문서 참조는 생략 가능.
- 씬·컷·테이크: **씬**은 장소·시간 연속 단위(SCR), **컷**은 편집상 한 화면 연속 구간(CNT), **테이크**는 같은 GEN의 생성 시도(TAK). 하나의 GEN은 여러 컷을 포함할 수 있다(예: 30초 4컷을 1회 생성).

## 3. 프로젝트 폴더

```
<Media_Studio>/<project_id>/
  ledger.json              # 아티팩트 레지스트리·상태·승인·판정 (production-ledger)
  .history/                # 시간순 작업 이력
  00_brief/  BRF.md  BMK-01.md …  BOR.md
  01_story/  SYN.md  PLT.md  SCR.md
  02_bible/  WLD.md  CHR-01.md  WRD.md  LOC-01.md  PRP.md  SND.md
  03_conti/  CNT.md  CTY.md
  04_board/  STB.md  index.csv
  05_sheet/  IMG/  REF/  SHT-01.png
  06_prompt/ GEN.md  VPR-01.md  VPR-01.map.json
  07_takes/  TAK-01-1.mp4 …
  08_post/   EDL.md  mix/  subs/
  qa/        QAR-1.md …
  final/
```

v1 결정 승계: 프로젝트 산출물은 스킬 저장소 밖에 저장하고 절대 경로로 보고한다.

## 4. 스토리보드 인덱스 행 (REQ-10의 정본)

`STB`는 패널 서술과 함께 **시트 수준 머리말 1개 + 컷마다 한 행**의 인덱스를 가진다. 기계 판독용 `04_board/index.csv`(행)와 `04_board/index-header.json`(머리말)이 정본이고, `STB.md`의 표는 그 보기다.

### 4.1 머리말 (프로젝트 전체에 걸리는 정본)

컷 행마다 반복하지 않는 문서는 머리말에서 버전을 고정한다. 모두 필수이며 빠지면 `index_lint` IX07. 예외: 벤치마크가 없으면 `"BMK": []`와 `"bmk_unknown_reason"`, 게이트를 아직 통과하지 않은 QAR은 목록에 없어도 된다.

```json
{"BRF": "BRF@v1", "BMK": ["BMK-01@v1", "BMK-02@v1"], "BOR": "BOR@v1", "SYN": "SYN@v2", "PLT": "PLT@v2",
 "SCR": "SCR@v3", "DNT": "DNT@v1", "WLD": "WLD@v1", "SND": "SND@v2", "LOOK": ["LOOK-01@v1"],
 "QAR": ["QAR-1@v2", "QAR-2@v1"], "runtime_s": 38.0, "aspect": "20:9", "fps": 24, "audio_path": "native"}
```

### 4.2 컷 행

| 열 | 필수 | 내용 | 예 |
|---|---|---|---|
| `cut` | ● | 컷 ID | `S01-C02` |
| `t_start`, `t_end` | ● | 전체 타임라인 초(소수 1자리) | `3.7`, `23.0` |
| `segments` | ○ | 하위 구간 목록 | `b1:3.7-6.5;b2:6.5-11.5;…` |
| `beats` | ● | PLT 비트 | `PLT@v2.B03;B04` |
| `scene` | ● | SCR 씬 | `SCR@v2.S01` |
| `dialogue` | ● | 대사 ID 또는 `none` | `D002;D003;D004` |
| `speakers_onscreen` / `speakers_offscreen` | ● | CHR | `CHR-02` / `—` |
| `characters_visible` | ● | 보이는 인물 | `CHR-02;CHR-01(fg-blur)` |
| `wardrobe` | ● | 의상 상태 | `WRD-01a;WRD-02a` |
| `location` | ● | 장소/세트/환경 | `LOC-01;SET-01;ENV-01` |
| `props` | ● | 소품 또는 `none` | `PRP-02(state-a)` |
| `camera` | ● | 카메라 셋업 | `CAM-02` |
| `lighting` / `look` | ● | 조명/룩 | `LGT-01` / `LOOK-01` |
| `performance` | ● | 연기 레이어 앵커 | `CNT@v3#S01-C02.perf` |
| `voice` | ● (대사 있을 때) | 목소리 | `VOC-02` |
| `ambience` / `sfx` / `music` | ● | 사운드 또는 `none(이유)` | `AMB-01` / `none(SND rule: no SFX)` / `none(SND rule: no BGM)` |
| `vfx` | ● | VFX 또는 `none(이유)` | `none(realistic drama)` |
| `transition_in` / `transition_out` | ● | 전환 | `hardcut` / `hardcut` |
| `continuity` | ● | 연속성 원장 항목 | `CTY.axis-01;CTY.dist-01` |
| `world_rules` | ○ | 세계관 금지/규칙 | `WLD#forbidden` |
| `gen` | P6 | 생성 묶음 | `GEN-01` |
| `panels` | ● | 패널 ID | `S01-C02-P1;P2;P3` |
| `scene_note` | ● | 연출 노트 | `DNT@v1#S01` |
| `sheet` | P5 | 시트 이미지 | `SHT-01#cell-05` |
| `audio_prompt` | P6 (separate) | 오디오 프롬프트 | `APR-01#voice-D002` |
| `adopted_take` | QA5 | 채택 테이크와 구간(GEN 로컬 초) | `TAK-01-2@5.0-28.5` |

**기계 판독 계약.** 보드의 아티팩트 참조에는 버전 핀을 붙이고, 대사 원문 비교용 `dialogue_text` 열을 둔다. 보드 생성 전 바이블 점검은 대상 목록 파일을 사용한다. 정확한 입력과 로케이터는 [인덱스 검사 규약](../../production-ledger/references/ledger-schema.md#단계별-인덱스-검사)에 따른다.

**겹침·걸침 표기.** 두 대사가 시간상 겹치면 `segments`에 `overlap:D004+D005@12.4-13.6`, 대사가 다음 컷으로 이어지면 `lcut:D008>S01-C03`을 쓴다. `timeline_check`는 이 표기가 있을 때만 대사 구간 겹침(TL02)을 허용한다. 대사 없는 작품은 `dialogue`·`voice` 열에 `none(무대사 작품)`을 쓰며 말속도 검사 대상이 아니다.

`●`필수 열의 빈칸은 금지다. 해당 없음은 `none(이유)`로 쓴다(미정 `TBD`는 QA2에서 차단 결함).

### 4.3 사운드 소스·큐 사용 연결

[DES-11 §3–5](11-sound-sourcing-integration.md#3-파일과-증빙을-기존-id원장에-등록)가 등록 순서/판정의 정본이다. 기존 ambience/sfx/music의 AMB/SFX/MUS 버전 핀을 사용하고 새 필수 보드 열은 만들지 않는다. 계획 문서 버전과 실제 선택 미디어 버전은 소스 원장의 cue_ref·local_path·sha256 및 use_stage로 구별한다. 바이너리 미디어에 Markdown anchor를 붙이지 않는다. source in/out·실측 길이·작품 시간·루프/J/L/덕킹 의도는 SND와 CNT의 기존 sound.cues에 연결한다.

rights REF → 실제 미디어 → review REF → 소스 원장 REF → SND → 실제 소비자 순서로 등록한다. 원장/파일 존재만으로 rights나 청취가 확인되는 것은 아니다. 직접 참조 파일 외의 증빙/리뷰 해시는 별도로 대조하고 source/rights/review 바뀜을 기존 consumes로 전파한다. 납품에는 실제 파일과 큐시트·출처/크레딧·권리/청취 근거·전달 허가 및 미해결 항목을 묶는다.

## 5. 변경 전파와 stale

- 아티팩트 버전이 오르면 `production-ledger`는 그 아티팩트를 `@v`로 소비한 모든 하위 산출물을 `stale`로 표시한다(`impact set`).
- `stale` 산출물을 입력으로 하는 콜시트는 발행할 수 없다. 감독은 영향받은 크루에 갱신 콜시트를 먼저 보낸다.
- 하위 항목만 바뀌었으면(`CHR-01#anchor` 등) 그 앵커를 참조한 행만 stale로 좁힌다(QA 2회차의 영향 범위 근거).
- **초안 버전.** 여러 부서가 차례로 채우는 문서(대표: 콘티 회의 중의 CNT)는 작업 중 `@draft`로 참조하고, 단계 종료 시 한 번만 버전을 확정한다. `@draft` 변경은 stale을 전파하지 않으며, `@draft`를 입력으로 하는 콜시트는 같은 단계 안에서만 허용한다.

## 6. 게이트별 QA 체크리스트

기계 검사(🅼)는 스크립트가 판정하고, 판단 검사(🅹)는 `production-qa`가 근거와 함께 판정한다.

### QA2 — 프리프로덕션 1차 완료

| # | 검사 | 종류 |
|---|---|---|
| 2.1 | `index_lint`: 머리말 완비, 필수 열 빈칸 0, 모든 참조가 존재하는 ID·버전으로 해결, stale 참조 0 | 🅼 |
| 2.2 | 고아 검사: 바이블의 모든 CHR/LOC/PRP/WRD/VOC가 최소 1개 컷에서 참조되거나 `unused(이유)` | 🅼 |
| 2.3 | `timeline_check`: 컷 구간이 빈틈·겹침 없이 0–러닝타임을 덮음, 하위 구간이 컷을 덮음 | 🅼 |
| 2.4 | 모든 `D`가 정확히 한 컷(또는 명시된 오버랩)에 배정, 대사 원문이 SCR과 동일 | 🅼 |
| 2.5 | 말속도: 구간 길이 대비 대사 길이가 언어별 상한 이하 ([07 §3](07-video-prompt-spec.md#3-타임라인-블록-규칙)) | 🅼 |
| 2.6 | 축·시선: CTY의 축 규칙과 각 컷의 화면 방향이 일치, 축 넘기는 컷은 사유 있음 | 🅹 |
| 2.7 | 의상·소품 상태 연속: 컷 순서대로 상태 전이가 CTY 사건과 맞음 | 🅹 |
| 2.8 | 이야기 기능: 각 컷이 비트 목적을 수행, QA1 수정 지시가 반영됨 | 🅹 |
| 2.9 | 부서 충돌 미해결 0 (`RUL` 기록 확인) | 🅼 |
| 2.10 | 권리: 실존 인물·브랜드·음악 사용 여부와 동의 상태 | 🅹 |
| 2.11 | [연결 계약](05-conti-collaboration.md#4-연속성-원장-cty): 모든 컷의 편집상 선행 컷·전환 유형·상태 기준 또는 초기 근거·진입/이탈·유지/변경·의도가 완비되고 관계상 모순·미해결 변화 근거 없음. 구조·핀 존재 검사만으로 이 판단을 대체하지 않음 | 🅹 |
| 2.12 | [사운드 통합](11-sound-sourcing-integration.md): 큐 기능/required·무음 근거·용도와 요청 범위·작품/소스 시간·실측/추정·탐색/확보 상태가 명확. 설계 PASS와 소스 준비 판정 분리; post_only 미확보를 독립 시각 작업 차단으로 확대하지 않음 | 🅹 |

### QA3 — 스토리보드 시트

| # | 검사 | 종류 |
|---|---|---|
| 3.1 | 모든 패널에 이미지 또는 `blocked(이유)`, 파일 해시 등록 | 🅼 |
| 3.2 | 정체성: 같은 CHR의 얼굴·나이·헤어가 REF와 시트 전체에서 일치 | 🅹 (실제 이미지를 열어 확인) |
| 3.3 | 의상·소품 상태가 인덱스 행과 일치 | 🅹 |
| 3.4 | 구도: 사이즈·앵글·좌우 배치가 CAM과 축 규칙에 맞음 | 🅹 |
| 3.5 | 가독성: 패널의 정점 표정/행동이 한눈에 읽힘 | 🅹 |
| 3.6 | 이미지 속 불필요한 글자·워터마크 없음 | 🅹 |
| 3.7 | 연결 계약에 상태 기준 패널이 있으면 현재 패널과 함께 비교: 손·소품·동작·시선·위치와 변화 근거 일치. initial은 초기 상태 근거·기준 이미지와 대조하고 선행 패널 비교는 해당 없음으로 기록. 비교한 파일·해시·관찰 상태를 남기며 필요한 이미지 미생성/미확인은 시각 QA 미검증 | 🅹 |

### QA4 — 제출 전 (프롬프트)

| # | 검사 | 종류 |
|---|---|---|
| 4.1 | [개별 프롬프트·전체 배치 제출 규약](../../production-director/references/qa4-submit.md)에 따라 실제 검수본 검사; 비제로 종료는 제출 차단 ([07 §6](07-video-prompt-spec.md#6-prompt_lint-규칙)) | 🅼 |
| 4.2 | 사이드카 역추적: 모든 블록이 인덱스 행 ID로 해결 | 🅼 |
| 4.3 | 모의 낭독: 프롬프트만 읽고 예상 결과(시작·행동·끝·대사)를 서술해 STB와 대조 | 🅹 |
| 4.4 | 논리 모순: 아직 말하지 않은 대사에 반응, 보이지 않는 인물의 표정 지시 등 | 🅹 |
| 4.5 | 모델 적합: 선택 엔드포인트의 길이·종횡비·오디오·언어 지원 확인. [레지스트리와 제출 차단 규칙](../../model-facts/_schema.md) 적용 | 🅹 |
| 4.6 | 해당 요청이 실제 소비하는 generation_input 오디오: 현재 파일/핀·기술/실측·최종 청취·개별 권리/전송 승인·실제 모델 입력/선택 참조를 대조. 미확인은 해당 제출 차단; post_only는 억지 공급자 입력으로 승격하지 않음 | 🅹 + 직접 파일/핀 검사 |
| 4.7 | 소스 확보 포함 요청의 프리 납품/인계: required 큐 전부의 현재 파일·기술 검사·최종 파일 청취·개별 권리/정확한 크레딧·Content ID 대응·수령자 원본 전달 조건과 사용 구간 확인. 미충족이면 관련 확보/납품 partial/blocked; 2회 후 residual_risk로 ready 처리하지 않음. 직접 사운드 납품은 같은 항목을 범위별 QAR-2로 검사 | 🅹 + 직접 파일/핀 검사 |

### QA5 — 테이크

| # | 검사 | 종류 |
|---|---|---|
| 5.1 | 대사·립싱크·화자 분리 | 🅹 (실제 재생) |
| 5.2 | 얼굴·의상 드리프트 | 🅹 |
| 5.3 | 표정 비트가 하위 구간 시점에 맞게 일어남 | 🅹 |
| 5.4 | 금지 목록 위반(글자·제3인물·현대 물품 등) | 🅹 |
| 5.5 | 채택 구간 in/out을 인덱스 `adopted_take`에 기록, 재생성 시 수정 지시는 VPR 블록 단위 | 🅼 |

### QA-F — 최종

재생 전수, 컷 경계, 음량, 자막 위치·오탈자, 플랫폼 규격. v1 `creative-production/references/creative-qa.md`의 출력본 검수 항목을 승계한다.
