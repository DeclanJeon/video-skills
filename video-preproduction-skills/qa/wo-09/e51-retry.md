# STB — 34초 세탁소 대화 / 채팅 초안

**기준:** 사용자 제공 `CNT@v1` 잠금 요약, `SCR@v1` 대사 입력(EX-02), `DNT@v1#S01` · **범위:** `S01-C01`–`S01-C04`, 0.0–34.0초, 세로 9:16. 판본 핀은 사용자가 제공한 것이며 원장 등록·현재 상태·해시는 확인하지 않았다.

문 닫은 오래된 세탁소, 늦가을 밤. 계산대(`PRP-01@v1`)를 사이에 두고 오빠는 왼편, 동생은 오른편이다. 녹백색 형광등과 유리문 바깥의 주황 가로등을 유지하고, 간판·영수증의 글자는 읽히지 않게 한다. 모든 패널에 `LGT-01@v1` / `LOOK-01@v1`을 적용하는 초안이다. 정식 PLT 비트 ID 대신 아래에는 패널의 서사 기능만 적었다. 패널의 시작·정점·끝 표시는 컷 안 상대 순서이며 별도 타임코드가 아니다.

| 패널 ID | 컷 구간 / 선택 시점 | 연기·구도 / 서사 기능 | 카메라 |
|---|---|---|---|
| `S01-C01-P1` | 0.0–3.0 / 시작, D001 | 계산대 왼편의 오빠(`CHR-01@v1`, `WRD-01a@v1`). 회색 점퍼와 안경, 계산대 가장자리로 위치를 잡는다. 보증금 인상 통보로 갈등을 연다. | `CAM-01@v1` |
| `S01-C02-P1` | 3.0–22.0 / 시작, D002 | 계산대 오른편의 동생(`CHR-02@v1`, `WRD-02a@v1`). 회색 니트 위 남색 앞치마. 맞은편을 보며 “버틴 건 매일 문 연 나야”로 오빠의 말을 받아친다. 이어지는 D003–D005도 같은 컷이다. | `CAM-02@v1` |
| `S01-C02-P2` | 같은 컷 / 정점, D006–D007 | 동생이 오른손등을 들어 다리미 자국을 보여 준다. 카메라를 바꾸거나 손 인서트를 추가하지 않는다. | `CAM-02@v1` |
| `S01-C02-P3` | 같은 컷 / 끝, D008 | 같은 프레임에서 동생의 얼굴과 마지막 질문을 남긴다. 오빠에게는 매각 대금이 남지만 자신에게 무엇이 남느냐고 묻는다. | `CAM-02@v1` |
| `S01-C03-P1` | 22.0–31.0 / 끝, D009–D010 | `CAM-01`로 돌아와 오빠가 듣는 얼굴을 보여 준다. 동생은 화면 밖에서 동네 사람들이 자신을 부르는 이름을 말하다 “그 간판 내리면 나는 그냥—”에서 멈춘다. 오빠에게 대사나 립싱크를 배정하지 않는다. | `CAM-01@v1` |
| `S01-C04-P1` | 31.0–34.0 / 끝, D011 | 동생 얼굴 타이트. 계산대는 프레임 밖에 두는 초안. D010에서 멈춘 문장의 결론 “아무것도 아니잖아.”를 동생 얼굴에 남긴다. D011만 이 컷에 둔다. | `CAM-03@v1` |

**공간·연속성:** 한 세트, 고정된 계산대, 오빠 쪽 `CAM-01` 복귀, 동생 쪽 `CAM-02` → `CAM-03`을 기준으로 검토했다. 제시된 내용에 소품 인계·복잡한 경로가 없어 3D 실행은 요청하지 않는다. 이미지 고정 전 같은 계산대 기준으로 (1) 오빠/동생의 좌우와 상호 시선, (2) C02에서 손등 자국이 계산대나 몸에 가려지지 않는지, (3) C03에서 동생이 화면 밖인지, (4) C04 타이트의 컷 연결을 확인한다. CAM/CTY 본문과 실제 이미지가 없어 검증하지 않았다. 평면으로 판정되지 않으면 카메라 위치·타깃·렌즈와 계산대·인물 기준점을 갖춘 공간 검증이 필요하다.

**패널 인계:** 6개 패널 모두 `blocked(패널 이미지 미제공·미생성)`. 패널 경로·해시, SHT와 조립 셀 매핑 없음. 텍스트 보드만 제공한다.

## index-header.json — 초안

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
  "bmk_unknown_reason": "제공된 고정 핀 목록에 BMK가 없음. 벤치마크 유무는 원장으로 확인하지 못함.",
  "LOOK": ["LOOK-01@v1"],
  "QAR": [],
  "runtime_s": 34.0,
  "aspect": "9:16",
  "fps": null,
  "audio_path": null
}
```

현장 음성은 각본의 음향 지시다. 생성 경로 `native`/`separate` 확정 근거는 아니다. 컷별 목소리와 환경음은 제공된 `VOC`/`AMB` 핀을 사용한다.

## index.csv — 4컷 초안

`beats`의 `TBD`는 필수 PLT 비트 ID 미제공을 나타내며 게이트에 제출할 수 없다. `CTY@v1`은 문서 수준 핀만 보존했다. 세부 항목과 대사별 시간표가 없으므로 `world_rules`, `segments`는 비워 두었다. D010→D011은 서로 다른 대사 ID의 문장 연결이며 같은 대사를 두 컷에 걸쳐 배정하지 않았다. `gen`, `sheet`, `audio_prompt`, `adopted_take`는 후속 단계 열이다.

```csv
cut,t_start,t_end,segments,beats,scene,dialogue,dialogue_text,speakers_onscreen,speakers_offscreen,characters_visible,wardrobe,location,props,camera,lighting,look,performance,voice,ambience,sfx,music,vfx,transition_in,transition_out,continuity,world_rules,gen,panels,scene_note,sheet,audio_prompt,adopted_take
S01-C01,0.0,3.0,,TBD,SCR@v1.S01,D001,"{""D001"":""다음 달부터 보증금 올린대. 더는 못 버틴다니까.""}",CHR-01@v1,none(화면 밖 대사 없음),CHR-01@v1,WRD-01a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-01@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C01.perf,VOC-01@v1,AMB-01@v1,none(강화 효과음 없음),none(각본상 배경음악 없음),none(초안 별도 VFX 없음),none(작품 시작),hardcut,CTY@v1,,,S01-C01-P1,DNT@v1#S01,,,
S01-C02,3.0,22.0,,TBD,SCR@v1.S01,D002;D003;D004;D005;D006;D007;D008,"{""D002"":""못 버틴다고? 오빠가 언제 버텼는데. 버틴 건 매일 문 연 나야."",""D003"":""새벽 여섯 시에 셔터 올리고 밤 열한 시에 내렸어. 이십 년을."",""D004"":""그동안 오빠는 어디 있었어?"",""D005"":""명절에 한 번 와서 장부만 넘겨 봤잖아."",""D006"":""이 손 좀 봐."",""D007"":""다리미 자국이야."",""D008"":""팔면 오빠는 돈이라도 남지. 나는 뭐가 남는데?""}",CHR-02@v1,none(화면 밖 대사 없음),CHR-02@v1,WRD-02a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-02@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C02.perf,VOC-02@v1,AMB-01@v1,none(강화 효과음 없음),none(각본상 배경음악 없음),none(초안 별도 VFX 없음),hardcut,hardcut,CTY@v1,,,S01-C02-P1;S01-C02-P2;S01-C02-P3,DNT@v1#S01,,,
S01-C03,22.0,31.0,,TBD,SCR@v1.S01,D009;D010,"{""D009"":""이 동네에서 내 이름 아는 사람 없어. 다들 세탁소 아줌마라고 불러."",""D010"":""그 간판 내리면 나는 그냥—""}",none(화면 안 대사 없음),CHR-02@v1,CHR-01@v1,WRD-01a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,PRP-01@v1,CAM-01@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C03.perf,VOC-02@v1,AMB-01@v1,none(강화 효과음 없음),none(각본상 배경음악 없음),none(초안 별도 VFX 없음),hardcut,hardcut,CTY@v1,,,S01-C03-P1,DNT@v1#S01,,,
S01-C04,31.0,34.0,,TBD,SCR@v1.S01,D011,"{""D011"":""아무것도 아니잖아.""}",CHR-02@v1,none(화면 밖 대사 없음),CHR-02@v1,WRD-02a@v1,LOC-01@v1;SET-01@v1;ENV-01@v1,none(타이트 프레임에서 계산대 제외 초안),CAM-03@v1,LGT-01@v1,LOOK-01@v1,CNT@v1#S01-C04.perf,VOC-02@v1,AMB-01@v1,none(강화 효과음 없음),none(각본상 배경음악 없음),none(초안 별도 VFX 없음),hardcut,none(작품 끝),CTY@v1,,,S01-C04-P1,DNT@v1#S01,,,
```

## DLV — 텍스트 초안 인계

```yaml
dlv_for: null
artifacts:
  - id: STB
    path: null
    changed: ["채팅용 패널 서술", "index-header.json 코드 블록", "index.csv 코드 블록"]
consumed: [BRF@v1, BOR@v1, SYN@v1, PLT@v1, SCR@v1, DNT@v1, WLD@v1, SND@v1, CNT@v1, LOOK-01@v1, CHR-01@v1, CHR-02@v1, WRD-01a@v1, WRD-02a@v1, LOC-01@v1, SET-01@v1, ENV-01@v1, PRP-01@v1, CAM-01@v1, CAM-02@v1, CAM-03@v1, LGT-01@v1, CTY@v1, VOC-01@v1, VOC-02@v1, AMB-01@v1]
assumptions:
  - "제공 핀을 기록했다. 핀 목록은 상위 문서 본문·원장 검증을 뜻하지 않는다."
  - "오빠/동생을 각각 CHR-01·WRD-01a·VOC-01 / CHR-02·WRD-02a·VOC-02에 대응시켰다."
  - "각 컷에 지정된 인물만 가시 인물로 썼다. C01–C03 계산대 포함, C04 제외, 컷 간 hardcut, 별도 VFX 없음은 초안이다."
conflicts: []
checks:
  - "로컬 초안 검사: CSV·JSON 파싱, 4컷 경계·카메라·패널·화자, D001–D011 원문과 단일 배정, 참조 형식·접두사·제공 핀 대조."
  - "index_lint --stage board 미실행: 실제 원장·정본 프로젝트 경로 없음. 대상 존재·로케이터·상태·해시 및 게이트 미판정."
  - "timeline_check 및 낭독 실측 미실행: 대사 시간표 미제공. 잠긴 구간을 수정하지 않음."
  - "이미지 또는 시트 조립·검수 미실행: 패널 파일 없음."
missing_inputs:
  - "감독/원장: 실제 ledger.json 및 상위 정본 파일·현재 등록 상태·해시, BMK/QAR 여부, 납품 콜시트 ID(발행 시)."
  - "작가/조연출: PLT@v1의 컷별 비트 ID 및 대사별 시간표."
  - "감독/사운드: fps와 audio_path 결정, VOC/AMB의 화자·환경 대응 및 강화하지 않은 별도 SFX 큐 유무."
  - "콘티·카메라·미술: CNT/DNT 앵커 본문, CTY 컷별 항목, CAM 프레이밍·시선·가림 및 PRP-01 프레임 내 상태, WLD 적용 규칙."
  - "이미지 담당(후속 단계): 패널 PNG·해시·시트 셀 매핑."
self_verdict: partial
```

## 실행 로그

- 각본 입력은 `evals/design/fixtures/SCR-ex02.md` 한 건이다. `storyboard-artist/SKILL.md`의 STB·인덱스·DLV 양식, 공간 프리비즈 분기, 아티팩트 및 인덱스 계약을 적용했다.
- 읽기 전용 초안 검사 통과: CSV 33열, 잠긴 4컷, 패널 6개, 원문과 일치하는 대사 11개(각 1회 배정), 제공된 `@v1` 핀 26개. 파서 형식·접두사 확인을 포함하되 원장·로케이터 대상 및 이미지 검사는 하지 않았다.
- 승인·등록·프로젝트 파일 쓰기나 외부 호출은 하지 않았다. 이 응답 기록만 지정 경로에 저장했다.
