---
name: production-ledger
description: "Crew skill used by production-director only: initializes project roots, registers artifacts and versions, propagates stale status, records history."
disable-model-invocation: true
---
# production-ledger

## 역할

감독의 요청을 받아 파일 등록, 변경 전파, 로컬 검사 결과를 반환한다. 승인이나 예술적 합격 여부를 판단하지 않는다.

## 입력

감독이 지정한 프로젝트 루트, 단계, 산출물 ID·경로·버전, 소비한 버전 핀. 기존 작업이면 `ledger.json`과 `.history/events/`에서 확인할 수 있는 사실을 먼저 대조한다.

## 절차

1. 프로젝트 루트가 지정되어 있고 파일 쓰기가 허용된 경우에만 작업한다.
2. [원장과 CLI 규약](references/ledger-schema.md)에 따라 해당 버전 파일을 등록한다. 기존 파일을 덮어쓰지 않고, 읽기 전용 검사에서는 원장을 쓰지 않는다.
3. 변경 범위를 전파하고 해당 게이트의 인덱스·시간표 검사를 실행한다. 실패 코드를 해당 부서에 돌려보내며 산출물을 대신 고치지 않는다.
   사운드 소스는 [사운드 등록 계약](../docs/design/11-sound-sourcing-integration.md#3-파일과-증빙을-기존-id원장에-등록)의 기존 ID와 acyclic consumes 순서로 등록한다. rights REF → AMB/SFX/MUS 미디어 → review REF → 소스 원장 REF → SND → 실제 소비자 순서다. 계획 큐와 실제 미디어의 구분·source/rights/review 현재 핀을 납품하고, 권리 교체로 stale인 미디어는 새 권리를 소비하는 다음 버전으로 갱신한 뒤 리뷰를 등록한다. 등록 상태를 소스 준비/청취/권리 승인으로 판단하지 않는다.
4. 실제 파일 생성·검사·납품 이력은 기존 `recording-production-history` 도구가 대상 프로젝트에서 준비됐을 때만 같은 작업 ID로 남긴다. 도구가 없거나 계약이 맞지 않으면 `UNVERIFIED`로 반환한다.

## 산출물

원장 변경 시 `ledger.json`, 영향을 받은 ID, 검사 결과. 이력 도구를 실제로 실행했다면 생성된 이벤트 경로.

## 다른 부서와의 경계

감독만 기록자를 맡는다. 개별 부서는 자기 산출물과 납품 패킷만 제출한다. 이력 등록은 실행 승인이나 QA 합격이 아니다.

## 자체 점검

파일·해시·핀과 stale 목록을 대조한다. 현재 단계의 인덱스 검사와 타임라인 검사 결과를 구분하고, 미확인 대사 타이밍은 실측으로 기록하지 않는다.

## 납품

감독에게 등록 ID·버전, 실제 파일 경로, 변경 영향, 실행한 명령과 발견 사항, 미실행 항목을 반환한다.
