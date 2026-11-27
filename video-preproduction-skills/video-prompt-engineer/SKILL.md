---
name: video-prompt-engineer
description: "Crew skill; production-director assigns at P6, or user asks to turn a storyboard into timeline AI video prompts: 8-block prompts, generation grouping, sidecars. Also learns patterns from reference prompts."
disable-model-invocation: true
---
# video-prompt-engineer

## 역할

시트에서 생성 배치와 프롬프트.

## 입력

검수된 인덱스·시트·SCR·모델 증거.

## 절차

[영상 명세](../docs/design/07-video-prompt-spec.md)의 8블록으로 컷과 비트를 기술한다. 각 대사는 현재 SCR 원문을 인용하고 화자·위치·전달을 분리한다. GEN 로컬 시간과 전역 오프셋을 분리하고 경계에서 컷·대사 유실을 막는다. 공통 해시를 원장에 핀하고 `prompt_batch_check.py`로 전체 배정을 대조한다.

액션 구간의 B5는 [액션 연출 계약](../docs/design/12-action-direction-contract.md) §7 블록 형식(블록당 카메라 1개·사건 동사 1–2개·결과 상태)으로 압축하고, 길게 쓰는 것은 불변 규칙에 한정한다.

## 산출물

양식: [VPR](assets/VPR-template.md) · [사이드카](assets/VPR-map-template.json) · [배치](assets/batch-template.json).

GEN 계획, VPR 텍스트, map, batch와 미확인 목록. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

승인·공급자 실행·원본 변경은 감독과 담당 부서가 맡는다.

## 자체 점검

모델 확인 없이 적합 판정을 내리지 않는다. 레퍼런스의 구조·샷 문법을 따르고, 원본 그대로 요청은 DES-13 대응표에 승인된 치환과 실제 재현 차이를 기록한다.

### 실행 안전

현재 컷에 필요한 참조와 오디오 경로만 고정한다. 모델 적합성이 불확실하고 실패 범위가 큰 항목만 제작 인계에 시험 대상으로 남긴다. [실행 안전 계약](../docs/design/13-execution-safety-contract.md)의 해당 게이트를 적용한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
