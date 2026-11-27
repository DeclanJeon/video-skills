# 부모 설계 QA — 문서 경로 추적

범위: 2026-11-26 고정 초안(7개 설계+README+연구2개). 실제 설치/편집/렌더/50개 수락 테스트를 실행한 것이 아니다. 아래 PASS는 해당 시나리오의 설계 경로가 문서에 존재하고 서로 연결됨을 뜻한다. 누락/모순/구현 결정을 놓친 점은 별도 fresh gate reviewer가 반증한다.

| ID | 시나리오/기대 | 직접 대조한 설계 | 문서 추적 판정 |
|---|---|---|---|
| Q07 | 필요한 앱 없는 정상 작업: 탐지만 하고 끝내지 않고 설치·검증 뒤 이어갈 것 | 00 흐름/총괄 → 06 §1–3 ensure_environment → §6 ready와 원래 work order 재개; 04 PG-E; P41/P42 | PASS, 문서 경로만 |
| Q08 | AutoClip 첫 실행: 기본 진단 전송 위험이 실제 미디어 실행으로 이어지지 않을 것 | 06 §5 최초 실행 전 deny/dummy → 설정/비기밀 egress → real-media-ready; 05 P39/P47; 연구 고정 소스와 부모 확인 | PASS, 보안 설계만/실제 차단 미시험 |
| Q09 | 유료/본인 로그인·관리자·재부팅/비지원 OS: 한정된 승인/조치로 복귀할 것 | 06 §3 도구별 판본/OS, §4 해당 사용자 조치, §6 상태·원복/재개; 05 P43–P46/P48/P50 | PASS, 정책 경로만 |
| Q10 | 이미 소비한 optional이 invalid·조건부 import 충돌·stale: 과거 binding을 지우지 않을 것 | 01 §4 actual consumed current AND usable+핀; 04 §2/4; 05 P23–P26, 미소비 optional positive 구별 | PASS, 불변식 명시/구현 미시험 |
| Q11 | 실제 Handoff만으로는 세부 요구 부족·handle0·mixed audio: 없는 것을 만들지 않을 것 | 01 §1 보완 snapshot/coverage 필수·take/range·stem; §3 event anchor/overlap; 02 §3 WAV+offset/교환 손실; P01/P04/P05/P08/P16 | PASS, 기존 생산 모델과 대조 |
| Q12 | 렌더 끝났으나 부분/오프라인/최종 audio 누락·QA 없음: 전체 납품 완료로 세지 않을 것 | 02 §4/5 placeholder·unknown; 04 PG4–PG6+§3–6 실제 파일/시청청취/독립 분모; P14/P18/P20/P35–P38 | PASS, 게이트 명시/실제 출력 미시험 |

인접 회귀 대조: 설치 기능 추가 후에도 (1) 현재 회차가 실제 설치 권한이 아니라는 표기, (2) 필요 도구만 설치, (3) 기존 사용자 앱/공유 환경 보존, (4) source·프로덕션 namespace 보존, (5) raw 템플릿 미복사/권리·폰트, (6) 독립 검수/사용자 설계 승인 전 구현 금지 규칙이 유지된다.

기계적 Q01–Q06 결과는 `manual-qa-01.json`에 기록한다. 이 문서는 독립 PASS나 실제 후반 품질 인증이 아니다.
