# WO-13 사전 검증 증거와 범위

| 검사 | 재현 명령 | 판정 범위 |
|---|---|---|
| 바이블·콘티·인덱스·시트 | `python3 -m pytest -q tests/test_index_lint.py tests/test_assemble_sheet.py` | 합성 입력의 핀 연결, stale, 셀 매핑 및 HTML 분기 |
| 프롬프트·전체 배치·제출 차단 | `python3 -m pytest -q tests/test_prompt_lint.py tests/test_prompt_batch.py tests/test_submission_gate.py` | EX-02 분할과 실패/미검증 차단; 승인 판단을 실제 사용자 입력으로 실행한 것은 아님 |
| 전환 준비 | `python3 -m pytest -q tests/test_cutover_preflight.py` | 임시 대상에서 파일 누락과 충돌 탐지, 기존 링크 불변 |

## 종단 점수 집계

`python3 scripts/e2e_grade.py --evidence-root qa/wo-13 --runs qa/wo-13/runs.json`

실행당 `scenario`, `variant`, `run_id`, `reviewer_id`, `model`, `reasoning`, `brief_sha256`, `input_tokens`, `output_tokens`, `elapsed_s`, `conti_s`, `checks`를 기록한다. `checks`의 키 "1"~"13"은 각 `{"score": 0, "evidence": "v2/X-1/review.md"}` 형태다. 증거는 루트 내 비어 있지 않은 파일이어야 하며 실제 항목을 뒷받침해야 한다. 별도 채점자가 내용과 세션 식별을 확인한다. 스크립트는 입력의 진실성이나 리뷰 내용까지 인증하지 않는다.

종료 0: 시나리오별 기준 충족 / 1: 완전한 증거 있으나 기준 미달 / 2: 입력 오류 / 3: 증거 미완·비교 불가. 현재 실제 runs 기록은 비어 있으며 종료 3으로 확인했다. 점수 통과는 배포 승인도 실행 권한도 아니다.

이 표는 로컬 검사 재현 목록이다. WO-13의 X-1~X-3 v1/v2 동일 모델 종단 비교, 에이전트 행동, 토큰·시간 비용, 실제 모델/미디어, 브라우저 독립 시각 검수는 미실행이다. 통합 합격이나 릴리스 승인 증거로 쓰지 않는다.
