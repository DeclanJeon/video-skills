# 감독 검수 증거 — 로컬 회귀

- E-05, E-09, E-10의 제출 금지 조건을 `tests/test_submission_gate.py`에서 기계적으로 재현한다. 종료 1/2/3, 리뷰 반려, 승인 없음, 예산 초과, 검수 뒤 바이트·엔드포인트 변경은 각각 차단된다.
- `tests/test_prompt_batch.py`의 EX-02 통합 사례는 실제 배치 종료 3을 함수에 넘겨, 다른 조건을 테스트용으로 충족시켜도 제출이 막히는지 확인한다.
- 위 결과는 에이전트 행동 평가를 대체하지 않는다. v1 기준선과 독립 세션의 E-01–E-10은 미실행. 특히 라우팅·재개·콜시트·연출 노트 사례는 행동 증거가 없다. 생성·비용·게시 호출은 실행하지 않았다.

재현: `python3 -m pytest -q tests/test_submission_gate.py tests/test_prompt_batch.py`.
