# 01 — 인계 및 배치 계약

## 1. 입구와 반환
입력은 현재 검수된 프리프로덕션 패키지다. 버전·파일·해시·검수 범위와 함께 캐릭터/의상/장소/소품/LOOK, 현재 보드, shot/panel 배정, 프롬프트, 계획 길이·화면비·음향, 연속성 예외를 받는다. 텍스트 계획만 있는 패키지는 실행 준비로 승격하지 않는다.

현재 승인과 모순되거나 필수 에셋이 누락되면 설계 담당에게 요구 ID·문제·보존 조건을 반환한다. 프로덕션 담당이 이야기·의상·샷 수·대사·길이를 조용히 수정하지 않는다. 단순 슬롯 표현 변경은 원래 의미를 보존하고 최종 요청문을 역대조한다.

## 2. 역할·기록 소유권
| 역할 | 입력 → 출력 | 하지 않는 일 |
|---|---|---|
| production-supervisor | 현재 패키지·권한 → 큐, 배정, 판정 통합, 프로젝트 상태 기록 | 증거 없는 합격·추가 지출 승인 |
| generation-operator | 잠긴 요청 → 실제 제출·원격 ID·다운로드·기술 관측 | 설계 변경·자기 결과의 독립 합격 선언 |
| take-reviewer | 원본·요구 ID → 실제 재생/청취·관측·테이크 판정 제안 | 프레임만 보고 운동/음향 확인 주장 |
| continuity-reviewer | 원본·참조·접합 → 상태 대조·경계·전체 흐름 판정 제안 | 모든 불연속을 무조건 오류로 처리 |
| production-handoff | 채택 소스·검수 → 편집 인계 패키지 | 최종 마스터·게시 |

역할 분리가 곧 독립 에이전트 실행을 뜻하지 않는다. 위임은 사용자/프로젝트 권한과 실제 도구가 있을 때만 수행한다. 자기검수는 self, 독립 검수는 실제 실행 주체·증거를 기록한다. 부서는 자기 결과를 반환하고 총괄만 정본을 갱신한다.

## 3. 논리 데이터 계약
아래는 구현 예정 논리 필드다. 새 경쟁 원장을 만들지 않고 기존 작품 원장에 매핑한다. 기존 ID를 재발급하지 않으며 생성 단위는 여러 shot을 포함할 수 있다.

| 레코드 | 필수 내용 |
|---|---|
| batch | batch_id/version, project_id, 입력 스냅샷 해시, clip 목록, 편집 순서, 의존 edge, 요구/권한 참조, 출력 정책 |
| clip | clip_id, scene/shot/panel ID, prompt artifact/version/hash, 계획 길이, in/out 계획 상태, 요구 ID, 필수 여부 |
| asset_pin | asset ID/version/hash/path, 역할, 장면별 유효 범위, 권위 원본/파생 구분 |
| reference_binding | source asset/채택 take, 정확한 source range, imports/excludes, 필수/선택, 실제 native ID/role/readiness, 변환 계보 |
| capability | provider/transport/account 식별자(비밀 제외), model, 실제 schema/관찰 근거와 확인 시각, 한도/음향/비용 정책 |
| attempt | 고유 attempt_id, clip_id, 최종 payload/참조/권한 핀, idempotency 지원 여부, lifecycle 상태, job ID, 실제 결과 |
| take | take_id, attempt_id, 원본 hash/path, 실측 frame/FPS/길이/음향, 사용 구간, QA와 채택 revision |
| review | 요구 ID, 실제 파일/해시/구간, 관측, pass/fail/unverified/N/A 사유, reviewer와 evidence, 수정·재검 |
| join | 앞뒤 clip 및 take/range revision, relation, state_out/in, allowed_changes와 설계 근거, 경계 검수 |
| handoff | 채택 파일/구간/해시, 접합·전체 검수, 음향·권리·조건부 작업, 실제 handle, 소비자 수령 상태 |

단순 파일 존재와 SHA 일치는 구조 증거이며 입력의 예술적 적합성·권리·승인을 인증하지 않는다.

## 3a. 필수 커버리지 불변식
G0는 batch 목록 자체가 아니라 승인된 프리프로덕션 스냅샷에서 필수 coverage_set을 먼저 고정한다. coverage_set은 required shot/panel·사건·대사/화자·필요 영상/음향 소스를 식별하고 원문 locator·버전·승인된 제외를 갖는다. 같은 사건에 여러 표현이 대응할 수 있으므로 단순 clip 개수 비교로 검사하지 않는다.

모든 필수 항목에 하나 이상의 생성/기존 소스 충족 경로를 배정한다. 기존 소스 재사용도 실제 파일·권리·채택구간 검증이 필요하다. 한 clip이 여러 shot을 담으면 각 항목별 계획 구간·충족 기준을 기록한다. 최초 미매핑·임의 선택화·일부 shot만 배정된 묶음 clip은 G0 차단이다. 패널은 계획 순간의 증거이며 영상에서 모두 동일 정지 프레임으로 재현하라는 뜻이 아니다.

G5에서는 같은 집합의 각 필수 항목이 실제 유효 take/range와 요구별 검수로 충족되었는지 역대조한다. 소스구간이 있다고 사건·대사가 실제 들어 있다고 단정하지 않는다. 제외/범위 변경은 승인된 프리프로덕션 scope revision에 결속하고 batch와 coverage_set을 함께 갱신한다. 필수 소스 분모는 이 집합에서 도출한다.

## 3b. 유효성 핀
reference_binding, attempt, review는 관련 설계/scope revision, 원본 asset version/hash, take_id, range_revision, acceptance_revision, imports/excludes 및 조건부 판정 revision을 핀한다. 이를 정렬된 canonical 입력 스냅샷으로 저장하고 input_fingerprint를 계산한다. 파일 바이트가 같아도 사용구간·채택/조건부 판정·가져올 속성이 바뀌면 새 fingerprint가 필요하다. 관련 없는 독립 노드의 revision 변경은 해당 fingerprint를 바꾸지 않는다. 전체 batch revision만으로 모든 노드를 불필요하게 무효화하지 않는다.

## 4. 시간 기준
- 편집 전역, clip-local, shot-local, 실제 source 시간을 필드로 구분한다.
- 계획 FPS와 실측 FPS는 별도다. 실제 구간은 0-based [in_frame,out_frame), 마지막 포함 프레임은 out−1.
- CFR 여부·프레임 수·FPS를 실측한다. VFR이면 PTS 기반 매핑 또는 승인된 conform 파생본과 계보가 필요하며 nominal FPS로 프레임 정밀성을 주장하지 않는다.
- 최종 길이와 생성 길이는 별도. 모델 최소 길이를 맞추려고 행동·대사를 늘리지 않는다.
- handle은 실제 채택구간 바깥에서 검사된 사용 가능 프레임 수다. 요청문에 여유를 적었다고 실제 handle이 생긴 것으로 세지 않는다.

## 5. 권한 계약
승인 근거는 작업·clip·전송할 참조 범위·계정/모델·길이/화면비·비용 모드·시도/재시도 범위를 특정한다. 없는 예산 상한을 발명하지 않는다. 업로드·생성·변환·검수용 렌더·최종 편집·게시 권한은 구분한다.

제출 직전 현재 설정과 승인 범위를 다시 비교한다. 실제 Unlimited 제어가 아닌 credit/bonus/구매 화면은 Unlimited가 아니다. 공급자/모델/전송 매체/참조 모달리티의 필수 변경은 승인 범위를 재확인한다.
