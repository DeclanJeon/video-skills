# WO-08 — 콘티 6부서 (콘티 회의)

**Goal:** DES-05 라운드 R0–R7을 수행하는 6개 크루와 회의 진행 규약.
**Spec:** DES-05 전체, DES-02 Phase C, DES-07 §3(말속도) · **의존:** WO-07, WO-04(`DNT` 입력)

## 부서별 파일과 계약

| 스킬 | 라운드 | references (v1 이관 출처) | 레이어 필수 필드 |
|---|---|---|---|
| `assistant-director` | R0, R7 | `breakdown.md` (씬→컷 분해), `timing-table.md` (`speech_rates.json` 사용, 쉼 0.3s), `continuity-ledger.md` (v1 26-state-causality-continuity), `meeting-protocol.md` (DES-05 §1·§5) | 컷 ID·구간·대사 배정·L컷 표기, `CTY` 항목, 충돌 목록 |
| `performance-director` | R1 | `facial-action.md` (부위 서술 사전 + FACS AU 표: AU1,2,4,5,6,7,9,10,12,15,17,20,23,24,25,26,28,43), `delivery.md` (속도·강세·쉼·떨림·비언어음), `listener-reaction.md` (v1 storyboard-direction 청자 반응), `restraint.md` (과장 금지 목록) | DNT 블로킹 콘셉트의 상세 동선, 하위 구간별 시작→정점→정착, 부위 서술, AU 보조, 감정의 목적 문장, 대사 전달, 청자 반응 + `reaction_to` |
| `cinematographer` | R2 | `lens-size-angle.md` (v1 06-shots, camera-spatial-design), `axis-eyeline.md`, `movement.md` (이유 있는 무빙/고정, 금지 목록), `previs-request.md` (Blender 장비 요청 조건) | `CAM-nn` 재사용, 렌즈 mm·사이즈·앵글·심도·구도 비율·무빙·전환, 좌우는 화면 기준 표기 |
| `lighting-director` | R3 | `lighting-setups.md` (v1 07-lighting, lighting-language-catalog), `look.md` (v1 05-visual·20 LOOK) | `LGT-nn`, `LOOK-nn`, 컷별 매칭 메모, 금지 룩 |
| `vfx-supervisor` | R5 | `vfx-triage.md` (v1 08, 21 위험), `motion-graphics.md` (v1 08a/08b/33 요약) | 필요/불필요 + 이유, 필요 시 `VFX-nn` 기능·구간·레이어·AI 위험 |
| `film-editor` | R6 (+P7) | `cut-rhythm.md` (v1 09-edit, animatic-direction), `overlap.md` (J/L컷), `gen-grouping-hint.md` (DES-07 §4 제안), `post.md` (P7: EDL·자막·납품, v1 09a·15·23·23a) | 컷 포인트·전환·오버랩·리듬 판단, GEN 경계 제안 |

`sound-designer`의 R4 레이어 계약은 WO-07 SND 스킬에 `conti-layer.md`로 추가한다.

## Steps
- [ ] **1. 평가 케이스** (입력: WO-07 산출 바이블 + SCR-ex02, 결함 검출 케이스는 [EX-02](../examples/synthetic-laundromat-34s/fixture.md) §3 시간표)
  - E-41 AD R0: 컷 시간표 합 = 러닝타임, 각 대사 배정, 말속도 초과 대사를 `timeline_check`로 검출하고 **보정안(러닝타임 연장 / 작가 축약 요청)** 둘을 감독에 제시
  - E-42 performance R1: 동선이 DNT 블로킹 콘셉트와 일치, 모든 하위 구간에 부위 서술, 감정 형용사 단독 0, 청자 반응에 `reaction_to`
  - E-43 cinematographer R2: 축 규칙 준수, 반복 셋업 `CAM-01` 재사용, 좌우 화면 기준, 정점 샷이 같은 인물의 이전 샷보다 타이트(PP-19), 샷별 키 라이트 방향 메모(SUP-10)
  - E-44 lighting R3(샷별 화면 기준 키 방향, 리버스 샷 대조) + E-45 vfx R5(`none(realistic drama)`) + E-46 editor R6(D008 뒤 정지 1.0s, C03 화면 밖 대사 표기)
  - E-47 충돌 주입: lighting "형광등 톱라이트만 유지" vs performance "눈 반사광 필요" → 각 부서가 상대 레이어를 고치지 않고 `conflicts`에 기록
  - E-48 경량 모드: 20초·1씬 브리프 → 한 콜시트로 R1–R6, `layer_by:` 유지
  - E-49 회의 중 참조는 `CNT@draft#layers.<dept>`, R7 종료 시 `CNT@v1` 한 번만 확정
- [ ] **2. 6개 SKILL.md 작성** (각 ≤120줄)
- [ ] **3. 평가 실행** — `qa/wo-08/run-1/`, CNT 결과를 `timeline_check`·`index_lint --stage board`(부분)로 검사
- [ ] **4. 수정·재실행 (최대 2회), 커밋** — `feat(v2): conti departments`

## Acceptance
- E-41–E-49 PASS. E-41에서 EX-02 결함판 시간표의 말속도 결함(SUP-01)을 프롬프트 단계 이전에 잡는다.
