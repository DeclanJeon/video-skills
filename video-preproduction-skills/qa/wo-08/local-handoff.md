# 에셋→콘티 로컬 인계 검증

재현: `python3 -m pytest -q tests/test_index_lint.py tests/test_assemble_sheet.py`

- `test_asset_bible_to_conti_board_and_timeline`: 임시 프로젝트에 인물·의상·장소·세트·환경·소품·목소리를 등록하고, 조명·환경음·연속성 원장·컷 연기 레이어 소비 핀을 함께 연결한다. 바이블, 보드, 타임라인 검사를 통과한 다음 소품만 새 버전으로 등록한다. 콘티 stale 및 바이블·보드의 낡은 참조 거절을 검증한다.
- `test_html_fallback_escapes_index_caption_and_maps_cells`: Pillow를 숨긴 분기에서 HTML과 매핑을 저장하고 캡션의 특수문자 이스케이프를 확인한다. PNG와 HTML이 같은 시트 ID를 재사용하지 않는 검사도 양방향으로 실행한다.

이 결과는 합성 입력으로 **기계적 인계와 파일 경계**를 검증한 것이다. 실제 부서 여섯 곳이 작성하는 라운드, 실제 미디어의 가독성·색·재생, 브라우저 픽셀 검수는 미검증이다.
