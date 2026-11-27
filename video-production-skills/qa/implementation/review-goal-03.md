---
slug: implement-production-design
type: pi-ultragoal
status: active
verification: independent
created: 2026-11-26
---

# Objective
独立再검수 PASS인 docs/design/00–05를 실행 가능한 프로덕션 스킬 패키지로 구현한다. 승인된 프리프로덕션 인계, 전체 클립 배치·다중 참조·연속성, 실행/복구, QA·포스트 인계의 로컬 계약을 테스트로 증명한다. 진행률 100%는 아래 12개 항목의 실제 검증과 최종 독립 검수 통과를 뜻하며 계획/모의 원격 응답을 실제 생성 성공으로 세지 않는다.

# Context
- 대상: /home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-production-skills (현재 비Git 프로젝트).
- 설계: docs/design/00-overview.md–05-validation-decisions.md. 독립 재검수: docs/reviews/independent-review-02.md.
- 기존 프리프로덕션 패키지와 작품별 원장은 수정하지 않는다. 기존 공유 실행 장비/검사기의 실제 계약을 확인하고 명시적 어댑터로 연결한다. 새 경쟁 원장·가짜 공급자 API를 만들지 않는다.
- Python 3.14.4 및 pytest 9.1.1 사용 가능. 새 패키지 설치 없이 로컬 구현·픽스처·검사 우선. 기존 도구로 불가능하면 경계를 기록하고 승인을 구한다.
- 구현 계획의 구조·정확한 CLI를 먼저 문서화하고 아래 검증 명령으로 연결한다. 테스트 파일 이름은 계획된 출력이며 지금 존재/통과한다고 주장하지 않는다.
- 이번 목표의 범위는 스킬·로컬 실행 계약·기존 지원 커넥터용 요청/결과 어댑터·재개 및 인계다. 실제 유료/Unlimited 생성, 외부 에셋 전송, 실영상 품질 인증, 설치/전환/배포/게시/Git 생성·커밋은 제외한다. 로컬 모의 어댑터 검증은 mock이라고 표시한다. 실제 공급자 접속·시청/청취 검증은 별도 권한으로 후속 수행한다.
- 노력: 고정 토큰/횟수 한도 없이 이 세션에서 유용한 작업을 계속하되 안전 차단·사용자 정지·필수 능력 부재 시 중단 사유와 재개점을 저장한다. 세션 종료 후 자동 실행 지속을 약속하지 않는다.
- 검수: 독립. 기존 worker/workflow 재시작 금지 유지. 새 최종 읽기 전용 검수자 1명에 대한 별도 승인을 활성화 확인 시 요청한다. 구현은 부모가 수행하고 목표 파일 단일 writer를 유지한다.

# Rubric
- [x] R01 역할 스킬 5개와 패키지 구조 구현 — check: `python3 scripts/check_package.py --json` → 총괄/operator/take/continuity/handoff의 입력·출력·권한·검수 경계 및 문서/템플릿 링크 오류 0.
  - Evidence: Fresh package-after-review2-fixes.json: skills 5, findings [], all 12 public schemas current.
- [x] R02 프리프로덕션 필수 coverage 완전성 — check: `python3 -m pytest -q tests/test_coverage.py` → 최초 누락·다중 shot 일부 누락·미충족 납품을 차단하고 승인된 재사용/제외만 허용.
  - Evidence: Fresh full-after-review2-fixes.txt: 146 passed, including coverage/reuse_scope/review_regressions; complete upstream closure, exact approved scope and real local reuse remain exercised.
- [x] R03 다중 참조 DAG와 계획 순서 — check: `python3 -m pytest -q tests/test_dependencies.py` → 필수 선행 채택 전 실행 차단, 독립 노드만 ready, 재등장/순환/선택 참조의 역할 검사.
  - Evidence: Fresh full suite 146 passed, including dependency DAG/order/optional-rationale tests; no old result used as current evidence.
- [x] R04 native 참조 요청 결속 — check: `python3 -m pytest -q tests/test_bindings.py` → source/range/imports/excludes/role/readiness·권한 핀 대조, 미지원/초과 필수 참조·미승인 전송 거절. 실제 공급자 성공은 미주장.
  - Evidence: Fresh full suite 146 passed, including bindings 16 and review_regressions 14: exact native refs and scoped config/transfer grants remain enforced. No live provider certification.
- [x] R05 attempt lifecycle·슬롯·중복 방지 — check: `python3 -m pytest -q tests/test_execution.py` → 제출 전 예약, unknown 유지, 원격 종료 증거 해제, 계정 점유 반영, 중복 제출 거절.
  - Evidence: Fresh review2-boundary-green.txt: execution 11, observation_recovery 17, consumed_approval 6, recovery 12 = 46 passed. Unknown occupancy, known-job nonreceipt conflict, request digest and recovered intermediate/terminal receipt checks preserve original facts.
- [x] R06 영속 저장·단일 writer·재개 — check: `python3 -m pytest -q tests/test_recovery.py` → 임시 프로젝트에서 프로세스 재진입/부분 기록 실패/잠금 충돌을 실제 파일로 검사, 미확인 작업 재제출 0.
  - Evidence: Fresh 46-case boundary suite + full 146 passed. Actual CLI/file/lock/CAS tests cover input loss/hash drift/unrelated dependency/coverage loss, durable fact before interrupted diagnostics, second-publication disk failure, foreign writer conflict, self-pinned mutable storage rejection. read_recorded/status never grant generation readiness.
- [x] R07 revision/CAS·stale 전파 — check: `python3 -m pytest -q tests/test_revisions.py` → running/QA 반영 직전 교체·동일 바이트의 range/판정 변경 차단, 무관한 독립 노드 유지.
  - Evidence: Fresh full suite 146 passed including revisions, quality, review_regressions and consumed_approval. Existing late A→B result/CAS cases remain green; source approval/media physical drift is checked even with unchanged serialized fingerprint.
- [x] R08 QA·서사·조건부 채택 계약 — check: `python3 -m pytest -q tests/test_quality.py` → G0–G5 증거·시청/청취 미확인 차단·승인된 비선형 공개 허용·조건부 참조 제한. 의미 QA를 코드가 실제 시청했다고 주장하지 않음.
  - Evidence: Fresh quality 19 + consumed_approval 6 within full 146. Distinct own/source approvals prove required/chosen-optional drift blocks initial generated admission; explicitly omitted unused optional input remains allowed. Existing real decode + reported semantic/nonlinear/conditional cases pass; no actual watching/listening claim.
- [x] R09 전체 흐름·포스트 인계/진행률 — check: `python3 -m pytest -q tests/test_handoff.py` → 유효 coverage·접합·전체 재생 증거·구간/음향/권리 수령 조건 대조, 누락/분모 축소 100% 거절.
  - Evidence: Fresh full suite 146 includes handoff 12 and review_regressions 14: G5 source replacement/deletion negatives at library and actual CLI, exact flow/joins/ranges/coverage/receiver/rights; review montage only.
- [x] R10 기존 원장/실행 장비와의 로컬 인계 seam — check: `python3 -m pytest -q tests/test_adapters.py` → 실제 기존 계약에서 도출한 fixture/정확한 경로 매핑·요청 대조·모의 응답 결과 등록, 원본 원장 무단 수정/가짜 remote 성공 0. 검증 범위가 로컬 어댑터임을 명시.
  - Evidence: Fresh full suite 146 includes adapters 9 and review_regressions 14 using actual read-only upstream seams/project_index closure. protected-after-review2-fixes.json: all three protected hashes unchanged. No original/external mutation.
- [x] R11 34개 설계 수락 사례 추적·통합 검증 — check: `python3 scripts/check_acceptance.py --json` 및 `python3 -m pytest -q` → T01–T34 각 실제 테스트 node ID/결과 연결, 의도적 결함이 검출됨, 임시 프로젝트 CLI 통합 흐름 통과. 단순 사례 번호 존재를 테스트 실행으로 세지 않음.
  - Evidence: Fresh full suite 146 passed in 31.44s (full-after-review2-fixes.txt). acceptance-after-review2-fixes.json: valid true, 34 mapped / 42 executed cases; typecheck-after-review2-fixes.txt: 0 errors/warnings. All new RED evidence retained separately. live_provider_verified=false, perceptual_quality_verified=false.
- [ ] R12 현재 구현 스냅샷의 독립 최종 검수 — check: 승인된 새 읽기 전용 검수자 1명이 목표/전체 변경/테스트/제약을 검토 → 미해결 차단/중요 결함 0 및 실제 PASS 보고서·검사 스냅샷 해시 기록. 권한 없으면 unchecked/pending.

# Constraints
- 프리프로덕션·작품·공유 원본 변경 금지 — check: 착수 전후 지정 입력의 SHA-256 비교 → 동일. 임시 실행 테스트는 이 패키지 test temp만 사용.
- 외부 전송·생성·결제·게시·배포·설치·Git 작업 금지 — check: 사용 명령/어댑터 로그·독립 검수 → 외부 mutation 0. mock/fixture와 실제 결과를 분리.
- 사용자/다른 터미널 파일 소유권 보존 — check: 착수 스냅샷/변경 목록과 단일 writer 기록. 충돌 발견 시 중단, worker/workflow 자동 재시작 0.
- 실패·unknown·stale·미검증을 완료 집계하지 않기 — check: R05/R07/R09 및 독립 검수.

# Stop conditions
사용자 정지, 안전/권한 경계, 필수 입력/능력 부재, 다른 writer 충돌, 같은 검사에 새 증거 없이 3회 실패. 차단 시 paused와 미완료 항목·정확한 재개점을 기록한다. 네트워크 오류를 이유로 미확인 원격 작업을 재제출하지 않는다.

# Verification log
- 초안 준비: 대상 폴더·기존 목표/지침 존재 여부 조회. 기존 .ultragoal 목표 없음. Python/pytest 가용성만 확인. 구현/테스트 실행 없음.
- 사용자 활성화 승인으로 새 최종 읽기 전용 검수자 1명 권한 확보. 기존 worker/workflow는 재시작하지 않음. R12는 현재 스냅샷 검수 전이므로 미완료.
- 제약 검사: `qa/implementation/protected-inputs-result.json`에서 보호한 기존 코드 3개 SHA 동일. 이 세션의 변경은 이 프로젝트와 임시 테스트 루트뿐. 외부 생성/전송/결제/설치/Git 작업 없음.
- 독립 최종 검수 1차 REVISE: `docs/reviews/implementation-review-01.md`. F1–F5로 영향받은 7항목을 재개방. 당시 유효 완료 4/12 (33%); 아래 과거 통과 출력은 회귀 재검 전의 역사 기록이며 현재 완료 증거로 사용하지 않음.
- 기존 검수자 1명의 동일 목표 후속 재검토만 사용한다. 기존 설계 worker/workflow는 재시작하지 않는다. F1–F5 한 보완 패스의 RED→GREEN 및 전체 재검 완료. 1차 보완 직후 11/12 (92%)였으며 R12는 새 스냅샷 독립 재검토 전이라 미완료.
- 보완 추적: `docs/reviews/implementation-remediation-01.md`. 현재 새 스냅샷을 검사받고 이전 REVISE를 PASS로 덮어쓰지 않는다.
- Ruling: 원본 전체 closure는 로컬 dependencies로 보존하고 실제 전송 assets와 분리한다. 추가된 approved reuse/scope revision은 기존 R02의 긍정 경로 구현이며 외부 권한 확대가 아니다. 필수 upstream invalid 상태의 후손 재검수 우회는 허용하지 않고, 유효 conditional source의 imports와 무관한 결함만 별도 검수로 유지한다.

- 독립 재검수 02 REVISE는 N1/N2로 저장/채택 경계를 재개방했다. 추가 RED→GREEN 후 현재 146 mixed local tests, type/package/34-case acceptance 및 보호 3개 hash 재검 완료. 현재 검증된 완료 **11/12 (92%)**. R12는 새 스냅샷에 대한 같은 검수자의 후속 판정 전까지 미완료다. 보완: `docs/reviews/implementation-remediation-02.md`.

# Decision journal
- 사용자 요청: `/goal 설계내용들을 구현하자. 진행률 100%에 도달할때까지 작업을 계속해라.`
- 사용자 `응 진행해`로 이 목표 활성화와 새 최종 읽기 전용 검수자 1명을 승인했다. 구현은 부모가 수행하고 기존 worker/workflow는 재시작하지 않는다.
- Ruling: 비Git 프로젝트이며 Git 초기화/커밋은 제외 조건이다. 별도 worktree·Git 의존 SDD 스크립트 대신 현재 명시된 프로젝트를 단독 구현 workspace로 사용하고 로컬 계획/진행 기록으로 체크포인트를 남긴다.
- Ruling: 추가 행동평가 에이전트는 승인되지 않았다. R01은 스킬 문서·구조 검사이며 행동 준수 인증이 아니다. 새 최종 검수자 1명만 독립 검증에 사용한다.

# Lessons
- 독립 재검수 02 REVISE에서 N1(준비 검증과 원격 사실 영속화 결합), N2(생성 최초 채택의 consumed approval 누락)를 발견했다. 영향받은 항목과 packaging/full-suite 증거를 다시 열고 새로운 RED→GREEN 회귀를 추가했다. `docs/reviews/implementation-remediation-02.md`. 기존 PASS 소견/과거 출력은 보존하되 최종 완료로 재사용하지 않는다.
설계 문서 PASS는 구현·실제 시청/청취·공급자 기능 증거가 아니다. 순수 계약 검사로 예술적 품질 또는 실영상 생성까지 완료했다고 주장하지 않는다.
