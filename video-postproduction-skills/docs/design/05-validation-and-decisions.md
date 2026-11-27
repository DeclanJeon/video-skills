# 05 — 수락 사례·판단·남은 검증

## 1. 증거 수준

- E0 문서/정적 소스: 공급자가 설명/구현한 경로. 실제 환경 성공 아님.
- E1 설치본 탐지/버전/help: 실행 파일과 help의 실제 응답.
- E2 metadata: 실제 명령 목록/검사 응답. 동작·품질·완전한 schema 인증 아님.
- E3 격리된 실제 native fixture 실행: 입력/명령/결과/디코드/불변 원본을 대조한 특정 경로의 성공.
- E4 프로젝트 통합: 실제 편집/분야 교환/최종 파일·실제 시청/청취와 승인까지 검증.

현재 Craft는 E1/E2만 확인했고 E3/E4는 미실행이다. 템플릿은 metadata 전수+대표 이미지 관찰이며 27개 동영상의 전구간 지각 검수를 하지 않았다. 외부 도구는 정적 조사 E0이다. 이 문서의 사례 수를 실제 테스트 통과 수로 세지 않는다.

## 2. 계획된 수락 사례 52개 — 전부 UNVERIFIED

구현 단계에서는 각 ID를 실제 실패 가능한 fixture/검사와 연결하고 실행 결과를 기록한다. 아직 테스트 파일/코드/렌더가 없으며 아래는 기대 결과다.

| ID | 검증할 사례 / 기대 결과 | 주 표면 |
|---|---|---|
| P01 | Handoff만 있고 요구 본문/필수 보완 snapshot 없음 → 정식 수령 차단 | import contract |
| P02 | source/approval 파일 삭제·교체·symlink·range 초과 → 차단 | 실제 파일 |
| P03 | batch/scope/selection hash가 다른 인계/원장 → 차단 | 기존 실제 모델 |
| P04 | 원본 mixed stereo만 있는데 stem 세 개를 제공했다고 주장 → 차단 | 실제 probe+inventory |
| P05 | 외측 handle0인데 range 밖 dissolve 사용 → 차단; 범위 내 승인 overlap은 별도 허용 | edit map+재생 |
| P06 | mixed FPS/VFR·timecode/PTS가 검증되지 않음 → conform 필요/차단 | 실제 native/독립 probe |
| P07 | 24000/1001·30000/1001·48k sample 변환/반올림 → 명시 정책 내 누적 동기 | 긴 clock fixture |
| P08 | 일부 source만 써 필수 사건/대사 삭제 → 차단, 분모 유지 | event anchor+story QA |
| P09 | overlay가 필수 접촉/표정을 가림, 음악이 대사를 묻음 → coverage 실패 | 실제 시청·청취 |
| P10 | approved nonlinear reveal/time elision 유지와 무승인 반전 누설 → 각각 허용/차단 | 보고+실제 범위 |
| P11 | readonly prepare가 파일/앱을 수정함 → 실패 | 파일 snapshot/native lease |
| P12 | 세 CLI에 동일한 가짜 batch 문법 적용 → 실패, 각 protocol로 교정 | 실제 CLI |
| P13 | import한 native resource ID와 실제 timeline clip/range readback 불일치 → 차단 | native inspect |
| P14 | FilmCraft offline placeholder·export warning/exit1 → 최종본 채택 차단 | 실제 export/decode |
| P15 | EffectCraft alpha premultiply/색·fps/길이 손실 → 차단/수정 | RGBA plate integration |
| P16 | FilmCraft AAF export만으로 SoundCraft AAF import 가능 선언 → 차단; 검증한 audio+offset 경로 | 실제 분야 교환 |
| P17 | unsupported proprietary/native 효과/폰트 누락을 universal round-trip 성공으로 표시 → 차단 | 왕복 손실표+native 확인 |
| P18 | 명령 실패 뒤 일부만 적용/프로젝트 미저장 → partial, 재대조 전 중복 적용 금지 | 실제 native 작업 사본 |
| P19 | 사용자 앱/포트에 무단 연결·recover·kill/덮어쓰기 → 거절 | 소유권/격리 |
| P20 | 렌더 timeout/crash 후 실제 job이 살아 있음 → unknown 보존, 자동 중복 렌더 금지 | process/bridge 재진입 |
| P21 | 확인된 job ID 뒤 입력 손상·진단 쓰기 실패 → 사실은 보존, 현재 채택 별도 차단 | 실제 영속 파일/오류 주입 |
| P22 | 동시 post/production writer·다른 root fields·CAS/원문 충돌 → 보존/명확한 실패 | 실제 공통 잠금 |
| P23 | 준비/QA 뒤 source/range/approval 교체 → 과거 성공 보존/current 채택 거절 | commit 직전 race |
| P24 | 실제 소비한 optional dependency가 invalid/conditional-import 충돌/stale → 재채택 거절 | 현재성+원본 binding |
| P25 | 근거 있는 미선택 optional / imports와 무관한 유효 conditional → 승인 범위 내 유지 | 양성 control |
| P26 | font/recipe/LUT/backend binary 변경 → 관련 결과/QA invalidation, 독립 결과는 유지 | dependency map |
| P27 | OS font fallback인데 원 템플릿 동일 디자인이라고 인증 → 차단; 승인 대체 후 reflow 허용 | 실제 글리프/줄바꿈 |
| P28 | MOGRT/ppro 정의를 EffectCraft native template로 무검증 import → 미지원/차단 | 실제 지원 탐지 |
| P29 | 한국어 장문/강조·복수 화자/하단·오른쪽 UI 침범 → bounds/의미/가독성 실패 | actual font/render+검수 |
| P30 | edit/retime/audio offset 후 이전 SRT/단어 강조 사용 → stale 차단 | source→master cue map |
| P31 | ASR/축약/번역이 승인 대사·화자를 바꿈 → 별도 승인 전 차단 | 원문/실발화 대조 |
| P32 | 없는 source separation/클론 음성·무승인 음악 생성/모델 설치 → 거절 | 권한/트랙 inventory |
| P33 | 실제 음원 LUFS/TP/channel/sync가 profile 초과 → 실패, native meter만으로 인증 금지 | 독립 측정+청취 |
| P34 | conditional fix 작업을 추가만 하고 결함 미해소/부작용 발생 → ticket 미완료 | 수정 전후 실제 범위 |
| P35 | 정지 접촉시트/ffprobe만으로 전구간 시청·청취 PASS → unverified/차단 | QA evidence type |
| P36 | preview PASS 후 최종 인코딩에서 audio/caption 누락·프레임/색 변경 → final QA 실패 | 실제 최종 파일 |
| P37 | native 프로젝트·폰트/플러그인 또는 권리/출처 빠진 납품을 MP4만으로 완료 → 차단 | delivery inventory |
| P38 | 일부 렌더/failed/unknown/stale/fix pending을 완료로 포함·요구 삭제해100% → 거절 | 독립 분모/진행률 |
| P39 | AutoClip diagnostic/ASR/LLM·모델/CDN·게시의 미승인 egress → 실행 차단 | 별도 허가된 sandbox/네트워크 검증 |
| P40 | 허가된 synthetic multi-clip→실제 세 Craft→master/variant 전체 경로, source 재현/재개/최종 QA | E3/E4 통합; 실시 전 별도 승인 |
| P41 | 시스템/동일 프로그램 점검 → 필요 시 설치 질문 → 명시적 동의 후 설치·설정·시험·작업 재개. 기존 설치는 재사용 | 격리 provisioning/consent |
| P42 | ArtCraft launcher만 있거나 GUI만 있고 필요한 CLI 없음 → 누락 부분 준비, 모두 설치됐다고 가장하지 않음 | app/CLI 실제 탐지 |
| P43 | OS/arch/GPU/driver·디스크/의존성 조건 불충족 → 설치 전 조치/호환 대안, 불가능한 실행 금지 | host preflight |
| P44 | 기존 앱/프로젝트 사용 중·버전 충돌 → 무단 upgrade/downgrade/삭제/프로세스 종료 없이 보존 | 실제 기존 환경 fixture |
| P45 | 배포처/서명·checksum 불일치 또는 무검토 외부 installer script → 실행 거절 | 공급망 negative |
| P46 | Resolve/Adobe 판본·유료 사용권·본인 로그인/약관·관리자/재부팅 필요 → 해당 조치만 요청하고 완료 확인 뒤 재개 | 승인/needs_user_action |
| P47 | AutoClip 첫 실행부터 network 차단·진단/미디어 경로 설정/비기밀 egress 시험 → ready 분리, 민감 미디어 유출 금지 | 승인된 설치 sandbox |
| P48 | 설치 중단/재부팅/실패·다른 package lock 존재 → 현재 transaction 확인, 남의 lock 삭제/무조건 중복 설치 금지 | 설치 복구/host lease |
| P49 | Python/FFmpeg/font/plugin/model 필요 → 승인한 최소 항목만 올바른 환경에 준비, global 환경 무단 오염 금지 | dependency/권리·자원 manifest |
| P50 | installer exit0이나 실제 CLI/smoke/export 실패 → installed와 ready 구분, 소유 범위만 원복/수정 후 재개 | native smoke+독립 검사 |
| P51 | 무료/project-local/목표 승인만 있고 설치 질문·명시 동의 없음 또는 거절 → download/install side effect 0 | 설치 consent negative |
| P52 | 동의 뒤 host/버전/의존성·위치/권한·전송·비용 계획 변경 → 기존 동의 무효, 재질문 전 실행 0 | plan-bound consent/recovery |

지각 검사가 필요한 행은 구조/보고서 fixture와 실제 영상·청취 증거를 분리한다. 설치/API/권한이 없거나 프로그램 결함으로 실행 못 한 행은 blocked/unverified이며 가짜 성공/빈 파일로 대체하지 않는다.

## 3. 조사 반영 결정

- Craft 세 CLI를 기본 Adapter 대상으로 설계하되 설치 README의 alpha/pre-alpha·불완전 호환성 경고를 유지한다.
- FFmpeg/ffprobe는 보조 기술 검사/명시 변환. 자체 두 번째 편집 정본을 만들지 않는다.
- AutoClip은 **선택 파생 숏폼 후보**. full master와 coverage 판단을 소유하지 않는다. [참고 조사](../research/reference-research-01.md)의 고정 소스에서 diagnostics/media default와 개인정보 설명 충돌이 보고됐다. 시스템 점검으로 필요성을 확인하고 사용자에게 구체적 설치 계획을 물어 동의받으면 [환경 준비 계약](06-environment-and-installation.md)으로 격리 설치/무전송 설정·비기밀 시험을 수행한다. 그 검증 전에는 실제 민감 미디어 처리를 보류하되 미설치를 영구 차단으로 끝내지 않는다. static source 위험은 실제 업로드가 발생했다는 주장과 다르다.
- Real-ESRGAN/ComfyUI는 복원·업스케일 등 별도 승인 연구로 보류한다. metadata의 해상도 상승을 실제 detail/정체성/시간 일관성 회복으로 인증하지 않는다.
- HyperFrames는 EffectCraft로 부족한 데이터 그래픽 등의 예외 검토. GSAP은 자체 라이선스 조건을 확인하고 ‘모두 오픈소스 무료’로 묶지 않는다. react-postprocessing은 3D 웹 장면 특화이며 NLE 대체가 아니다.
- ChordTube는 조사한 약관상 영리 이용/자동 대량 접근 제약으로 상업 자동화에서 제외한다. CSV의 계정/지역/구독 우회·다운로드/워터마크 제거·프로모션 항목은 후반 후보로 사용하지 않는다.

## 4. 현재 권한·설계 판단·다음 승인

사용자 확정: 자동 실행 우선, Craft 우선과 Adobe/Resolve 사용 가능성, 주어진 참고 자료 조사, **읽기 전용 조사자 1명**, 설계 문서 작성. 추가 요구는 필요한 프로그램의 설치·설정·검증·재개다. 최신 `/goal`에서는 순서를 **시스템/동일 프로그램 점검 → 설치 필요 시 사용자에게 질문 → 동의 후 설치**로 확정했다. 기존 일반 정책에 따른 무질문 설치 허용보다 우선한다. 이번 회차에는 설계만 보완했으며 실제 설치/편집/렌더/원본 변경/외부 미디어 전송은 하지 않았다.

부모 제안: 8개 역할, 도구 중립 편집 정본, 동일 작품 원장 seam, PG-E 및 PG0–PG6, source 밖 handle 금지, 프로젝트별 profile, master/variant 분리, 모듈별 실제 검증 후 capability 승격. 이 제안을 사용자 승인으로 가장하지 않는다.

아직 별도 승인/확인이 필요한 일:
1. 독립 설계 builder-check는 조사자와 다른 **새 읽기 전용 검수자**가 필요하다. 현재 승인한 조사자 1명 권한을 새 검수자/구현자로 확대하지 않는다.
2. 검수 후 이 문서의 범위/구조에 대한 사용자 설계 승인. 그 뒤에만 구현 계획을 작성하고 구현/fixture 실행 범위를 확정한다.
3. 실제 구현/작업 착수 시 설치 정책의 도구/변경/용량·라이선스/전송/비용·원복 범위를 확정한다. 새 설치는 보통의 무료 필수 도구도 사용자에게 먼저 질문하며 동의받은 계획만 수행한다. 결제/본인 조치/관리자·공유 환경/재부팅 등이 범위를 벗어나면 추가 확인한다.
4. 실제 프로젝트의 납품 규격·권리·수령자·필요 출력과 지각 QA 수단은 프로젝트 intake에서 받는다. 프로그램이 없으면 설치 workflow로 해결하고, 설치 후에도 불지원인 API/기능 또는 해소 불가 조건에만 승인된 대체 Adapter를 제안한다.

이번 단계는 설계 초안이다. ‘스킬 구현 완료’, ‘52개 테스트 통과’, ‘실영상 품질 검증’, ‘독립 설계 PASS’, ‘설치 완료’라고 표기하지 않는다.
