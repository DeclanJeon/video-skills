# 04 — 검수·조건 해소·최종 마스터·납품

## 1. 게이트와 책임

아래 PG는 production의 G0–G5를 대체하지 않는 post 게이트다. 모든 판정은 pass/fail/unverified/not_applicable와 범위·이유·현재 evidence를 가진다. 증거 종류는 문서/metadata, 실제 기술 검사, 보고된 시청·청취, 직접 관측을 구분한다.

| 게이트 | 통과 조건 / 결과 |
|---|---|
| PG-E 환경 준비 | 필요한 앱/실제 CLI·의존성·권리/환경 적합성 탐지. 없으면 설치·설정·격리 기능/보안 검증 후 재개. 미해결 조치가 있으면 구체적 상태로 보존. 실제 미디어 투입 전 통과. |
| PG0 수령 | 원본 Handoff+요구/인덱스 보완 입력, source/approval/권리·범위/실제 stream/timebase/색, 조건부 ticket·수령 범위. 미제공 stem/handle을 생성하지 않음. |
| PG1 편집 계획 | 승인 edit brief/변경 범위·정확한 clock/profile, 필수 사건/대사와 edit map, backend capability·권한·출력/비용. 새 서사/부족 범위·지원 불가를 사람에게 반환. |
| PG2 picture | 실제 assembly/fine cut에서 사건/연기/화자/반응·공개 순서·페이싱/연속성·J/L cut/retime/재구도 검수. 미변경 범위의 재사용 근거와 변경 범위의 새 검수 구분. |
| PG3 분야 | 합성·색·음향·자막의 실제 결과, 해시/recipe/폰트/clock, conditional fix 결과와 분야별 리뷰. 원본+각 patch/합친 결과의 부작용 대조. |
| PG4 결합 검수본 | 고정 timeline/분야 결과를 결합한 파일의 전체 재생·해당 청취. 의미·정체성·표정/가시성·대사/자막/음향·접합·룩·전체 흐름을 다시 확인. |
| PG5 최종 파일 | 승인 설정으로 실제 전체 렌더 종료, 파일/hash/전체 decode·길이·frame/sample/channel/색/audio·loudness 등 대조. PG4 후 재인코딩/수정됐으면 최종 파일에 필요한 새 검수. |
| PG6 채택/납품 | 최종 파일 전구간 시청·해당 청취, 현재 요구 전부/해소 ticket·권리·attribution·수령자/납품물 completeness. 최종 채택 승인과 현재 CAS. |

기술 decode나 정지 contact sheet는 PG4/PG6의 시간 흐름·청취 검사를 대체하지 않는다. 실제 검사 능력이 없으면 unverified이고 preview는 만들 수 있어도 정식 master release는 닫힌다. 사람이 제공한 선언도 ‘보고된 evidence’로 식별하고 code가 동의·시청 진위를 인증했다고 쓰지 않는다.

## 2. 조건부 source와 변경의 해소

production의 conditional verdict는 과거 사실로 보존한다. post는 `FixTicket(source/range/defect/required_fix/receiver/acceptance_policy)`를 받아 별도 `ResolutionRecord`로 닫는다. resolution에는 실제 적용 산출물/recipe, 수정 전·후 구간, 결함 해소와 부작용 검수, reviewer·현재 revision이 필요하다.

‘작업 예정’, native effect가 추가됨, 담당자 이름만 있음은 해소가 아니다. imports/필수 행동에 영향을 준 결함, 실행 불가능한 복구는 production 반환 또는 명시적 scope 변경으로 처리한다. 미해소 conditional/stale을 최종 master accepted로 올리지 않는다. 원래 조건부 source를 후속 변형/효과에 소비할 때도 현재 usable한 속성인지 확인한다.

scope/구간/순서/retime/합성/자막·번역/대사·믹스/색/재구도가 바뀌면 영향받은 event coverage·접합·분야/전체 증거를 invalidate한다. 미변경 독립 작업의 evidence는 relevant fingerprint가 동일하고 물리 핀이 유효한 경우만 유지한다. 전체 재검을 무조건 매번 요구하는 것과 관련 변경 검수를 건너뛰는 것을 모두 피한다.

## 3. 실제 파일 QA

- source/offline/relink: basename 비슷함이 아니라 hash/native resource ID/range/편집 readback으로 확인. 누락을 검정 프레임/placeholder로 메우지 않는다.
- 영상: 전체 frame decode, 실제 크기/SAR/DAR/fps/PTS/길이, 예상한 공백/hold와 예상 밖 black/freeze/duplication 구분, 색 range/transfer·잘림·alpha edge·오류/워터마크·기밀 노출 확인.
- 음향: 필요한 stream/채널/sample rate, 실제 길이/입출구/접합 sync, clipping·true peak·LUFS와 profile 허용치, 대사 가청성/중복·음악/SFX 관계. 의도된 무음/암전은 승인 구간과 대조한다.
- 자막/그래픽: 승인 원문/화자/번역·cue timing, 실제 font/glyph/line bounds, face/action/UI safe mask 가림, 중복 burn-in·오탈자·반전 누설, attribution.
- 최종 인코딩 변경으로 마지막에 오디오/자막이 빠지거나 duration이 바뀔 수 있다. 중간 preview PASS만으로 최종 master를 인증하지 않는다.

profile은 프로젝트가 정한 수치/허용치를 가진다. 모르는 규격을 임의 숫자로 채워 ‘표준 PASS’로 만들지 않는다. 기술/지각/권리·동의의 서로 다른 판정 범위를 보존한다.

## 4. 채택은 작업 성공과 별도 원자적 commit

실행 사실은 원래 job/명령 snapshot에 남긴다. 채택 직전에는 현재 요구/편집 fingerprint, 실제 소비한 source·승인/권리·recipe/font/LUT/plugin/backend/output 파일, PG 증거를 동일 writer/CAS에서 다시 대조한다. 틀리면 역사적 succeeded/rendered를 유지하되 current/master/납품을 열지 않는다.

특히 GUI export 성공·파일 존재·렌더 queue 완료·native inspect의 명령 개수는 최종 품질 판정이 아니다. 이미 관측한 job 사실을 준비 파일 검증 오류로 지우지 않고, 반대로 역사적 완료를 현재 유효성으로 쓰지 않는다.

## 5. 납품 구성

승인된 `DeliveryProfile`은 필수 납품물과 각각의 형식/길이/대상/수령 조건을 명시한다.

- 최종 master 및 지정 variant(가로/세로·clean/burned caption·언어·해상도 등 실제 요구만).
- 실제 존재하는 mix/stems와 cue/offset/측정 기록. 없는 stem은 제공하지 못한 것으로 표시.
- 실제 편집 가능한 native 프로젝트/교환 프로젝트와 필요한 자산·폰트·플러그인 의존성, relink 지침·손실 목록. 재배포 불가 자산을 무단 bundle하지 않는다.
- 선택 범위/전체 edit map, 원본→변환→출력 hash/버전, 요구 충족표, QA/수정/승인, 권리/표기/수령자·주의사항.
- checksum manifest와 실제 파일 inventory. credentials·쿠키·signed URL·불필요한 개인 절대경로를 제거하고 수령자 접근/원본 제공 권한을 확인한다.

master-only 계약과 editable-project 계약은 다르다. 편집 프로젝트에 필수 폰트/플러그인이 빠졌는데 영상만 재생된다고 전체 납품 PASS를 하지 않는다. 필수 납품물 변경은 새 승인이 필요하다. 이 패키지는 로컬 납품 패키지까지이며 외부 업로드·게시를 기본 제공/자동 실행하지 않는다.

## 6. 진행률

각 branch별 서로 다른 분모를 별도로 표시한다: 수령 필수 입력, 필수 사건/대사 보존, 승인된 편집 work order, 분야별 작업·검수, 조건부 fix 해소, 실제 렌더, 최종 전구간 QA, 필수 납품물. 작업 성공/렌더 프레임률을 품질 완료율과 합치지 않는다.

planned/failed/unknown/unverified/stale/미해소 conditional은 해당 완료 분자에서 제외한다. 실제로 미선택인 optional만 근거에 따라 제외하고, 실제 소비한 optional의 실패는 감추지 않는다. 필수 요구/납품을 줄이려면 원/새 revision과 delta 승인이 필요하다. 프로젝트 완료는 필요한 환경의 PG-E 및 PG0–PG6와 필수 coverage/fix/deliverables가 현재 모두 닫힌 경우다.
