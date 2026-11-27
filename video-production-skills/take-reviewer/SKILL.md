---
name: take-reviewer
description: "Use when assessing a generated take against approved actions, acting, camera, identity, or audio requirements."
disable-model-invocation: true
---
# take-reviewer

## 입력
현재 요구 ID/설계·에셋, 실제 원본과 채택 후보 구간, request fingerprint. [QA 계약](../docs/design/04-qa-handoff.md)을 읽는다.

## 절차
1. 실제 파일·구간을 열어 전구간 재생한다. 오디오가 있으면 해당 구간을 실제 청취한다. 도구가 없으면 미검증이며 프레임/설명문만으로 운동·청취 PASS를 내지 않는다.
2. 사건·대사/화자·공개·연기·카메라·접촉·얼굴·의상·에셋·음향·문자/워터마크를 요구별로 관찰한다. 기술 probe와 의미 관측은 별도다.
3. playback 파일 해시/구간·검수자·증거, fulfilled ID와 결함 속성/프레임을 적는다. approved 예외는 locator와 대조한다.
4. accepted/conditional/rejected를 제안한다. conditional은 필수 행동/대사/정체성 결함을 숨기지 않고 실제 후반 수정 가능 근거·정책·수령자를 요구한다.
5. 총괄이 현재 fingerprint/CAS와 후보 및 소비한 source의 media/승인 핀·설정 grant를 재검사해 최초 review와 재검수를 반영한다. 실제로 선택한 optional history도 검사하고, 명시적으로 생략한 미소비 optional source와 구별한다. 승인 증거가 바뀌면 원격 성공 이력은 보존하고 채택은 차단한다. 검수 중 입력이 바뀌면 새 유효성 판정이 필요하다. 새 승인으로 재검수하더라도 과거 요청 핀을 덮어쓰지 않는다.

## 납품·완료
Review와 관측 증거·정확한 문제 구간·수정 소유자를 반환한다. 코드의 증거 필드 검사는 실제 시청·청취의 진실성을 인증하지 않는다. 원장 쓰기/외부 재생성은 총괄 권한이다.
