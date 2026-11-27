# 구현 독립 리뷰 03 보완

원본: [implementation-review-03.md](implementation-review-03.md). 독립 판정은 REVISE이며 이 추적 문서는 PASS를 대신하지 않는다.

- [x] N3 재현: 실제 선택한 optional source invalid + media/approval 부재, conditional pose/import 충돌, valid flag만 true인 stale fingerprint가 consumer 재검수에 통과함을 RED에서 확인. `qa/implementation/review3-n3-red.txt`: 3 failed, 5 passed.
- [x] 좁은 수정: 명시적으로 생략한 미소비 optional만 건너뛴다. 나머지는 source 존재·현재 검수 fingerprint·imports에 대한 usable을 모두 요구한 뒤 media/approval 핀을 무조건 검사한다. 원격 시도/원래 binding은 수정하지 않는다.
- [x] `review3-n3-green.txt`: 33 passed. `full-after-review3-fixes.txt`: 154 passed (39.46s). typecheck 0 errors/warnings; package 5/findings []; acceptance 34 mapped/42 executed, live/perceptual false; 보호 3개 해시 동일 (`*-after-review3-fixes.*`).
- [x] 같은 검수자 run 3449daea-aea6-4e23-98aa-69004d4b9205의 [review 04](implementation-review-04.md): N3 resolved, scoped PASS. 76/76 소스 해시 동일, 전체 154/집중 33 독립 실행 통과.

회귀는 실제 CLI invalidate → revalidate → progress를 포함한다. required invalid control, 미선택 optional 생략과 imports 무관 conditional의 유지 경로도 검증한다. provider/semantic 관측은 fixture이며 로컬 probe/decode만 실제 기술 검사다. 실제 생성·지각 품질·설치·배포는 범위 밖이다.
