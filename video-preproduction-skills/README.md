# video-preproduction-skills — 영상 프리프로덕션 스킬 패키지

프로젝트명·로컬 저장소 디렉토리명은 `video-preproduction-skills`다. 과거 평가 기록의 `contents-production-skills-v2`는 이전 이름이며 해당 증거 원문은 보존한다. 개별 스킬 ID와 진입 스킬 `production-director`는 변경하지 않는다.

> 상태: **설계 단계 종료 · 미릴리스 · 설치 금지**. 사용자 지정 종료점은 프리프로덕션 및 영상 프롬프트 설계다. [설계 마감 기록](docs/work-orders/DESIGN-CLOSEOUT.md)에 완료 범위와 미검증 항목을 분리했다. 실제 생성·정식 비교·설치/전환은 완료가 아니며, [실행 큐](docs/work-orders/QUEUE.md)와 [변경 기록](CHANGELOG.md)을 보존한다.

영상을 종합 엔터테인먼트로 보고, **감독(오케스트레이터) 1명이 부서별 팀원(스킬) 19명을 지휘**하는 제작 파이프라인이다.

```
P0 접수·벤치마크 → P1 시놉·플롯·각본 초안 → [QA1 수요·반응] → P2 에셋 설계(세계관·캐릭터·의상·미술·사운드)
→ P3 콘티 회의(조연출·연기·촬영·조명·사운드·VFX·편집) → P4 스토리보드+인덱스 → [QA2 프리프로덕션]
→ P5 이미지 프롬프트·스토리보드 시트 → [QA3 시트] → P6 타임라인 영상 프롬프트 → [QA4 제출 전]
→ 생성 → [QA5 테이크] → P7 포스트 → [QA-F 최종]
```

## 문서 지도

| 문서 | 내용 |
|---|---|
| [00 개요](docs/design/00-overview.md) | 요구사항 추적표, v1 진단(허점 10개), 원칙, 결정 로그, 위험 |
| [01 파이프라인·게이트](docs/design/01-pipeline-and-gates.md) | 단계표, 게이트 판정, 콜시트/납품 패킷, 승인, 직행 표 |
| [02 크루 명부](docs/design/02-crew-roster.md) | 20개 스킬의 직함·책임·산출물·경계, RACI |
| [03 아티팩트·인덱스](docs/design/03-artifact-index.md) | ID 문법, 폴더, **스토리보드 인덱스 행**, stale, 게이트 체크리스트 |
| [04 QA1 수요·반응](docs/design/04-qa1-audience-reaction.md) | 모방→내재화 원장, 3레인 검수, 루브릭, 판정 |
| [05 콘티 회의](docs/design/05-conti-collaboration.md) | 부서 라운드, 충돌 판정, CNT 형식, 연속성 원장 |
| [06 이미지 프롬프트](docs/design/06-image-prompt-spec.md) | REF→패널, 블록 순서, 시트 조립, I-규칙 |
| [07 영상 프롬프트](docs/design/07-video-prompt-spec.md) | **8블록 템플릿**, 타임라인·말속도 규칙, GEN 묶음, L-규칙, 사이드카 |
| [08 v1 이관](docs/design/08-v1-migration.md) | v1 스킬·모듈 → v2 부서 매핑 |
| [09 레퍼런스 프롬프트 학습](docs/design/09-reference-prompt-learning.md) | **구조·패턴만** 학습: 배울 패턴 25개(PP), 보완 19개(SUP), 패턴 원장 절차, 내용 격리 규칙 |
| [11 사운드 소스 통합](docs/design/11-sound-sourcing-integration.md) | 단계별 설계/확보·사용 준비, 소스/권리/리뷰 등록, 큐 시간표·변경 영향, QA와 인계 |
| [내용 제거 골격](docs/examples/ref-prompt-01/masked-skeleton.md) | 레퍼런스 프롬프트에서 내용을 지우고 구조·패턴 ID만 남긴 것 |
| [합성 픽스처 EX-02](docs/examples/synthetic-laundromat-34s/fixture.md) | 예시·테스트·평가용 원작 장면(구조만 동형), 결함판/보정판 시간표 |
| [레퍼런스 분석(분석 전용)](docs/examples/ref-prompt-01/slot-map.md) | 원문 블록 분해·결함 분석. 내용은 이 폴더 밖으로 내보내지 않음 |
| [작업지시서](docs/work-orders/WO-00-index.md) | WO-01–WO-14 |
| [QA 보고](docs/qa/2026-11-25-design-qa.md) | 설계 QA 결과와 보완 기록 |

## 크루

| 부서 | 스킬 |
|---|---|
| 감독 | `production-director` |
| 개발 | `concept-benchmark`, `story-writer`, `audience-reaction-qa` |
| 에셋 설계 | `world-designer`, `character-designer`, `costume-designer`, `production-designer`, `sound-designer` |
| 콘티 | `assistant-director`, `performance-director`, `cinematographer`, `lighting-director`, `vfx-supervisor`, `film-editor`, `storyboard-artist` |
| 프롬프트 | `image-prompt-engineer`, `video-prompt-engineer` |
| 운영 | `production-qa`, `production-ledger` |

v1(`../contents-production-skills`, 2.66)은 수정하지 않으며, v1 공급자 스킬은 v2에서 "장비"로 재사용한다.
