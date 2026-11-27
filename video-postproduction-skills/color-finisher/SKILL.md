---
name: color-finisher
description: Use when source or final-output color tags, explicit assignments or look evidence need postproduction verification.
disable-model-invocation: true
---

# 색·룩 검증

## 입력
현재 source/output pins, LOOK evidence, stream tags와 승인 source assignment/output target. [공통 실행 계약](../references/execution-contract.md)을 먼저 읽는다. 분야 변경안은 총괄의 정본 commit으로 반영한다.

## 절차
1. 시스템·동일 프로그램/필수 dependency를 먼저 점검해 적합한 설치를 재사용한다. 새 설정·폰트·프로그램은 정확한 계획을 실제 사용자에게 질문하고 명시 동의 후 설치한다. 동의 전 download/installer를 실행하지 않는다.
2. 실제 primaries/transfer/matrix/range/pixel format/bit depth를 조회한다. 누락은 unknown으로 보존하고 명시 assignment는 검출 사실과 분리한다.
3. 정본 source SHA·assignment evidence·target을 결속한다. metadata 충돌/미확인 gamut을 표준 Rec709 PASS로 채우지 않는다.
4. 현재 구현의 색 경로는 actual tag 검사·assignment/target 대조다. 실제 grade/LUT/shot-match 변환은 verified native recipe가 있을 때만 수행하며 없으면 구체적 needs_user_action을 반환한다.
5. 최종 인접 컷/피부·의상/black·highlight/alpha edge·변환 순서를 실제 파일 QA로 보낸다. identity/의미 결함을 색 보정으로 자동 수락하지 않는다.

## 반환
관측 tags/unknown, 별도 assigned evidence, 실제 수행 변환 또는 미지원 조치, target/current LOOK QA 근거. tag는 gamut/지각 인증이 아니다.
