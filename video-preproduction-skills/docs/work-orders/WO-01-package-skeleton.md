# WO-01 — 패키지 골격·manifest·스킬 검사기

**Goal:** 20개 스킬 디렉터리와 공통 골격, 패키지 정본 목록, 골격 검사기를 만든다.
**Spec:** DES-00 §5 D1/D7, DES-02 §2 · **의존:** 없음

## Files
- Create: `manifest.json`, `README.md`(설계 링크 포함 갱신), `CHANGELOG.md`
- Create: `<skill>/SKILL.md` ×20 (골격만: frontmatter + 7개 헤딩 + "WO-xx에서 작성" 표시)
- Create: `scripts/check_skills.py`, `tests/test_check_skills.py`, `pytest.ini`

## Interfaces
- Produces: `check_skills.py [--root PATH] [--json]` → exit 0/1. 검사 코드:
  - `SK01` frontmatter `name` ≠ 디렉터리명
  - `SK02` 공통 7개 헤딩 누락/순서 오류 (`역할, 입력, 절차, 산출물, 다른 부서와의 경계, 자체 점검, 납품`; 감독은 `역할, 단계표, 콜시트, 게이트, 승인, 직행, 마감`)
  - `SK03` 크루 description 길이 초과 또는 "production-director" 미포함
  - `SK04` manifest `skills`와 디렉터리 불일치
  - `SK05` (경고) 전체 description 추정 토큰 > 2,500 — 추정식: 영어 단어×1.3 + 한글 글자×0.9
  - `SK06` 깨진 상대 링크(references/, assets/, ../)
  - `SK07` 레퍼런스 내용 누출: `docs/examples/*/leak-terms.txt`의 단어가 스킬 디렉터리·`tests/`·`evals/`에 등장 (DES-09 §5 Q-5)

## Steps
- [ ] **1. 실패 테스트 작성** — `tests/test_check_skills.py`
  - `test_name_mismatch_SK01`: 임시 디렉터리 `foo/SKILL.md`에 `name: bar` → 결과 코드에 `SK01`
  - `test_missing_heading_SK02`: `## 절차` 없는 크루 → `SK02`
  - `test_crew_description_too_long_SK03`: 41단어 → `SK03`
  - `test_manifest_mismatch_SK04`
  - `test_description_budget_warning_SK05`: 20개×130단어 → 경고 존재, exit 0
  - `test_broken_link_SK06`
  - `test_reference_leak_SK07`: 임시 leak-terms에 `zebra-term`, 스킬 references에 같은 단어 → `SK07`
- [ ] **2. 실행해 실패 확인** — `pytest tests/test_check_skills.py -q` → 6 failed
- [ ] **3. `check_skills.py` 구현** — 표준 라이브러리만, frontmatter는 첫 `---` 블록의 `key: value` 줄만 파싱(YAML 라이브러리 금지)
- [ ] **4. 통과 확인** — 6 passed
- [ ] **5. 20개 골격 생성** — description은 [초안 20개](../design/skill-descriptions.json)를 기준으로 작성. `python3 scripts/budget_descriptions.py`는 초안 추정치이며, 설치 검증은 실제 등록된 설명문과 하네스 측정값을 따로 기록
- [ ] **6. 실제 패키지 검사** — `python3 scripts/check_skills.py --json` → SK01–SK04, SK06, SK07 0건. SK05 토큰 추정치를 `qa/wo-01/description-budget.json`에 저장
- [ ] **7. 위험 R1 판정** — 추정치 > 2,500이면 DES-00 D1 재검토 메모를 `qa/wo-01/R1.md`에 작성하고 감독에게 보고(구현 중단 아님)
- [ ] **8. 커밋** — `feat(v2): package skeleton and skill checker`

## Acceptance
- 20개 디렉터리, `check_skills.py` 0 error, 토큰 추정치 기록.
