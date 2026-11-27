# POSTPRODUCTION DESIGN — 독립 gate / builder QA 01

## 1. 판정과 범위

**판정: APPROVE — 고정된 설계 초안의 구현 계획 가능성에 한정.**

요구/제약을 구체적으로 위반하는 차단 설계 결함은 발견하지 못했다. 특히 마지막 보완 요구인 **필요 프로그램 탐지 → 정책 범위 내 설치·설정 → 실제 기능/보안 검사 → 원래 작업 재개**가 doc06에 실행 책임·도구별 경로·권한·복구까지 연결되어 있다. 단순히 문서가 추가됐다는 이유로 통과시키지 않았다.

- **신뢰도:** 문서 계약·추적 가능성은 높음. 실제 설치/편집/교환/지각 품질의 실현 가능성은 아직 미검증.
- **승인하지 않는 것:** 사용자 설계 승인, 구현/설치 착수 권한, 소프트웨어 실행 PASS, 미디어 품질·동의·권리의 실질 인증, 자동 게시 권한.
- **대상:** README + `docs/design/00`–`06` 7개 전부 + 연구 문서 2개, 합계 frozen 10개. 부모 QA 자료와 실제 이웃 production 계약을 추가로 읽었다.
- **독립성:** 이번 신규 검수자 1명이 직접 수행했다. 연구자를 설계 QA로 재사용하지 않았고 추가 위임/하위 에이전트 실행은 없다.
- **변경:** 이 라우팅 보고서만 작성. 설계·QA 원본·템플릿·CSV·기존 패키지는 읽기 전용이었다.

아래 `01:41`은 `docs/design/01-input-timeline-contract.md`의 41행을 뜻한다. 동일하게 00–06은 README의 문서 지도에 있는 설계 파일이다.

## 2. 요구·목표·제약·증거 매트릭스

| 요구/제약 | 설계 근거 | 독립 검토 결과 / 증거 한계 |
|---|---|---|
| 세 번째 패키지, production에서 받은 실제 소스의 후반 자동 실행 | 00:7–23, 27–35; 02:21–28 | 정본 결정과 실제 native 실행/산출물/QA를 연결한다. 편집 제안서만 반환하는 설계가 아니다. 이전 production 완료를 새 패키지 완료로 상속하지 않는다. |
| Craft CLI 기본, Adobe/Resolve는 작업별 선택 | 02:9–17, 34–49; 06:37–43 | 실제 CLI 셋의 차이를 보존한다. optional 도구나 FFmpeg를 기본 creative 실행자로 몰래 치환하지 않는다. |
| 필요한 프로그램이 없으면 설치·설정·시험·재개 | 06:7–31, 35–43, 73–83; 04:9 | `ensure_environment`, Installer Adapter, readiness와 설치 성공의 구분, 원래 work order 재개가 있다. 정확한 package ID/설치 flag를 검증 후 정하는 것은 합리적인 구현 책임이다. |
| 필요한 것만 설치, 유료/로그인/관리자/공유 환경/재부팅은 범위 확인 | 06:18–20, 28–31, 47–54 | 보통의 승인된 설치는 자동 수행하되 새 권한만 사용자에게 넘긴다. 현재 설계 보완 요청을 실제 설치의 포괄 동의로 취급하지 않는다. |
| 로컬 기본·미승인 전송/게시 금지 | 00:54–58; 02:53–55; 06:62–69 | AutoClip 첫 실행 전 차단, 설치됨과 real-media-ready 분리가 구체적이다. 네트워크 차단의 실제 유효성은 향후 시험 대상이다. |
| Handoff 부족분·handle0·없는 stem 보존 | 01:5–22, 46–49; 03:43 | 실제 모델/인계 코드와 일치한다. 필수 snapshot과 upstream 보완 입력을 별도로 받으며 raw 여유 프레임이나 가짜 stem을 만들지 않는다. |
| 정확한 시간·coverage·consumed dependency 현재성 | 01:30–35, 41–59; 04:22–26, 40 | source anchor/edit map, rational clock/sample/PTS, 실제 소비 optional의 current AND usable, 조건부 해소·현재 채택 CAS가 명시되어 있다. |
| 정본 namespace·단일 writer·공통 잠금/CAS | 01:26, 53–55; 02:61–67 | 이웃 `ProjectStore`의 실제 `.production.lock`/원자 publish/원문 bytes 검사와 연결 가능한 설계다. 새 독립 lock으로 같은 원장을 쓰겠다는 약속이 아니다. 확장은 아직 미구현이다. |
| 8개 역할·native 편집/교환/재수령 | 00:39–50; 01:35–37, 59; 02:44–49 | 8개 역할은 책임 구분이며 별도 에이전트 실행 권한이 아니다. readback·손실표·baked와 editable의 구분으로 무손실 왕복을 과장하지 않는다. |
| 템플릿/CSV 연구·폰트/권리·비파괴 | 03:5–31; 05:76–79 | 139파일/27정의·38 CSV 기록과 일치. 원본 바이너리 복사/배포가 없고 빈 licenseID나 폰트 fallback을 허락/동일 디자인으로 취급하지 않는다. |
| master/variant 분리·실제 전구간 QA·납품/권리/프라이버시 | 00:58; 04:14–18, 30–60 | 각 branch/profile/QA, 최종 파일 시청·해당 청취, 필수 납품물/권리/attribution·민감정보 제거가 있다. 실행자 성공이나 preview PASS만으로 release하지 않는다. |
| 증거 수준·미실행을 솔직히 표시 | 05:5–15, 70, 93; README:28–32 | Craft E1/E2, 외부 정적 자료 E0, E3/E4 미실행과 P01–P50 전부 UNVERIFIED를 구별한다. 본 판정도 runtime PASS가 아니다. |

## 3. 대표 시나리오 추적 — 문서 검증, 실제 실행 아님

### S1. 승인된 다중 소스 → Craft master → editable 납품

Handoff에 전체 요구/LOOK이 없으므로 **01:16–22의 snapshot·upstream pin·delivery profile**을 먼저 결속한다. PG-E 준비 후 PG0 기술/권리 검사, PG1 편집 승인, 01:30–35의 정본 ID/계보와 native mapping을 만든다. FilmCraft readback과 오프라인 검사를 거치고, EffectCraft plate는 검증한 alpha/색/길이 계약으로, SoundCraft는 실제 음원과 sample offset으로 교환한다(02:44–49, 57). PG2–PG6에서 현재 결과를 검수하고 editable 의존성/권리·손실 목록까지 닫아야 완료다(04:9–18, 46–60).

**결론:** 범용 왕복이나 stem을 상상하지 않고 계획할 수 있다. 정확한 교환 포맷은 fixture에서 검증 후 허용한다는 명시적 경계가 있다.

### S2. 필요한 Craft CLI 없음 / launcher만 있음

필요 기능을 결정하고 app과 별도 CLI를 각각 탐지한다. launcher만 있다고 준비 완료가 아니며 필요한 앱/CLI만 provision한다(06:26–29, 37). 정책 안의 무료 설치는 자동, 관리자/로그인 등 새 조치만 요청한다(06:47–54). binary/version·native smoke·독립 decode/egress 확인 후 ready를 부여하고 원래 입력/권한/capability를 다시 고정해 재개한다(06:75–83; P41/P42/P50).

**결론:** “missing tool”에서 종료하는 이전 문제를 실질적으로 해결한 설계다. GUI 또는 설치 관리자 exit0만으로 자동 진행할 수 없다.

### S3. 승인 master의 AutoClip 파생 숏폼

선택된 작업에 필요한 경우에만 격리 Desktop/CLI/container 경로를 준비한다(06:38). 첫 실행 전부터 외부 전송을 막고 실제 기밀 미디어를 연결하지 않는다. diagnostics/media/analytics/crash/cloud/publish를 각각 검토·설정하고 비기밀 fixture와 실패 경로를 시험해야 real-media-ready가 된다(06:62–67). master 승인과 별개 branch/profile/의미·자막·재구도 QA 및 채택이 필요하다(00:58; 04:48, 58–60).

**결론:** 설치 허용을 진단 전송/클라우드/게시 동의로 바꾸지 않는다. 정적 default-on 위험은 근거가 있지만 실제 유출 관측으로 서술하면 안 된다.

### S4. Resolve가 필요한 finishing 작업

OS/arch/GPU/driver·Free/Studio·등록/배포 조건을 확인하고 공식 경로로 설치한다. 사용자만 할 수 있는 입력·약관·키·관리자/재부팅은 해당 단계만 넘기고 검증 뒤 재개한다(06:39, 47–54). scripting/headless/remote/codec은 정확한 판본의 실제 시험으로 capability를 부여한다. 앱 설치로 불지원 API가 지원된다고 하지 않는다(06:75–76; 02:48).

**결론:** 연구의 Blackmagic 404를 API 부재나 지원 성공으로 잘못 확정하지 않는다. 실제 불지원 환경만 구체 상태/승인 대안으로 돌린다.

## 4. 경계·실패·동시성 반증 추적

| 경로/구체 실패 시나리오 | 설계에서 강제하는 처리 | 판단 |
|---|---|---|
| E1. installer exit0이나 CLI 누락/첫 export 실패 | 06:29, 75–76; P50: installed와 ready 분리, 해당 기능 시험 실패 상태 유지 | 경로 있음; 실행 미검증 |
| E2. AutoClip failed/partial가 진단 excerpt upload를 유발 | 06:64–67; P39/P47: 첫 실행 전 차단, 실패/로그까지 비기밀 egress 시험, 보장 못 하면 real-media-ready 금지 | 경로 있음; 실제 차단 미검증 |
| E3. 두 작품이 같은 전역 runtime을 설치하며 package lock과 충돌 | 06:78–80: host/tool lease와 실제 package-manager lock 모두 존중, 선행 설치 재탐지, 타 lock/process 삭제 금지 | 프로젝트 JSON lock만으로 전역 설치를 보호한다고 하지 않음 |
| E4. 설치 timeout/재부팅 후 성공 여부 불명, 부분 변경 존재 | 06:77–81: receipt/resume point, 현재 package/binary/process/transaction 대조 후 소유 변경만 원복·repair·재개 | 무조건 재설치/공유 환경 삭제 금지. 구체 transaction 구현은 builder 책임 |
| E5. post/production 동시 저장 또는 준비 후 원문 bytes 변경 | 01:53–55; 04:40; P22/P23: 동일 lock seam, namespace 보존·revision/CAS·원문 conflict 검사 | 실제 store.py:44–66, 73–87, 184–200과 연결 가능. legacy `_save` 동시 사용은 지원하지 않음 |
| E6. 24000/1001 영상·48k audio, trim/retime/VFR로 cue가 밀림 | 01:41–45; 03:36, 45; P06/P07/P30: rational/PTS map·sample clock·반올림/누적 오차·자막 stale | upstream float나 SRT ms를 정본 clock으로 쓰지 않음 |
| E7. 선택한 optional source가 stale/invalid, 조건부 imports 충돌 | 01:55–58; 04:22–26, 40; P24/P25: 실제 소비 핀 current AND usable 검사, 과거 binding 보존, 미해소 fix/현재 채택 차단 | 미소비 optional 양성 경로와 구별됨 |
| E8. handle0에서 dissolve, 일부 trim 또는 overlay/음악으로 필수 사건/대사 소실 | 01:46–49; 04:26; P05/P08/P09: anchor 없으면 전구간 유지, 범위 내 overlap도 승인·재검수, 가시성/가청성 실패는 coverage 실패 | 범위가 남았다는 이유로 의미 보존 PASS 불가 |
| E9. 사람이 native 효과를 추가했으나 정본에 표현 불가, export는 성공 | 01:35, 59; 02:49; 04:30, 50–54; P13/P17: 재수령 pending, 지원 결정 수입 또는 정본 확장/승인 baked 계보, 손실·editable 계약 대조 | 손실 없는 round-trip으로 위장할 경로 없음 |
| E10. render timeout 후 job은 살아 있음 / preview 이후 최종 audio 누락 | 02:61–67; 04:14–18, 30–42; P20/P21/P35/P36: unknown 관측·중복 금지, 관측 사실 보존, 최종 파일 기술/전구간 QA 별도 | historical success와 current release가 분리됨 |
| E11. 세로 variant 자막이 얼굴 가림, 재배포 불가 font 또는 credentials가 납품에 섞임 | 03:20–23, 31, 38; 04:16, 33, 50–54, 58–60: variant별 검수·권리/attribution·패키지 민감정보 제거 | master 통과가 variant/권리/프로젝트 completeness 통과를 대신하지 않음 |

위 경로는 **설계상 처리 가능 여부**를 독립적으로 추적한 결과다. P 사례를 실행하거나 실패 주입한 결과가 아니다.

## 5. grounded gate findings

### 차단 이슈 — 우선순위순

**없음.** 인용 가능한 목표/제약 위반과 구체 실패 시나리오를 함께 충족하는 REJECT 사유를 찾지 못했다. 설계만 있는 단계에서 구현/실제 렌더/실제 설치 시험이 없다는 사실 자체를 결함으로 올리지 않았다.

### 비차단 관찰 및 남은 위험

아래는 수정이 필요한 설계 결함이 아니라 이미 설계가 공개한 검증/승인 경계다. **설계 수정 요구 0건**이다.

| 중요도 / 위치 | 구체 시나리오 / 남은 위험 | 필요한 최소 후속조치 / 분류 |
|---|---|---|
| 높음 · 02:15, 44–49; 05:8–11, 58 | alpha/pre-alpha Craft가 실제 export·alpha·audio offset/색 교환을 만족하지 못할 수 있음 | 계획에 해당 E3 fixture와 E4 통합 gate를 유지. 검증 전 capability 승격 금지. **answered-by-existing-docs** |
| 높음 · 06:62–67 | 설치 release가 조사 SHA와 다르거나 실패 진단이 다른 전송 경로를 가질 수 있음 | 정확한 release/설정/차단·실패 경로의 실제 시험 후 real-media-ready. 연구의 정적 확인을 런타임 무전송 보증으로 재사용 금지. **answered-by-existing-docs** |
| 중간 · 01:53–54; 06:78–80 | 실제 lock/transaction 구현이 독립 writer나 타 installer와 안전하게 공존하지 못할 수 있음 | 공통 ledger seam과 host/package lock을 실제 경쟁/중단 fixture로 증명. lock 순서/receipt 저장 형식은 제약을 만족하는 **reasonable-builder-choice** |
| 높음 · 04:18, 36; 05:87–91 | 프로젝트의 실제 권리·납품 profile·지각 QA 수단 또는 설치 권한이 아직 없을 수 있음 | 지정된 설계 승인/구현 권한/프로젝트 intake에서 받기. 값을 추측해 PASS하지 않음. 사용자 입력은 필요하나 **이미 수집 시점이 정의된 항목**이며 이번 설계의 미결 질문이 아님 |

## 6. 부모 QA 증거 감사와 독립 재현

### 실제 수행한 읽기 전용 검사

1. `sha256sum qa/design/draft-scope.sha256` 및 `sha256sum -c qa/design/draft-scope.sha256`: 시작 시 manifest 기대 SHA와 **10/10** 일치.
2. Python 표준 라이브러리 인라인 검사: manifest/10개 hash, local Markdown target 존재, 역할/사례 ID, 보호 입력 SHA, template inventory/definition SHA, CSV 파싱, CLI binary SHA와 저장 metadata 수, 부모 matrix 범위, 현재 파일 inventory를 대조했다. 파일 출력/외부 호출/기존 패키지 import는 하지 않았다.
3. `nl -ba`/`sed`/`rg`/`cat`으로 설계·연구·QA 자료, 실제 `../video-production-skills/production/{models,handoff,store}.py`, 설치본 `/usr/share/doc/{filmcraft,effectcraft,soundcraft}/README.md`의 해당 계약을 읽었다. CLI/GUI는 실행하지 않았다.

| 부모 항목 | 독립 재현/감사 결과 | 의미 / 주장하지 않는 것 |
|---|---|---|
| Q01 frozen integrity | manifest SHA `28f273f73131f75ac05d3d14ce36528212e0fd3300308be78a91c6cd24ed153e`; 10/10 일치 | 해당 snapshot 식별·동일성. 문서가 옳다는 증명 아님 |
| Q02 local links | frozen 문서의 local inline target 및 절대경로 reference **27개, missing 0** | 존재 검사만. 외부 URL live 성공/본문 품질/의미 적합성 검사 아님 |
| Q03 역할/사례 | 역할 **8 unique**; **P01–P50 정확히 50개**, 실행 0 | 명세 inventory. 50개 runtime 테스트 PASS 아님 |
| Q04 보호 원본 | **216/216 SHA 일치** = template139 + CSV1 + production76 | baseline 대상 보호. 시스템 전체 무변경 감사 아님 |
| Q05 CLI 증거 | binary3 SHA 일치; 저장 unique command IDs **718/766/483** 일치; 저장 help와 recorded exit0 확인 | 이번 reviewer는 help/metadata도 재실행하지 않음. recorded exit가 현재 성공했음을 증명하거나 native 실행을 인증하지 않음 |
| Q06 비구현·바이너리 미복사 | 현재 프로젝트 **27개 텍스트 artifact**, runtime/installer/template media binary 없음 | `inventory-at-qa-01.txt`는 시점별 목록이며 전체 시스템의 변경 이력 증명 아님 |
| Q07–Q12 trace | `manual-trace-01.md`의 설치/AutoClip/사람 조치/consumed optional/Handoff/최종 QA trace를 읽고 위 S1–S4/E1–E11로 별도 반증 추적 | 문서 경로·불변식 확인에 한정. 설치/보안/영상 품질의 실제 실행 PASS 아님 |

추가 대조:

- template 실제 **139 files = PNG43 + JPG9 + MP4 27 + prgraphic27 + JSON27 + MOGRT6**, 저장 27 definition hash 일치. 새 시각/동영상 재생 검수는 하지 않았다.
- CSV를 UTF-8 BOM 인식 CSV로 파싱해 **38 data records + header**, 번호1–38 확인. CSV 링크를 실행/계정 접근하지 않았다.
- `models.py:109–125,154–160,322–332` 및 `handoff.py:75–104`를 직접 확인했다. Handoff는 full 요구/LOOK 계약이 아니고 실제 builder가 exterior handles를 0으로 만든다. `build_handoff`의 검증 성공을 후반 full probe/decode나 지각 검수로 바꾸지 않았다.
- 설치본 README의 Craft alpha/pre-alpha, FilmCraft `.prproj` 미지원, SoundCraft AAF/OMF 미구현, EffectCraft 독점 프로젝트/AE SDK plug-in 미지원이 설계의 보수적 경계와 일치한다. 문서 설명은 native 시험이 아니다.
- `autoclip-parent-source-check.json`의 고정 SHA/consent·service·upload 발췌는 연구의 default-on·내장 endpoint 위험 설명과 정합적이다. 보고서 전체 원문 fetch를 재현하지 않았고 실제 upload/차단/서버 삭제를 관측하지 않았다.
- `manual-qa-01.json` Q01–Q12 PASS는 `surface: design artifacts and source/evidence consistency only`, runtime0, render 미인증과 일치한다. 이를 전체 구현 PASS로 확대하는 근거는 없다.
- `self-check.json`의 `new_reviewer_authorized:false`, `independent_design_reviewed:false` 및 README의 독립 검수 미완료 표기는 **이번 신규 검수 전 frozen 상태**다. 이번 명시적 QA 요청을 부정하는 현재 권한 판정으로 해석하지 않았고 원본 상태를 수정하지 않았다.

### 마지막 무결성 대조

보고서 작성 후 `sha256sum qa/design/draft-scope.sha256`, `sha256sum -c qa/design/draft-scope.sha256` 및 Python SHA 재대조를 수행했다. **manifest 기대 SHA 불변, frozen 10/10 OK, 보호 baseline 216/216 불변, CLI binary 3/3 불변**이었다. 시작/종료 모두 같은 snapshot이며 라우팅 한국어 보고서의 존재·APPROVE 표기도 확인했다. 모든 검증 명령은 성공 종료했다.

## 7. builder check — 저자에게 묻지 않고 계획할 때의 질문

**nothing important left — 구현 계획을 materially 바꿀, 문서만으로 해결되지 않는 중요한 저자 질문은 남지 않았다. 순위화할 미결 질문 0개.**

확인하려던 쟁점의 분류는 다음과 같다. 아래는 추가 질문 목록이 아니다.

1. **answered-by-existing-docs:** 앱 없음/launcher만 설치됨, AutoClip 첫 실행 전 egress, Resolve 판본/OS/등록/관리자, installed vs ready, 조건부·actual-consumed 현재성, native 손실/최종 QA. 해당 답은 §2–4에 인용했다.
2. **reasonable-builder-choice:** 검증된 설치 recipe/package ID와 버전 탐색, 정본 스키마의 구체 필드 타입, lock ordering/fixture 구성, 실제 지원이 확인된 교환 포맷. 사용자에게 새로운 정책을 발명하지 않는 범위에서 builder가 결정·증명할 수 있다.
3. **needs-user-decision, 단 이미 명시된 후속 gate:** 설계 승인·구현/fixture 실행 권한, 실제 설치 정책의 범위, 작품별 DeliveryProfile/권리/수령자/지각 QA 수단. 05:87–91과 06:28,47–54에서 수집 시점과 권한 경계가 정해졌다. 지금 특정 값이 없다고 설계 blocker나 저자 미응답 질문으로 중복 등록하지 않는다.

## 8. 결론과 다음 단계

**APPROVE (설계 한정).** 부모는 이 독립 보고서를 사용자에게 제시하고 설계 승인을 받은 뒤, 문서가 정한 별도 구현 계획/권한 gate로 진행하면 된다. 실제 설치·편집·렌더·무전송·round-trip·전구간 시청/청취·권리 수락은 이 보고서로 통과하지 않는다.

금지 작업 미수행: 설계/프로젝트 QA 수정, 설치/업데이트/모델·폰트·바이너리 다운로드, GUI/CLI 편집·렌더·ASR·생성, provider/media upload, 구매/로그인/게시, Git/worktree 명령·초기화·stage, 추가 reviewer/연구자 위임 모두 0. 비Git 프로젝트임을 `.git` 경로 부재로 확인했으며 Git index/staged 목록을 조회했다고 주장하지 않는다.
