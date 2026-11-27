---
name: concept-benchmark
description: "Crew skill; production-director assigns at P0, or user asks to research comparable successful videos. Writes brief, benchmark anatomy and borrow ledger (structure only)."
disable-model-invocation: true
---
# concept-benchmark

## 역할

브리프와 시장 관측.

## 입력

사용자 요청·목표 플랫폼·러닝타임·사용 가능한 근거.

## 절차

1. BRF에 목적·대상·포맷·언어·길이·고정 제약·권리 범위를 잠근다. 미정과 추론은 구분한다.
2. [개발·QA1 정본](../docs/design/04-qa1-audience-reaction.md)의 사례 필드로 BMK를 채운다. 게시 경과·채널 규모·단위가 비교되는 사례만 묶고 중앙값에 표본 수를 붙인다. 순위나 약속된 성과를 추정하지 않는다. 출처·수집일을 붙인 관측은 `observed`, 근거 없으면 `unknown`과 최소 확인 행동을 남긴다.
3. BOR에 차용/변주/고유, 원본 근거, 우리 장면에서의 변환 방법을 놓는다. 레퍼런스 대사·인물·공간·고유 사건은 옮기지 않는다.

사용자가 레퍼런스 영상/링크를 주면 실제 프레임을 열어 분해한다(최소 1fps, 핵심 구간 촘촘히). 글 프롬프트만 있으면 영상 미확인을 명시하고 그 글의 촬영 문법을 차용 원장에 옮긴다. 장소·색만 가져오고 촬영 문법을 버리지 않는다([액션 연출 계약](../docs/design/12-action-direction-contract.md) §2).

룩 선택이 미정이고 내용 차이가 비교를 방해하면, 가능한 동일한 짧은 내용·구도·길이·화면비의 기존 승인 샘플로 비교한다. 통제하지 못한 차이는 BRF/BMK/BOR의 해당 판단에 비교 한계로 남기고, 스타일 선호를 조회수·제작 품질·모델 성능의 우열로 바꾸지 않는다. 이미 확정된 스타일은 재선택하지 않는다. 샘플이 없으면 한계와 필요한 입력을 반환하고, 새 생성은 감독/오케스트레이터에게 기존 단계·승인 범위로 요청한다. 직접 생성·결제·전송하거나 모든 작품에 비교 샘플 생성을 요구하지 않는다.

## 산출물

양식: [BRF](assets/BRF-template.md) · [BMK](assets/BMK-template.md) · [BOR](assets/BOR-template.md).

BRF·BMK·BOR. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

판단은 QA1, 이야기 표현은 작가가 소유한다.

## 자체 점검

BMK 없는 날에도 지표를 만들어내지 않는다. 비트 클러스터별 고유 요소를 확인한다.

### 실행 안전

해당 부서의 스타일·단계별 참조·원본 대응·오디오 증거를 반환한다. [실행 안전 계약](../docs/design/13-execution-safety-contract.md)의 해당 게이트를 적용한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
