# video-production-skills — AI 영상 프로덕션 설계

상태: **로컬 구현 · 미릴리스 · 미설치**. [설계 1차 지적](docs/reviews/independent-review-01.md) 4건을 보완하고 [2차 재검수](docs/reviews/independent-review-02.md)에서 문서 수준 통과했다. 현재는 5개 역할 스킬과 로컬 배치/참조/복구/QA/인계 CLI를 구현했다. 실제 공급자 전송·생성·컨디셔닝·예술적 품질은 검증하지 않았다. 구현 최종 검수와 진행 상태는 [활성 목표](.ultragoal/goals/active/implement-production-design/goal.md)에 기록한다.

프리프로덕션의 승인된 캐릭터·에셋·보드·영상 프롬프트를 받아, 여러 클립을 참조 의존성에 맞게 생성하고 검수·채택하여 포스트프로덕션에 인계한다.

## 문서 지도
| 문서 | 소유하는 설계 |
|---|---|
| [00 개요](docs/design/00-overview.md) | 목표, 경계, 사용자 요구, 전체 구조 |
| [01 인계·배치 계약](docs/design/01-batch-contract.md) | 필수 데이터, 권한, 시간 기준, 역할 경계 |
| [02 참조·연속성](docs/design/02-reference-continuity.md) | DAG, 실제 입력 결속, 드리프트, 변경 영향 |
| [03 실행·복구](docs/design/03-execution-recovery.md) | 상태 전이, 제출/재개, 동시성, 실패 |
| [04 QA·포스트 인계](docs/design/04-qa-handoff.md) | 검사 게이트, 조건부 채택, 완료율, 납품 |
| [05 검증 계획·결정](docs/design/05-validation-decisions.md) | 수락 사례, 구현 경계, 단계별 검증 |
| [설계 문서 검토](docs/design-review.md) | 문서 자체 점검과 남은 검증 |

## 분리 원칙
- 프리프로덕션: 무엇을 만들지 설계. 기존 `../video-preproduction-skills/`는 수정하지 않는다.
- 프로덕션: 실제 소스를 생성하고 채택. 기존 공급자 실행 스킬·원장·검사기를 재사용한다.
- 포스트프로덕션: 채택 소스를 편집·합성·믹싱·최종 출력. 여기서는 검수용 러프 연결본과 편집 인계까지만.
- 작품 데이터는 작품 프로젝트에 저장한다. 이 패키지에 얼굴 원본·인증 정보·실제 작품 원장을 넣지 않는다.

## 실행·검증

- [운영 절차와 제한](docs/operations.md), [예제](examples/README.md), `schemas/`의 입력 계약을 먼저 확인한다.
- `python3 scripts/production.py --help`: 로컬 명령. 외부 upload/generate 기능은 없다.
- `python3 scripts/check_package.py --json`: 5개 스킬 구조·리소스·스키마 검사.
- `python3 scripts/check_acceptance.py --json`: T01–T34에 매핑한 실제 로컬 계약 테스트 실행. 미디어 의미 검수는 보고서 fixture이며 실영상 예술적 검증이 아니다.
- `python3 -m pytest -q`, `basedpyright production`.

자동 호출은 꺼져 있고 패키지는 설치하지 않았다. 실제 외부 실행은 현재 지원하는 기존 실행자와 해당 프로젝트 승인 범위가 있을 때만 수행한다. 설계·로컬 테스트 통과는 외부 전송·과금·설치·게시 승인과 별개다.
