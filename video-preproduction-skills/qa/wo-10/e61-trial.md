## 채팅 응답

**EX-02 이미지 텍스트 인계 — 작성 순서와 입력 목록**

| 순서 | 만들 참조 프롬프트 | 소비할 입력 |
|---|---|---|
| 1. CHR | 오빠·동생 각각 7뷰: 정면, 좌우 ¾, 좌우 측면, 후면, 표정 3종 시트. 오빠의 반백 머리와 안경, 동생의 묶은 단발과 **오른손등** 다리미 자국을 고정. | 두 사람의 `CHR#anchor` 정본 원문. 선행 이미지 참조 없음. |
| 2. WRD | 의상 상태별 전신: 오빠는 회색 점퍼·남색 바지, 동생은 회색 니트·남색 앞치마. | 각 인물의 `WRD` 정본 원문과 같은 인물의 `REF-CHR`. |
| 3. LOC | 폐점한 세탁소 4뷰. 시점이 바뀌어도 같은 공간 배치를 유지. | `LOC`의 4뷰·평면·전경/중경/원경, 해당 `SET`·`ENV`가 있으면 그 정본. |
| 4. PRP | 계산대 기준 이미지. | `PRP` 외형·상태 정본. 세탁소 안에서의 위치나 방향이 필요한 뷰는 해당 `REF-LOC`도 참조. |
| 5. LOOK | 녹백 형광등과 주황 가로등을 대비시키는 저채도 기준 프레임 1장. | `LOOK` 공통 스타일, 해당 `WLD#palette`·`LGT`, 맞는 세탁소 `REF-LOC`. |

6. **컷 안의 패널별 프롬프트(`IMG-Snn-Cnn-Pn`)** — 기준 이미지가 준비된 뒤, `STB`·인덱스의 패널과 `characters_visible`을 기준으로 화면에 보이는 인물의 `REF-CHR`·해당 `REF-WRD`, 앵글에 맞는 `REF-LOC`, 공통 `REF-LOOK`, 계산대가 보이면 그 상태의 `REF-PRP`를 소비. 텍스트 입력은 `BRF`·`CAM`의 화면비·프레이밍, `CNT`의 한 순간, `CTY`의 축·시선·손/소품 상태, 버전 고정된 `CHR#anchor`·`WRD` 원문과 `LOOK` 공통 문장. 패널별 `.map.json`에 출처와 사용 REF를 남기고, 화면 글자·워터마크는 제외. 참조 이미지 입력을 지원하지 않는 모델은 정본 앵커 문장으로 대체하고 QA3에서 정체성을 엄격히 확인.
7. **미확인 입력** — 정본 원문·ID/버전, `STB`·인덱스, 패널별 순간·카메라·축·손/계산대 상태, 실제 `REF-*` 파일은 이번 인계에 없음. 지금은 목록만 제공.

## 실행 로그

- 읽은 범위: `image-prompt-engineer/SKILL.md`, 직접 연결된 `docs/design/06-image-prompt-spec.md`, `docs/design/03-artifact-index.md`, `image-prompt-engineer/assets/IMG-template.md`, `image-prompt-engineer/assets/IMG-map-template.json`, `production-director/assets/DLV-template.yaml`. 평가 문서나 별도 픽스처를 열거나 사용자 입력에 덧붙이지 않음.
- 프롬프트 본문, 이미지, 패널/시트, 프로젝트 파일과 원장을 만들거나 수정하지 않음. 이 파일은 런타임이 지정한 응답·로그 전달물임.
- `prompt_lint.py --kind image` 미실행: 목록만을 요청했고 검사할 프롬프트와 맵이 없음. 스테이징을 수행하지 않음. 현재 작업 디렉터리에 Git 저장소가 없어 읽기 전용 상태 확인 명령은 실패함.
