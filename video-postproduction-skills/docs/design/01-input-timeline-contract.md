# 01 — 수령·편집 정본·시간·계보

## 1. 기존 Handoff가 실제로 제공하는 것

실제 생산 모델은 이웃 패키지의 [production/models.py](../../../video-production-skills/production/models.py)에 있는 `Handoff`, `Selection`, `Take`다.

- Handoff: batch/scope revision, selection hash, ordered selections, join reports, full-flow review, receiver, rights evidence, handles/policy.
- Take: source pin/hash, 정수 source frame range `[in,out)`, frame count/FPS/CFR·크기·audio 존재, attempt 또는 approved-reuse origin.
- Selection: 원본 take, 적용 approval, 판정/조건부 작업, reviewed fingerprint, acceptance revision.
- 현재 인계는 **검수된 외측 handle 0**이다. raw 파일의 여유분은 ‘사용 가능하다고 검수된 프레임’이 아니다.

Handoff 단독에는 원래 batch/coverage의 모든 요구 본문·LOOK·대사/화자·에셋 인덱스가 들어 있지 않는다. 따라서 후반 입력은 다음 `PostIntake` 제안으로 묶는다. 기존 모델을 몰래 확장하지 않는다.

| 입력 | 필수 대조 |
|---|---|
| 원본 Handoff + schema/version pin | 엄격한 parse, 현재 selection/scope hash, source/approval/검수 파일의 실제 hash |
| 승인 batch/state의 불변 snapshot + coverage envelope/origin | batch/scope/selection 연결, 전체 필수 요구/순서/접합과 조건부 정책. mutable 원장 자체를 불변 source hash로 삼지 않음. |
| upstream script/board/index/LOOK/음향 cue·문자/로고 요구 | 실제 제공되는 계약과 핀만 사용. 없는 항목은 추정하지 말고 누락/정책으로 기록. |
| 실제 source media·해당 승인/권리 evidence | 파일 존재/비symlink 경로 정책·hash, 실제 probe/full decode, range bounds, 채널/색/timebase |
| edit brief + EditAuthority + delivery profile | 편집 목적, 허용 변경/길이·형식, 수령자, 외부 전송/예산·최종 채택 범위 |

누락 입력은 조사/초안 작업과 분리하고 정식 수령/현재 채택은 차단한다. Handoff/G4 검수용 montage를 원본이나 최종 마스터로 대신 쓰지 않는다. 라이브러리의 인계 검증과 CLI의 기술 montage 검증 차이도 확인하고 후반 수령에서 필요한 기술 검사를 직접 수행한다.

## 2. 편집 정본: 승인 결정과 native 투영의 분리

제안하는 versioned `PostTimeline`은 기존 작품 원장의 **postproduction namespace**에 저장한다. 별도 경쟁 작품 registry를 만들지 않는다. native `.fcproj/.ecproj/.scraft`, interchange, 렌더 파일은 실행/교환 산출물이며 결정 원장의 대체가 아니다.

최소 제안 필드:

- project/branch/parent handoff digest, required coverage revision, timeline revision, target clock/profile.
- source registry: 기존 ID·bytes hash·source range/QA revision·권한/동일 source lineage. ID는 구조화하며 `:` 문자열 이어붙이기로 의미를 합치지 않음.
- picture/audio/graphic/caption tracks와 segments: stable ID, source ref/range, timeline interval, 실제 사용한 dependencies, retime/transform/link group/role.
- event/speech map: 필수 requirement ID → 정확한 source 관측 anchor → master/variant 구간·가시성/가청성 검수.
- 분야 work order/recipe/font/LUT/plugin/asset pins, 조건부 수정 ticket, 승인·현재 QA와 변경 이력.
- native project/result mapping: native item/clip/layer/track ID와 정본 ID 대조, 작업 전/후 fingerprint, 손실 보고.

편집 가능한 작업 파일도 납품 대상이면 필요한 미디어/폰트/플러그인과 복구 설명을 함께 요구한다. 파일 하나가 열리는 것과 전체 재현 가능한 프로젝트는 다르다.

## 3. 시간과 coverage

source 범위는 끝을 포함하지 않는 frame 범위다. 실제 ffprobe/native probe의 rational FPS/timebase를 확인하고 upstream float FPS만으로 23.976과 24000/1001을 임의 동일시하지 않는다. timeline은 정수 tick + 명시 rate/정수 sample 위치를 사용한다. FilmCraft CLI의 확인된 clock은 초당 254016000000 ticks이며 다른 실행자의 frame/second/sample 단위는 Adapter에서 명시 변환한다.

- source→timeline edit map을 저장한다. 속도/정지/역재생/오디오 stretch/리샘플은 변환과 허용치가 승인된 경우만 수행한다.
- mixed FPS/VFR/드롭프레임·시작 timecode는 식별한다. 구현 초기에는 검증된 conform/PTS map 없는 조합을 차단하고 지원을 가장하지 않는다.
- 오디오 sample·picture frame의 반올림 정책을 저장하고 전체 길이/누적 A/V 오차를 측정한다. SRT 밀리초는 출력 표현이며 편집 정본 clock이 아니다.
- 원래 source range의 일부만 남았다는 사실로 ‘필수 사건이 보존됐다’고 추론하지 않는다. production의 fulfilled 목록은 보통 세부 event anchor를 대신하지 못한다. anchor가 없으면 전구간 유지가 기본이고, 축약은 anchor 관측/승인 후 진행한다.
- overlay가 중요한 소품/표정/접촉을 가리거나 음악이 대사를 묻으면 range가 남아 있어도 coverage 실패다.

외측 handle=0이면 외부 프레임을 당겨 쓰는 transition을 생성하지 않는다. **인증된 구간 내부 overlap**은 별개다. 사건/대사 보존, 전체 길이 변경과 접합을 승인·재검수한 경우에만 허용한다. 불가능하면 hard cut이나 production 재요청을 제안한다. 임의 freeze/interpolation은 대체 수단이 아니다.

## 4. 상태·수정과 원장 seam

- 기존 production writer의 실제 공통 잠금/atomic publish/CAS와 **동일한 잠금 seam**을 사용한다. 독자적인 다른 lock으로 같은 JSON 파일을 동시에 갱신하지 않는다.
- 새 post writer는 production과 다른 소유자의 root fields를 보존한다. namespace별 revision/원문 bytes conflict check를 적용하고 legacy `_save`와 동시 writer는 지원하지 않는다. 구현에서 seam의 실제 재사용/안전한 확장을 증명해야 하며 현재 구현됐다는 뜻은 아니다.
- source snapshot은 mutable 원장과 분리한다. 판단 fingerprint는 실제 소비한 선택·범위·approval·요구/recipe·font·backend 등에 결속하며 무관한 remote polling 때문에 원장 파일 전체 hash로 모든 편집을 무효화하지 않는다.
- 물리적 file/approval drift, consumed source의 invalid/conditional-import 충돌/stale 검수, 범위/순서/대사/retime/룩/음향/폰트·backend 변경은 영향받은 분야/접합/master QA를 재개방한다.
- optional이어도 **실제로 소비했다면** current AND usable과 파일·승인 핀 검사를 우회하지 않는다. 생략 근거와 실제 미선택이 함께 기록된 dependency만 생략한다. 이미 사용한 입력을 재검수 때 몰래 ‘안 쓴 것’으로 바꾸지 않는다.
- 요구 제외/의미 변경은 이전/새 scope와 정확한 delta의 승인으로만 한다. 버린 컷을 분모에서 지워 진행률을 올리지 않는다.
- native 프로젝트를 사람이 고쳤다면 diff/재수령을 pending으로 두고 지원되는 결정은 정본 변경안으로 가져온다. 표현 못 하는 native 효과는 정본 확장 또는 승인된 baked artifact+계보로 명시한다. 무손실 자동 round-trip을 주장하지 않는다.
