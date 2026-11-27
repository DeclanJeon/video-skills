# 감독 인계 · 조연출 R0 · 30.0초

`acting_as: assistant-director` · `CNT@draft` / `CTY` 채팅 초안 · **현행 타임라인 차단**

감독님, 원본 `index.csv`와 `SCR.md`를 그대로 넣어 `timeline_check`를 실행했습니다. 컷과 하위 구간은 0.0–30.0초를 빈틈·겹침 없이 덮고, 입력 대사 D001–D011은 모두 한 컷에 배정돼 있습니다. **발화 밀도에서 TL04 3건과 TL05 경고 1건으로 종료 코드 1**입니다. 대사는 고치지 않고 C03의 무대사 시간을 앞 컷과 C03 발화에 재배분하는 30초안을 권합니다.

## CNT — 원본 컷·대사 배정

아래 초는 모두 전역 시간입니다. 대사 ID와 시간창은 두 작업 입력 기준입니다. 화자·화면 내외·장면 기능은 별도 정본 핀이 없는 상태에서 DES-05가 연결한 EX-02 예시를 참고한 R0 배정입니다. 묶음 내부의 개별 대사 시점은 원본에 없으므로 나누어 실측한 것처럼 쓰지 않았습니다.

| 컷 / 범위 / 길이 | 하위 구간과 발화·무대사 | 장면 기능 |
|---|---|---|
| `S01-C01` / 0.0–2.0 / 2.0초 | `.b1` 0.0–2.0 `D001` 오빠(`CHR-01`, 화면 안) **TL04** | 보증금 인상과 더는 못 버틴다는 압박 제시 |
| `S01-C02` / 2.0–18.5 / 16.5초 | 동생(`CHR-02`, 화면 안): `.b1` 2.0–4.5 `D002` **TL04**; `.b2` 4.5–8.0 `D003`; `.b3` 8.0–12.0 `D004+D005`(사이 쉼) **TL05**; `.b4` 12.0–15.5 `D006+D007`(사이 쉼); `.b5` 15.5–18.5 `D008` | 반격 → 20년 노동 → 오빠의 부재 → 손의 화상 자국 → 매각으로 잃는 것 |
| `S01-C03` / 18.5–28.0 / 9.5초 | 오빠의 청자 컷: `.b1` 18.5–21.0, `.b2` 21.0–24.5 모두 **무대사**(합계 6.0초); `.b3` 24.5–28.0 동생(`CHR-02`, 화면 밖) `D009+D010`(사이 쉼) **TL04** | 무언 방어에서 정체성 상실의 고백을 듣는 장면으로. 무대사는 영상 공백이나 환경음까지 없는 무음이 아님 |
| `S01-C04` / 28.0–30.0 / 2.0초 | `.b1` 28.0–30.0 `D011` 동생(`CHR-02`, 화면 안), `pauses: 1`. 발화·쉼 내부 경계는 원본 미지정 | “아무것도 아니잖아”로 문장과 장면 마무리 |

입력에 오버랩·L컷 선언은 없습니다. C03의 화면 밖 발화 자체는 L컷이 아니며, C03–C04는 `D010`→`D011`의 문장 연결로 다룹니다. EX-02 예시처럼 C03.b2를 “세탁소 아줌마”에 대한 특정 반응으로 연출하면, 원본에서는 자극이 `.b3`에서 뒤늦게 나오므로 순서가 뒤집힙니다. 이는 **문서 대조로 발견한 연출 위험**이지 `timeline_check`가 출력한 오류는 아닙니다.

## 보정안 — 30.0초 고정, 원문 유지 권고

감독 승인용 시간표입니다. C03 앞의 무대사 6.0초를 줄여 C01·C02와 C03 대사에 시간을 줍니다. 대사 겹침이나 L컷을 가정하지 않습니다.

| 컷 / 새 범위 | 새 하위 구간과 배정 |
|---|---|
| `S01-C01` / 0.0–2.8 | `.b1` 0.0–2.8 `D001` (19 / 2.8 ≈ 6.79음절/초) |
| `S01-C02` / 2.8–19.6 | `.b1` 2.8–6.1 `D002` (23 / 3.3 ≈ 6.97); `.b2` 6.1–9.6 `D003`; `.b3` 9.6–13.7 `D004+D005` (쉼 0.3초 가정, 26 / 3.8 ≈ 6.84); `.b4` 13.7–16.8 `D006+D007` (손과 쉼 확보); `.b5` 16.8–19.6 `D008` |
| `S01-C03` / 19.6–27.8 | `.b1` 19.6–20.6 무언 방어; `.b2` 20.6–24.6 `D009` 화면 밖 (26 / 4.0 = 6.50); `.b3` 24.6–27.8 오빠 반응 시작 → 25.2–27.2 `D010` 화면 밖 (10 / 2.0 = 5.00) → 27.2–27.8 무대사 유지. 특정 반응은 `D009`가 끝난 뒤에 둠 |
| `S01-C04` / 27.8–30.0 | `.b1` 27.8–28.1 흡기(무대사), 28.1–29.5 `D011` (8 / 1.4 ≈ 5.71), 29.5–30.0 무대사 정지 |

새 컷 길이 합은 2.8 + 16.8 + 8.2 + 2.2 = **30.0초**입니다. 음절/초는 DES-07 기본값(보통 상한 7.0, 차단 >8.5, 쉼 0.3초/회)을 이용한 **계산 추정**이며, 낭독 실측도 수정안의 CLI 통과 결과도 아닙니다. C01·C02.b1은 보통 상한에 가까워 실제 호흡을 넣어 확인해야 합니다. 현행 `D004+D005`는 쉼을 빼면 26 / 3.7 ≈ 7.03이므로 경고를 무시하거나 격앙으로 임의 표기하지 않고 0.1초를 더 배정했습니다.

**대안 — 기존 컷 경계·발화창을 유지해야 한다면:** 감독·각본 담당 승인 아래 축약을 검토합니다. 예: `D001` “다음 달 보증금 올라. 못 버텨.”, `D002` “오빠가 버텼어? 매일 문 연 건 나야.”, `D009` “내 이름 대신 세탁소 아줌마래.” + `D010` “간판 내리면 난 그냥—”. `D004+D005`도 경고가 남으므로 한두 음절 축약을 검토합니다. C03의 반응은 이 안에서도 자극이 들린 뒤에 와야 합니다. 이는 원문 변경과 감정 정보 손실이 있는 대안이며 **적용하지 않았습니다**.

## CTY 초안과 감독 판정 요청

- `CTY.axis-01` / `CTY.dist-01`: EX-02 예시 기준 오빠 화면 좌, 동생 화면 우, 계산대를 사이에 두고 약 1.2m. C01→C02 시선 정합, C03에서 동생 목소리의 방향은 동생이 서 있는 쪽, C04에서 같은 축 복귀. 실제 화면 방향·거리·축 이탈은 촬영과 확인 전 미확정입니다.
- `CTY` 상태 전이: C02.b4에서 동생의 오른손 등 화상 자국 공개 → C03에서 같은 동생이 화면 밖에서 계속 말함 → C04에서 동생 화면 복귀. EX-02 예시의 의상(`WRD-01a`·`WRD-02a`)은 유지 후보입니다. 장부 언급은 소품을 건네거나 움직였다는 근거가 아니므로 소품 소유·이동과 정확한 손 위치는 바이블·블로킹 확인 전 미확정입니다.
- **미판정:** 30초 안에서 원문을 유지하려면 앞 컷과 C03 발화에 시간을 주고 초기 무언 정지를 짧게 해야 합니다. 컷 경계가 고정이면 대신 각본 축약이 필요합니다. 감독이 택한 안만 관련 부서에 넘겨, C03 자극→반응 순서와 C04 정지를 확인한 뒤 실제 낭독 및 승인본 `timeline_check`를 다시 요청합니다. `RUL` 발행이나 R1 이후 레이어 변경은 하지 않았습니다.

```yaml
dlv_for: "사용자 지정 조연출 R0 (CALL ID 미제공)"
artifacts: [] # 채팅의 CNT@draft·CTY 초안만 반환, 프로젝트 등록 요청 없음
consumed:
  - "tests/fixtures/ex02-defect-30s/index.csv (버전 핀 미제공)"
  - "tests/fixtures/ex02-defect-30s/SCR.md (버전 핀 미제공)"
assumptions:
  - "화자·화면 배정·축은 EX-02 예시를 근거로 한 R0 제안; 작업 입력의 정본 핀이 아님"
  - "시간·발화율은 계산 추정; 실측 없음"
conflicts:
  - "30.0초 고정 vs 원문 발화 시간/무언 정지; 감독 판정 대기"
  - "C03 특정 반응을 원본 b2에 두면 발화 자극보다 앞섬; 연기/편집 확인 대기"
checks:
  - "원본 timeline_check: exit 1, TL04 3건 / TL05 1건"
  - "컷·하위 구간 0.0–30.0초 연속 및 D001–D011 배정 대조"
  - "실행 전후 원본 2개 SHA-256 동일"
missing_inputs:
  - "DNT#S01, P2 바이블·SND#speech-rate 실측, PLT 비트·정본 버전 핀, CALL ID"
self_verdict: partial # R0 인계 완료, 타임라인 승인/마감은 보류
```

## 실제 도구 로그

1. `find`/`ls`로 스킬 위치 확인. `read`: `assistant-director/SKILL.md`, `docs/design/05-conti-collaboration.md`, `docs/design/03-artifact-index.md`, `assistant-director/assets/{CNT-template.md,CTY-template.md,conti-layers-template.yaml}`, `production-director/assets/DLV-template.yaml`, 작업 입력 두 파일. `find **/timeline_check.py` → `scripts/timeline_check.py`. 평가기 소스는 열지 않았습니다.
2. 사전 `bash`: `git status --short; git diff --cached --name-only; sha256sum tests/fixtures/ex02-defect-30s/{index.csv,SCR.md}; python3 -B scripts/timeline_check.py --help`. Git은 현재 위치가 저장소가 아니라고 반환했고 `--cached` 조회를 할 수 없었습니다. 스테이징 작업은 전혀 하지 않았습니다. `--help` 종료 0, 실제 usage: `timeline_check.py [-h] --index INDEX --runtime RUNTIME [--script SCRIPT] [--json]`.
3. 실행한 검사 명령 (그 뒤 셸에서 종료 코드를 출력하고 두 입력의 해시를 다시 계산):

```sh
python3 -B scripts/timeline_check.py --index tests/fixtures/ex02-defect-30s/index.csv --script tests/fixtures/ex02-defect-30s/SCR.md --runtime 30 --json
```

실제 JSON 출력 및 종료 코드:

```text
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
timeline_check exit=1
```

`sha256sum` 사전·사후 동일 출력:

```text
9781c6992ae7a15dae5adb8284d960c07e03f422268c42218299ef3ec5327b78  tests/fixtures/ex02-defect-30s/index.csv
42057aaac00fe7e8a161c3e19f4e02004c7a42f97982e648d9b1c80a645b78af  tests/fixtures/ex02-defect-30s/SCR.md
```

4. 규정과 예시 확인: `grep`으로 `docs/design/07-video-prompt-spec.md` §3, `docs/design/01-pipeline-and-gates.md` §4, `production-ledger/references/ledger-schema.md`의 타임라인 계약 확인; `read`로 `docs/examples/synthetic-laundromat-34s/fixture.md` 및 `docs/design/01-pipeline-and-gates.md` §4.2 확인. 예시는 연출 참고이며 보정 픽스처를 CLI에 넣지 않았습니다.
5. 지정된 세션 보고서만 작성했습니다. 프로젝트 파일·원장 쓰기 및 외부 실행 없음.
