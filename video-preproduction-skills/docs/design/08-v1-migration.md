# 08 — v1 → v2 이관 지도

- 문서 ID: `DES-08` · 상태: `draft-r1`
- 원칙: v2는 새로 설계하되, v1에서 **검증된 안전 장치와 지식은 가져오고**, 조직 구조와 라우팅은 버린다. v1 원본은 수정하지 않는다(병행 설치, D7).

## 1. 스킬 매핑

| v1 스킬 | v2 처리 | v2 대상 | 가져올 것 |
|---|---|---|---|
| `creative-production` | **대체** | `production-director` | 승인 분리·단일 기록자·닫는 줄(policy.md), 공급자 전송 잠금(explicit-video-execution), storyboard-timing-to-prompt 원칙 |
| `concept-intake-design` | **흡수** | `concept-benchmark` | 9개 판단 요소, `inferred` 기록 규칙, 한 번에 묻기 |
| `topic-demand-selection` | **흡수** | `concept-benchmark` (수요 근거), `audience-reaction-qa` (레인 C) | 비교 정규화, 증거 라벨, 사실 게이트 분리 |
| `searching-social-media` | **장비** | concept-benchmark가 호출 | 그대로 |
| `developing-video-synopses` | **흡수** | `story-writer` | synopsis-craft |
| `orchestrating-video-preproduction` | **폐기** | (감독 단계표로 대체) | stage-execution의 스파인 개념 → ledger |
| `designing-video-character-sheets` | **흡수** | `character-designer` | character-craft, 7뷰 |
| `designing-character-personas` | **흡수** | `character-designer` | MBTI/에니어그램 렌즈, 음성 정체성 |
| `storyboarding-video` | **분할** | `storyboard-artist` (+ 콘티는 회의로) | storyboard-contract 슬롯, split_storyboard 스크립트 |
| `video-production-assets` (15 모듈) | **분할** | 각 부서 | 아래 §2 |
| `camera-spatial-design` | **흡수** | `cinematographer` | 수치 카메라 설계 |
| `ai-camera-control` | **흡수** | `video-prompt-engineer` (카메라 문장화), `cinematographer` (설계) | 시작/끝 프레임 제어 |
| `camera-motion-reference-analysis` | **장비** | concept-benchmark·cinematographer가 레퍼런스 분석 시 | 그대로 |
| `blender-previsualization`, `open-3d-production` | **장비** | cinematographer 요청 → 감독 실행 | 그대로 |
| `animatic-direction` | **흡수** | `film-editor` | 시간화·hold 규칙 |
| `silent-visual-storytelling` | **흡수** | `story-writer`(무성 모드), `performance-director` | 무대사 인과 설계 |
| `storytelling-with-still-images` | **보류** | 별도 모드(스틸 영상) 후속 설계 | — |
| `silent-satire-animatic`, `community-shorts-stills-pipeline` | **유지(외부)** | v2 범위 밖 특화 파이프라인 | — |
| `recording-production-history` | **흡수** | `production-ledger` | production_history.py |
| `higgsfield-*`, `suno-music` | **장비** | 감독이 실행 | 그대로 |

## 2. `video-production-assets` 모듈 분배

| v1 모듈 | v2 부서 |
|---|---|
| 01-brief, 13-ideation-brand, 19 브랜드 | concept-benchmark |
| 02-story, 03-screenplay, 16-concept-emotion-retention, 17-genre-comedy, 18-episodic-series, 30-marketing-story-craft, writing-craft, korean-script-postediting | story-writer |
| 04-performance, performance-and-style-recipes, 22-dialogue-lipsync(연기 부분) | performance-director |
| 05-visual, 20-visual-mode-ssot | lighting-director(LOOK) + production-designer |
| world-rules-and-information-recipes | world-designer |
| 06-shots, visual-scene-communication, directing-vocabulary-crosswalk | cinematographer |
| 07-lighting, lighting-language-catalog | lighting-director |
| 08-animation, 08a/08b 모션, 33 모션 스타일 | vfx-supervisor (모션그래픽 레인) |
| 09-edit, 09a 숏폼, edit-sound-language-catalog(편집) | film-editor |
| 09-edit(사운드), edit-sound-language-catalog(사운드), 22(음성), voice-mix-finishing | sound-designer |
| 10-evidence | story-writer (사실 주장) + production-qa |
| 11-ai-handoff, 11a-ai-video-prompting, video-prompt-dialects.json | video-prompt-engineer |
| 32-still-asset-generation-jobs, storyboard-media | image-prompt-engineer + 감독 실행 |
| 12-qa, 21-generated-video-qa-retry, 26-state-causality-continuity, 27-camera-motion-qa, preproduction-review | production-qa |
| 14-production-ops, 15-delivery, 23-finishing, 23a 자막 | film-editor (P7) + production-ledger |
| 24-production-execution, sequence-execution | production-director (실행) |
| 25/29/29a/31 레퍼런스 분석·재현 | concept-benchmark |

이관은 **복사가 아니라 재작성**이다. 각 부서 WO에서 v1 참조를 읽고 v2 산출물 필드에 필요한 지식만 `references/`로 옮긴다. 원 출처는 각 references 파일 머리에 `source: v1 <경로>@2.66`으로 남긴다.

## 3. 버리는 것

| v1 요소 | 버리는 이유 |
|---|---|
| 3축 슬롯 라우팅(`routing.csv` 33행 + 판별표 + craft-bridge) | 요청→오너 1명 구조. v2는 단계→편성 |
| `orchestrating-video-preproduction`의 텍스트 레인 | 감독 단계표와 중복 |
| Rofan 관찰 색인, Matt 원고 후보 등 실험 기록 | 제작 절차가 아닌 이력. v1에 보존 |
| 크래프트 트리거 목록(감독 본문 속 링크 나열) | 부서 소유로 이동 |

## 4. 전환 절차 (요약, 상세는 WO-14)

1. v2를 별도 이름으로 설치, v1과 병행.
2. 동일 브리프 3종(대사극·쇼츠 광고·무성 애니)을 v1/v2로 실행해 비교(WO-13).
3. v2가 기준을 넘으면 `DEVELOPMENT-WORKFLOWS.md`의 "Content production" 지시를 v2로 변경.
4. v1은 보관(읽기 전용), 장비 스킬은 계속 공유.
