# 로컬 프로덕션 운영

## 사용 범위와 실제 실행
이 구현은 배치/참조/권한/상태/QA/인계 계약을 검사하고 프로젝트 JSON에 원자적으로 기록한다. 업로드·생성·결제·설치·시청/청취 도구가 아니다. 실제 지원 실행자와 검수자가 낸 정확한 관측을 입력한다. **offline fixture를 실제 원격 작업이라고 표시하지 않는다.**

부모 총괄이 유일한 writer다. 프로젝트의 기존 ledger/project JSON을 명시해서 production namespace만 추가한다. 다른 필드는 보존한다. legacy cp2.Ledger._save는 알 수 없는 namespace를 보존하지 않으므로 이 세션의 원장 writer로 동시에 호출하지 않는다. legacy 연동은 현재 핀을 읽는 resolve_legacy seam만 지원한다. 동시 legacy 쓰기가 필요한 실제 통합은 별도 매핑/어댑터 없이는 차단한다.

## 명령
패키지 루트에서 `python3 scripts/production.py --help`로 실제 인수를 확인한다.
- coverage: 실제 project의 shot/panel/beat/speech/cue coverage와 필수 자산 의존성 closure·origin 핀을 함께 도출한다. 출력 envelope는 같은 작품 루트에 저장하고 원본 origin 파일도 보존한다.
- init: State JSON으로 기존 프로젝트 namespace 초기화. 이미 있으면 중단한다.
- validate/ready/progress: 현재 입력·필수 coverage·상태와 생성 가능 노드를 읽는다. 현재 scope 파일이 손상되면 새 작업의 준비/실행을 차단한다.
- status: 현재 준비 파일이 없어도 모델 검증된 기존 job ID·phase·예약과 scope 입력 진단을 읽는다. inputs_ready는 scope 구조/파일 검사 결과일 뿐 실행 승인·native 지원·지각 검수 통과가 아니다.
- prepare: 실제 capability/authority/bindings 증거를 받아 정확한 로컬 요청 패킷 출력. 공급자 제출 아님.
- reserve: 설정/입력 재검사 후 제출 전 슬롯·attempt 예약. 현재 revision과 외부 계정 점유 수가 필요하다.
- observe: 원격 응답/unknown/종료의 관측 receipt를 입력. 잠금/CAS·기록된 요청 digest·receipt hash·job ID·허용 전이를 검사하고, 원격 사실을 같은 원장에 먼저 fsync한다. 그 뒤 mutable 입력 진단을 별도 commit한다. 파일 삭제/해시 변화/진단 중단은 이미 확인한 job ID를 지우지 않는다. submitting/downloaded 같은 로컬 게이트를 이 경로로 우회할 수 없다. 이미 확인된 job을 단순 부재로 not_received로 바꿀 수 없다.
- review: 실제 후보 파일을 decode/probe하고 보고된 playback·요구 충족을 검사해 채택 제안을 기록한다. fingerprint·현재 승인 증거·설정 grant와 ledger revision을 비교한다.
- reuse: 기존 로컬 영상의 정확한 파일·구간에 대한 별도 reuse grant와 검수로 소스를 채택한다. remote attempt/job을 발명하지 않는다.
- revise-scope: ScopeGrant가 이전/새 scope와 요구·자산 변경 집합을 정확히 승인한 경우에만 분모를 바꾼다. 기존 원격 시도/unknown 슬롯은 보존하고 이전 채택/접합을 재검수 상태로 둔다.
- invalidate/revalidate: 수정 영향을 보수적으로 전파하고 명시적으로 재검수한다. 필수 선행 소스가 invalid이면 후손 재검수로 우회할 수 없다. 조건부 소스의 결함이 imports에 영향을 주지 않는다고 유효 판정된 경우만 재검수 가능하다. 새 scope/설정 승인은 revalidate의 --authority로 새 핀을 전달하고, 과거 요청의 승인은 수정하지 않는다.
- join: 실제 경계 재생 보고서를 현재 take/range/acceptance에 결속한다.
- flow-hash: 전체 흐름을 검수할 정확한 선택 스냅샷. 이것만으로 재생했다고 주장할 수 없다.
- render-review: 현재 채택 구간의 실제 로컬 기술 검수용 연결본과 source lineage를 생성한다. 혼합 포맷·VFR·음향 형식 차이는 승인된 conform 없이는 차단한다. 최종 마스터가 아니다.
- handoff: 실제 FlowReview와 수령/권리 근거로 로컬 JSON 출력. CLI는 연결본을 검사하고, 라이브러리도 작품 root를 필수로 받아 모든 납품 원본·승인 핀의 현재 바이트를 재확인한다. 렌더 뒤 원본 삭제/교체는 차단한다. 최종 편집/게시는 별도다.

## 관측 복구와 준비 검증의 분리

init 전에 coverage source와 exported origin을 변경할 원장과 분리한 불변 스냅샷으로 준비한다. 원본 project JSON을 원장으로 사용할 때는 같은 프로젝트 루트에 승인된 버전 사본을 만들고 그 사본에서 coverage를 내보낸다. 저장이 자기 자신의 source 핀을 즉시 깨는 구성은 init/일반 commit에서 거절한다.

라이브러리는 원격 관측에 ProjectStore.record_observation만 사용한다. 이 API는 기존 attempt ID와 Receipt만 받고 State 대체나 임의 callback을 허용하지 않는다. 일반 transaction의 current-scope 검사를 끄는 옵션이 아니다. mutable 준비 입력이 망가져도 exact remote ID/terminal 사실은 원자적으로 보존하고, unknown인 다른 작업의 예약은 유지한다.

사실 commit과 진단 commit 때문에 revision은 두 번 증가할 수 있다. 반환된 revision 또는 status를 읽고 다음 CAS를 수행하며 +1을 가정하지 않는다. 진단/두 번째 쓰기가 중단되면 원격 사실과 conservative pending 진단이 첫 commit에 남는다. 오류 뒤에는 status/read_recorded로 먼저 대조하고 원격 재제출이나 init으로 복구하지 않는다. observed_input_issues는 관측 시 진단 기록이며 status는 현재 scope를 다시 검사한다.

read_recorded/status는 준비 완료를 부여하지 않는다. 새 reserve/채택/reuse/인계는 원래 current-input·권한·media 게이트를 유지한다. ledger 자체의 모델/요청 식별자가 손상되면 관측도 중단하며 실제 receipt 파일과 기존 원장을 보존해 수동 대조한다.

## 파일·증거
`schemas/`의 JSON Schema와 런타임 Pydantic 모델이 입력 계약이다. pin path는 프로젝트 상대 경로, symlink·상위 탈출은 거절한다. capability·authority 파일 해시와 실제 native selected IDs/ready를 확인한다. 외부 서명 URL·쿠키·토큰을 로그로 남기지 않는다.

ready는 기록·구조 준비다. 실제 role 지원과 제출 직전 계정/모드/가격은 operator가 확인하고 capability 증거를 갱신한다. 모달리티가 바뀌면 필수 계약 변경이므로 자동 fallback하지 않는다. 원격 exactly-once는 보장하지 않으며 unknown을 점유로 유지하고 실제 이력부터 대조한다.

## 승인과 자산 closure

Authority.configurations는 클립별 scope·coverage source hash·clip 구성 hash·길이·출력 크기/화면비·요청 음향을 명시한다. 모델이 지원한다는 이유만으로 이를 승인하지 않는다. prepare/reserve와 채택 commit에서 해당 설정·승인 핀을 재검사한다. 증거 파일이 바뀌면 역사적 원격 성공은 보존하지만 현재 채택은 차단한다. 기존 소스 재사용에는 별도의 reuse 플래그와 exact source/range grant가 필요하다.

현재 upstream projection은 shot 직접 자산, character→identity/SSOT, panel 이미지/시트/asset_version_refs, active LOOK, voice/spatial artifacts, cue/caption, source/master lineage 및 artifact dependency/asset closure를 보존한다. 버전 충돌과 미해결 의존성은 차단한다. 기존 project_index의 대표 closure와 실제로 대조한다. 이 변환기는 upstream 전체 품질 검사기가 아니므로 원본 프로젝트의 기존 preproduction validator도 적용해야 한다. 미래 schema/실행자 기능을 자동 지원한다고 가정하지 않는다.

Clip.dependencies는 로컬 검수·계보용 핀이고 Clip.assets는 외부 전송할 명시적 참조다. 필수 identity나 보드 의존성을 dependencies로 보존하더라도 전체 closure를 일괄 업로드하지 않는다. 실제 필요한 conditioning 역할과 자산은 현재 모델·전송 권한에 맞춰 별도로 결정한다. 원본 에셋이 로컬에 있다는 것만으로 얼굴 일치가 생성에서 보장되지는 않는다.

## 채택 시 소비한 소스의 재확인

생성 결과의 최초 채택, 재검수, approved reuse는 필수 upstream 및 실제 선택한 optional binding의 source media·approval 핀과 현재 판정을 검사한다. 후보 자신의 별도 승인 파일이 정상이어도 소비한 source의 승인 파일이 바뀌면 채택을 차단하고 원격 성공 사실만 보존한다. 명시적 생략 근거가 있고 실제 요청에서 선택하지 않은 optional history는 현재 후보의 소비 입력으로 가장하지 않는다.

## 검수 근거
Review/JoinReview/FlowReview는 검수자가 실제로 관측한 범위에만 작성한다. 순수 코드 검사는 필드/해시/버전/구간/상태를 검증할 뿐 의미 관측의 진실성을 인증하지 않는다. 실제 파일 decode/probe는 기술 품질만 증명한다. 다른 사람이 JSON을 위조해 넣는 것에 대한 인증/전자서명 시스템은 이 범위가 아니다.

프레임 범위는 [start,end), 마지막 포함은 end−1. VFR는 명시적 PTS/conform 근거가 필요하다. handoff의 handles는 현재 별도 외부구간 검수 입력이 없으므로 0으로 인계한다. 원본 frame_count와 source_range로 미검수 raw margin 크기는 조회할 수 있지만 이를 사용 가능한 handle이라고 인증하지 않는다. 비제로 handle 채택은 별도의 구간 재생/검수 확장이 필요하다.

## 검증
`python3 scripts/check_package.py --json`, `python3 scripts/check_acceptance.py --json`, `python3 -m pytest -q`.
check_acceptance는 map의 실제 pytest node들을 실행하고 결과를 qa/implementation/acceptance-results.json에 기록한다. T01–T34의 사람 지각 부분은 합성 보고서 계약 테스트이며 실영상 예술 QA 통과를 뜻하지 않는다. 기술 영상 fixtures는 임시 디렉토리에서 ffmpeg로 만들고 실제 ffprobe/decode한다. 공급자 생성은 아니다.
