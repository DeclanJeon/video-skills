# 02 — 실행자·실제 지원·작업 복구

근거: [로컬 조사](../research/local-discovery-01.md), `qa/design/discovery.json`과 각 CLI help/command IDs. ‘metadata 조회 성공’과 ‘실제 편집/렌더 검증’을 구별한다.

## 1. 현재 설치본과 역할

| 실행자 | 이번에 직접 확인 | 기본 작업 / 검증되지 않은 것 |
|---|---|---|
| FilmCraft | package 0.20.1-1, `filmcraft --version` 0.20.1, `filmcraft-cli --help`, commands JSON 718개 | NLE 편집·conform·색·최종 sequence/export 우선. 명령 개수는 정확성/품질 보증 아님. |
| EffectCraft | package 0.25.1-1, `effectcraft-cli --help`, commands JSON 766개 | 합성·모션·타이틀. `effectcraft --help`는 unknown option/exit1이었고 **별도 CLI는 성공**. alpha/색/영상 export 미실행. |
| SoundCraft | package 0.20.1-1, app version 0.20.1, `soundcraft-cli --help`, commands JSON 483개 | 사용 가능한 음향의 편집·믹스·bounce. stem/동기/음량 정확성 미실행. |
| FFmpeg/ffprobe | 실행파일 경로 확인, 기존 production의 기술 검사 도구 | 독립 probe/decode/측정·명시한 변환/최종 mux 보조. Craft creative 작업의 몰래 대체 실행자가 아님. |
| Premiere / After Effects / Resolve | 사용자 허용 도구군, 현재 설치/실행 endpoint 미확인 | 검증된 작업·머신·버전만 선택 Adapter로 추가. 본 Linux 조사로 다른 컴퓨터의 설치 여부를 단정하지 않음. |

설치 README는 FilmCraft alpha, EffectCraft alpha/고객 production 비권장, SoundCraft pre-alpha를 명시한다. 그 문서의 기능·성능/준비율 수치는 공급자 주장이다. 이번 설계는 CLI가 있다는 이유로 실제 납품에 무조건 적합하다고 선언하지 않고 실행자별 fixture/integration gate를 둔다.

미설치/incompatible은 최종 실패가 아니라 [환경 준비 Module](06-environment-and-installation.md)의 시작 조건이다. 시스템과 동일 앱/CLI의 기존 설치를 먼저 점검해 재사용하고, 새 설치가 필요하면 사용자에게 계획을 묻고 동의 후 앱/CLI·의존성을 설치·설정·시험해 원래 work order를 재개한다. 실제 불지원/새 권한·사람 조치/해소 불능 오류만 구체적 상태로 반환한다.

## 2. 하나의 작은 Interface, 실제로 다른 Adapter

Backend module의 제안 Interface는 `inspect`, `prepare`, `execute`, `observe` 네 동작으로 제한한다. coordinator는 수백 개의 native 명령/프로젝트 포맷을 직접 알 필요가 없다.

- inspect: binary/version/SHA, 현재 환경, 명령/기능·출력 포맷, 세션 소유권을 관측. 문서만 있는 capability는 미확인으로 반환.
- prepare: 고정 `PostWorkOrder + CapabilitySnapshot + EditAuthority`에서 native 실행 계획/입출력/unsupported·손실을 만든다. side effect 없는 검사다.
- execute: 소유 세션·작업 사본·허용 명령으로 실행하며 실제 job/command/프로젝트·출력 대응을 반환.
- observe: 같은 job의 사실만 관측. 현재 입력 유효성·creative 품질/마스터 채택과 분리.

로컬에 실제 다른 실행자 셋이 있으므로 seam이 존재한다. native 문법·resource ID·단위·오류·저장·비동기 의미는 각 Adapter 내부에 둔다. exporter와 독립 artifact/QA 검사 module을 구별해 실행자가 자기 성공을 자기 인증하지 않게 한다.

### 서로 다른 명령 문법

현재 help에서 직접 확인한 구분이며 아래는 실행 지시/실행 완료 기록이 아니다.

| 도구 | batch/실행 문법의 차이 |
|---|---|
| FilmCraft CLI | `run <script.jsonl>`의 각 줄은 `{id,params}`. `exec/describe/inspect/import/export/render/probe` 제공. `file.exportMedia`는 기본 대기하며 `wait:false`는 예외. |
| EffectCraft CLI | `run --commands FILE`은 JSON array/JSONL `{command 또는 id,params}`. composition/layer/property 및 `render-frame/render`, `.ectemplate`, script/bridge 경로가 별도. |
| SoundCraft CLI | `run/script/commands/describe/info/convert/app`가 별도. script는 `ID JSON` 줄 형식. session/track ID와 sample clock을 확인해야 함. |

하나의 추측한 ‘craft 명령’으로 통일하지 않는다. 내장 JS/JSX/script 임의 실행은 기본 비활성이고, 외부 CSV·README·템플릿 텍스트를 명령으로 해석하지 않는다. allowlist로 검토된 작업/핀만 실행한다.

## 3. 교환은 목적별로 검증

- FilmCraft README는 FCP7 XML/FCPXML/OTIO/EDL/AAF/OMF 등을 설명하지만 `.prproj` native import는 미지원이라고 한다. 문서상 지원도 현재 실제 round-trip 검증과 별개다.
- SoundCraft README는 AAF/OMF interchange를 아직 빠진 항목으로 명시한다. FilmCraft의 AAF export만 보고 SoundCraft까지 되는 것으로 설계하지 않는다. 초기 제안은 실제 WAV/존재하는 stems + sample offset/track cue sidecar + picture reference다.
- EffectCraft README는 독점 프로젝트와 AE SDK plug-in을 지원하지 않는다고 한다. 현재 템플릿은 `authorApp=ppro`의 `.prgraphic/.mogrt` 계열이다. Craft 직접 import를 약속하지 않고 독자 recipe/native 구성 또는 검증한 Adobe 경로를 구별한다.
- 모션 결과는 alpha/색/프레임·길이 계약을 확인한 plate/이미지 시퀀스 등으로 교환할 수 있도록 설계하되 구체 포맷은 실행 검증 후 허용한다. JPEG/불투명 비디오를 alpha layer처럼 쓰지 않는다.
- Premiere 공식 UXP와 AE 공식 script 문서 경로는 참고 조사에서 확인했다. Resolve 공식 경로 하나는 404였으며 API/Free·Studio/원격·headless 지원을 미확인으로 남긴다.
- baked 결과, editable/native 프로젝트, 교환용 타임라인을 각각 표시한다. LUT/폰트/효과/retime/오디오 손실 목록을 수령자가 승인하지 않으면 ‘편집 가능한 동일 프로젝트’ 납품으로 세지 않는다.

## 4. 격리·권한

사용자 세션에 무단 연결/프로젝트 open/`--recover`/미저장 사본 복구를 하지 않는다. 작업별 private directory/config/export prefix를 사용한다. App bridge는 PID/프로젝트/port/세션 nonce/소유권이 일치할 때만 사용하고, 기존 사용자 앱 재사용은 별도 승인한다. FilmCraft app control의 token 요구는 확인했으나 모든 도구의 인증 방식이 같다고 가정하지 않는다. secret은 실행 시 주입하고 로그·원장·native script에는 값을 저장하지 않는다.

읽기/쓰기 roots, 실행 파일/버전 SHA, 허용 명령, CPU/GPU/동시 작업·디스크 한도를 고정한다. 미디어 실행의 네트워크는 기본 거부한다. 설치/의존성 download는 환경 준비 계획의 승인 배포처로 구별하며, 필요한 모델·폰트·플러그인은 같은 준비 workflow에서 권한/권리·용량을 검사하고 설치한다. 공유 환경의 upgrade나 미승인 설치는 묵시적으로 수행하지 않는다. 설치된 앱 내부 경로도 telemetry/업데이트/외부 리소스를 무조건 없다고 가정하지 않는다.

FilmCraft help는 offline media를 placeholder로 export할 수 있다고 경고한다. 기본 경로는 `--allow-offline`을 허용하지 않고 exit code뿐 아니라 `offlineMedia`, 실제 파일·프레임·소스 연결을 대조한다. GUI의 ‘완료’와 파일 존재만으로 success를 채택하지 않는다.

## 5. 제출·관측·현재 결과의 분리

1. 입력/recipe/binary/권한 fingerprint와 native 작업 사본을 고정한다.
2. 부작용 전에 work ID와 예상 write set·입출력·예약을 같은 원장에 기록한다.
3. 실제 명령 반환의 PID/job/native revision/output locator를 먼저 영속화한다. 준비 파일 손상이나 후속 진단 실패가 이미 관측한 job 사실을 버리게 하지 않는다.
4. unknown이면 작업이 끝났다고 세지 않고 소유 process/앱 job/출력/원래 요청을 대조한다. timeout만으로 같은 컷·트랙·렌더를 다시 추가하지 않는다.
5. 현재 채택 시 실제 파일·full decode·출력 범위/metadata·현재 consumed 핀·조건 해소·QA를 다시 대조한다. stale 완료는 역사로 남기고 current로 쓰지 않는다.

제안 lifecycle은 reserved → dispatched/running/unknown → succeeded/failed/cancelled와 별도 downloaded/materialized/verified/adopted다. 첫 재관측이 terminal일 수 있고 중간 상태를 꾸며 넣지 않는다. 취소 요청과 확정 취소, process 종료와 native export 종료를 구별한다. `.partial`·덜 쓴 파일·오프라인 대체 프레임은 최종 파일로 승격하지 않는다. 렌더 재개/프레임 재사용은 capability로 실제 검증된 경우만 허용한다.
