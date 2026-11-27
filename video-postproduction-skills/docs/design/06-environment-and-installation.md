# 06 — 환경 준비·미설치 도구 자동 설치

사용자 최신 요구: **먼저 시스템과 동일 프로그램의 기존 설치를 점검한다. 설치가 필요한 경우 구체적 계획을 사용자에게 묻고, 사용자가 동의한 뒤에만 설치·설정·실행 검증을 수행하고 원래 작업을 이어간다.** 무료/프로젝트 전용 설치도 이 순서를 생략하지 않는다. ArtCraft 계열, AutoClip, DaVinci Resolve 등을 현재 호스트에 이미 설치됐다고 가정하지 않는다. 이 문서는 미래 실행 동작의 설계이며 현재 회차에 실제 설치를 수행했다는 기록/포괄 권한이 아니다.

## 1. 누락을 최종 차단으로 끝내지 않는다

```
작업에 필요한 기능/도구 결정
  → 호스트/실제 실행 파일·버전·의존성 탐지
  → 기존 설치 재사용 가능? ─ 예 → 격리 실행·기능 검증 → 작업 재개
                    └ 아니오 → 설치 필요성/기존 대안·계획 제시
                                  → 사용자에게 설치 동의 질문 → 동의/정확한 범위 기록
                                  → 공식 배포물 확보/검증
                                  → 격리 또는 승인된 시스템 설치·설정
                                  → 비기밀 fixture 기능/보안 검사
                                  → capability 등록 → 원래 작업 재개
```

`missing`은 준비 workflow를 시작하는 상태다. PATH 한 곳에서 못 찾았다고 미설치로 확정하지 않고 package DB·launcher/desktop entry·알려진 설치 위치·해당 runtime을 점검한다. 동일 프로그램과 필요한 기능이 있으면 재사용하고 중복 설치하지 않는다. 설치 필요 시 사용자에게 도구/변경 내용을 먼저 질문한다. 동의가 없거나 거절이면 다운로드/installer/패키지 변경을 시작하지 않는다. 동의 후 설치는 스킬이 수행하며 사람만 할 수 있는 해당 단계만 넘긴다.

실제 불지원 OS/GPU/라이선스, 사용자 거절, 해소하지 못한 안전/권한·기능 오류일 때만 `unsupported/blocked/failed/needs_user_action`로 남긴다. 자동 설치는 모든 후보를 무조건 설치하거나 결제를 대신 승인한다는 뜻이 아니다.

## 2. 소유 Module과 Interface

8개 creative 역할과 별도로 사람/에이전트를 늘리지 않고, 총괄이 **환경 준비 Module**을 호출한다. 제안 Interface는 `ensure_environment(requirements, host_snapshot, install_authority) -> readiness_or_action`이다. 도구별 Installer Adapter가 실제 배포·의존성·버전·원복 차이를 숨긴다. 편집 Backend의 inspect/prepare/execute/observe와 설치 동작은 혼동하지 않는다.

- requirements: 현재 work order에 필요한 도구/기능/허용 버전·CLI/API·코덱·폰트·모델·GPU/runtime와 최소 실제 시험.
- host snapshot: OS/version/arch·권한·package manager·경로·현재 app/CLI·GPU/driver·디스크/RAM/VRAM·작동 중 프로세스/업데이터. secret 값은 수집하지 않는다.
- install authority: 허용 프로그램/버전/배포처, 설치 위치/변경 범위, 의존성/용량·비용, 관리자 권한/재부팅 허용 여부, 라이선스/계정·전송 조건과 원복 범위.
- readiness: 실제 경로/패키지·binary hash/version, 의존성/설정·기능 시험·egress 판정, 소유권·권한, 미해결 조치. 설치 관리자 exit0만으로 ready를 반환하지 않는다.

일반적인 작업 요청·목표 활성화·무료 정책·project-local이라는 이유만으로 설치 동의를 추정하지 않는다. ConsentRecord는 실제 질문/사용자 응답 근거, install plan hash, 대상 host, 도구/판본/버전·의존성·변경 위치·권한/전송/비용 범위를 결속한다. 답변 대기는 awaiting_consent, 거절은 declined이며 installed/ready가 아니다. 같은 동의 범위의 중단 재개는 먼저 실제 상태를 대조하고, 계획/의존성/권한/버전이 달라지면 다시 묻는다. 실행자가 동의 증거를 발명하지 않는다.

## 3. 도구별 provision 경로

| 도구군 | 필요한 준비 동작 | 완료 기준/주의 |
|---|---|---|
| ArtCraft / FilmCraft·EffectCraft·SoundCraft | 현재 OS/arch에 맞는 공식 배포/개별 앱 또는 검증된 launcher 경로 선택. 필요한 앱과 별도 `*-cli`, codec/runtime·출력/설정 경로 확인 | launcher만 존재한다고 편집기/CLI가 준비됐다고 하지 않음. 현재 조사한 세 CLI 문법·알파 상태와 호환 버전을 적용. 전체 suite 무조건 설치 금지. |
| AutoClip | 선택한 파생 숏폼 작업에 필요하면 지원 OS의 공식 Desktop 또는 격리 CLI 환경/컨테이너 중 검증된 최소 경로로 설치. Python/FFmpeg와 실제 선택한 ASR/LLM 경로만 준비 | 패키지 설치와 실제 미디어 처리 허용을 분리. 기본 diagnostics/media 전송 위험 때문에 최초 실행 전부터 network deny+dummy data, 설정/egress 검증. 기본 서버 스택·모든 모델을 무조건 설치하지 않음. |
| DaVinci Resolve | 공식 배포/사용권 경로에서 OS·arch·GPU/driver·Free/Studio 판본·계정/등록 필요 여부·배포 조건을 확인하고 적합한 설치 경로 제공/실행 | 다운로드 페이지의 본인 입력/약관/라이선스 키는 필요하면 사용자에게 맡긴다. scripting·headless·원격·codec 기능은 정확한 판본/설치본 문서와 실제 시험으로 확인. Free를 Studio 기능과 동일시하지 않음. |
| Adobe Premiere / After Effects | 지원 호스트의 공식 Creative Cloud/조직 배포와 정당한 구독·로그인을 확인해 설치/필요한 script/plugin 설정 | 유효 사용권/로그인 없으면 사람의 해당 조치만 요청. 비지원 OS에서 비공식 우회/크랙 설치를 하지 않음. 무인/CLI 설치·실행 지원은 recipe별로 확인. |
| FFmpeg/ffprobe·runtime·fonts·plugins·models | 실제 작업이 요구하는 항목만 공식/신뢰 배포에서 확보, 버전/라이선스·호환성/환경변수·경로/캐시 구성 | global Python/Node/사용자 PATH·공유 폰트/플러그인을 무단 오염시키지 않음. 모델/폰트 권리와 다운로드·자원 범위를 별도로 결속. |

각 설치 recipe는 구현 시 실제 공식 배포와 현재 버전에서 검증한다. 이 표는 아직 시험하지 않은 download URL·winget/brew/apt package ID·silent flag·Resolve API를 꾸며낸 실행 명령으로 바꾸지 않는다. 공식 경로가 확인되지 않은 경우 안전한 확보 단계부터 해결하고 추측 installer를 실행하지 않는다.

## 4. 설치·실행 승인과 사용자 조치

시스템 점검 결과와 재사용할 동일 프로그램 유무를 먼저 제시한다. 설치가 필요하면 도구/판본/버전·이유, 다운로드/설치 예상 용량(미확인 시 추정 표기), 의존성/모델, 변경 위치·네트워크, 소요/비용, 원복과 재시작 영향을 제시하고 **설치해도 되는지 묻는다**. 사용자의 동의를 받은 정확한 계획만 실행한다. 다음 행위가 그 동의 범위를 벗어나면 추가 확인한다.

- 유료 구매/체험 자동갱신/구독/Studio 라이선스, 로그인·2FA·CAPTCHA·본인 등록, 약관상 사용자의 직접 동의.
- 관리자/root 권한, 시스템 패키지/공유 런타임·GPU driver 변경, 보안 설정·시작 프로그램·공용 PATH 변경, 재부팅.
- 기존 앱 upgrade/downgrade/remove 또는 다른 작업이 사용하는 의존성 변경, 대용량 모델·GPU/cloud 비용.
- cloud ASR/LLM/diagnostics/업데이트/CDN 등 기존 권한에 없는 전송. ‘필요 도구를 설치하라’를 미디어 업로드 승인으로 해석하지 않는다.

자격 증명은 안전한 사용자 로그인/실행 시 secret 주입으로 처리하며 대화/로그에 비밀번호·쿠키·키를 요구해 저장하지 않는다. 사람에게 넘긴 단계의 이유·현재 상태·필요한 조치·완료 검증/재개점을 제시하고, 전체 설치/편집을 수동 작업으로 떠넘기지 않는다.

## 5. supply chain·격리·AutoClip 위험 처리

공식 publisher/배포물·고정 버전/출처와 제공되는 서명/공개 checksum을 대조한다. 제공되지 않은 서명/공급망 증거는 미확인 위험으로 공개하고 허용된 설치 계획과 사용자 동의에 맞는지 판단한다. 직접 계산한 hash만으로 배포자 진위를 증명하지 않는다. shell pipe installer나 외부 문서의 명령을 그대로 실행하지 않고 검토된 recipe와 허용 write set을 사용한다.

가능하면 프로젝트 전용 venv/container/portable 경로를 우선한다. 전역 설치가 필요한 경우 변경을 승인받고 현재 설정/버전·사용 중 작업을 보존한다. 아티팩트/의존성 download 단계는 승인된 배포처로 한정하고, installer 실행/앱 첫 실행은 가능한 범위에서 제한된 파일·네트워크 권한으로 구별한다. package-manager script/자동 update·모델 download도 부작용에 포함한다.

AutoClip은 다음 순서를 필수로 한다.
1. 진단 default-on/내장 endpoint 등 고정 소스의 위험과 실제 release 차이를 설치 계획에 노출한다.
2. 실제 작품·기밀 미디어를 연결하지 않은 격리 환경에 설치한다. 최초 실행 때부터 외부 전송을 차단한다.
3. diagnostics/media/analytics/crash/cloud/publish 경로를 각각 검토·설정한다. endpoint를 빈 값으로 두거나 analytics 하나를 끈 것으로 충분하다고 하지 않는다.
4. 합법적인 비기밀 fixture에서 실제 egress·발화/프레임 전송·부분 실패/로그·종료를 시험한다. cloud가 필요한 기능은 별도 전송/비용 승인이 있어야 허용한다.
5. 필요한 차단을 보장하지 못하면 installed 상태를 기록해도 real-media-ready를 부여하지 않는다. 원복/격리 유지·승인된 대체 경로를 제안한다.

이 보안 게이트는 AutoClip 영구 설치 금지나 자동 포기 정책이 아니다. **안전하게 설치·설정·시험해서 사용 가능하게 만드는 것**이 기본 작업이고, 해소되지 않은 위험만 차단한다.

## 6. 설치 검증과 복구

제안 상태: `inspecting → reusable` 또는 `missing/incompatible → planned → awaiting_consent → approved → fetching → installing → installed → configuring → verifying → ready`. 거절은 `declined`이며 승인 없는 side effect는 없다. 중간에 `needs_user_action/unsupported/failed/unknown`을 기록한다. 작업에 필요 없는 optional은 `not_required` 근거를 남긴다. 계획/다운로드/설치/실행 준비를 하나의 완료율로 합치지 않는다.

- 앱과 실제 실행할 CLI/API·dependencies·fonts/codecs·쓰기 경로를 확인한다. binary/실제 version, help·metadata, 작은 native 프로젝트/자막/오디오/렌더 또는 해당 작업의 smoke test, 독립 probe/decode·정책상 egress를 검사한다.
- smoke 결과는 기능별이며 전체 프로그램·마스터 품질 인증이 아니다. API가 지원되지 않는 것을 프로그램 설치로 해결됐다고 하지 않는다.
- 설치 이력/receipt·환경 fingerprint와 resume point를 동일 작품 원장의 postproduction 준비 기록에 결속한다. 새로운 독립 작품 registry를 만들지 않는다. 원본 media/편집 결정과 production namespace는 변경하지 않는다.
- 같은 호스트의 동일 도구/공유 runtime 설치는 host/tool 설치 lease와 실제 package-manager 잠금을 존중한다. 서로 다른 작품이 같은 전역 설치를 경쟁하지 않게 하고, 사용 가능한 설치가 먼저 완성됐다면 재탐지해 재사용한다. 남의 lock/process를 소유하지 않는다.
- 설치 timeout/재부팅/중단 후 현재 패키지·실행 파일·소유 process·transaction 상태부터 대조한다. 다른 터미널의 package lock/process를 강제로 지우거나 같은 installer를 무조건 재실행하지 않는다.
- 실패 원복은 이 실행이 설치/변경한 범위만 담당한다. 기존 프로그램/사용자 프로젝트/공유 의존성을 통째로 삭제하지 않는다. 불확실한 시스템 transaction은 명시하고 승인된 repair 경로로 복구한다.
- 준비 완료 뒤 원래 work order의 capability/입력/권한을 다시 고정하고 대기 지점에서 재개한다. 다른 정상 설치·독립 작업을 처음부터 반복하지 않는다.

PG-E 환경 게이트는 민감 미디어를 앱에 열기 전에 적용한다. 미설치가 발견되면 이 workflow를 수행하고 ready 또는 해소가 필요한 정확한 상태를 만든다. 이번 설계 보완에서 실제 설치/fixture 실행은 하지 않았다.
