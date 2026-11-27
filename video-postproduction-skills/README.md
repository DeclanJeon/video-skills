# video-postproduction-skills — 포스트프로덕션

로컬 후반작업 구현. 최신 상태·기준별 검증은 `.ultragoal/goals/active/implement-postproduction-design/goal.md`를 따른다. 사용자 `응 진행해`로 부모 직접 구현과 새 최종 독립 검수자1명을 승인받았다. 새 설치는 별도 실제 질문/동의가 필요하다. 이전 production/설계 PASS를 이번 구현 완료로 재사용하지 않는다.

이전 전체 체크포인트는 **Task11 404 tests passed/type0/보호216/216**다. 해당 source의 독립 검수01은 NOT APPROVED였고, branch-content/portable scope/audio codec/attribution/current-variant progress 결함의 회귀 테스트와 수정이 뒤따랐다. 이전 통과 수를 수정 후 전체 회귀나 독립 승인으로 재사용하지 않는다. 이후 현재 QA·로컬 master/editable 납품·수령 revision·분모·CLI·8역할·14개 runtime schema/manifest/예시·검사기를 추가했다. 신규 targeted 결과와 새 whole-suite 결과는 `qa/implementation/` 및 Goal 검증 log에서 구별한다. 이후 실제 conditional 수정의 master-consumption, export warning/result 경로, 준비 비변경·중간 native/원장 쓰기 장애, 명시 LUFS/true-peak와 native clean branch·개별 QA/계보·6개 native 프로젝트 editable 재개방을 보강했다. 52개 사례의 실제 pytest 연결은 행별 증거 범위이며 지각/신규 vendor 설치 미확인은 완료로 세지 않는다. [로컬 entry](SKILL.md)와 [운영·검증·제약](docs/operations.md)을 따른다. 글로벌 등록/배포는 하지 않았다.

Retained review02는 **NOT APPROVED**: source239/전체423 통과에도 raw finishing packet/order 결속과 실제 portable install/recovery inventory 전달이 남았다. 부모가 공통 admission(prepare/dispatch/current QA)과 실제 driver-produced/recovered payload→native smoke를 보강했다. 새 전체 검증·같은 검수자의 재검수 전에는 완료/독립 승인을 주장하지 않는다. 실제 vendor 다운로드/신규 설치는 하지 않았다.

## 확정한 방향

- 사용자가 자동 실행 중심을 선택했다. 승인된 범위의 반복 편집은 자동화하고 주요 편집 의도·권리/전송/비용·최종본 채택은 승인 게이트로 둔다.
- 기본 실행자는 **FilmCraft / EffectCraft / SoundCraft의 별도 CLI**다. 먼저 시스템/동일 프로그램을 점검해 재사용하고, 설치가 필요하면 사용자에게 묻고 동의 후 설치·의존성 설정→실행 검증→작업 재개를 수행한다. Premiere / After Effects / DaVinci Resolve도 선택된 작업에 필요하면 같은 준비 경로를 따른다.
- AutoClip과 링크 목록은 후보 조사 대상으로 사용한다. AutoClip은 현재 설치하지 않았으며, 승인 마스터의 파생 숏폼 후보 모듈로만 검토한다.
- `/home/declan/Documents/쇼츠템플릿`은 비파괴 참고 자료다. 모델 훈련·원본 변경·템플릿 바이너리 재배포가 아니라 콘셉트/배치/자막 모션 규칙을 연구한다.

## 문서 지도

| 문서 | 소유 내용 |
|---|---|
| [00 목표·구조·역할](docs/design/00-overview.md) | 단계 분리, 선택한 접근, 8개 제안 역할, 승인 범위 |
| [01 수령·편집 정본](docs/design/01-input-timeline-contract.md) | 실제 production Handoff의 보완 입력, coverage/시간/원장/계보 |
| [02 실행자와 실제 지원](docs/design/02-backends-and-execution.md) | 확인된 CLI, 서로 다른 프로토콜, 작업/세션 격리와 복구 |
| [03 자막·템플릿·음향·룩](docs/design/03-craft-and-templates.md) | 139개 참고 파일, 27개 자막 정의, 라이선스/폰트/안전영역 |
| [04 검수·마스터·납품](docs/design/04-gates-and-delivery.md) | 단계 게이트, 조건부 결함 해소, 유효성·진행률·인계 |
| [05 수락 사례·미확인](docs/design/05-validation-and-decisions.md) | 계획된 52개 사례, 검증 표면, 남은 승인 |
| [06 환경·자동 설치](docs/design/06-environment-and-installation.md) | 미설치/비호환 탐지, 설치·설정·기능 검증·복구와 재개 |
| [로컬 조사 근거](docs/research/local-discovery-01.md) | 실제 설치본 help/metadata, 템플릿 관찰과 제한 |
| [외부 참고 조사](docs/research/reference-research-01.md) | AutoClip, CSV 38개 기록 선별, 9개 후보 공식 자료 |
| [현재 로컬 운영](docs/operations.md) | 실제 CLI, 지원 범위·복구·QA·납품·검증/미완료 |
| [실행 사례 연결](docs/acceptance-map.json) | P01–P52의 exact node/scopes/unverified. 연결은 전체 사례 완료가 아님 |

원본 입력/CLI 근거는 `qa/design/`에 보관한다. 템플릿 이미지·영상·MOGRT 자체는 이 패키지에 복사하지 않는다. 기존 제작 패키지/공유 도구/작품 프로젝트는 변경하지 않는다.

## 현재 검증 수준

- 확인: 세 CLI 도움말/metadata 조회, 설치 패키지 버전, 참고 파일/정의 inventory, 일부 대표 이미지 직접 관찰, 공개 소스 정적 조사.
- 추가 확인: 실제 synthetic 로컬 source/review-only 파일의 probe/full decode, rational 24000/1001, 실제 mux audio fixture에 대한 target sample map. fixture의 semantic/listening 필드는 보고된 시험값이지 실제 인간 시청·청취 인증이 아니다.
- 실제 Native 추가 확인: FilmCraft의 작은 비기밀3-cut 프로젝트 import/edit/readback/CPU export→독립144-frame24fps160×90 decode와 RGB 순서. Native API test에서는 stale source/native range/partial file/replay/transcript failure를 거절했다. EffectCraft의 실제12-frame RGBA/linear position Adapter와 독립 alpha/bounds 검사, SoundCraft의 실제 mono/stereo sample-offset/gain/mix/bounce 및 완전한 독립 waveform 비교도 초기 기술 계약을 통과했다. Native mix 성공은 청취/최종 마스터 PASS가 아니다.
- 추가 구현: 실제 native picture+12 motion+24 literal text PNG+SoundCraft WAV를144-frame master에 결합하고 전체 video/pixel/AAC waveform 대조, current QA/로컬 checksum bundle 및 실제 다섯 native 프로젝트의 세 앱 relink/reopen을 시험했다. reported semantics는 technical_fixture다. 전체 CLI의 실제 prepare→run→observe/재시작 거절과 8역할 문서·schema/examples의 deterministic 검사도 추가했다.
- 미확인: 실제 전구간 인간 시청/청취·작품 채택/법적 권리/설치 응답 발급자 진위, 임의 grade/LUT/native retime/conform·보편 교환, AutoClip 무전송 실행, 신규 벤더 설치와 최종 독립 구현 검수. 행별 전용 보강은 acceptance map/운영 문서에 명시했다. 설계 문서의 ‘아직 미구현’은 설계 시점 기록이며 현재 상태는 이 README/Goal/운영 문서를 따른다.
- 환경 기반: 실제 PATH/package DB/desktop/known locations/CLI file을 읽기 전용 대조해 세 기존 Craft를 reusable로 판정했다(ready는 false). 질문 초안과 실제 질문/응답 record를 분리하고 host/plan/의존성·위치·권한·네트워크·비용 변경을 거절한다. 임시 installer/아카이브/mock HTTPS 시험은 실제 벤더 설치나 실제 사용자 동의 인증이 아니다. 실제 bwrap0.11.1의 network namespace에서 `/usr/bin/true` 실행을 확인했다(앱/미디어 실행 아님).
- 초기 편집 경로는 source당1개 cut/CFR/identity playback이며 명시 승인과 관측 anchor 없는 trim/overlap, 외측 handle, 미검증 retime/conform/stem은 차단한다. 일부는 후속 작업에서 확장한다. 현재 로컬 CLI/disabled-auto-invocation 8역할/14개 public schema/manifest는 구현했고 전용 검사기로 대조한다. 에이전트 행동 pressure/compliance 시험은 미실시이며 deterministic 계약 검증과 구별한다.
- 계획/추적: `docs/superpowers/plans/2026-11-26-postproduction-implementation.md`, `.superpowers/sdd/2026-11-26-postproduction-implementation/progress.md`, `.ultragoal/goals/active/implement-postproduction-design/goal.md`. Git 생성·스킬 설치·배포·실제 신규 프로그램 설치는 하지 않았다.
