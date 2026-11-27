# 03 — 실행·동시성·복구

## 1. 상태를 섞지 않는다
clip은 planned/blocked/ready/active/reviewing/accepted/conditional/rejected 상태를 투영한다. attempt는 아래 lifecycle을 별도 기록한다. 채택 변경으로 결과가 stale이 되어도 과거 attempt의 성공 사실을 덮어쓰지 않는다.

| attempt 전이 | 조건·증거 |
|---|---|
| prepared → submitting | 정확한 입력/설정/승인 핀, 현재 기능 확인, 제출 전 저널, 배타 잠금 |
| submitting → submitted | 반환된 실제 remote job ID와 요청 대응 저장 |
| submitting → unknown | timeout/연결 중단/접수 여부 불명 |
| submitting/unknown → running/succeeded/remote_failed/cancelled | 중간 상태를 놓쳤더라도 원래 request와 일치하는 실제 job/status 확인. 관측하지 않은 중간 사건을 꾸며 넣지 않음 |
| submitted → running | 해당 job 상태 관측 |
| submitted/running → remote_failed | 해당 job의 확정 실패 증거 |
| submitted/running → succeeded | 해당 job 성공과 결과 locator 관측 |
| succeeded → downloaded | 원본 파일·hash·decode·실측 metadata, input-as-output 오인 배제 |
| 어느 활성 상태 → cancelled | 실제 취소 확인. 취소 요청만으로 완료 취급 금지 |

원격 성공은 테이크 채택이 아니다. downloaded 후 QA에서 clip의 accepted/conditional/rejected를 정한다. local 다운로드 실패는 원격 작업 재생성 사유가 아니다.

## 2. 스케줄링
총괄이 프로젝트 실행 잠금과 단일 writer를 소유한다. 동일 프로젝트의 다른 실행자가 있으면 충돌을 보고한다. 시간 만료만으로 lock을 훔치지 않고 소유자 생존과 원격 활성 작업부터 확인한다.

ready 조건 = 현재 입력 핀 유효 + 필수 선행 참조 채택/유효 + 기능/권한/비용 적합 + 실행 슬롯 가용. 실동시성은 공급자 현재 한도·사용자 한도·실행 도구 안전 한도의 최솟값이다. 모르면 동시 실행을 추정하지 않는다.

슬롯은 외부 제출 부작용 전에 원자적으로 예약한다. submitting/unknown/submitted/running은 실제 원격 점유 가능 상태로 세고, unknown 때문에 예약을 풀지 않는다. 명확한 미접수 또는 원격 succeeded/remote_failed/cancelled의 확인 증거가 있을 때만 해제한다. 원격 종료 뒤 로컬 다운로드·QA는 원격 생성 슬롯과 구분한다. 중단 후 예약을 원장으로 복원하고, 같은 계정의 관측된 다른 활성 작업도 중복 계산 없이 한도에 포함한다. 기존 작업 점유를 확인할 수 없으면 추측으로 새 슬롯을 열지 않는다.

독립 준비/검수 작업은 진행할 수 있다. 반려 노드의 필수 후손은 blocked. 모두 막혔거나 unknown이면 큐를 완료로 비우지 않고 원인과 정확한 재개 지점을 남긴다.

## 3. 제출 프로토콜
- 공식/기존 지원 커넥터 우선. browser는 지정 계정/프로필·탭을 검증하고 무관한 초안을 보존한다.
- 입력 이미지/클립 hash, ready 상태, 최종 선택 ID, 모델·길이·비율·해상도·오디오·모드 및 실제 가격을 제출 직전 확인한다.
- 시도 ID와 요청 스냅샷을 제출 전에 저장. 공급자 idempotency가 있으면 의미·유효기간을 확인해 사용한다. 지원이 없으면 exactly-once를 보장한다고 말하지 않는다.
- 반환된 job ID를 즉시 저장. 서명 URL·토큰·쿠키는 원장·보고서에 노출하지 않는다.
- 입력이 변경되면 prepared 패킷을 무효화하고 재검사한다.

관측 receipt는 현재 준비 파일 검증과 분리해 먼저 같은 원장에 영속화한다. 입력 손상이나 진단 중단 때문에 확인된 remote ID/종료 사실을 버리지 않는다. scope의 source/origin은 변경할 원장 자신이 아닌 불변 스냅샷을 사용한다. 자세한 로컬 API·revision 복구는 [운영 절차](../operations.md#관측-복구와-준비-검증의-분리)를 따른다.

## 3a. 채택 반영의 원자적 검증
원격 성공·다운로드 사실은 원래 attempt 스냅샷에 그대로 기록한다. 그러나 현재 clip의 채택/후속 참조를 여는 것은 별도 commit이다. 총괄은 제출 직전과 QA 결과 반영 직전에 관련 입력 fingerprint, source take/range/acceptance revision, 설계/권한 유효성, validity를 현재 정본과 비교한다.

검사와 채택 반영은 프로젝트 단일 writer의 동일 트랜잭션 또는 compare-and-swap으로 수행한다. 다르면 과거 성공/QA는 보존하지만 current validity=pending_revalidation으로 두고 accepted 투영·후속 참조·완료 집계에 사용하지 않는다. 결과 도착 후와 반영 직전 사이의 변경도 다시 검사한다. 유지 판정은 현재 근거를 대조한 새 QA/acceptance revision으로만 반영한다. 이미 제출된 결과를 실패로 꾸미거나 과거 요청 핀을 덮어쓰지 않는다.

## 4. unknown 복구
같은 계정/세션/원격 이력에서 원래 시도와 시간을 대조하고, pagination·job ID·업로드/요청 지문 등 관찰 가능한 증거를 확인한다. 시간만 비슷한 작업을 내 결과로 단정하지 않는다. 첫 페이지에 없다고 실패 확정하지 않는다.

접수 확인 → 해당 작업 추적. 명확한 미접수/확정 실패 → 기존 시도 종료를 기록하되 새 시도 권한은 별도 확인. 불명 지속 → 차단 유지. polling 종료는 생성 취소나 실패가 아니다. 계정 challenge는 우회하지 않고 사용자에게 반환한다.

## 5. 재시도·재개
재시도는 원인, 바꿀 입력, 보존 조건, 기대 개선, 허용 추가 시도·비용이 있어야 한다. 새 attempt ID를 발급하고 기존 실패를 보존한다. “큐 전체 승인”을 무제한 재시도 승인으로 해석하지 않는다.

중단 후에는 마지막 유효 스냅샷·활성 remote ID·로컬 파일부터 대조한다. 이미 다운로드한 채택 소스는 다시 생성하지 않는다. 실제 도구 가용성과 인증을 재확인하며 프로세스가 종료되어도 자동 실행이 살아 있다고 약속하지 않는다.

## 6. 실패 분류
- 설계: 상충 행동/누락 보드/시간 불가능 → 프리프로덕션에 반환.
- 실행: 잘못된 역할/첨부/설정 → 정확한 요청 결속 수정, 원격 접수부터 조사.
- 생성 결과: 얼굴/운동/음향 결함 → QA 증거로 최소 수정/재생성 제안.
- 운영: 네트워크/저장공간/다운로드 → 원격 결과 보존, 로컬 복구 우선.
- 권한/지원: 플랜·가격·모달리티 불일치 → 실행 차단, 무단 대체 금지.
