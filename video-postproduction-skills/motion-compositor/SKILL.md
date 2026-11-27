---
name: motion-compositor
description: Use when an approved postproduction work order needs native composition, alpha plates or literal text layers.
disable-model-invocation: true
---

# 모션·합성

## 입력
현재 timeline/보호 mask, 승인 composite 범위, source/recipe와 필요한 literal caption/font/권리 핀. [공통 실행 계약](../references/execution-contract.md)을 먼저 읽는다. 분야 변경안은 총괄의 정본 commit으로 반영한다.

## 절차
1. 시스템·동일 프로그램/필수 dependency를 먼저 점검해 적합한 설치를 재사용한다. 새 설정·폰트·프로그램은 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후 설치한다. 동의 전 download/installer를 실행하지 않는다.
2. 실제 native comp/layer/property 목록을 확인하고 현재 `post-motion/1` 또는 `post-text/1`을 준비한다. MOGRT/prgraphic/JSX는 실행·호환 권한이 아니다.
3. 정본 work context와 실제 picture provenance를 구별한다. geometry/fps/alpha/color assignment와 개념 참조/실제 pixels 사용을 명시한다.
4. EffectCraft actual IDs/linear keys/sourceText·system font를 readback하고 모든 RGBA frame/bounds/straight RGB를 독립 검사한다. 작은 glyph AA coverage와 완전 opaque solid 약속을 구별한다.
5. 결합 파일에서 required event·얼굴/행동/UI 가림과 identity를 QA로 보낸다. 새 외부 모델/정체성 변경은 별도 소유자에게 반환한다.

## 반환
실제 native 프로젝트·frame inventory/hash/alpha/timing/bounds, context/source 구분, 실제 font/text와 변경 영향·current QA 필요 상태.
