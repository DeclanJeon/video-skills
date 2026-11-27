---
name: character-designer
description: "Crew skill; production-director assigns at P2, or user asks for a character sheet or persona: identity anchors, motives, voice identity, expression habits."
disable-model-invocation: true
---
# character-designer

## 역할

인물 정체성과 페르소나.

## 입력

잠긴 SCR·WLD와 화자/등장인물 목록.

## 절차

1. 인물별 CHR ID와 등장 씬을 배정한다.
2. `## anchor`에 나이대·체형·헤어·얼굴 식별 표지를 1–3문장으로 고정한다. 손의 흉터 같은 얼굴 외 표지는 추가 기준이지 얼굴 표지의 대체가 아니다. 얼굴 표지가 입력에 없으면 확인이 필요한 초안 제안임을 별도 메모로 남기고, 앵커 문장 안에는 메모를 섞지 않는다. 영어와 한국어 버전을 섞지 말고 사용 언어별로 관리한다.
3. persona에는 욕망·회피·결정 규칙, voice-identity에는 음역·질감, expression-habits에는 관찰 가능한 습관을 쓴다. 7뷰의 불변 요소를 적는다.

## 산출물

양식: [CHR](assets/CHR-template.md).

CHR 바이블과 뷰 가이드. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

의상과 실제 음성 캐스팅은 각 부서에 넘긴다. 실존 정체성 모방을 기본값으로 삼지 않는다.

## 자체 점검

뷰·씬마다 정체성 기준이 동일하며 패션·광원 지시가 anchor를 덮지 않는지 확인한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
