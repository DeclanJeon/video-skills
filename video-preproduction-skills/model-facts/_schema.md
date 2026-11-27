# 모델 사실 레지스트리 (RR-6)

모델마다 `model-facts/<model-id>.json` 한 파일. 설계에 모델 사실을 고정하지 않고, **확인된 사실만 출처·날짜와 함께** 여기에 둔다.

```json
{
  "model": "<id>", "endpoint": "<선택>",
  "facts": {
    "max_duration_s":   {"value": 10,        "source": "doc:<url>|experiment:<EXP-id>|user", "verified_at": "2026-11-25", "status": "verified"},
    "aspects":          {"value": ["16:9","9:16"], "source": "...", "verified_at": "...", "status": "verified"},
    "native_audio":     {"value": "UNVERIFIED", "status": "unverified"},
    "dialogue_languages": {"value": [], "status": "unverified"},
    "reference_images_max": {"value": null, "status": "unverified"},
    "prompt_chars_max": {"value": null, "status": "unverified"}
  },
  "ttl_days": 30
}
```

규칙
- `native_audio`의 확인된 값은 `true`(원생 동기 대사 지원) 또는 `false`다. 일반 음향 지원만으로 `true`를 기록하지 않는다.
- `status`: `verified`(출처+날짜 있음) / `unverified` / `expired`(verified_at + ttl_days 경과 → 자동 `expired`로 취급).
- `video-prompt-engineer`는 GEN 묶음 전에 필요한 사실(`max_duration_s`, `aspects`, `native_audio`)을 읽고, 사이드카 `model_facts`에 **값과 status를 그대로 복사**한다.
- **제출 차단 규칙:** `max_duration_s`와 `aspects`가 `verified`가 아니면 QA4 4.5는 PASS 불가. 사용자가 위험을 수락한 경우만 `accepted_risk: <사용자 문구>`로 진행하고 QAR에 남긴다. `native_audio`가 `UNVERIFIED`이면 `audio_path`는 `separate`로 시작한다.
- 사실의 출처는 (a) 공급자 문서 열람, (b) 짧은 실험 생성(`EXP-`), (c) 사용자 제공 중 하나. 기억이나 추정은 출처가 아니다.
- 이 저장소에는 **검증된 사실을 넣지 않은 빈 템플릿만** 둔다. 사실은 실제 확인 시점에 채운다.
