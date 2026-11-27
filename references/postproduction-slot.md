# 포스트프로덕션 연결 슬롯

상태: **package path registered / entry unavailable**.

사용자 요청으로 video-postproduction-skills 디렉터리는 공용·agent 검색 경로에 등록했다. 현재 패키지에는 SKILL.md 진입 파일이 없으므로 실행 스킬 적용은 미완료다. 별도로 제작 중인 패키지의 파일·위치·설계는 변경하지 않는다. 실제 entry가 준비되기 전에는 추측한 스킬 이름을 호출하지 않는다.

## 향후 연결 계약

사용자가 준비된 패키지의 실제 진입점과 사용 승인을 제공하면 이 문서의 상태·entry·계약을 갱신하고 인계 QA 후 연결한다. 폴더나 README가 생겼다는 사실만으로 자동 활성화하지 않는다.

- 입력: 실제 production handoff, selections와 정확한 range/revision/hash, join/flow 근거, 권리·전송 범위, 요청한 러닝타임·화면비·출력·자막·음향 요구.
- 수령: 실제 담당자의 검증된 receipt/수령 근거. G5 수령이나 조건부 결함 인수는 기존 계약대로 확인.
- 출력: 실제 최종 master 경로·핀, 편집/음향/자막 납품, 필수 전구간 시청·청취와 기술 검수 근거.
- 재개: 현재 원장 위치, 마지막 판정, 미해결 결함과 원격 unknown, 다음 실제 명령/입력을 전달.

## 현재 차단 시 응답

최종 영상 요청은 요청 목표=final master로 유지한다. 가능한 승인된 프리/프로 작업은 진행하고, 필수 post receipt가 없으면 G5도 blocked로 남긴다. 실제 산출물과 sources_ready 여부, G5/포스트 미연결, 필요한 entry/receiver, 재개점을 보고한다. 러프 연결본·소스·인계 패킷을 최종 영상이라 부르지 않는다. 임의 FFmpeg/legacy P7 대체 구현을 추가하지 않는다.
