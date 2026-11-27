---
name: costume-designer
description: "Crew skill; production-director assigns at P2, or user asks for costume, hair or makeup design: wardrobe states per character and scene."
disable-model-invocation: true
---
# costume-designer

## 역할

의상·헤어·분장 상태.

## 입력

SCR, CHR, WLD 팔레트.

## 절차

1. 인물×씬에서 의상 변화 지점을 정한다.
2. 상태별 WRD ID를 배정하고 `## prompt`에 소재·색·핏·헤어·분장·소지 상태를 고정 문장으로 쓴다.
3. 상태가 바뀌는 원인과 이전/다음 씬을 모두 연결한다.

## 산출물

양식: [WRD](assets/WRD-template.md).

WRD 상태 문서와 인물×씬 매트릭스. [부서와 산출물 정본](../docs/design/02-crew-roster.md)와 [인덱스 정본](../docs/design/03-artifact-index.md)의 ID를 사용한다.

## 다른 부서와의 경계

인물 신원은 CHR 정본을 따른다.

## 자체 점검

임의 의상·헤어 바뀜, 장르/시대 불일치, 미배정 씬을 확인한다.

## 납품

[납품 패킷](../production-director/assets/DLV-template.yaml)으로 입력 핀, 산출물, 점검, 미확인 사항을 감독에게 반환한다. 원장을 직접 쓰지 않는다.
