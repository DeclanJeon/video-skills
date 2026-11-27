# 조연출 R0 → 감독 인계 | EX-02, 목표 30.0초

**30초 입력은 컷 자체에 공백·겹침이 없지만 발화 밀도에서 차단 3건, 경고 1건입니다.** 원문 보존을 우선하면 34.0초안을 권고합니다. 30.0초와 현 배정을 유지해야 하면 작가에게 `D001`, `D002`, `D009+D010` 축약을 요청해 주세요. 어느 안도 채택·반영하지 않았습니다.

## CNT@draft · 입력 기준 컷/대사 배정

작업 입력: `tests/fixtures/ex02-defect-30s/index.csv`, `tests/fixtures/ex02-defect-30s/SCR.md`. 두 파일에는 버전 핀이 없습니다. 아래는 실측이 아닌 전역 초 단위 추정입니다. 씬 `S01` 하나, 컷 4개, `D001`–`D011`은 각 1회 배정됩니다. 화자와 화면 안/밖, 기능은 EX-02 참고 예시에 근거한 R0 가정이며 작업 입력이 확정한 값은 아닙니다.

| 컷 · 전역 초 | 하위 구간 → 대사/무대사 | 화자·씬 기능(가안) |
|---|---|---|
| `S01-C01` 0.0–2.0 | `.b1` 0.0–2.0 `D001` | 오빠(`CHR-01`), 화면 안 가안: 보증금 인상으로 갈등 제기 |
| `S01-C02` 2.0–18.5 | `.b1` 2.0–4.5 `D002`; `.b2` 4.5–8.0 `D003`; `.b3` 8.0–12.0 `D004`→쉼→`D005`; `.b4` 12.0–15.5 `D006`→쉼→`D007`; `.b5` 15.5–18.5 `D008` | 동생(`CHR-02`), 화면 안 가안: 반격 → 노동·부재·손의 증거 → 매각이 남기는 것 |
| `S01-C03` 18.5–28.0 | `.b1` 18.5–21.0 무대사(받아들이는 시간); `.b2` 21.0–24.5 무대사(계속 듣는 자세, 특정 단어에 대한 선행 반응 금지); `.b3` 24.5–28.0 `D009`→쉼→`D010` | 동생 화면 밖 가안, 오빠가 듣는 컷: 정체성 상실의 고백. 초반 6.0초는 영상 공백이 아니라 대사 없는 구간. 환경음은 미정 |
| `S01-C04` 28.0–30.0 | `.b1` 28.0–30.0 `D011` + 호흡 1회 기본 배정(0.3초). 발화·정지 세부 분리는 입력에서 확정되지 않음 | 동생 화면 안 가안: 고백의 결말 |

`D004+D005`, `D006+D007`, `D009+D010`은 각각 한 큐에 묶여 있어 파일에서 확인되는 것은 그룹 구간과 쉼 횟수까지입니다. 동시 발화·오버랩·L컷 표기 없음. `D010`→`D011`은 문맥상 이어지되 입력상 28.0초 경계에서 서로 다른 큐입니다. 컷을 걸쳐 발화를 이어 붙이기로 하면 R6에서 양쪽 컷과 L컷을 명시하고 재검합니다.

### CTY 초안(참고 예시 기반, 미승인)

| 항목 | R0 인계 상태 |
|---|---|
| `CTY.axis-01` · `CTY.dist-01` | `S01-C01`–`C04`: 오빠 화면 좌 / 동생 화면 우를 공간 기준으로 유지(한 사람만 보여도 상대 위치·시선은 유지). 계산대 사이 약 1.2m는 예시 값, 실측 아님. 축 이탈 제안 없음, R2 확인 필요. |
| 인물·손 | `S01-C02.b4` 손등 자국 언급; 손을 보여주는 시점·자세는 R1에서 확인. `S01-C03`는 상대를 듣는 상태를 유지하되 특정 말에 대한 반응은 그 말 뒤. `C04`는 같은 장면의 연속. |
| 의상·소품·공간 | 예시상의 `WRD-01a`/`WRD-02a`와 계산대 위치는 네 컷에서 유지하는 가안. `D005`에서 장부를 언급하나 현시점 소품 이동·인계 근거는 없음. 손에 든 소품의 변경도 제안하지 않음. `DNT`, 의상·장소·소품 바이블로 확인 필요. |

## 발화 밀도와 감독 판정 요청

한국어 패키지 기본값: 보통 7.0음절/초 이하, 차단은 8.5 초과. 쉼 1회당 0.3초를 구간에서 뺍니다. 실측 낭독이 아닙니다.

| CLI 결과 | 대상 | 유효 발화 밀도 |
|---|---|---:|
| `TL04` 차단 | `S01-C01.b1` · `D001` | 19 / 2.0 = **9.50** |
| `TL04` 차단 | `S01-C02.b1` · `D002` | 23 / 2.5 = **9.20** |
| `TL05` 경고 | `S01-C02.b3` · `D004+D005` | 26 / 3.7 = **7.03** |
| `TL04` 차단 | `S01-C03.b3` · `D009+D010` | 36 / 3.2 = **11.25** |

`TL01`/`TL02`/`TL03` 보고 없음. 컷 및 하위 구간은 0.0–30.0초를 덮습니다. 반응 순서, 실제 호흡, CTY는 이 검사 결과가 보증하지 않습니다.

### 안 1 — 원문 보존, 종료 34.0초(+4.0초)

영향 컷은 `S01-C01`–`S01-C04` 모두입니다. EX-02 보정판의 배정을 적용한 가안입니다. **동일 원문으로 메모리 내 `timeline_check` 통과**(아래 로그). 연기·편집 확정 전입니다.

| 컷 · 새 경계 | 전역 하위 구간 → 대사/무대사 |
|---|---|
| `S01-C01` 0.0–3.0 | `.b1` 0.0–3.0: 0.0–0.2 무대사, `D001` 0.2–3.0 |
| `S01-C02` 3.0–22.0 | `.b1` 3.0–6.5 `D002`; `.b2` 6.5–10.0 `D003`; `.b3` 10.0–14.5 `D004+D005`(쉼 1); `.b4` 14.5–18.0 `D006+D007`(쉼 1); `.b5` 18.0–22.0: `D008` 18.0–21.0, 21.0–22.0 정지 |
| `S01-C03` 22.0–31.0 | `.b1` 22.0–23.0 무대사; `.b2` 23.0–27.0 `D009`(화면 밖 가안); `.b3` 27.0–31.0: 27.0–28.5 오빠의 무언 반응, 28.5–30.5 `D010`(화면 밖 가안), 30.5–31.0 무대사. `D009`의 ‘세탁소 아줌마’ 발화 뒤로 반응을 둠 |
| `S01-C04` 31.0–34.0 | `.b1` 31.0–34.0: 31.0–31.3 흡기, `D011` 31.3–32.8, 32.8–34.0 정지 |

### 안 2 — 종료 30.0초·현 타임슬롯 고정, 작가에게 축약 요청

컷 경계와 쉼을 유지하면서 보통 상한(7.0음절/초)을 목표로 잡습니다. 아래는 **수정 지시의 분량 목표**이지 새 대사나 확정본이 아닙니다.

| 요청 대상 | 분량 목표 | 유지할 씬 기능 |
|---|---:|---|
| `D001` · 0.0–2.0 | 19 → **14음절 이하**(최소 5 감소) | 보증금 인상과 버틸 수 없다는 갈등 제기 |
| `D002` · 2.0–4.5 | 23 → **17음절 이하**(최소 6 감소) | 오빠의 말에 맞서는 동생과 노동의 주체 |
| `D009+D010` · 24.5–28.0 | 36 → **합계 22음절 이하**(최소 14 감소, 쉼 0.3초 유지) | 이름 대신 가게로 불리는 정체성 및 `D011`로 이어지는 고백. 특정 단어에 대한 반응은 발화 뒤에 배치 |
| `D004+D005` · 8.0–12.0 | 경고도 해소할 경우 **합계 25음절 이하** | 오빠의 부재 추궁. 필수 차단 항목은 아님 |

`S01-C03`의 6.0초 무대사 일부를 재배분하는 방안은 별도 선택지입니다. 반응 여백이 줄고 컷 경계가 바뀔 수 있으므로 감독 판정 없이 적용하지 않습니다. 30초 축약안은 작가 수정본 수령 후 재검해야 합니다.

## DLV · 감독 전달

```yaml
dlv_for: "사용자 직접 요청: 조연출 R0 (CALL ID 미제공)"
artifacts:
  - {id: CNT@draft, location: "이 인계의 컷/대사 표", status: "등록 전"}
  - {id: CTY, location: "이 인계의 CTY 초안", status: "등록 전"}
consumed:
  - {path: tests/fixtures/ex02-defect-30s/index.csv, pin: null}
  - {path: tests/fixtures/ex02-defect-30s/SCR.md, pin: null}
assumptions:
  - "화자·화면 배치·연속성은 EX-02 참고 예시 기반이며 작업 입력의 정본 핀 아님"
  - "발화량은 패키지 기본 추정값, 실측 없음"
conflicts:
  - "목표 30.0초 / 현 타임슬롯 vs 원문 발화량: D001, D002, D009+D010 차단; D004+D005 경고"
  - "D009의 자극보다 반응이 앞서지 않도록 R1/R6에서 확인"
checks:
  - "30초 입력 CLI: exit=1; TL04 3건, TL05 1건"
  - "34초 가안 익명 파이프 입력 CLI: exit=0; []"
missing_inputs:
  - "감독: 러닝타임/원문 변경 판정(RUL), DNT 및 SCR 버전 핀"
  - "담당 부서: PLT 및 P2 바이블 버전 핀, SND 발화속도 실측(있다면)"
self_verdict: partial
```

**다음:** 감독이 34.0초 연장 또는 30.0초 유지·작가 축약 중 하나를 판정한 뒤, 결정안으로 낭독과 타임라인을 재검합니다. 작업 입력·프로젝트 파일·원장 수정, 스테이징, 외부 실행은 없었습니다. 기록은 이 지정 인계 파일에만 남겼습니다.

## 실제 도구 로그

- `read`: `assistant-director/SKILL.md`, `assistant-director/assets/{CNT-template.md,CTY-template.md,conti-layers-template.yaml}`, `production-director/assets/DLV-template.yaml`, `docs/design/{05-conti-collaboration.md,03-artifact-index.md,07-video-prompt-spec.md,01-pipeline-and-gates.md}`, `docs/examples/synthetic-laundromat-34s/fixture.md`, 작업 입력 2개, 구현 CLI `scripts/timeline_check.py`. 평가기/테스트 소스는 열지 않았습니다.
- `find`: `**/timeline_check.py` → `scripts/timeline_check.py`.
- `bash`: `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/timeline_check.py --help` → `--index INDEX --runtime RUNTIME [--script SCRIPT] [--json]`, exit 0.

### 원본 30초 CLI (실제 출력)

```console
$ PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/timeline_check.py --index tests/fixtures/ex02-defect-30s/index.csv --runtime 30 --script tests/fixtures/ex02-defect-30s/SCR.md --json
[
  {
    "code": "TL04",
    "target": "D001",
    "message": "speech-rate block: 19 units / 2s, 0 pauses",
    "severity": "error"
  },
  {
    "code": "TL04",
    "target": "D002",
    "message": "speech-rate block: 23 units / 2.5s, 0 pauses",
    "severity": "error"
  },
  {
    "code": "TL05",
    "target": "D004+D005",
    "message": "speech-rate warn: 26 units / 4s, 1 pauses",
    "severity": "warning"
  },
  {
    "code": "TL04",
    "target": "D009+D010",
    "message": "speech-rate block: 36 units / 3.5s, 1 pauses",
    "severity": "error"
  }
]

exit=1
```

### 34초 가안 (실제 출력)

`PYTHONDONTWRITEBYTECODE=1 python3 -B -` 실행기에서 원본을 읽고 위 안 1의 경계·쉼을 메모리에서 적용했습니다. `D009`/`D010`은 원문을 바꾸지 않고 큐만 나눴고, `D011`은 흡기를 큐 앞에 별도 배정했습니다. 익명 파이프 2개로 검사기에 전달했으며 임시 파일은 만들지 않았습니다.

```console
D001 0.2–3.0s, 19 syllables, 0 pauses, 6.79/s
D002 3.0–6.5s, 23 syllables, 0 pauses, 6.57/s
D003 6.5–10.0s, 23 syllables, 0 pauses, 6.57/s
D004+D005 10.0–14.5s, 26 syllables, 1 pauses, 6.19/s
D006+D007 14.5–18.0s, 11 syllables, 1 pauses, 3.44/s
D008 18.0–21.0s, 18 syllables, 0 pauses, 6.00/s
D009 23.0–27.0s, 26 syllables, 0 pauses, 6.50/s
D010 28.5–30.5s, 10 syllables, 0 pauses, 5.00/s
D011 31.3–32.8s, 8 syllables, 0 pauses, 5.33/s
running: /usr/bin/python3 -B scripts/timeline_check.py --index /dev/fd/3 --runtime 34 --script /dev/fd/4 --json
[]
exit=0
```

- `bash`: `git status --short; git diff --cached --name-only` → Git 저장소 아님(exit 129). `git rev-parse --is-inside-work-tree`로 재확인 → `Not a Git work tree; no repository index here.`
