---
name: caption-editor
description: Use when approved literal dialogue, speaker labels or supplied word timings need mapped or rendered captions.
disable-model-invocation: true
---

# 자막 편집

## 입력
승인 literal text/speaker/kind·실제 word evidence, 현재 edit map, 정확한 기존 font/style/license와 safe/protected mask. [공통 실행 계약](../references/execution-contract.md)을 먼저 읽는다. 분야 변경안은 총괄의 정본 commit으로 반영한다.

## 절차
1. 시스템·동일 프로그램/필수 dependency를 먼저 점검해 적합한 설치를 재사용한다. 새 설정·폰트·프로그램은 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후 설치한다. 동의 전 download/installer를 실행하지 않는다.
2. 물리 source approval pin과 원문/화자/translation/editorial 구분을 대조한다. ASR·약칭·번역은 새 원문 승인이 아니다.
3. 정본 source→master interval을 매핑한다. cut-crossing/repeated-source 모호함과 retime stale을 막는다. 단어 강조는 실제 공급된 character/word timestamp만 사용한다.
4. 정확한 font 파일/face/style/version/charset를 재사용하고 advance/줄수/읽기 정책을 확인한다. 누락 font fallback은 같은 디자인이 아니다.
5. 실제 native sourceText readback과 각 RGBA frame alpha/bounds를 검사한다. 최종 가시성·오탈자·화자·스포일러·중복 자막을 QA로 보내고 burned/clean variant를 분리한다.

## 반환
원문/화자/승인 pin, 현재 timeline digest·실제 cue/word map, font/glyph/bounds 결과와 native/sidecar/variant 증거, unverified 검수.
