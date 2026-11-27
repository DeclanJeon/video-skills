# 제작 원장 v1 — 로컬 계약

- 프로젝트 루트의 `ledger.json`: `schema_version: 1`, `artifacts: {ID: [버전 레코드, …]}`.
- 버전 레코드: `version`(1부터 연속 증가), `path`(프로젝트 기준 상대경로), `sha256`(등록 시 파일 해시), `consumes`(현재 유효한 버전 핀 목록), `status`(`current`, `stale`, `superseded`).
- 버전 증가 시 이전 버전 소비자와 그 하위 소비자는 stale. `mark-stale`에 앵커를 주면 해당 앵커 또는 전체 아티팩트 참조 소비자부터 전파한다. `@draft` 변경은 전파하지 않는다.
- 등록 파일은 루트 내부에 먼저 만들어야 한다. 기존 버전의 파일은 덮어쓰지 않는다. 원장 쓰기는 임시 파일 교체 방식이나 동시 쓰기 잠금은 없으므로 감독만 순차 실행한다.

## CLI

저장소 루트에서 `python3 scripts/ledger.py --project ROOT` 뒤에 아래 명령을 붙인다.

- `status SCR`: 현재/낡음/미등록 조회. 쓰지 않는다.
- `register CNT conti/CNT-v1.md 1 --consumes SCR@v1`: 현재 핀이 존재할 때만 등록.
- `mark-stale CHR-01#anchor`: 영향을 받은 아티팩트 ID를 JSON으로 반환.

원장 자체는 아티팩트 버전만 처리한다. 승인 상태를 만들거나 이력을 기록하지 않는다.

## 단계별 인덱스 검사

`python3 scripts/index_lint.py --project ROOT --stage bible|board|sheet|prompt --json`은 읽기 전용이다.

- `bible`: 보드 생성 전에는 감독이 각본에서 추출한 대상 목록을 `bible-inventory.json`에 넣는다. 예: `{"screenplay":"SCR@v1","entries":[{"entity":"첫 씬의 화자","kind":"CHR","ref":"CHR-01@v1"}]}`. 미배정 대상은 `ref:null`로 포함한다. 검사는 선언된 항목만 검증하며 자연어 각본에서 누락 대상을 자동 추출하지 않는다.
- `board` 이후: `04_board/index-header.json`과 `04_board/index.csv`를 읽는다. 컷의 참조는 모두 버전 핀이 있어야 한다. 로케이터는 정확히 같은 이름의 Markdown 헤딩 또는 명시적 HTML ID를 쓴다. 이미지 셀을 참조할 때는 동일한 셀 ID를 선언한 Markdown 시트 명세를 원장에 등록하고 실제 이미지 위치를 명세에 연결한다. 픽셀 자체는 이 검사의 범위가 아니다.
- 각본의 대사 정본은 `- D001: 발화 원문` 줄이다. 컷은 `dialogue_text` 열에 `{"D001":"발화 원문"}`처럼 실제 인용을 남긴다. 단순 발화 ID만으로 원문 일치를 확인할 수 없다.
- 정상 종료 0, 발견 사항 있음 1, 읽을 수 없거나 입력 형식 오류 2. 이 검사로 실제 렌더나 파일 납품을 인증하지 않는다.

## 사운드 소스·증빙 소비 관계

[사운드 통합 정본](../../docs/design/11-sound-sourcing-integration.md#3-파일과-증빙을-기존-id원장에-등록)을 따른다. AMB/SFX/MUS는 계획 문서와 실제 선택 미디어를 버전/경로/소스 원장으로 구별한다. REF-* 문법을 권리·청취 보고서·검색/소스 CSV에 재사용하고 등록 순서는 rights → media → review → manifest → SND → CNT/STB/VPR/QAR다. 미디어가 자기 리뷰를 역소비하지 않는다. 원본 파일·권리·리뷰 변경은 해당 소비자에게 기존 stale을 전파한다. 같은 바이트의 미디어도 새 권리 핀을 소비해야 하면 다음 버전으로 갱신한다.

index_lint는 직접 참조 큐의 파일·해시·상태를 검사할 뿐 consumes 전체를 재귀 확인하지 않는다. 감독/제작 QA는 소스 원장과 각 증빙/리뷰의 현재 파일·해시를 별도 대조한다. 삭제/비정상 덮어쓰기는 저절로 새 버전이나 stale 이벤트가 되지 않으므로 바이트 검사와 필요한 mark-stale/수정을 실제 수행한다. 현재 등록은 법적 허가·실측·청취·채택 인증이 아니다. 기존 combined 원장의 writer 격리를 지킨다.

## 감사 이력 연동

형식 출처: v1 `recording-production-history`의 `.history/events/` 순차 Markdown 이벤트. 해당 도구를 사용하는 감독은 먼저 실제 설치본의 CLI 규약을 읽고, 동일 작업의 시작 및 터미널 상태를 실제 출력과 연결한다. v1 초기화가 만드는 `project.json`은 v2 승인·단계 정본으로 승격하지 않는다. 별도 런타임 의존성이므로 이 패키지의 로컬 테스트가 이력 연동 성공을 의미하지 않는다.

## 타임라인 계산 입력

`scripts/timeline_check.py --index index.csv --runtime SEC --script SCR.md --json`은 컷 범위와 기계 판독용 대사 구간을 검사한다. `SCR.md`에는 선택적으로 코드 펜스 `speech-timing` 하나를 두고 JSON 배열로 기록한다. 각 항목은 `ids`, `start`, `end`, `text`, `lang`과 선택적인 `pauses`, `mode`를 가진다. 같은 시간창으로 판정할 연속 문장은 ID 배열 하나로 묶는다. 시간표가 없는 대사는 TL05(미확인)로 분리한다. 예시는 [EX-02 보정 픽스처](../../tests/fixtures/ex02-fixed-34s/SCR.md).

시간창의 말속도는 계산값이다. 이 검사로 발화 실측이나 원문 일치가 확인된 것으로 기록하지 않는다.
