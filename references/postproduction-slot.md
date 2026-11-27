# 프로덕션 → 포스트 연결 계약

## 정본과 적용 조건

현재 포스트 진입점은 [video-postproduction-skills/SKILL.md](../video-postproduction-skills/SKILL.md)이며 [후반 총괄](../video-postproduction-skills/postproduction-supervisor/SKILL.md)이 후반 상태를 소유한다. 요청에 후반작업이나 최종 영상이 포함되면 이 파일들을 실제 지침으로 읽는다. 자동 호출 금지 플래그는 유지한다.

실행 절차·지원 범위·권한은 포스트의 [references/execution-contract.md](../video-postproduction-skills/references/execution-contract.md), [운영 문서](../video-postproduction-skills/docs/operations.md), 현재 CLI `--help`와 [schemas](../video-postproduction-skills/schemas/)가 정본이다. 이 연결 계약은 별도 후반 구현이나 범용 입력 변환기가 아니다.

## 1. 프로덕션 G5와 실제 수령자

프로 총괄이 현재 [G5 구현](../video-production-skills/production/handoff.py)과 [운영 계약](../video-production-skills/docs/operations.md)을 적용한다. 실제 source/approval 파일·범위·selection revision/hash·coverage·접합 및 전체 흐름 재생/해당 오디오 청취·권리·receiver를 확인한다. 조건부 결함은 실제 수령자가 인수한 범위와 수리 책임을 유지한다.

사용자가 승인한 실제 작업 수령자를 receiver로 사용한다. 폴더 이름·슬롯·오케스트레이터 이름만 넣어 수령 근거를 만들지 않는다. G5 Handoff 생성과 포스트 intake 검증은 별도 판정이다. G5가 막히면 sources_ready 여부와 정확한 결함·다음 조치를 반환하고 handed_off로 승격하지 않는다.

## 2. 후반 입력과 원장 경계

후반 총괄이 현재 [IntakeRequest](../video-postproduction-skills/postproduction/intake_models.py)와 [실제 intake 검증](../video-postproduction-skills/postproduction/intake.py)을 읽고 작품 입력으로 요청 파일을 작성한다.
- 고정된 production Handoff, 불변 production snapshot, 실제 production model schema pin.
- 편집 brief, 출력/branch/자막/음향/납품 profile, 유효한 편집 authority와 source 승인.
- full original 요구 분모, 정확한 source/take/range/revision/hash, 필수 upstream 자산·별도 stem·권리 근거.
- 실제 receiver, 조건부 결함의 인수·해소 계약, 요청한 master-only/editable 및 필수 variant/native/font 범위.

단독 Handoff나 임의 MP4 목록만으로 수령을 통과시키지 않는다. 현재 초기 경로가 지원하지 않는 exterior handle/retime/format/세로 reframe 등을 지원으로 꾸미지 않는다. 예제 fixture의 승인·소스·QA를 작품 데이터로 복사하지 않는다.

프리는 ledger.json, 프로는 별도 production-ledger.json을 유지한다. 포스트는 기존 프로젝트 JSON의 postproduction namespace만 후반 총괄이 단일 writer로 commit하며 production/foreign 필드를 보존한다. 실제 프로젝트 상태 위치는 기존 작품 링크에서 확인한다. intake용 snapshot은 mutable 상태 파일과 분리된 불변 핀으로 준비하고, 프로젝트와 snapshot 경계는 실제 intake 검증을 따른다. 같은 내용을 담은 병렬 상태 원장을 새로 만들지 않는다. 프리 writer를 프로/포스트 정본에 적용하지 않는다.

## 3. 실행과 다음 단계

포스트 디렉터리를 기준으로 `python3 scripts/postproduction.py --help`와 해당 명령의 도움말을 먼저 확인한다.
1. `inspect-env`: 기존 시스템·동일 프로그램을 점검하고 충분하면 재사용한다. unknown은 미설치 판정이 아니다. 새 프로그램/font/plugin/model/dependency 설치는 정확한 계획에 대한 실제 사용자 명시 동의 후에만 수행한다.
2. `intake PROJECT.json --request REQUEST.json` → `validate PROJECT.json`: 현재 입력·승인·범위·전체 요구를 실제 검증한다. 재수령은 실제 IntakeRevision으로 과거 상태를 보존한다.
3. `plan`: 명시한 EditProposal을 검사하고 승인 범위에서만 commit한다. 분야 지침은 포스트 entry가 연결한 파일을 읽고 변경안·관측을 후반 총괄에게 반환한다.
4. `prepare` → `run` → `observe`: 명시 WorkOrder, 실제 지원 Craft, 실제 job/native readback/full decode/출력 핀을 대조한다. 예약·성공 메모·렌더 파일 존재와 현재 materialization/QA/채택을 구분한다.
5. `review`: 정확한 최종 파일에 대한 PG-E/PG0–PG6, 전구간 시청·청취, coverage·조건부 결함·권리·현재 계보를 검증한다.
6. `deliver`: current QA·receiver·권리·필수 main/variant/mix/stem/native/font와 bundle hashes를 다시 확인하고 로컬 no-clobber 납품을 수행한다. 외부 업로드·게시를 포함하지 않는다.

기존 유효한 승인은 재사용하고 통상 단계 전환을 다시 묻지 않는다. 실제 도구 부재/미지원·누락 입력·필수 승인·현재 QA 실패에서만 해당 조치를 요청한다. unknown/live/이미 완료한 job은 process/files/journal 대조 없이 재실행하지 않는다.

## 4. 반환과 완료

현재 프로젝트/branch/revision, 실제 명령·job·source→native→output 계보·핀, G5와 intake, 분야/coverage/fix/render/QA/delivery별 진행, 열린 조치·소유자·정확한 재개점을 기존 작품 상태에 반환한다.

`technical_fixture`는 synthetic 기술·보고된 의미 계약 시험이며 실제 작품의 인간 시청/청취가 아니다. `reported_not_authenticated`도 보고서의 scope/hash 대조이지 발급자 진위 인증이 아니다. metadata/contact sheet·옛 QA를 현재 최종본의 전구간 검수로 바꾸지 않는다.

필수 납품물·현재 QA·로컬 bundle까지 충족될 때만 오케스트레이터가 master_delivered로 판정한다. 누락되면 요청 목표=final master를 유지하고 실제 sources_ready/G5/intake/PG/delivery 중 막힌 위치를 보고한다. 임의 FFmpeg/legacy P7로 포스트 계약을 우회하지 않는다.
