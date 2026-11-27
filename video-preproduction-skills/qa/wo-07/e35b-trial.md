# P6 별도 사운드 트랙 — `tmp:APR-01` 초안

**범위:** S01 D001–D003의 한국어 대사만. `audio_path: separate`. 아래 **원문**만 발화하고 연기 지시는 읽지 않는다. 화자 ID는 이 초안용 임시 표기다.

### `#voice-D001` — 오빠 (`tmp:CHR-01`)

**원문:** “다음 달부터 보증금 올린대. 더는 못 버틴다니까.”  
**연기:** 낮고 건조한 목소리로 보증금 인상 소식을 통보한다. 목소리를 높이거나 설득하듯 늘이지 말고, 마지막 “다니까”를 짧게 닫는다.

### `#voice-D002` — 동생 (`tmp:CHR-02`)

**원문:** “못 버틴다고? 오빠가 언제 버텼는데. 버틴 건 매일 문 연 나야.”  
**연기:** 첫 반문 “못 버틴다고?”를 빠르게 꺼낸다. 마지막 “나야”는 소리를 키우기보다 두 음절을 또렷이 눌러 닫는다.

### `#voice-D003` — 동생 (`tmp:CHR-02`)

**원문:** “새벽 여섯 시에 셔터 올리고 밤 열한 시에 내렸어. 이십 년을.”  
**연기:** “새벽 여섯 시”와 “밤 열한 시”를 각각 또박또박 짚는다. “내렸어.” 뒤, “이십 년을.” 바로 앞에서 짧게 쉰다. 쉼은 발화 원문에 삽입하지 않는다.

**별도 레이어:** `#sfx` 추가·강화 없음. `#music` 배경음악 없음. 이 대사 트랙에는 환경음과 내레이션을 넣지 않는다.

**근거 및 범위:** EX-02 `SCR` S01 원문과 요청에 적힌 CNT 연기 레이어를 반영했다. 상대 속도와 쉼은 연기 지시이며 발화 길이는 실측하지 않았다. 텍스트 초안만 작성했으며 녹음·음성 생성·업로드는 하지 않았다.

## 도구 로그

- `read`: `sound-designer/SKILL.md`, `sound-designer/assets/SND-template.md`, `sound-designer/assets/APR-template.md`, `docs/design/02-crew-roster.md`, `docs/design/03-artifact-index.md`, `production-director/assets/DLV-template.yaml`, `docs/design/01-pipeline-and-gates.md`, `docs/design/07-video-prompt-spec.md` (1–150행 및 164행–끝).
- `read`: `evals/design/fixtures/SCR-ex02.md`만 평가 입력으로 열었다. 그 외 평가 파일은 열지 않았다.
- `bash`: `git diff --cached --name-only` (실패: Git 작업 트리가 아니어서 `--cached` 사용 불가), `git rev-parse --is-inside-work-tree` (Git 작업 트리 없음 확인). 스테이징은 수행하지 않았다.
- `write`: 지정된 세션 아티팩트 한 건만 작성했다. 프로젝트 파일·원장 쓰기나 외부 호출은 하지 않았다.
- `bash`: Python으로 저장된 초안과 각본을 대조했다. D001–D003만 포함되며 세 화자 표기와 대사 원문이 모두 일치한다.
- `edit`: 검증 결과를 같은 세션 아티팩트의 로그에 추가했다.
