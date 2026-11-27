# 프로덕션 설계 독립 재검토 — 2차

## 판정: PASS

**설계 문서 수준에서 이전 발견 4건은 모두 해소되었다.** 실제 수정된 계약을 기준으로 기존 실패 시나리오를 다시 대조했다. 수정으로 생긴 새로운 조치 필요 모순이나 미해결 P1/P2/P3는 이번 범위에서 발견하지 못했다.

이 판정은 구현·설치·공급자 실행·생성 품질의 승인이나 테스트 통과 판정이 아니다. `docs/reviews/remediation-01.md:4–10`의 체크 표시는 결론의 증거로 대신 사용하지 않았다.

## 기존 발견별 판정

### P1-1 — 필수 소스 집합의 완전성: 해소

**실제 근거**
- `docs/design/01-batch-contract.md:37–42`: 큐 작성에 앞서 승인된 프리프로덕션 스냅샷으로부터 coverage_set을 고정한다. shot/panel뿐 아니라 사건·대사/화자·영상/음향 소스를 식별한다. 최초 미매핑, 임의 선택화, 다중 shot clip의 일부 배정을 G0에서 차단한다. G5에서는 실제 유효 take/range와 요구별 검수로 역대조하고, 제외는 승인된 scope revision에 결속한다.
- `docs/design/04-qa-handoff.md:6–11,44–53`: G0/G5의 완전성 조건, clip 채택률과 별도인 요구 충족률, coverage 전 항목을 충족해야 하는 완료 조건을 명시한다.
- `docs/design/05-validation-decisions.md:48–49,57`: 최초 누락·묶음 clip 일부 누락·등록 clip 채택 후 실제 요구 누락의 반례를 계획에 추가했다.

**기존 실패 시나리오 재대조**
승인 패키지의 S07을 batch에서 빼면 이제 batch 내부 여섯 clip만으로 분모를 정할 수 없다. S07의 필수 coverage 항목이 미매핑되어 G0가 닫힌다. 배정만 해 놓고 실제 영상에서 해당 사건을 누락한 경우도 G5의 요구별 역대조로 차단한다. ‘모든 필수 소스’가 등록된 clip 목록의 자기증명에 머물던 결함이 해소되었다.

### P1-2 — 변경 중 실행·채택 경합과 stale: 해소

**실제 근거**
- `docs/design/01-batch-contract.md:44–45`: reference_binding·attempt·review가 관련 설계/scope, asset, take, range, acceptance, imports/excludes, 조건부 판정 revision을 핀한다. 동일 바이트라도 구간·판정·소비 속성이 바뀌면 fingerprint를 바꾼다. 무관한 독립 노드는 불필요하게 무효화하지 않는다.
- `docs/design/02-reference-continuity.md:31–39`: 영향받은 후손을 pending_revalidation으로 두고 재판정 전 채택·참조·ready·완료 사용을 금지한다. 경합 중 도착한 성공도 예외가 아니다. 유지 시에는 새 revision과 QA 결속을 기록하되 과거 요청 핀은 수정하지 않는다.
- `docs/design/03-execution-recovery.md:35–38`: 원격 성공 기록과 현재 채택 commit을 분리한다. 제출 및 QA 반영 직전 현재 fingerprint·source revision·설계/권한·validity를 비교하고, 검사와 반영을 동일 트랜잭션 또는 CAS로 묶는다. 불일치 시 과거 성공은 보존하지만 현재 채택과 후속 참조는 열지 않는다.
- `docs/design/04-qa-handoff.md:47–53`: 현재 유효한 판정만 집계하고 pending_revalidation/stale을 완료에서 제외한다.
- `docs/design/05-validation-decisions.md:50–52`: running 중 교체, commit 직전 변경, 동일 파일의 구간·판정 변경을 별도 반례로 추가했다.

**기존 실패 시나리오 재대조**
C03이 C01의 A를 소비하며 실행되는 동안 C01을 B로 바꾸면, 늦게 도착한 C03 성공은 과거 attempt 사실로만 남는다. 현재 입력과 불일치하는 채택 commit은 차단되고 C04의 참조도 열리지 않는다. QA 관측 뒤 commit 직전 변경도 원자적 비교로 차단한다. 같은 hash의 채택 구간이나 조건부 판정 변경도 더 이상 동일 입력으로 간주하지 않는다. 재검수로 유지할 수 있는 경로와 역사 보존 경로도 서로 모순되지 않는다.

### P2-1 — unknown의 슬롯 예약: 해소

**실제 근거**
- `docs/design/03-execution-recovery.md:22–24`: 외부 제출 부작용 전에 슬롯을 원자적으로 예약하고 submitting/unknown/submitted/running의 점유를 유지한다. 해제는 명확한 미접수나 원격 종료 증거로 한정한다. 예약 복원, 같은 계정의 다른 활성 작업 반영, 점유 미확인 시 신규 슬롯 차단도 명시한다.
- `docs/design/03-execution-recovery.md:40–48`: unknown 대조·불명 지속 시 차단·재개 절차와 위 예약 규칙이 양립한다.
- `docs/design/05-validation-decisions.md:53,55–56`: unknown 예약, 원격 성공 뒤 다운로드 실패, 같은 계정의 다른 작업 점유 반례를 추가했다.

**기존 실패 시나리오 재대조**
한도 2에서 A가 unknown이면 예약 1을 유지하므로 독립 B/C를 둘 다 새로 제출할 수 없다. 원격 성공이 확인된 뒤에는 생성 슬롯을 해제하면서 다운로드만 복구할 수 있다. 이는 ‘재생성하지 않음’ 원칙과도 충돌하지 않는다. 이전 보고서가 구분했던 중복 제출 방지와 전체 원격 동시성 통제가 이제 각각 규정되어 있다.

### P2-2 — 리액션 공개 순서와 비선형 서사: 해소

**실제 근거**
- `docs/design/02-reference-continuity.md:26–29`: 극중 인과·시간과 관객 공개 순서를 분리하고, 승인된 반응 선공개 후 원인 공개를 그대로 보존한다. 승인 없는 인과 역전 또는 설계의 공개 순서 위반만 오류로 판정한다.
- `docs/design/01-batch-contract.md:4–6`, `docs/design/04-qa-handoff.md:15–16`: 현재 프리프로덕션의 이야기와 공개 순서를 보존하는 기존 원칙과 정합적이다.
- `docs/design/05-validation-decisions.md:54`: 승인된 반응 선공개와 승인 없는 역전을 구별하는 계획을 추가했다.

**기존 실패 시나리오 재대조**
놀란 표정 다음에 파손된 소품을 공개하는 승인 보드는 이제 reaction이라는 이유만으로 반려되지 않는다. 그렇다고 모든 역전을 허용하는 것은 아니며, 승인된 인과·공개 순서 위반은 계속 오류로 남는다.

## 남은/새로운 조치 필요 발견

**없음.** 이전 반례를 막는 규칙이 상세 계약에 들어갔고, 검수·완료·참조 사용 조건에도 연결되어 있다. 이번 재검토에서 단순 문구 선호나 선택적 확장을 새 결함으로 추가하지 않았다.

특히 다음 연결은 유지된다.
- coverage의 계획 배정은 G0, 실제 요구 충족은 G5가 검사하므로 파일/구간 존재를 서사 충족으로 오인하지 않는다.
- 과거 원격 성공은 보존하되 현재 유효성은 별도로 판정하므로 재개 기록과 stale 차단이 충돌하지 않는다.
- 독립 노드는 유지하고 영향받은 후손만 재검수하므로 배치 병렬성과 연속성 보존을 함께 만족시킬 수 있다.
- 조건부 참조의 imports별 적합성 판정과 사용자 정책·포스트 수령 확인은 계속 필요하다(`docs/design/04-qa-handoff.md:28–32`).

## 범위·한계

- `README.md`, `docs/design/00-overview.md`부터 `05-validation-decisions.md`, `docs/reviews/remediation-01.md`를 현재 파일에서 전부 재독했다. 총 365줄이다.
- 첫 보고서의 네 결함 해소 및 보완으로 인한 모순을 중심으로 한 독립 정적 설계 재검토다. 인접 프로젝트·실제 어댑터·계정 기능·공급자 동작은 확인하지 않았다.
- **T01–T34는 계획된 수락 사례이며 실행된 테스트가 아니다.** `docs/design/05-validation-decisions.md:13–14,43–44,59–64`와 보완 추적 문서의 미실행 표기를 그대로 유지해 해석했다.
- 프로젝트 문서 수정, 구현, 생성, 외부 작업, 설치, 커밋, 위임은 하지 않았다. 지정된 보고서만 작성했다. 작업 디렉터리는 Git 저장소가 아니므로 staging은 해당하지 않는다.

## 권장 다음 단계

문서 설계의 네 건은 종결하고, 다음 승인 단계에서 coverage·revision/CAS·슬롯 복원·서사 예외의 로컬 계약 테스트를 구현·실행한다. 실행 결과가 나오기 전에는 이 PASS를 운영 준비 완료나 실제 품질 검증으로 확대하지 않는다.

```acceptance-report
{
  "criteriaSatisfied": [
    {"id":"criterion-1","status":"satisfied","evidence":"현재 설계 문서와 보완 추적을 읽기 전용으로 재검토하고 지정 보고서만 작성했다."},
    {"id":"criterion-2","status":"satisfied","evidence":"이전 네 발견 각각에 실제 파일·줄번호와 기존 실패 시나리오의 차단 근거를 제시하고 미실행 테스트를 구분했다."}
  ],
  "changedFiles": ["/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/fa7ea6f7-546d-43e7-8a17-bd48a587b36f/reviews/production-design-independent-review-02.md"],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {"command":"for f in README.md docs/design/0*.md docs/reviews/remediation-01.md; do echo \"--- $f\"; nl -ba \"$f\"; done","result":"passed","summary":"현재 대상 문서 전체를 줄번호와 함께 재독"},
    {"command":"wc -l README.md docs/design/0*.md docs/reviews/remediation-01.md; if git rev-parse --show-toplevel 2>/dev/null; then git diff --cached --name-only; else printf 'NOT_A_GIT_REPOSITORY\\n'; fi","result":"passed","summary":"365줄 및 Git 저장소 아님 확인"}
  ],
  "validationOutput": ["문서 수준 PASS", "기존 4건 해소, 새로운 조치 필요 발견 없음", "T01–T34 및 구현·원격 검증 미실행"],
  "residualRisks": ["실제 구현의 원자성·복원·검수 능력은 아직 검증되지 않음", "공급자 기능과 프로젝트별 실행 권한은 별도 확인 필요"],
  "noStagedFiles": true,
  "diffSummary": "프로젝트 변경 없이 지정된 2차 한국어 검토 보고서만 작성",
  "reviewFindings": ["미해결 또는 신규 차단 사항 없음; 이전 P1 2건·P2 2건 문서 수준 해소"],
  "manualNotes": "Git 저장소가 아니므로 staging 해당 없음. 이 판정은 설계 재검토에 한정하며 테스트 실행이나 운영 승인을 의미하지 않는다."
}
```
