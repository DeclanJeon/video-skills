# 실행 정본과 증거

## 범위와 소유권
이 패키지는 로컬 source→edit→native→QA→delivery를 다룬다. 한 프로젝트의 총괄 한 명만 기존 JSON의 `postproduction`을 commit한다. 분야 역할은 변경안과 실제 관측을 반환한다. 역할 문서 읽기는 별도 에이전트 실행·설치·전송·게시 권한이 아니다. 기존 production/foreign 필드와 원본을 유지한다.

## 환경과 설치
1. `python3 scripts/postproduction.py inspect-env`로 시스템·동일 프로그램의 CLI/PATH/package/desktop/알려진 위치를 대조한다. adequate이면 재사용한다. `unknown`은 미설치가 아니다. `reusable` metadata는 native E3/작품 PASS가 아니다.
2. 신규 프로그램/폰트/모델/plugin/dependency가 필요하면 정확한 호스트·버전·원본 URL/hash·의존성·위치·권한·network·비용·license·원복 계획의 `InstallationPlan`을 만든다. `install-plan PLAN.json`은 질문 **초안**이며 실제로 물은 기록이 아니다.
3. 실제 사용자에게 질문하고 정확한 계획에 대한 명시 동의를 받는다. 현재 CLI의 vendor `install PLAN.json`은 interactive TTY에서 전체 질문과 정확한 digest 응답을 요구한다. goal/free-policy/`--yes`/다른 host·plan 응답은 동의가 아니다. 미동의 상태에서는 download-for-install도 실행하지 않는다.
4. 동의 후 bounded adapter/host-tool lease/사실 선영속/격리 native smoke로 설치와 ready를 구분한다. callback 실패·timeout/unknown은 원본 journal/경로를 보존하고 `InstallRecovery`의 실제 process/files/source audit 후에만 재개한다. 새 계획은 다시 질문한다. 기존 사용자 파일/프로세스/manager lock은 보존한다.

## 실제 로컬 경로
`python3 scripts/postproduction.py --help`가 현재 CLI 인자 정본이다.

- `intake PROJECT.json --request request.json`: 실제 pinned Handoff/snapshot/schema/brief/profile/authority와 소스/승인/범위/커버리지를 수령한다. 변경된 수령은 `--revision`의 `IntakeRevision`으로 과거 기록을 보존한다.
- `plan`은 명시한 `EditProposal`을 검사하고 `--commit`일 때만 승인 범위에서 기록한다. main/variant 요구 분모를 별도로 유지한다.
- `prepare PROJECT.json ORDER.json` → canonical reservation 출력. `run PROJECT.json JOB-ID` → 실제 앱. `observe PROJECT.json JOB-ID` → current native readback/full decode/실제 파일의 materialization. `--facts-only`는 역사적 사실 읽기이며 신규 dispatch 권한이 아니다.
- `review PROJECT.json REPORT.json` → exact final-file `QualitySubmission`의 PG-E/PG0–PG6 계산. `deliver PROJECT.json CONTRACT.json` → current QA·권리·receiver·모든 필수 파일을 다시 검사하고 로컬 no-clobber bundle을 만든다. 실제 외부 업로드 기능은 없다.
- `invalidate`/`progress`: 실제 consumed pin/producer lineage만 전파하고 source·작업·coverage·fix·전구간 QA·납품 분모를 구별한다.

## 증거 경계와 한계
`dispatching/running/unknown/succeeded`, 실제 materialized 파일, current artifact, 보고된 QA와 formal adoption은 별개다. export0/metadata/contact sheet는 시청·청취 PASS가 아니다. `technical_fixture`는 synthetic 기술·보고된 의미 계약 시험이며 실제 인간/권리 발급자 진위 인증이 아니다. `reported`도 외부 보고의 scope/hash 일치를 검사할 뿐 진위를 인증하지 않는다.

실제 확인한 native 경로는 같은 geometry/CFR hard cut H264 MP4, native RGBA solid/text/linear keys, WAV/cue/stereo native mix, 실제 per-frame PNG+mix 재결합과 로컬 세 앱 relink이다. VFR/nonidentity retime/다른 format/Adobe MOGRT 호환/필요 모델·plugin·미확인 egress를 지원으로 꾸미지 않는다. 필요한 기능/입력이 없으면 정확한 `needs_user_action/unsupported/unverified`와 소유자·다음 조치를 반환한다.

## 반환 계약
역할, project/branch/revision, consumed pins와 범위, 결정/실행/관측의 구분, 실제 command/job/resource/output 증거, currentness와 gate 상태, 미해결/권리·설치 질문을 반환한다. artifact만으로 story/청취/게시 완료를 선언하지 않는다.
