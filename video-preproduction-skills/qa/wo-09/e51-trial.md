# EX‑02 세탁소 — 34초 스토리보드 초안

**기준:** 잠긴 `CNT@v1` 요약의 4컷과 이야기 자료의 `S01`·대사 원문. 9:16 한국어 사실주의. 아래는 텍스트 보드이며, 패널은 컷 안에서 포착할 순간이다. 패널 수가 컷 수나 추가 편집점을 뜻하지 않는다.

**공통 프레임:** 늦가을 밤, 영업을 마친 오래된 세탁소. 계산대를 사이에 두고 오빠는 화면 좌에서 우를, 동생은 화면 우에서 좌를 본다. 한 사람이 프레임 밖이어도 그 방향은 유지한다. 천장의 차가운 녹백색 형광등과 유리문 밖의 따뜻한 주황빛은 같은 물리적 위치에 둔다. 옷걸이 줄과 스팀 다리미대는 보이는 범위에서만 배경으로 쓰고, 간판·영수증 글자는 읽히지 않게 한다. 오빠의 안경·회색 점퍼·남색 바지, 동생의 회색 니트·남색 앞치마는 바뀌지 않는다.

## 패널

| 패널 | 컷 / 대사 기준 | 그릴 순간 |
|---|---|---|
| `S01-C01-P1` | 0.0–3.0초 · 정점 `D001` · `CAM-01` | 화면 왼쪽의 오빠가 계산대 너머 오른쪽을 보고 보증금 인상을 말한다. 상대는 프레임 밖. 계산대 가장자리로 둘 사이의 거리를 잡고, 형광등 아래 얼굴에 문 밖의 따뜻한 빛을 보조로 남긴다. |
| `S01-C02-P1` | 3.0–22.0초 · 시작 `D002` · `CAM-02` | 화면 오른쪽의 동생이 왼쪽의 오빠를 향해 즉각 받아친다. `D003`–`D005`까지 같은 셋업에서 일한 시간과 오빠의 부재를 짚는다. 오빠는 프레임 밖. |
| `S01-C02-P2` | 같은 컷 · 정점 `D006`–`D007` · `CAM-02` | 동생이 자기 오른손 등을 들어 다리미 자국을 보여 준다. 같은 화면에서 얼굴과 손등을 읽게 하되 별도 인서트, 소품 접촉·인계는 넣지 않는다. |
| `S01-C02-P3` | 같은 컷 · 끝 `D008` · `CAM-02` | 손 제스처를 거두면서도 시선은 왼쪽에 둔 채 질문을 던진다. 계산대와 두 광원은 앞 패널과 같은 위치다. |
| `S01-C03-P1` | 22.0–31.0초 · 시작 `D009` · `CAM-01` | 첫 컷의 오빠 프레이밍으로 돌아온다. 오빠는 오른쪽을 보며 입을 열지 않는다. 오른쪽 화면 밖에서 동생이 동네 사람들이 자신을 부르는 이름을 말한다. D009부터 화면 밖으로 들린다. |
| `S01-C03-P2` | 같은 컷 · 끝 `D010` · `CAM-01` | 동생의 “그 간판 내리면 나는 그냥—”까지 오빠 얼굴을 유지한다. 오빠는 끼어들지 않는다. 문장이 미완인 채 컷이 끝나며, D010 발화가 다음 컷에 걸친다고 가정하지 않는다. |
| `S01-C04-P1` | 31.0–34.0초 · 끝 `D011` · `CAM-03` | 동생 얼굴 타이트. 시선은 왼쪽의 오빠 쪽에 남고, “아무것도 아니잖아.”를 동생 얼굴에서 직접 받는다. 계산대는 프레임 밖이지만 두 사람의 위치와 광원은 바뀌지 않는다. |

## 인덱스 헤더 초안

```json
{
  "BRF": "BRF@v1",
  "BOR": "BOR@v1",
  "SYN": "SYN@v1",
  "PLT": "PLT@v1",
  "SCR": "SCR@v1",
  "DNT": "DNT@v1",
  "WLD": "WLD@v1",
  "SND": "SND@v1",
  "BMK": [],
  "bmk_unknown_reason": "벤치마크 핀 미제공; 존재 여부 미확인",
  "LOOK": ["LOOK-01@v1"],
  "QAR": [],
  "runtime_s": 34.0,
  "aspect": "9:16",
  "fps": null,
  "audio_path": null
}
```

`fps`와 제작 오디오 경로(`native`/`separate`)는 미제공이다. 이야기 속 대사는 현장 음성이고 배경음악·효과음 강화·내레이션은 없다. `QAR: []`는 확인된 승인 핀이 없다는 뜻이다.

## 컷 인덱스 초안 — 헤더 + 데이터 4행

`@v1`은 원장에 정본이 있다는 사용자 가정이지 파일 검증 결과가 아니다. `CHR-01`/`WRD-01a`/`VOC-01`은 오빠, `CHR-02`/`WRD-02a`/`VOC-02`는 동생에 대한 **임시 매핑**이다. `LOC-01`/`SET-01`/`ENV-01`은 세탁소/실내 세트/늦가을 밤, `PRP-01`은 계산대, `LGT-01`은 공통 두 광원의 임시 매핑이다. `beats`와 `ambience`는 정본 문서까지만 핀을 건다. 연기·CTY·씬 노트 로케이터도 대조 전 후보이며, 목록에 없는 실측 하위 구간이나 대사 걸침은 추가하지 않았다. 인접 컷의 하드컷과 단독 프레이밍 세부는 초안 제안이다.

```csv
cut,t_start,t_end,segments,beats,scene,dialogue,dialogue_text,speakers_onscreen,speakers_offscreen,characters_visible,wardrobe,location,props,camera,lighting,look,performance,voice,ambience,sfx,music,vfx,transition_in,transition_out,continuity,world_rules,gen,panels,scene_note,sheet,audio_prompt,adopted_take
S01-C01,0.0,3.0,,PLT@v1,SCR@v1.S01,D001,"{""D001"":""다음 달부터 보증금 올린대. 더는 못 버틴다니까.""}",CHR-01@v1,none(화면 밖 대사 없음),CHR-01@v1,WRD-01a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-01@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C01.perf,SND@v1.VOC-01,SND@v1,none(별도 효과 배정 없음),none(배경음악 없음),none(별도 VFX 배정 없음),none(장면 시작),hardcut,CNT@v1#CTY,WLD@v1,,S01-C01-P1,DNT@v1#S01,,,
S01-C02,3.0,22.0,,PLT@v1,SCR@v1.S01,D002;D003;D004;D005;D006;D007;D008,"{""D002"":""못 버틴다고? 오빠가 언제 버텼는데. 버틴 건 매일 문 연 나야."",""D003"":""새벽 여섯 시에 셔터 올리고 밤 열한 시에 내렸어. 이십 년을."",""D004"":""그동안 오빠는 어디 있었어?"",""D005"":""명절에 한 번 와서 장부만 넘겨 봤잖아."",""D006"":""이 손 좀 봐."",""D007"":""다리미 자국이야."",""D008"":""팔면 오빠는 돈이라도 남지. 나는 뭐가 남는데?""}",CHR-02@v1,none(화면 밖 대사 없음),CHR-02@v1,WRD-02a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-02@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C02.perf,SND@v1.VOC-02,SND@v1,none(별도 효과 배정 없음),none(배경음악 없음),none(별도 VFX 배정 없음),hardcut,hardcut,CNT@v1#CTY,WLD@v1,,S01-C02-P1;S01-C02-P2;S01-C02-P3,DNT@v1#S01,,,
S01-C03,22.0,31.0,,PLT@v1,SCR@v1.S01,D009;D010,"{""D009"":""이 동네에서 내 이름 아는 사람 없어. 다들 세탁소 아줌마라고 불러."",""D010"":""그 간판 내리면 나는 그냥—""}",none(오빠 무발화),CHR-02@v1,CHR-01@v1,WRD-01a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-01@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C03.perf,SND@v1.VOC-02,SND@v1,none(별도 효과 배정 없음),none(배경음악 없음),none(별도 VFX 배정 없음),hardcut,hardcut,CNT@v1#CTY,WLD@v1,,S01-C03-P1;S01-C03-P2,DNT@v1#S01,,,
S01-C04,31.0,34.0,,PLT@v1,SCR@v1.S01,D011,"{""D011"":""아무것도 아니잖아.""}",CHR-02@v1,none(화면 밖 대사 없음),CHR-02@v1,WRD-02a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,none(타이트 프레임에 노출 소품 없음),CAM-03@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C04.perf,SND@v1.VOC-02,SND@v1,none(별도 효과 배정 없음),none(배경음악 없음),none(별도 VFX 배정 없음),hardcut,none(장면 종료),CNT@v1#CTY,WLD@v1,,S01-C04-P1,DNT@v1#S01,,,
```

## 공간 분기와 인계

이 보드에서 중요한 공간 관계는 **C01→C03의 `CAM-01` 복귀**, **C03 화면 우측 밖 목소리→C04 화면 안 동생**, **C02의 같은 샷 안 오른손 자국**이다. 평면 기준은 `오빠(화면 좌) — 계산대 — 동생(화면 우)`와 같은 쪽 카메라 축으로 잡는다. 물건 인계나 경로를 새로 만들 필요가 없어 3D 프리비즈는 실행하지 않았다. 실제 시야·가림, 손과 얼굴의 동시 가독성, 문광이 각 앵글에서 닿는 위치는 미검증이다.

```yaml
dlv_for: EX-02 채팅 초안
artifacts:
  - id: STB
    scope: S01-C01–S01-C04 텍스트 패널·인덱스 헤더·컷 행 4개
    status: draft
consumed:
  - 사용자 제공 잠긴 콘티 요약 (CNT@v1 가정)
  - SCR-ex02.md 이야기와 대사 원문 (SCR@v1 파일 자체는 미제공)
assumptions:
  - 상위 핀과 관련 에셋 정본 버전은 v1로 가정; 임시 ID와 로케이터는 원장과 대조 전
  - 하드컷과 패널별 자세·프레이밍은 제안이며 컷 경계와 화자 배정은 잠금대로 유지
conflicts: []
checks:
  - 텍스트 기준 0.0–34.0초 4컷, D001–D011 배정, C03의 화면 밖 동생과 오빠 무발화
  - 패널 이미지 7개 모두 미생성(요청 범위 밖); 이미지 파일·해시·셀 매핑·SHT 없음
missing_inputs:
  - 원장·정본 파일, PLT 비트 ID 및 CNT/DNT/CTY 로케이터, 실제 에셋 ID·SND 음성/환경음 앵커, fps·오디오 경로
  - 발화별 실측 없음; 특히 C01 3초 및 C02 19초의 쉼을 포함한 낭독 여유 미확인
self_verdict: partial
```

요청한 텍스트 초안은 제공했다. 정본 핀 해석·stale·고아 검사, 정식 QA2/QA3, 이미지 검수와 시트 조립은 수행하지 않았다.

## 실제 도구 로그

| 순서 | 호출 | 실제 결과 |
|---|---|---|
| 1 | `find` — `**/storyboard-artist/SKILL.md` | `storyboard-artist/SKILL.md` 확인. |
| 2 | `read` — `storyboard-artist/SKILL.md` | 스킬 절차와 출처를 읽음. |
| 3 | 병렬 `read` 7건 — `storyboard-artist/references/spatial-previs.md`, `docs/design/03-artifact-index.md`, `storyboard-artist/assets/STB-template.md`, `storyboard-artist/assets/index-template.csv`, `storyboard-artist/assets/index-header-template.json`, `production-director/assets/DLV-template.yaml`, `evals/design/fixtures/SCR-ex02.md` | 분기·형식 계약과 지정 이야기/대사만 읽음. |
| 4 | `read` — `production-ledger/references/ledger-schema.md` | 버전 핀·로케이터·`dialogue_text` 계약을 읽음. 원장 자체는 열지 않음. |
| 5 | 병렬 `read` 2건 — `docs/design/01-pipeline-and-gates.md` 1–150행, `docs/design/07-video-prompt-spec.md` 1–115행 | 납품 패킷 및 타임라인 규칙을 읽음. |
| 6 | `write` — 지정된 `conti-board.task-3.md` | 초안 작성. |
| 7 | `bash` — `python3 -B` 초안 검사 + `git --no-optional-locks diff --cached --quiet --` | 실패: 초기 검사에서 열 수를 34로 잘못 가정했고, 작업 디렉터리는 Git 저장소가 아님. |
| 8 | `bash` — `pwd`; `git --no-optional-locks rev-parse --show-toplevel`; `python3 -B` CSV 열 비교 | Git 저장소가 아님을 확인. 양식과 같은 33열이며 헤더와 4개 데이터 행 모두 길이가 33. Git 스테이징 수행 없음. |
| 9 | `bash` — `python3 -B`로 JSON 키·CSV 열을 양식과 대조하고, 4컷의 구간/카메라, 대사 원문, C03 화자, 패널 ID를 검증 | 통과: 데이터 행 4×33, 원문 11개 일치, 패널 연결 7개 일치. |
| 10 | `edit` — 지정 `conti-board.task-3.md` | 이 실제 도구 로그를 같은 산출물에 추가. |

지정 이야기 자료 외 평가 파일, 프로젝트 파일 쓰기, 외부 호출, 이미지 생성, 3D 실행은 없었다.
