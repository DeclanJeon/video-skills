# 변경 기록

## 2026-11-28 — Declan 자료의 조건부 편집·룩 비교 지침

- film-editor에 의미 전달 모션의 시작/변화/지속/종료를 기존 승인 설계와 한 번만 통합하고, 여러 정보 모션의 중심·보조 시선 위계와 도식의 연결 대상/방향/색·공개 순서를 보강했다. 일반 대화·단일 강조의 추가 양식은 요구하지 않으며 승인된 동시 강조·결과 선공개를 보존한다.
- concept-benchmark는 룩이 미정이고 내용 차이가 비교를 방해할 때만 통제된 기존 샘플 비교 또는 비교 한계를 기록한다. 확정 룩을 다시 선택하게 하지 않고, 새 생성은 감독/오케스트레이터의 기존 단계·승인 범위로 요청한다.
- 새 스킬·필수 양식·게이트·스키마·원장·실행기·설치는 추가하지 않았다. 프리 구조 검사 20개 스킬/findings 0, 기존 pytest 273 통과. 문안 자체 점검과 실제 에이전트 행동/영상 품질 검증을 구분하며 후자는 미수행이다. 근거·제한은 ../qa/declan-skill-integration.md에 기록했다.

## 2026-11-27 — 변신·봉인 세트피스 계약(DES-12 §8)

- 사용자가 준 변신 장면(39.5초)·봉인 장면(96초) 레퍼런스를 실제 프레임으로 분해한 결과를 근거로 세트피스 규칙을 추가했다: 컷 표 작성, 구조·문법만 이전하고 고유 소품 교체, 신체 노출 불가, 변신/봉인 구조, `setpiece` 세그먼트.
- `action_lint.py`에 `setpiece` 세그먼트와 AL11(속도)·AL12(움직임)·AL13(클로즈업/와이드 비율)을 추가하고 RED→GREEN 회귀 2개를 더했다(10 통과).

## 2026-11-27 — 액션 연출 계약(DES-12)과 action_lint

- 관측된 실패(교회 PLTC 드래곤 콘티: 액션 ASL 4.6초, 위협 노출 7/24, 정면 일렬 타블로, 인서트 0, 추상 공격 서술, 공간 지도 부재 — 인덱스/타임라인 검사는 모두 PASS)와 사용자 제공 레퍼런스 8편 실제 프레임 분해를 근거로 DES-12를 추가했다.
- 2템포·콜-리스폰스 라운드·고유 기술·인과 체인·위치 유지, 샷 팔레트 기본값, 존 기반 공간 지도, 패널 전 프리비즈와 구도 참조, 액션 B5 블록 압축, 레퍼런스 영상 실제 확인 규칙을 정했다.
- `scripts/action_lint.py`(AL00–AL10)와 액션 샷 표 양식을 추가하고 RED(7 실패)→GREEN(8 통과)로 회귀를 만들었다. 조연출·촬영·스토리보드·영상 프롬프트·제작 QA·벤치마크 SKILL에 포인터를 추가했다. 인덱스 CSV 열과 기존 게이트는 바꾸지 않았다. 수치는 운영 기본값이며 박진감 판정은 실제 패널/테이크 검수가 맡는다.

## 2026-11-27 — 사운드 소스의 프리프로덕션 전체 통합

- DES-11을 통합 정본으로 추가하고 감독·단계표·크루 명부·제작 QA·등록/인덱스·조연출·콘티/SND/QAR 양식을 연결했다. 단계별 설계와 확보 완료를 분리하고 generation_input 제출 차단과 post_only 후반 소스 납품 차단을 구별한다. 필수 근거 미확인을 2회 상한 뒤 잔여 위험으로 준비 완료 처리하지 않는다.
- 기존 AMB/SFX/MUS와 REF-* 및 consumes를 재사용해 권리 → 미디어 → 리뷰 → 소스 원장 → SND/소비자 등록 순서를 명시했다. 실제 source in/out·실측 여부·use_stage와 현재 cue/rights/review 핀을 소스 원장·콘티에 연결했다. 새 보드 필수 열·핀 문법·병렬 원장은 만들지 않았다.
- 설계 QA의 소유권 충돌을 수정했다: 조연출은 CNT/컷·발화 시간만 보정하고 감독이 APR/VPR을 각 소유 부서에 다시 배정한다. 실제 믹싱/최종 출력은 포스트 소유이며 이 작업에서 포스트 구현을 변경하지 않는다.
- 실제 등록 슬롯 누락을 RED 재현 후 CSV 양식에 반영했다. 파일 누락/해시 변화·권리/소스/리뷰 교체·현재 핀 갱신 순서 및 index_lint의 비재귀 한계를 실제 원장/임시 WAV로 검사하는 14개 회귀를 추가했고 전체 238개가 통과했다. 문서/일관성/패키지 검사와 등록 경로 read 결과는 통합 목표 evidence에 기록한다. 이 문서 변경에서 실제 사이트 순회·음원 다운로드·청취·개별 권리 승인·포스트 납품은 수행하지 않았다.

## 2026-11-27 — 프리프로덕션 스톡 사운드 탐색·확보

- 사용자 요청으로 sound-designer에 자료처 CSV 기반 실제 다중 사이트 검색·후보 청취/비교·개별 권리 확인·필요 파일 확보·큐별 포스트 인계 계약을 추가했다. 목록 추천만으로 소스 확보 완료로 처리하지 않는다.
- SND에 검색/선정·실제 파일 핀·권리 증빙/크레딧·Content ID·미해결 항목을 연결하고 검색 기록/소스 원장 CSV 양식을 추가했다. 실제 작품 데이터와 음원은 작품 프로젝트에 보관한다. 포스트의 배치·편집·믹싱 구현은 변경하지 않았다.
- 기존 CSV 50개 자료처(오디오 범주 35개)의 미검증 상태와 원본 해시를 보존했다. 등록 별칭의 상위 상대 경로가 read 도구에서 실패한 것을 재현하고 정본 절대 경로+coordinator 별칭 fallback으로 수정했다.
- 행동 사례 6개 검토와 경로 결함의 실제 read 도구 회귀(18개 정본 접근+6개 fallback), 기존 pytest 224 통과와 스킬 구조 findings 0을 확인했다. 실제 웹 탐색·청취·다운로드·개별 권리 승인·작품 인계는 이 문서 변경에서 수행하지 않았다. 검수/제한은 ../qa/sound-sourcing-validation.md에 기록한다.

## 2026-11-27 — 컷 간 연결 계약 보완

- 원인: CTY에 컷 시작·끝 상태는 있었지만, 편집상 선행 컷과 서사적 상태 기준·초기 출처를 나누는 필수 슬롯이 없어 교차편집·회상 설계에서 근거가 누락될 수 있었다. 기준선 에이전트는 손 변경 충돌 자체는 이미 발견했다.
- `docs/design/05-conti-collaboration.md` §4를 연결 계약 정본으로 확장했다. CTY·CNT·부서 레이어 양식과 7개 소비 스킬, QA2/QA3, 이미지 명세에 연결했다. 직전 이미지 첨부는 일괄 의무화하지 않으며 미생성 시 텍스트 설계를 허용한다.
- 기존 핀/CSV 문법을 유지한다. 실제 CTY 양식의 컷 앵커를 기존 원장·index_lint로 해결하고 누락/초안/무버전/구버전을 차단하는 회귀 5개를 추가했다. 자연어 문구 고정 검사는 최종 테스트에서 제외했다.
- 로컬 회귀 224 통과, 패키지 findings 0, 문서 errors 0, 일관성 inconsistencies 0. 행동 사례·최종 독립 검증은 `docs/qa/cut-continuity-contract-qa.md`에 실제 결과를 기록한다. 이미지 생성·시각 품질 검증·설치본 동기화·커밋/푸시는 수행하지 않는다.

## 프로젝트 이름 변경

- `contents-production-skills-v2` → `video-preproduction-skills`: 패키지 manifest·README·로컬 Git 저장소 디렉토리 이름 변경. 기존 커밋 이력과 개별 스킬 ID는 유지한다.
- 등록된 원격 저장소가 없으므로 GitHub 등 원격 저장소 이름 변경은 수행하지 않는다. 과거 증거의 이전 경로·이름은 당시 기록으로 보존한다.

## 설계 종료 스냅샷 — 미릴리스

- 사용자 지정 범위인 프리프로덕션·영상 프롬프트 설계에서 작업 종료. `docs/work-orders/DESIGN-CLOSEOUT.md`에 완료/미검증/재개 조건 기록. WO-15 실제 실행 및 릴리스 항목은 보존한다.
- v2 전용 로컬 Git 저장소와 최초 스냅샷을 마련한다. 아래 과거의 ‘Git 저장소 아님’ 기록은 당시 사실로 보존. v1 변경·설치·전환·원격 푸시 없음.
- 마감 검증: pytest 219 통과, 20스킬 구조 findings 0, 문서 errors 0, 일관성 inconsistencies 0. 원본 평가 기록의 Markdown 줄바꿈 공백과 CSV CRLF는 증거 바이트 보존을 위해 수정하지 않는다.

## 0.1.0 — 개발 중

- QA3 PNG·패널 순서·셀 매핑·검수 기록의 스냅샷 검사 추가. X-3의 실제 평가 인덱스로 사전 검사를 실행했고 시트 누락으로 차단됨. 합성 회귀는 실제 시각 검수를 대신하지 않는다.

- 에셋→콘티→보드/타임라인 기계적 인계와 소품 갱신에 따른 stale 전파를 합성 입력으로 검증했다. 콘티 공통 레이어 양식을 추가했다. Pillow 미설치 분기의 HTML 조립·캡션 이스케이프를 검증하고 같은 시트의 PNG/HTML 중복 출력을 막았다.

- WO-05–12 주요 산출물 양식과 개발·QA1 합성 평가 입력 추가. 파일 구조·마커 일치, 각본/정체성 헤딩 규약, 보드→시트→이미지 프롬프트 로컬 인계를 테스트했다. 인물 버전 변경 뒤 기존 시트와 프롬프트가 차단된다. 이 결과는 에이전트 행동이나 실제 생성 이미지 품질 증거가 아니다.

- **WO-04 구현 착수:** 감독 SKILL, 콜시트·납품·판정·연출 노트 양식, QA4 배치 제출 규약을 추가했다. 기존 단계표·판정 정본을 링크해 중복을 피했다. 자동 발동은 꺼져 있으며 감독 행동 평가와 공급자 실행은 미검증.

- **WO-01 로컬 골격:** 20개 SKILL.md, manifest, 구조 검사 SK01–SK07, 테스트 8건. 설치/행동 평가는 미실행.
- **WO-02 진행 중:** ID 파서에 이어 로컬 버전 원장과 `timeline_check` CLI를 구현했다. 결함판 30초는 말속도 차단 3건·경고 1건, 보정판 34초는 0건. `index_lint`와 제작 원장 스킬 안내까지 연결했다. 로컬 검사는 실행됐고, v1 이력 도구를 붙인 실제 운영은 미검증.
- **WO-03 착수:** 다국어 블록 마커, 인용문 추출, 공백 정규화 해시를 구현했다. `prompt_lint` CLI 1차 연결: 영상 구조·대사·말속도·고정 블록·금지/ID 검사 및 일부 오디오·모델 조건, 이미지 일부 검사. EX-02 시간표로 CLI 검증. 후속으로 자극 큐보다 앞선 반응(L9), 원장에 고정된 공통 기준 해시(L5), 이미지 인물·의상 정본(I1)을 연결했다. 컷별 카메라 축·조명과 시트별 인물 수·스타일도 원장 정본에 대조한다. 자유 서술 경고 규칙과 일부 명시적 글자 모순 차단, 두 GEN 공통 기준 회귀를 추가했다. 자유 서술의 의미 판정, 실제 이미지와의 일치, 큐 내부의 정확한 자극 시각은 남아 있다. EX-02 두 GEN(22초+12초) 프롬프트 및 배치 CLI를 테스트했다. 컷·대사·공통 핀 배정에서 차단 0건, 모델 사실 미검증으로 제출 불가.
- **운영 판정:** v2는 Git 저장소가 아니므로 요청 경로에만 저장했고 커밋하지 않았다. 골격은 자동 발동을 끄고 구현 전 설치 금지를 명시했다. 기존 말속도 계산 도구는 재사용하며 WO-02 타임라인 검사 통합 전에는 완료로 세지 않는다.

## Unreleased — set-piece ASL measured from references
- AL11 limit relaxed 1.6s -> 2.2s: measured reference ASL is 1.65s (transformation T1) and 2.09s (seal S1-B); the 1.6s value came from an eyeballed estimate. DES-12 §8 now says 1:1 reproduction follows the reference ASL.

## Unreleased — DES-13 execution safety
- Reuse the current brief, continuity and handoff notes. No global visual style default; reference comparison, timed previews and pilot generation are scoped to unresolved, applicable needs. Keep approval and final review gates.
- Separate visual style and voice direction; require per-stage reference inputs, source-shot mapping, native/post audio path, representative pilot, durable request keys and evidence-bound final review.
- Added execution-safety-template.json and pointers in seven departments. No provider calls or project media changed.
- Structural regression: 24 new checks (RED 24 failed before files/pointers; GREEN 24 passed); full suite 272 passed; check_skills findings empty. These are document/template checks, NOT independent agent-behavior or media-quality validation. Runtime enforcement remains unimplemented.
