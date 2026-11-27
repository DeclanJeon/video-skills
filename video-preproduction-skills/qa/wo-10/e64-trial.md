# IMG-S01-C01-P1 — 채팅 초안

**임시 대안: 16:9 가로 원본을 설계하고, 나중에 일반 편집기로 중앙 9:16 크롭.** 완성 목표는 **9:16**, 사용자 제공 합성 모델 계약에서 확인된 출력은 **16:9 한 종류**입니다. 따라서 모델용 초안에는 16:9만 지시합니다. 9:16은 모델 출력이 아니라 별도 후편집 결과입니다. 이번에는 생성·제출·크롭을 모두 하지 않았습니다.

## 모델용 프롬프트 초안

```text
[style]
Realistic cinematic film still, subtle grain, muted colors.

[identity]
An older brother in a neighborhood laundromat; he is the only person visible.

[composition]
Visible people: 1
Axis: The man is on screen left of the frame midpoint; the light comes from the doorway behind him to his left.
One still moment in a 16:9 landscape frame. Eye-level medium shot. Keep his entire face, shoulder line, and the lit inner edge of the doorway comfortably within the central 30 percent of the wide frame. Place his face slightly left of center, with visible space on its right. The light from the doorway catches the left edge of his face and shoulder. His hands remain below frame; no handheld prop is visible. Laundry racks fade softly into the background. Keep both outer sides expendable, with no essential subject or detail there.

[negative]
No text, no watermark, no captions, no legible signs, no logos, no speech bubbles, no panel borders, no crop guides, no other people.
```

## 크롭 메모 — 모델에 보내지 않음

가로 원본 중앙에서 전체 높이와 가로폭의 **약 31.64%**(원본 왼쪽 기준 **34.18%–65.82%**)를 남기면 9:16입니다. 얼굴 중심을 원본 너비 **약 44%**에 두는 것이 구도 목표입니다. 그러면 세로본에서 얼굴 중심이 왼쪽 **약 31%**에 놓입니다. 문 전체를 남길 필요는 없지만, 빛이 들어오는 문 가장자리와 얼굴·어깨에 닿는 빛은 크롭 안에 함께 남겨야 합니다. 좌우가 합계 약 68.36% 잘리므로 세탁소 공간감은 줄어듭니다. 이 위치들은 편집 기준이지 모델 기능이나 결과 보장이 아닙니다. 추후 승인된 원본에서 얼굴·문 가장자리·빛이 함께 남는지 확인하고, 하나라도 잘리면 이 크롭을 완성본으로 채택하지 않습니다.

## 사이드카 — `IMG-S01-C01-P1.map.json` (인라인)

```json
{
  "id": "IMG-S01-C01-P1",
  "panel": "S01-C01-P1",
  "status": "chat_draft_not_ready_for_submission",
  "moment": "Single still of the older brother catching doorway light; exact storyboard time unconfirmed",
  "block_markers": {
    "style": "[style]",
    "identity": "[identity]",
    "composition": "[composition]",
    "negative": "[negative]"
  },
  "sheet_baseline": null,
  "identity_sources": [],
  "references": [],
  "reference_inputs": [],
  "sources": {
    "style": ["draft:provisional look; no canonical LOOK pin supplied"],
    "identity": ["user:older brother in a laundromat; no canonical CHR/WRD pin supplied"],
    "composition": ["user:S01-C01-P1, screen-left subject, doorway light", "draft:one visible person, shot, hand/prop treatment, crop-safe blocking"],
    "negative": ["common:no-text", "common:no-watermark", "draft:no visible crop guides or other people"],
    "aspect": ["user:9:16 required finish", "user:verified 16:9-only synthetic model output contract"]
  },
  "model": null,
  "model_facts": {
    "aspects": {"value": ["16:9"], "status": "verified", "source": "user", "verified_at": null}
  },
  "prompt_language": "en",
  "target_aspect": "9:16",
  "model_output_aspect": "16:9",
  "native_target_aspect_supported_by_contract": false,
  "postprocess": {
    "operation": "center_crop",
    "execution": "not_run",
    "output_aspect": "9:16",
    "x_bounds_percent_of_source_width": [34.1796875, 65.8203125],
    "height": "full height before pixel rounding",
    "keep": ["face on the left of the resulting frame", "shoulder", "illuminated inner doorway edge", "visible doorway light on face and shoulder"],
    "reject_if": "Any keep element is cropped out, or the man no longer reads as screen left"
  },
  "unverified": ["model ID, endpoint, and verification date not supplied", "model language, reference support, resolution, and exact framing behavior not established", "STB/index, BRF/CAM/CNT/CTY, CHR/WRD, LOOK/WLD, LOC/LGT/PRP and REF pins not supplied"],
  "submitted": false,
  "generated": false
}
```

`verified`는 사용자가 제공한 비율 계약의 상태입니다. 모델 ID·엔드포인트·확인 날짜가 없어 별도 레지스트리 검증으로 간주하지 않습니다. 인물 1명·샷·손/소품·룩은 초안 선택이며 정본 확인이 아닙니다. 기준 이미지(REF)나 정본 앵커를 붙였다고 가정하지 않았습니다. 이 초안은 제출·생성 승인용이 아닙니다.

## 납품 패킷 (DLV)

```yaml
dlv_for: null
artifacts: ["IMG-S01-C01-P1 chat draft", "IMG-S01-C01-P1.map.json (inline)"]
consumed: ["user chat brief", "user-verified 16:9-only output aspect contract"]
assumptions: ["Single visible person; provisional style/framing; center crop after later authorized generation"]
conflicts: ["Requested 9:16 finish is not available natively under the 16:9-only contract"]
checks:
  - "Actual lint run and result recorded below; not a production QA pass"
  - "Crop geometry checked; visual result untested"
missing_inputs: ["versioned STB/index, canon sources and REF pins", "model identity and verification date"]
self_verdict: partial
```

## 실제 작업 로그

- `functions.read`: `image-prompt-engineer/SKILL.md`, `docs/design/06-image-prompt-spec.md`, `image-prompt-engineer/assets/IMG-template.md`, `image-prompt-engineer/assets/IMG-map-template.json`, `docs/design/03-artifact-index.md`, `production-director/assets/DLV-template.yaml` 및 링크된 `docs/examples/synthetic-laundromat-34s/fixture.md`, `model-facts/_schema.md` 열람. 픽스처는 명세 예시로만 읽었으며 정본 핀으로 사용하지 않음. 평가자 문서는 열람하지 않음.
- `python3 scripts/prompt_lint.py --help`: 종료 0. 입력 인수 확인.
- `git status --short`: 종료 128, 작업 디렉터리가 Git 저장소가 아님. 뒤에 연결한 `git diff --cached --name-only`는 실행되지 않았고 스테이징 작업은 수행하지 않음.
- 보고서에서 프롬프트와 사이드카를 임시 파일로 추출. Python으로 JSON 파싱, 프롬프트에는 16:9만 포함되는지, 모델 비율과 후편집 비율이 분리됐는지, 크롭 기하 및 미생성·미제출 표기를 검사: **PASS**. 원본 폭 31.64062500% 유지, x=[34.1796875%, 65.8203125%], 원본 x=44% → 크롭 안 x=31.04%.
- 실제 린트 명령: `/usr/bin/python3 scripts/prompt_lint.py --kind image --prompt /tmp/board-image-task-4-9lfa8q_9/IMG-S01-C01-P1.txt --map /tmp/board-image-task-4-9lfa8q_9/IMG-S01-C01-P1.map.json --project /tmp/board-image-task-4-9lfa8q_9/project --json`. 정본 프로젝트가 제공되지 않아 빈 임시 프로젝트를 사용했으며 임시 입력은 검사 후 삭제함. **종료 1 (제출 차단)**. 반환 원문:

```text
I1 error: zero-cast exception requires an empty registered panel roster, a reason, and no identity text
I2 unverified: registered sheet baseline not supplied
I3 unverified: registered sheet baseline not supplied
I7 unverified: registered sheet baseline not supplied
```

I1은 정본 인물·의상 소스가 없는 인물 포함 초안의 오류이며, 무인 패널로 선언해 우회하지 않았습니다. I2/I3/I7은 인물 수, 공통 스타일, 축을 등록된 시트와 대조하지 못했다는 뜻입니다. 모델·편집기를 호출하지 않았고, 실제 크롭 결과나 QA 통과는 주장하지 않습니다.
