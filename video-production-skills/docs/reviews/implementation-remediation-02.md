# 구현 독립 리뷰 02 보완

원본: [implementation-review-02.md](implementation-review-02.md). 이 문서는 코드/회귀 보완 추적이며 PASS 판정이 아니다.

- [x] N1: ProjectStore.record_observation은 기존 attempt의 원격 Receipt만 받아 모델·lock·CAS·payload digest·request/job·전이 검사를 유지하고 사실을 같은 namespace에 먼저 fsync한다. mutable scope 진단은 뒤의 별도 commit이다. status/read_recorded로 입력 손상 중에도 알려진 ID를 읽되, reserve/채택/인계는 기존 current-input 게이트를 유지한다.
- [x] N1 회귀: 입력 삭제/해시 변경, 무관한 clip dependency 손상, coverage 파일 부재 중 acknowledged ID 보존. terminal success/failure/cancel 후 해당 slot만 해제, 다른 unknown 예약 유지. wrong receipt/CAS·local downloaded 우회 거절. 진단 중단/두 번째 디스크 쓰기 실패/비협조 writer 변경 시에도 먼저 저장한 사실을 보존.
- [x] N2/F4: 생성 최초 채택도 실제 consumed binding과 필수 source의 현재 media/approval을 검사한다. 후보 자신과 source의 승인 파일을 분리한 회귀로 원래 누락이 재현됨을 확인했다.
- [x] N2 회귀: required/chosen-optional source의 승인 또는 media drift는 own approval과 fingerprint가 그대로여도 차단. 명시적 생략 근거가 있으며 실제 선택하지 않은 optional source는 잘못 소비한 것으로 처리하지 않음.
- [x] 복구 경계 보강: 첫 재관측이 running/terminal이어도 정확한 request/job 확인으로 기록. 요청 digest 손상·known-job nonreceipt 모순 거절. 저장으로 source 또는 exported origin의 자기 핀을 깨는 init/일반 commit 거절.
- [x] 전체 로컬 혼합 suite 146 passed: `qa/implementation/full-after-review2-fixes.txt` (31.44s). 최종 type/package/acceptance/protected 재검은 아래 goal 근거를 따른다.
- [x] 같은 검수자의 [review 04](implementation-review-04.md)에서 N1/N2 및 N3 보완까지 현 스냅샷 scoped PASS 확인. 이전 판정은 보존.

다른 로컬 소스 reuse/scope·G5·coverage 계약은 유지한다. 실제 provider·외부 전송·설치·결제·Git 실행 및 지각 품질 검증은 여전히 이 목표 범위 밖이다.
