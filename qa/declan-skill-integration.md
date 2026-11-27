# Declan 자료 스킬 반영 — 2026-11-28

## 승인·범위
사용자가 설계와 기대 효과를 확인한 뒤 “좋아 반영하자”로 반영 승인.
정본: docs/superpowers/specs/2026-11-28-declan-skill-integration-design.md.
실행 지침 변경은 프리의 film-editor/SKILL.md, concept-benchmark/SKILL.md 두 파일뿐이다. 출처는 Declan 한정 조사 문서에 유지하고 사적 대화/미디어는 복사하지 않았다.

## 기준선 감사와 실제 변경
기존 파일은 /tmp/declan-skill-integration-before/에 보존했다.
- film-editor: 진입/이탈·홀드·J/L컷·시간 근거는 이미 있어 유지. 의미 전달 모션의 명시 시작/종료 계약은 기존 승인 설계에만 있고 실제 현재 SKILL에는 없어 이번 A/B 문단과 한 번만 통합했다. 중심/보조의 시선 경쟁·정착 순서, 도식 연결 대상/방향/색과 공개 순서의 조건부 판단을 보강했다.
- concept-benchmark: BMK의 시장 지표 비교와 BRF 잠금·BOR는 유지. 룩 자체를 비교할 때 내용·구도·길이·화면비 차이를 통제/한계로 표시하는 지침, 확정 룩 재선택 방지와 새 샘플 생성의 소유권을 짧은 문단으로 보강했다.
- no-op: 기존 영상 실제 확인·시장 지표·서사 연속성·호출 플래그·description은 변경하지 않았다. 후반 motion-compositor·루트 라우팅·등록·스키마·원장은 변경하지 않았다.

이 기준선은 **기존 지침의 명시 계약에 대한 작성자 감사**다. 새 컨텍스트 모델의 실제 실패 출력이나 인과적 행동 RED/GREEN 시험은 수행하지 않았다. 지침에 없다는 사실만으로 모델이 반드시 실패한다고 주장하지 않는다.

## 설계 사례 대조 — 문안 자체 점검, 행동 PASS 아님
| 사례 | 반영/보존된 계약 |
|---|---|
| A1 시선 경쟁 | 중심 요소와 보조 요소의 강조/시작/정착 순서 |
| A2 정상 단일 강조 | 추가 모션 계층/양식 요구 없음; 기존 해당 모션 시간 계약만 사용 |
| A3 승인된 혼란/동시 강조 | 승인 의도 보존 |
| B1 잘못된 관계 | 연결 대상·방향·색 의미 대조 |
| B2 결과 선공개 | 승인된 공개 순서 유지, 일률 시간순 교정 없음 |
| B3 일반 대화 | 도식 항목 비적용 |
| C1 다른 내용 demo | 내용/구도/길이/화면비 통제 또는 비교 한계; 선호와 성능/성과 구분 |
| C2 스타일 확정 | 재선택 없음 |
| C3 샘플/권한 없음 | 필요한 입력 반환, 감독/오케스트레이터에 요청; 직접 생성/결제/전송 없음 |
| unsupported native motion | 후반 기존 실행 계약 그대로 사용. 새 지원 선언/백엔드/설치 없음 |

## 실행한 검사
- `python3 scripts/check_skills.py --json` (프리 루트): 20 skills, findings=[]; /tmp/declan-integration-package.json.
- `python3 -m pytest -q` (프리 루트): 273 passed in 5.29s; /tmp/declan-integration-pytest.txt.
- `node --test qa/routing-contract.test.mjs`: 8 passed, 0 failed/skipped. 여섯 기존 등록 경로가 현재 정본과 동일한 스킬 바이트를 참조하는 검사 포함.

## 검증 한계
PASS로 확인한 것은 패키지 구조와 기존 로컬 회귀다. 행동/의미 판단·새 컨텍스트 대조·독립 검수·실제 모션 렌더·전구간 시청/청취·품질/재작업 감소는 UNVERIFIED다. 위임·외부 실행·새 설치·유료 생성·커밋·푸시는 하지 않았다. 이번 문서 변경 때문에 프로/포스트 구현 전체 회귀를 다시 실행한 것으로 주장하지 않는다.

## 최종 확인
PASS: 두 스킬의 frontmatter/호출 플래그/description이 수정 전과 동일하고 모든 로컬 링크가 존재한다. 수정 전 해시와 비교해 다른 18개 프리 SKILL은 동일하며 변경된 SKILL은 film-editor/concept-benchmark뿐이다. 등록 경로는 기존 정본 symlink를 유지했다. root와 변경된 프리 파일의 `git diff --check` 통과. 이 확인은 지침/등록의 현재성 증거이며 행동 준수 증거는 아니다.
