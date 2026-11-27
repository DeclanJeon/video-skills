## 응답

**S01-C02-P2 이미지 프롬프트 — 채팅 초안**

인물·의상 기준문은 그대로 넣고, 구도와 동작만 자연스럽게 다듬었어요.

```text
[identity]
50대 중반의 다부진 여성으로, 질끈 묶은 단발과 눈썹 바깥의 작은 점이 있다.
회색 니트 위에 남색 앞치마를 두르고 소매를 걷었다.

[composition]
세로 9:16. 계산대 오른쪽에 선 여성이 오른손을 들어 손등을 보여 준다. 화면에는 이 여성 한 명만 등장하며, 얼굴과 들어 올린 오른손등이 한 프레임에 함께 보인다.

[negative]
글자, 자막, 로고, 워터마크 없음.
```

공통 스타일, 인물·장소 참조 이미지, 스토리보드의 인물 수와 카메라 축은 미확인이라 제출용 확정본은 아니에요. 이미지 생성이나 외부 호출은 하지 않았어요.

## 실제 작업 로그

1. `find`로 `image-prompt-engineer/SKILL.md` 위치를 확인한 뒤 `read`로 읽었다.
2. 스킬이 직접 연결한 자료만 읽었다: `docs/design/06-image-prompt-spec.md`, `image-prompt-engineer/assets/IMG-template.md`, `image-prompt-engineer/assets/IMG-map-template.json`, `docs/design/03-artifact-index.md`, `production-director/assets/DLV-template.yaml`. 평가 문서나 예시 픽스처는 읽지 않았다.
3. 이미지 명세의 I1에 따라 사용자가 제공한 CHR-02·WRD-02a 기준문과 초안의 두 줄을 대조했다. 두 문장을 원문 그대로 두고, 계산대 기준 오른쪽 위치·오른손등·9:16을 단일 정지 순간으로 정리했다. 계산대 기준 오른쪽을 화면 기준 오른쪽으로 바꾸지 않았다. 제공되지 않은 버전 핀, 스타일, 참조 이미지, 축·소품 상태는 추정하지 않았다.
4. 스테이징 확인용 로컬 명령 `git diff --cached --exit-code --name-only`는 종료 코드 129였고, 이어 실행한 `git rev-parse --is-inside-work-tree`는 종료 코드 128로 현재 작업 경로가 Git 작업 트리가 아님을 확인했다. 스테이징 작업은 하지 않았다.
5. 지정된 보고서만 작성했다. 채팅 초안에 필요한 문장 대조만 했으며, 정식 프롬프트/사이드카와 검사용 정본 입력이 없어 `prompt_lint.py --kind image`는 실행하지 않았다. 이미지 생성·외부 모델 호출·과금·원장 수정은 하지 않았다.
