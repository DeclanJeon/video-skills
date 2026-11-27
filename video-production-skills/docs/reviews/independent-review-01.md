# 프로덕션 설계 독립 검토

## 판정: REVISE

큰 구조는 요구에 부합한다. 그러나 **필수 소스 집합의 완전성**, **변경 중인 배치에서 실행·채택 결과의 유효성**, **접수 불명 작업의 슬롯 점유**를 구현자가 서로 다르게 해석할 여지가 남는다. 아래 P1은 구현 착수 전 해소할 차단급 계약 결함이며, P2도 정확한 운영·서사 처리를 위해 수정해야 한다. 단순 편의 기능이나 특정 공급자 선택을 차단 사유로 삼지는 않았다.

## 발견 사항

### P1-1. ‘전체 필수 클립’의 분모를 프리프로덕션 요구에서 완전하게 도출하는 불변식이 없다

- **근거:** `docs/design/01-batch-contract.md:19–25`, `docs/design/04-qa-handoff.md:6–7,44–52`, `docs/design/05-validation-decisions.md:33–35`.
- **문제:** G0의 요구 추적표와 충돌 없는 대응은 좋은 출발점이지만, 승인된 프리프로덕션의 필수 shot/panel·사건·대사·필요 소스를 **빠짐없이** 큐의 필수 생성/채택 단위로 덮어야 한다는 통과 조건이 명확하지 않다. 완료율의 분모는 이미 만들어진 batch의 필수 clip 목록이다. 또한 한 생성 단위가 여러 shot을 포함할 수 있으므로 단순 shot 수와 clip 수 비교로도 누락을 검출할 수 없다. 분모 변경 통제는 최초 등록 시 누락을 막지 못한다.
- **실패 시나리오:** 승인 패키지에 필수 S01–S07이 있지만 batch 작성 중 S07을 빼고 C01–C06만 등록한다. 등록된 여섯 클립과 그 접합을 모두 통과시키면 배치 내부 지표는 100%다. T17은 이미 등록된 노드 삭제만 검사하므로 이 누락을 직접 검증하지 않는다.
- **최소 수정:** G0에 승인 패키지로부터 고정한 **필수 커버리지 집합**과 clip/shot/panel/요구 ID 매핑을 명시한다. 각 필수 항목은 하나 이상의 실제 납품 소스·사용 구간으로 충족되어야 하며, 미매핑·임의 선택화는 차단한다. 여러 shot을 한 clip으로 충족하는 경우도 항목별 대응을 남긴다. 제외는 승인된 범위 revision으로만 허용한다. ‘배치 최초 작성 시 필수 항목 누락’과 ‘다중 shot clip의 일부 shot 누락’ 수락 사례를 추가한다.

### P1-2. stale 의도는 있으나 변경과 실행·채택의 경합을 닫는 revision 검증 규칙이 부족하다

- **근거:** `docs/design/01-batch-contract.md:27–31`, `docs/design/02-reference-continuity.md:31–39`, `docs/design/03-execution-recovery.md:4–17,20–24,28–31`, `docs/design/00-overview.md:38,53`.
- **문제:** 결과를 stale로 만들고 완료에서 제외한다는 상위 원칙은 있다. 하지만 상세 전이는 준비된 입력의 무효화만 명시하며, **이미 제출된 작업의 완료/QA 반영 시점**에 현재 revision과 대조하는 규칙은 없다. 후손도 ‘재검수 후보’로 지정할 뿐, 재검수 전 참조·채택 가능 여부가 명확하지 않다. source 바이트가 같더라도 채택 구간·imports·조건부 결함 판정이 바뀌는 경우까지 어떤 revision을 참조 결속이 핀하는지도 필수 필드에서 확정되지 않았다. 단일 writer는 변경과 원격 완료가 시간차로 도착하는 논리적 경합까지 해결하지 않는다.
- **실패 시나리오:** C01의 테이크 A를 사용한 C03이 running인 동안 C01이 B로 교체된다. 이어 A에 결속된 C03의 성공과 QA 통과가 도착한다. 과거 시도의 성공 사실을 유지하는 것은 맞지만, 현재 배치의 C03을 accepted로 갱신하거나 C04의 선행 참조로 여는 것을 막는 명시적 commit 조건이 없다. 또는 같은 A의 채택 구간이 바뀌어도 파일 hash만 비교하는 구현은 변경을 놓친다.
- **최소 수정:** attempt와 QA를 입력·참조의 **take/range/채택 판정 revision 및 관련 설계 revision**에 결속한다. 제출 직전뿐 아니라 결과 채택 반영 시에도 현재 정본과 비교하고, 불일치 결과는 과거 성공으로 보존하되 현재 채택·후속 참조·완료 집계에 사용하지 못하게 한다. 영향받은 후손은 유효성 재판정 전까지 보수적으로 차단하고, 유지 판정은 새 revision으로 기록한다. running 중 교체, QA 반영 직전 교체, 동일 파일의 구간/판정 변경에 대한 경합 수락 사례가 필요하다.

### P2-1. unknown 작업의 동시 실행 슬롯 예약·해제 조건이 없다

- **근거:** `docs/design/03-execution-recovery.md:8–15,19–24,33–41`, `docs/design/05-validation-decisions.md:24,38,44–45`.
- **문제:** unknown은 재제출하지 않고 이력으로 대조하도록 잘 설계되어 있다. 그러나 실행 슬롯을 계산할 때 unknown을 원격 작업일 수 있는 점유로 계속 세는지, 언제 해제하는지는 없다. ‘같은 시도를 중복 제출하지 않음’과 ‘전체 원격 동시성 한도를 지킴’은 다른 조건이다.
- **실패 시나리오:** 사용자 동시성 한도가 2다. A는 공급자에 접수되었지만 응답을 잃어 unknown이 된다. 스케줄러가 submitted/running만 세면 독립 B와 C를 함께 제출하여 실제 3개가 실행된다. A를 재시도하지 않았어도 승인된 병렬 실행 범위는 초과한다.
- **최소 수정:** 외부 부작용 직전에 슬롯을 예약하고, submitting/unknown/submitted/running 동안 보수적으로 유지한다. 명확한 미접수 또는 원격 종료·취소 확인 등 해제 근거를 정의하고 재개 시 예약을 복원한다. 원격 성공 후 로컬 다운로드·QA는 원격 슬롯 점유와 구분한다. 동일 계정의 관찰된 다른 활성 작업도 한도 계산에 반영한다. ‘한도 2, unknown 1, 독립 ready 2’에서 새 제출이 최대 1개인 사례를 추가한다.

### P2-2. 리액션의 공개 순서 규칙이 승인된 비선형 서사를 일괄 금지한다

- **근거:** `docs/design/02-reference-continuity.md:3–5,26–29`, `docs/design/01-batch-contract.md:4–6`, `docs/design/04-qa-handoff.md:15–16`.
- **문제:** 편집 그래프는 회상·교차편집을 허용하고 프리프로덕션의 공개 순서를 보존해야 한다. 반면 접합 규칙은 ‘리액션은 원인보다 먼저 나오지 않아야’ 한다고 무조건 규정한다. 극중 인과관계와 관객에게 보여주는 순서는 다르다.
- **실패 시나리오:** 보드가 인물의 놀란 표정을 먼저 보여준 뒤, 다음 컷에서 그 원인인 파손된 소품을 공개하도록 승인되어 있다. 현재 문구대로면 충실하게 생성한 테이크도 G3에서 반려하거나 공개 순서를 바꾸도록 요구하게 된다.
- **최소 수정:** 반응의 극중 인과·시간 정합성과 관객에 대한 공개 순서를 분리한다. 기본 순서 검사에는 설계상 예외를 허용하고, 승인된 보드/공개 순서에 반하는 경우만 오류로 판정한다. ‘반응 선공개 후 원인 공개’와 ‘승인 없는 인과 역전’을 각각 통과·실패 사례로 추가한다.

## 강점

- 편집 그래프와 생성 DAG를 분리하여 이전/다른 관련 채택 클립을 필요한 역할로 사용할 수 있다.
- 정체성 원본·현재 장면 에셋·실제 테이크의 권위를 속성별로 구분하고, native 참조 선택과 바이트/구간 결속을 요구한다.
- 원격 성공, 실제 다운로드, 테이크 채택, 전체 흐름, 후반 인계를 별도 게이트로 둔다. 실제 시청·청취 없는 PASS와 막연한 후반 수정 가정을 금지한 점이 특히 좋다.
- 외부 전송·과금·재시도 권한을 설계 승인과 분리하고, 불명확한 접수를 자동 재제출하지 않는다.

## 범위·한계 및 검증 증거

- 읽은 범위: `README.md` 전체와 `docs/design/00-overview.md`부터 `05-validation-decisions.md`까지 전체, 총 321줄. 인접 패키지·실제 도구 구현·공급자 기능은 조사하지 않았다.
- 문서만 대상으로 한 독립 정적 설계 검토다. 수락 사례 T01–T24와 단계별 검증은 **실행된 테스트가 아니다**. README에 연결된 자체 검토도 독립 검증 증거로 사용하지 않았다.
- 미디어 생성·재생, 외부 서비스 호출, 설치, 위임, 소스 수정, 커밋은 수행하지 않았다. 지정된 검토 산출물만 작성했다.
- `pwd`, `ls -la`, `wc -l`, `nl -ba`로 위치·문서·줄번호를 확인했다. `git rev-parse --show-toplevel`은 Git 저장소가 아님을 확인했고, `find docs/design ...`으로 대상 여섯 문서를 대조했다. Git 저장소가 아니므로 staged diff 자체가 적용되지 않는다.
- 새 테스트 또는 테스트 수정 없음. P3 선택적 개선 제안은 별도로 부풀리지 않았다. 위 네 항목은 편의 개선이 아닌 계약 수정 요청이다.

## 권장 다음 단계

P1 두 항목의 커버리지·revision 불변식을 먼저 확정하고, P2 슬롯·서사 규칙을 반영한 뒤 해당 반례를 로컬 계약 테스트로 구현한다. 그 후 재검토한다. 이 보고서는 구현 또는 공급자 실행 준비 완료를 인증하지 않는다.

```acceptance-report
{
  "criteriaSatisfied": [
    {"id":"criterion-1","status":"satisfied","evidence":"요청된 README와 설계 6개 문서만 독립 정적 검토하고 지정 보고서만 작성했다. 구현·외부 실행·위임은 하지 않았다."},
    {"id":"criterion-2","status":"satisfied","evidence":"각 발견에 우선순위, 정확한 문서 경로와 줄 범위, 실패 시나리오, 최소 수정안을 제공하고 미실행 검증을 구분했다."}
  ],
  "changedFiles": ["/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/35a3fc1d-75f2-4e67-b174-18abf1f789b6/reviews/production-design-independent-review.md"],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {"command":"pwd; ls -la; for f in README.md docs/design/0*.md; do echo \"--- $f\"; wc -l \"$f\"; done","result":"passed","summary":"대상 위치와 문서별 줄 수 확인"},
    {"command":"for f in README.md docs/design/0*.md; do echo \"--- $f\"; nl -ba \"$f\"; done","result":"passed","summary":"README 및 설계 여섯 문서 전체를 줄번호와 함께 검토"},
    {"command":"if git rev-parse --show-toplevel 2>/dev/null; then git diff --cached --name-only; else printf 'NOT_A_GIT_REPOSITORY\\n'; fi; find docs/design -maxdepth 1 -type f -name '0[0-5]-*.md' -print | sort","result":"passed","summary":"NOT_A_GIT_REPOSITORY 및 대상 여섯 문서 확인"},
    {"command":"python - <<'PY' (보고서 JSON 검증)","result":"failed","summary":"python 실행 파일 없음; python3로 재실행"},
    {"command":"python3 - <<'PY' (pathlib로 보고서 읽기, json.loads로 acceptance-report 파싱, 발견 4건 및 REVISE 확인)","result":"passed","summary":"Report exists; acceptance-report JSON valid; four findings; verdict REVISE."}
  ],
  "validationOutput": ["문서 321줄 정적 검토", "테스트·미디어·공급자 검증 미실행"],
  "residualRisks": ["문서 외 구현·인접 패키지·공급자 기능은 검증하지 않음", "P1 2건 및 P2 2건 수정 필요"],
  "noStagedFiles": true,
  "diffSummary": "프로젝트 소스 변경 없음. 지정된 한국어 독립 검토 보고서만 작성.",
  "reviewFindings": ["P1: 필수 커버리지 집합의 완전성 계약 부족", "P1: 실행·채택 경합의 revision 검증 부족", "P2: unknown 작업의 슬롯 점유 계약 부족", "P2: 리액션 공개 순서 규칙의 비선형 서사 충돌"],
  "manualNotes": "Git 저장소가 아니므로 staging은 해당 없음. 설계 수락 사례는 실행 테스트로 계산하지 않았다. 최종 승인에는 별도 리뷰 게이트가 필요하다."
}
```
