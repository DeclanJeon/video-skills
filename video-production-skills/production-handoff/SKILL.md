---
name: production-handoff
description: "Use when delivering accepted production sources and reviewed source ranges to postproduction."
disable-model-invocation: true
---
# production-handoff

## 입력
현재 coverage와 selections, G2–G4 검수, 실제 음향/권리/조건부 후반 작업과 수령자. [운영 계약](../docs/operations.md)을 읽는다.

## 절차
1. 필수 coverage의 모든 항목이 실제 소스구간과 검수로 충족되는지 확인한다. 모든 clip 존재와 모든 사건 충족은 다르다.
2. stale/unknown/미검증·반려를 납품 완료에 포함하지 않는다. conditional은 승인된 허용 정책과 실제 post 수령자의 수정 수락이 필요하다.
3. handoff 직전에 모든 원본 파일과 승인 증거를 작품 root에서 다시 열어 핀을 대조한다. 예전 연결본이 남아 있어도 원본 삭제/바이트 변경이면 차단한다. handoff로 원본·해시·in/out/FPS/PTS·실측 handle·접합·flow·트랙 유무·권리·제한을 묶는다. 존재하지 않는 음향 stem은 인계하지 않는다.
4. post가 구간·순서를 바꾸면 새 접합 QA가 필요함을 명시한다. 최종 편집/합성/믹싱·마스터·게시는 post 범위로 넘긴다.

## 납품·완료
Handoff JSON과 원본 에셋의 안전한 로컬 경로를 전달한다. 수령 확인·필수 요구·필수 경계·전체 흐름이 닫혀야 G5 완료다. 최종 작품 품질 인증이나 게시 승인을 주장하지 않는다.
