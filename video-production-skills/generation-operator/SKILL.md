---
name: generation-operator
description: "Use when preparing or reconciling an authorized AI video generation attempt, reference binding, or downloaded take."
disable-model-invocation: true
---
# generation-operator

## 입력
총괄의 clip/attempt, 입력 핀·참조 역할, 현재 capability/authority와 prepared packet. [운영 계약](../docs/operations.md)을 먼저 읽는다.

## 절차
1. 로컬 원본/채택구간·native ID/role/ready·선택 목록을 대조한다. 미지원 영상/음향 참조를 이미지/텍스트로 임의 대체하지 않는다.
2. 클립별 승인된 길이·출력 크기/화면비·요청 음향·scope/configuration grant를 capability와 따로 확인한다. prepare 후 총괄이 reserve를 영속 기록했는지 확인한다. 현재 설정/전송 권한/실제 Unlimited 버튼 또는 승인된 비용을 제출 직전 재확인한다.
3. 실제 공급자 도구로 제출할 때는 확인된 현재 계약만 사용한다. 이 패키지는 공급자 호출 기능이 없으므로 설치된 지원 실행자를 사용하고 실제 tool/arguments·응답을 남긴다. 최종 payload를 바꾸면 다시 검사한다.
4. 반환된 작업 ID를 즉시 총괄에게 전달하고 observe/record_observation으로 먼저 원장에 보존한다. 로컬 입력이 망가졌어도 원격 사실 저장을 기다리지 않는다. 진단 오류 뒤에는 status로 이미 저장된 job ID를 확인하며 재제출하지 않는다. timeout이면 unknown으로 보고한다. 이력 첫 페이지 부재를 미접수라고 간주하지 않고 대조를 계속한다. 재제출·유료 대안·계정 변경은 별도 권한 필요.
5. 해당 job 결과 원본을 다운로드하고 probe로 실제 길이/프레임/FPS/크기/음향·디코드를 확인한다. 참조 썸네일을 출력으로 오인하지 않는다.

## 납품·완료
정확한 receipt·take 후보·해시·기술 probe와 남은 불확실성을 반환한다. 원격 성공/다운로드는 예술적 채택이 아니다. 개별 부서는 원장을 직접 갱신하지 않는다.
