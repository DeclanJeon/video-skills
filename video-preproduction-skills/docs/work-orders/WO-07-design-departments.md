# WO-07 — 에셋 설계 5부서

**Goal:** 잠긴 각본의 모든 대상(세계·인물·의상·장소·건물·환경·소품·소리)에 정본 바이블과 ID를 부여하는 5개 크루.
**Spec:** DES-02 Phase B, DES-03 §1, DES-01 §2 P2·CK-B · **의존:** WO-04 (WO-02의 `index_lint --stage bible`)

## 부서별 파일과 계약

| 스킬 | references (v1 이관 출처) | assets | 필수 필드 |
|---|---|---|---|
| `world-designer` | `world-rules.md` (v1 world-rules-and-information-recipes), `period-research.md` (고증 출처 표기 규칙) | `WLD-template.md` | `#rules`, `#forbidden`(화면 금지 목록), `#palette`(색·재질 근거), 사실/허구 구분 |
| `character-designer` | `identity-anchor.md` (v1 character-craft), `persona-lenses.md` (v1 designing-character-personas), `voice-identity.md` | `CHR-template.md` | `#anchor`(프롬프트에 그대로 쓸 1–3문장, 영어·한국어 병기), `#persona`(동기·결핍·결정 규칙), `#voice-identity`, `#expression-habits`, 실존 인물 모방 금지 문장, 7뷰 서술 |
| `costume-designer` | `wardrobe-states.md` | `WRD-template.md` | CHR×씬 매트릭스, 상태별 고정 문장(`WRD-nnx`), 헤어·분장, 변화 사유 |
| `production-designer` | `locations-sets.md` (v1 05-visual 공간 부분), `props-states.md` | `LOC-template.md`, `SET-template.md`, `ENV-template.md`, `PRP-template.md` | LOC 4뷰 서술 + 텍스트 평면도(`#plan`: 출입구·창·광원 위치) + 배경 레이어(`#layers`: 전경/중경/원경), ENV 시간대·날씨·계절, PRP 상태·소유 |
| `sound-designer` | `audio-path.md` (DES-07 §9 native/separate 판단), `audio-prompts.md` (`APR` 작성: 대사별 TTS 연기 지시·SFX·음악 프롬프트), `voice-casting.md` (v1 audio-production-routing 공급자 후보는 '제안'으로만), `ambience-sfx.md` (v1 edit-sound-language-catalog), `music-policy.md`, `speech-rate-calibration.md`, `mix.md` (P7, v1 voice-mix-finishing) | `SND-template.md` | `VOC-nn`(음역·질감·속도·감정 범위), `AMB-nn`, `SFX-nn`, `MUS-nn` 또는 `none(방침)`, `#policy`(`audio_path` 제안 포함), `#speech-rate`(프로젝트 보정값); P6 separate 경로에서 `APR-nn` |

부서 순서: world → character → (costume ∥ production-designer) → sound. 감독이 병렬 콜시트를 낼 때 costume과 production-designer는 서로 입력이 아니다.

## Steps
- [ ] **1. 평가 픽스처** — `evals/design/fixtures/SCR-ex02.md` ([EX-02](../examples/synthetic-laundromat-34s/fixture.md) §2의 전제·대사를 각본 형식으로; 바이블 요약은 정답지로만 쓰고 입력에 넣지 않음), `SCR-office-shorts.md`(WO-05 E-13 출력)
- [ ] **2. 평가 케이스**
  - E-31 world: SCR-ex02 → `#forbidden`에 화면 속 읽히는 글자(간판·영수증), `#palette` 근거(형광 녹백 vs 가로등 주황)
  - E-32 character: CHR 2명, `#anchor`가 1–3문장이고 나이·체형·헤어·얼굴 표지 포함, 의상 언급 없음(의상은 WRD)
  - E-33 costume: WRD-01a, WRD-02a, 전 씬 상태 유지 명시
  - E-34 production-designer: LOC-01 4뷰, `#plan`에 광원(천장 형광등, 유리문 밖 가로등)과 계산대 위치, `#layers` 전경/중경/원경
  - E-35 sound: VOC 2, AMB 1, `MUS none(방침)`, `SFX none(방침)`, `audio_path` 제안과 근거
  - E-35b sound(P6, separate): 대사 D001–D003에 대해 `APR-01#voice-Dnnn` — 대사 원문 동일, 연기 지시가 CNT 연기 레이어와 일치
  - E-36 CK-B: 위 산출물로 `index_lint --stage bible` → 0 error; 각본에 소품 한 개 추가 후 → `IX04`가 아니라 "미부여 대상" 보고로 production-designer 재배정
- [ ] **3. 5개 SKILL.md 작성** (각 ≤120줄)
- [ ] **4. 평가 실행** — `qa/wo-07/run-1/`
- [ ] **5. 수정·재실행 (최대 2회), 커밋** — `feat(v2): design departments`

## Acceptance
- E-31–E-36 PASS. CHR `#anchor` 문장이 WO-10·WO-11 프롬프트에 문자 단위로 재사용 가능한 형태(따옴표·메모 없음).
