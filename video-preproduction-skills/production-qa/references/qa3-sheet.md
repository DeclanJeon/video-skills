# QA3: 패널·시트 검수 증거

`python3 scripts/check_sheet_evidence.py --project <project-root> --spec <spec.json>`

입력은 `evidence_kind`(`production` 또는 공간용 `previs`), `index`(프로젝트 기준 CSV 경로)와 `sheets` 배열이다. 각 시트는 `image`(정적 PNG 경로), `cells`(시트의 행 우선 순서대로 `cell`, `panel`, `image` 항목)를 갖는다. 패널 파일명은 `<panel>.png`, 시트 안 셀은 `cell-01`부터 연속이다. 인물·소품 기준 이미지를 함께 대조한 경우 `references`에 프로젝트 상대 PNG 경로를 명시한다. 원본 바이트가 스냅샷에 포함되어 교체 시 검수 기록이 무효화된다. 조립기의 셀 매핑을 가져올 때 이미지 경로를 프로젝트 상대경로로 바꾼다. HTML 미리보기나 빈 칸은 이 검사에서 실제 시트 증거가 아니다.

1. 프롬프트·레퍼런스 승인과 별개로 실제 패널 및 조립 시트를 확보한다. 인덱스 버전과 등록 자산을 먼저 확인한다.
2. 스크립트를 실행해 `snapshot`을 얻는다. 여기까지는 디코딩·순서·해시 검사뿐이다. 시트가 실제 의도대로 조립됐는지와 패널 정체성을 자체 판정하지 않는다.
3. 검사자가 같은 시트와 패널을 열어 `identity`, `continuity`, `framing`, `legibility`, `unwanted_text` 각각의 관찰 근거를 기록한다. spec의 `review`는 `snapshot`, `reviewer`, `mode`(`inline`/`independent`), `checks`(각 `verdict`와 `note`)를 담는다. 이름이나 판정은 작성자가 제공하는 기록이지 인증 정보가 아니다.
4. 다시 실행한다. 종료 0은 현재 바이트와 연결된 합격 기록, 1은 파일 또는 검수 차단, 3은 미검증이다. 원본·인덱스·셀 매핑이 바뀌면 다시 검수한다. 증거 종류도 스냅샷에 포함된다. `previs` 및 미지정 입력은 기록상 합격 판정이 있어도 최종 QA3에 사용할 수 없다. 정식 QA3는 현재 버전 원장과 인덱스 검사 및 실제 리뷰도 필요하다. 종료 0은 QA4나 실행 승인이 아니다.
