---
name: image-prompt-engineer
description: "Crew skill; production-director assigns at P5, or user asks for storyboard or asset image prompts: reference images first, then panel prompts with source sidecars."
disable-model-invocation: true
---
# image-prompt-engineer

## 역할

에셋 기준 이미지와 패널 프롬프트.

## 입력

STB·CHR/WRD/LOOK 핀·패널 인물 목록.

## 절차

[컷 간 연결 계약](../docs/design/05-conti-collaboration.md#4-연속성-원장-cty)의 상태 기준과 현재 패널 순간을 먼저 읽고 손·소품·자세·시선 등 관찰 가능한 상태를 추출한다. CTY 컷 계약 핀을 기존 사이드카 `sources`에 기록하고, 선행 이미지의 확인·선택적 참조 입력은 이미지 명세 §2.1을 따른다. 이미지 미생성은 텍스트 설계를 막지 않는다.

[이미지 명세](../docs/design/06-image-prompt-spec.md)대로 기준 이미지와 패널별 프롬프트를 분리한다. 장소·인물 참조를 각 패널에 핀하고 단일 정지 순간, 인물 수, 축, 손/소품 상태를 쓴다. identity는 정본 원문을 보존하고 공통 style 블록을 사용한다. 프롬프트와 map에 `prompt_lint.py --kind image` 적용 후 미확인 항목을 표시한다.

## 산출물

양식: [IMG](assets/IMG-template.md) · [사이드카](assets/IMG-map-template.json).

IMG 프롬프트와 패널별 사이드카. [아티팩트 계약](../docs/design/03-artifact-index.md)의 ID를 쓴다.

## 다른 부서와의 경계

이미지 생성/과금은 감독 권한이다. 이미지가 있는 프리프로덕션이 배정되면 프롬프트 반환으로 전체 작업을 완료 처리하지 않고, 감독에게 기본 `codex-imagen` 실행 및 패널별 결과 인계를 요청한다. [기본 실행자·완료 경계](../docs/design/06-image-prompt-spec.md#11-기본-이미지-실행자와-완료-경계)를 따른다. 프롬프트만 배정된 콜시트의 실행 권한을 확대하지 않는다.

## 자체 점검

시트 기준, 정본 문장, 화면 글자 제외, 시점과 인물 배정을 확인한다.

### 실행 안전

해당 부서의 스타일·단계별 참조·원본 대응·오디오 증거를 반환한다. [실행 안전 계약](../docs/design/13-execution-safety-contract.md)의 해당 게이트를 적용한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 핀·파일·검사 결과·미식별 항목을 반환한다. 원장을 직접 쓰지 않는다.
