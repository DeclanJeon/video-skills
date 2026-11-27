# SND — 작성 양식

이 문서는 양식이다. 예시·미정 값은 정본으로 등록하지 않는다.

## policy

audio_path / 근거 / 무음·음악·권리 / 요청 범위(설계·텍스트-only·실제 소스 확보)

단계별 준비/등록/영향 판단은 [사운드 통합 정본](../../docs/design/11-sound-sourcing-integration.md)을 따른다. 설계 current와 실제 확보/권리/최종 청취 ready는 다르다.

## speech-rate

측정 또는 추정 / 출처 / 언어 단위

## 큐

VOC / AMB / SFX / MUS / 컷·대사·시간·공간

| cue_id·cue_ref | use_stage | required·근거 | 컷·대사 | 작품 사용 구간(초) | source in/out·실측/추정 길이(초) | 기능·감정·질감 | 루프·끝맺음 | 전경/배경·거리 | 대사 회피·덕킹/J/L 의도 | 금지·무음 사유 |
|---|---|---|---|---|---|---|---|---|---|---|

use_stage: generation_input / post_only / design_only. rights_ref·review_ref 및 소스 원장의 현재 등록 핀도 기록한다. generation_input만 해당 제출의 실제 오디오 입력이며 post_only는 후반 배치 의도다.

## 탐색·후보 비교

- 실제 소스 확보 / 텍스트 전용 / 다운로드 금지의 요청 범위:
- 플랫폼·수익화·유료광고·고객사/수령자 이용 범위와 승인 근거:
- 자료처 정본: [자료처 CSV](/home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-skills/free_commercial_media_resources_50.csv) (작품 사본에서는 실제 정본 위치/버전 기록). 별칭에서 `../`로 탈출하지 않고 이 절대 경로 또는 `<skills-root>/video-skills/free_commercial_media_resources_50.csv`로 읽는다.
- 작품의 검색 기록 파일·버전: [검색 기록 양식](audio-search-log-template.csv)
- 필요 유형별 실제 검색한 사이트·검색어·필터·접근 차단·미탐색 범위:
- 큐별 후보 비교·선정/탈락 이유 (제목/태그가 아니라 실제 청취와 요구 적합성 근거):

## 확보 소스·권리·청취

- 작품의 소스 원장 파일·버전: [소스 원장 양식](audio-source-manifest-template.csv)

| cue_id | candidate_id | 로컬 경로·버전·SHA-256 | 원본·저작자 URL | 개별 라이선스·허용 범위·확인일·증빙 | 정확한 크레딧 | Content ID 상태·대응 | 다운로드·decode 상태 | 최종 파일 청취 구간·방법·관측 | 선정 상태·미해결 |
|---|---|---|---|---|---|---|---|---|---|

후보/권리 확인/다운로드/청취/채택 상태는 구분한다. 미확인을 완료로 채우지 않는다. 필수 큐의 파일·권리·최종 파일 청취가 미완이면 소스 확보는 partial/blocked다.

## 포스트 인계

| cue_id | 컷·작품 시간 | 소스 in/out·단위 | 루프 구간·단위 | 전환·대사 덕킹 의도 | 파일 핀 | 증빙·크레딧 위치 | 수령자 원본 전달 허용 범위 | 미해결·다음 작업 |
|---|---|---|---|---|---|---|---|---|

- 설계 완료 판정과 근거:
- 필수 소스 확보 완료/partial/blocked 판정과 근거:
- 실제 파일・큐시트・검색/소스 기록・권리 증빙 묶음의 위치:
- 누락된 필수 큐·정확한 재개점:

실제 배치·트리밍·믹싱·마스터 검수는 포스트 담당이다. 위 사용 구간은 편집 지시이며 실제 적용/청취한 상태와 구분한다. 원장 등록은 감독이 수행한다.
