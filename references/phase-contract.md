# 단계·인계 계약

## 정본과 소유권

이 문서 경로는 video-skills 루트 기준이다.
- 프리: video-preproduction-skills/production-director/SKILL.md.
- 프로: video-production-skills/production-supervisor/SKILL.md와 video-production-skills/docs/operations.md.
- 기존 장비 정본: 이 루트의 형제 ../contents-production-skills/. 각 하위 패키지 README의 옛 ../contents-production-skills는 이관 전 경로다.
- public entry와 프리/프로/포스트 패키지 디렉터리를 공용·agent 경로에서 동일 정본으로 참조한다. 부서의 자동 호출 금지 플래그는 보존하며 배정된 파일을 명시적으로 읽는다. 포스트의 실제 진입점은 video-postproduction-skills/SKILL.md이며 실행·지원·수령·QA는 해당 패키지의 현재 계약으로 검증한다. 등록이나 파일 존재를 실제 작품 실행·납품 검증 완료로 재해석하지 않는다.

요청한 범위만 수행한다. 프롬프트만이면 실제 이미지/음성/영상 생성 없음. 이미지 포함이면 감독의 P5/QA3 실제 산출물 계약을 수행한다. 종합 인계는 영상 프롬프트와 QA4를 포함한 영상 생성 전 설계까지 감독 소유다. QA4 이후 실제 영상 생성과 테이크 검수는 총괄 소유이며 legacy P7은 포스트 대체물이 아니다.

### QA4 전 separate 오디오 선행 작업

video-preproduction-skills/docs/design/07-video-prompt-spec.md §9의 audio_path를 유지한다. native로 임의 전환하지 않는다. separate이면 오케스트레이터가 다음 한정 작업의 책임자다: sound-designer의 실제 APR → 필요한 음성/음악/SFX 실행자에 승인된 콜시트 배정 → 실제 파일·발화 실측·청취 근거 수령 → assistant-director에게 실측 시간 보정 배정 → 인덱스/의존 핀 갱신과 timeline 재검사 → video-prompt-engineer의 VPR → QA4. 실제 도구·전송·비용 승인이 없으면 해당 선행 작업에서 차단한다.

이 음성 생성은 프리 설계에 필요한 prerequisite이며 전체 영상 배치 init/G0/QA4 통과를 꾸미지 않는다. 실제 출력·job/attempt·승인·실측 근거는 기존 작품 이력/프리 원장에 기록하고 이후 프로 projection에 자산·핀·음성 coverage로 인계한다. 감독은 프리 설계 소유권을 유지하고 장비 결과가 돌아온 뒤 보정된 설계부터 재개한다. 별도 포스트 구현이나 legacy P7을 호출하지 않는다. 텍스트 전용 요청에서는 추정/미실측임을 표시하고 실제 음성을 생성하지 않는다.

## 프리 사운드 소스 확보 → 인계

실제 스톡 사운드가 필요한 요청은 video-preproduction-skills/sound-designer/SKILL.md와 해당 references/stock-audio-sourcing.md에 따라 CSV의 관련 사이트를 실제 순회·검색하고 후보 청취·개별 권리 확인·필요 파일 확보까지 프리에서 수행한다. 사이트 목록을 소스 납품으로 대체하지 않는다. 설계 완료와 소스 확보 완료를 구분하고 미확인 권리/청취/필수 파일은 partial/blocked로 남긴다. 확보된 AMB/SFX/MUS는 [프리 사운드 통합 정본](../video-preproduction-skills/docs/design/11-sound-sourcing-integration.md)의 단계/등록 계약에 따라 파일·해시·기술 정보, 큐별 사용 구간/용도, 검색·소스 원장, 권리 증빙·크레딧·수령자 전달 조건을 함께 핀한다. generation_input만 해당 생성 요청의 실제 입력이며 post_only를 일괄 업로드하지 않는다. 감독이 기존 writer 계약에 맞춰 등록하고 아래 projection의 audio_cues/asset closure와 포스트 인계에 보존한다. 포스트 패키지 구현은 이 변경의 대상이 아니다.

## 프리 → 프로: agent-authored projection

프로덕션은 artifact ledger/CSV를 직접 받는 범용 변환기가 아니다. 다음 절차로 **실제 작품 입력에서** 지원되는 Project JSON을 작성한다. 추출이 불명확하면 원본을 확인/교정하고 미매핑을 G0 blocker로 남긴다. 예제 fixture를 작품 데이터로 복사하지 않는다.

1. 프리 패키지의 production-ledger/SKILL.md와 scripts/index_lint.py --help, scripts/timeline_check.py --help를 읽는다. 원래 프로젝트 ledger.json, 04_board/index-header.json, index.csv, 정본 각본·아티팩트·QA 보고에서 현재 버전/상태를 검사한다. 프로젝트 단계에 맞는 index_lint와 timeline 및 QA4 검사를 실행해 실제 결과를 보존한다. 성공 판정/승인은 파일 존재로 만들지 않는다.
2. 프로 패키지 video-production-skills/production/upstream.py의 Project/Shot/Panel/Asset/Artifact/Character/CoverageEnvelope 모델과 video-production-skills/production/models.py를 읽는다. 각 CSV cut을 동일 ID의 shots[].id로 옮긴다. 각 패널은 실제 보드 ID, shot_id, beat_ids를 보존한다. segments의 로컬 b1은 컷별 소속을 유지하며 전역 ID를 새로 발명하지 않는다. 단일 컷 dialogue의 각 ID는 speech[].id로, 실제 사운드 cue는 audio_cue_ids로 옮긴다. 자막/cue의 시간·소속도 포함한다. 구조가 다르면 열 이름을 추측하지 말고 header/인덱스 계약에서 확인한다.
   **L/J-cut 중복 대사:** 같은 canonical dialogue ID가 여러 컷에 나타나면 Project의 speech:<id> 전역 중복 제약으로 직접 derive하지 않는다. 대신 지원되는 CoverageEnvelope 원본을 작성한다. 일반 shot/panel/beat/cue 의무와 전체 asset_uses closure는 모두 유지하고, 대사만 각 교차 컷별 고유 requirement 키 speech:<cut>:<dialogue>로 표현한다. 이는 coverage 키의 스코프이지 원본 대사 ID 변경이 아니다. 각 Requirement.shot/panels는 해당 컷, locator는 원본 CSV 행·대사 ID·L/J-cut 및 정확한 시간 구간을 가리킨다. canonical D001·교차 컷·실측 오디오/구간은 source_map 사이드카에도 보존하고 모든 교차 구간을 원본 timeline과 대조한다. 한 컷의 발화를 지워 중복을 숨기지 않는다. 이 envelope 원본도 불변으로 핀하고 export_coverage를 거쳐 origin 대조를 유지한다. 실제 mapping/closure 대조가 미완이면 G0 차단이다.
3. 컷/패널/대사/비트/cue마다 원본 상대 경로, 행 또는 anchor, artifact ID@vN와 해시를 projection의 source_map 메타데이터에 기록한다. 원본 CSV·header·각본·원장 스냅샷의 해시도 기록한다. 요구사항 분모를 clip 목록에서 역산하지 않는다. 미매핑/누락/중복을 원본과 대조해 해소한다.
4. mandatory 자산 closure를 완전히 포함한다: 컷 자산, 인물 identity와 SSOT, panel 이미지/시트/asset_version_refs, active LOOK, voice/spatial, cue/caption, artifact dependencies/asset_ids/required_asset_versions, source/master lineage. 실제 current 등록에서 id/version/path/sha256를 읽고 파일 바이트를 검증한다. legacy 원장의 consumes는 artifact dependencies로 유지한다. 누락된 identity 등의 새 역할 매핑은 실제 문서를 확인해야 하며 임의로 empty 처리하지 않는다. Asset status는 미디어 확인 근거에 따라 available/verified이며 legacy current를 검수 증거 없이 verified로 승격하지 않는다.
5. 원본과 대조·검수한 Project 또는 CoverageEnvelope projection을 작품 루트 내부의 새 불변 파일(예: production-input-v1.json)로 저장한다. 원본 ID·version·path·sha256는 보존한다. provenance/source_map은 별도 불변 사이드카로 저장하고 그 해시도 인계한다(CoverageEnvelope는 extra=forbid). Project의 extra=ignore로 무시되는 메타데이터 역시 별도 대조한다. source_map은 자동으로 검증되는 권리/창작 승인 증거가 아니다.
6. 프로 패키지의 실제 derive_coverage/derive_asset_uses로 projection을 읽고 export_coverage로 coverage envelope를 내보낸다. CLI를 쓸 때는 먼저 python3 scripts/production.py --help 및 coverage --help를 확인한다. origin.path는 작품 루트 기준 실제 상대 경로여야 한다(export가 basename만 쓸 수 있으므로 origin을 정확히 확인한다). origin과 envelope는 mutable ledger와 별개이며 둘 다 핀을 유지한다.
7. 모든 coverage와 mandatory 자산 핀을 clip.requirements와 assets/dependencies에 빠짐없이 결속한다. dependencies는 로컬 계보이고 외부 전송 승인이 아니다. 총괄의 실제 validate/ready와 기존 verify_scope를 적용한다. G0 통과 전 실제 reserve/submit로 넘어가지 않는다.

이 절차는 에이전트가 수행하는 변환·대조 계약이다. 일반 CSV 자동 변환기, QA4 통과 인증기 또는 공급자 연결 구현을 제공한다고 주장하지 않는다. qa/boundary-check.py는 합성 pre ledger/board → production projection 계약만 실행한다.

## 원장 writer 격리와 재작업

최초 초기화부터 프리 writer는 ledger.json만, 프로 ProjectStore는 별도의 production-ledger.json만 사용한다. 기존 작품 상태의 파일 링크로 둘을 연결한다. 한 writer만 활성화하고 이력 도구는 별도 .history를 사용한다. immutable coverage origin을 mutable 상태 파일과 같은 경로로 쓰지 않는다.

기존 ledger.json에 production namespace가 있으면 **cp2.Ledger.register/mark-stale 등 쓰기를 차단**한다. 단순 순차 실행으로는 namespace 손실을 막을 수 없다. 현재 파일과 원격 ID를 보존하고 status/read_recorded만 수행한 뒤 명시적 preservation migration을 마련할 때까지 프리 수정은 차단한다.

분리된 원장에서 프리 수정이 있으면 현재 projection/coverage와 영향받는 downstream을 invalid 상태로 기록한다. 실제 scope 변경 승인과 revise-scope/invalidate/revalidate 절차로 새 핀을 적용한다. 새 init으로 기존 원격 이력이나 unknown 예약을 지우지 않는다.

## 장비 keep / retire

| 구분 | 대상 | 정책 |
|---|---|---|
| public coordinator | video-skills | 공용 및 기존 agent roots에서 동일 canonical SKILL.md |
| source-only equipment | higgsfield-*, blender-previsualization, open-3d-production, suno-music | 구형 스킬 활성 등록은 전부 해제. 필요할 때 canonical legacy root의 <name>/SKILL.md를 명시적으로 읽고 현재 도구·승인으로 실행. 콜시트에 coordinator=video-skills, phase owner, no callback 전달 |
| source-only history | recording-production-history | 활성 등록 해제. 필요할 때 canonical legacy root의 recording-production-history/SKILL.md를 읽고 .history 도구 사용. 기존 설치본 별칭 대신 원본 경로 사용 |
| resource-only | video-production-assets/scripts | historical registration은 SKILL.md 없는 호환 디렉터리로 교체해 기존 auditor import 유지. 공급자는 canonical legacy root에서 관련 참조를 읽음 |
| retire planner/router | creative-production 및 나머지 legacy 기획·카메라 설계·스토리·보드·animatic 라우팅 | 활성 symlink와 Pi 양의 explicit 항목만 제거. 원본 전체는 보존 |

standalone image/web provider는 이번 영상 라우팅의 대상이 아니다. 영상 장비의 옛 creative-production callback은 현재 콜시트에서 superseded이며, 실제 지원 schema·선택 ref·승인은 계속 필수다.

## 프로 → 포스트

video-production-skills/docs/operations.md와 video-production-skills/production/handoff.py의 G5를 그대로 적용한다. 수령자·권리 근거·현재 selection/구간·접합·전체 흐름 재생이 없으면 sources_ready일 수 있어도 handoff 완료는 아니다. 실제 승인된 편집 수령자의 근거로 G5를 진행하고, 포스트 총괄은 별도 IntakeRequest로 현재 입력을 수령·검증한다. 슬롯 이름이나 오케스트레이터 자신을 가짜 post receiver로 입력하지 않는다. 요청 범위에 후반/최종 영상이 있으면 [포스트 연결 계약](postproduction-slot.md)에 따라 실제 entry → intake/validate → 편집·현재 QA·로컬 납품으로 진행한다. 필수 입력·승인·지원·검수가 부족하면 정확한 단계 차단과 재개점을 남기고 final 목표를 유지한다.
