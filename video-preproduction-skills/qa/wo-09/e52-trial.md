## 보드 QA 처리 — PRP-04@v1

**QA2 §2.2 고아 검사: 의도적 미사용으로 기록할 건입니다.** 제공된 설명상 벽시계는 잠긴 각본·콘티 어디에도 쓰이지 않고(소리·컷·배경 포함), 보드 인덱스 네 컷에도 참조가 없습니다. 누락된 컷 참조를 보완할 사안이 아닙니다. 바이블의 `PRP-04@v1`은 그대로 두고, QA2 기록에는 `PRP-04@v1 — unused(잠긴 각본·콘티의 소리·컷·배경 및 보드 인덱스 네 컷에서 사용·참조 없음)`을 남기는 것이 맞습니다. 근거는 아티팩트·ID·인덱스 규약 §6 QA2 2.2의 ‘최소 1개 컷에서 참조되거나 `unused(이유)`’입니다.

네 컷의 `props`는 실제 사용 소품만 유지합니다. 소품이 전혀 없는 행은 해당 없음 값(`none(이유)`)을 쓰되, 이 벽시계의 미사용을 기록하려고 컷 행에 핀을 추가하지 않습니다. 새 컷·패널·배경 소품·시계 소리·촬영이나 이미지 생성을 추가하지 않습니다. 미사용 사유가 기록되면 이 항목 자체는 차단 사유가 아니지만, 지금은 사용자 설명에 근거한 검토 의견일 뿐입니다. 실제 프로젝트 파일을 확인하거나 `index_lint --stage board`를 실행하지 않았으므로 기계 검사 결과나 QA2 전체 PASS를 주장하지 않습니다.

## 감독에게 보낼 메시지 (초안, 미발송)

> 감독님, QA2 고아 검사에서 바이블의 벽시계 `PRP-04@v1`은 누락이 아니라 의도적 미사용으로 처리하는 것을 권고합니다. 잠긴 각본·콘티의 소리, 컷, 배경에 쓰이지 않으며 네 컷 인덱스에도 참조가 없습니다. 바이블 핀과 보드는 그대로 유지하고, QA2 기록에 `PRP-04@v1 — unused(잠긴 각본·콘티와 네 컷 보드에서 사용·참조 없음)`을 남겨 주세요. 참조를 만들기 위한 추가 촬영·패널·배경·사운드는 필요 없습니다. 이 의견은 해당 항목에 한하며, 실제 보드 lint나 전체 QA2 통과는 확인하지 않았습니다.

**채팅 인계(DLV 요약):** 확인 범위는 제공된 `PRP-04@v1`과 네 컷 상태 설명입니다. 제작 산출물 변경·등록 없음. 확인하지 못한 입력은 잠긴 SCR/CNT의 실제 핀·파일과 STB 인덱스 파일입니다. 규약 대조 완료, 프로젝트 기계 검사는 미실행(`partial`).

## 실제 도구 로그 (보고서 저장 직전까지)

1. `find` — `**/storyboard-artist/SKILL.md` 1건 확인.
2. `read` — `storyboard-artist/SKILL.md` 열람.
3. 병렬 `read` — `docs/design/03-artifact-index.md`, `storyboard-artist/assets/STB-template.md`, `storyboard-artist/assets/index-template.csv`, `storyboard-artist/assets/index-header-template.json`, `production-director/assets/DLV-template.yaml` 열람.
4. `read` — `production-ledger/references/ledger-schema.md` 열람.
5. `read` — `docs/design/01-pipeline-and-gates.md` 열람.
6. `git diff --cached --quiet --` — 종료 129 (`--no-index` 모드에서 `--cached`를 지원하지 않음).
7. `git rev-parse --is-inside-work-tree` — 종료 128 (현재 위치와 상위 폴더에 Git 작업 트리 없음). 스테이징 작업은 하지 않음.

평가자 파일 열람, 프로젝트 파일·원장 변경, 조립, 생성, 메시지 발송, 외부 작업 없음.
