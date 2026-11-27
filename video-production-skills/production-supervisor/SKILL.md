---
name: production-supervisor
description: "Use when coordinating an approved multi-clip AI video production batch or resuming its production queue."
disable-model-invocation: true
---
# production-supervisor

## 입력과 소유권
작품 프로젝트 경로, 현재 프리프로덕션·coverage_source, batch, 실행/전송 승인, 계정/모델의 실제 기능 근거를 받는다. 프로젝트 원장의 production namespace는 총괄만 기록한다. 역할별 산출물은 보고서로 받아 통합한다.

## 절차
1. [운영 계약](../docs/operations.md)을 읽고 coverage를 원본에서 도출한다. batch의 clip 수만으로 필수 소스 분모를 만들지 않는다.
2. init/validate/ready로 현재 상태를 읽는다. 기존 production이 있으면 init 대신 재개한다. 준비된 독립 clip만 현재 계정 슬롯 안에서 배정한다. 필수 identity·보드·계보 핀은 dependencies로 보존하고, 외부 참조 assets와 구별한다. 기존 영상은 명시적 reuse grant로 인계하고, 요구 제외는 revise-scope의 정확한 변경 승인 없이는 하지 않는다.
3. operator에게 정확한 prepared request를 맡긴다. 원격 작업·모달리티·비용은 현재 지원 장비와 승인 범위로만 실행한다. 이 패키지 CLI 자체는 외부 실행하지 않는다.
4. 테이크·연속성 검수 결과를 정확한 source/range/revision에 결속한다. 변경된 선행 결과는 invalidation으로 후손과 접합을 재검수한다.
5. 모든 필수 coverage, 접합, 전체 흐름과 post 수령을 닫고 handoff를 만든다. 차단이면 원인·남은 항목·정확한 재개점을 남긴다.

## 납품·완료
progress와 handoff, 원격 ID/시도·핀/검수 증거를 반환한다. 100%는 G0–G5 정책 충족이며 제출률과 채택률은 별개다. 독립 리뷰를 실제로 수행하지 않았으면 자체 검수로 표시한다.
