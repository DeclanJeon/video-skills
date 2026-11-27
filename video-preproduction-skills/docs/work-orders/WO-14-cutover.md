# WO-14 — 전환·설치

**Goal:** v2를 기본 콘텐츠 제작 패키지로 전환하되 v1로 즉시 롤백 가능하게 한다.
**Spec:** DES-08 §4 · **의존:** WO-13 합격

## Steps
- [ ] **1. 설치 문서** — `INSTALL.md`: 스킬 20개 등록 경로(Pi `~/.pi/agent/skills/`, Codex `~/.codex/skills/` 등)에 심볼릭 링크, v1과 이름 충돌 없음 확인 명령(`ls` 비교)
- [ ] **2. 장비 의존 확인** — v1 공급자 스킬(higgsfield-*, suno-music, codex-imagen, blender-previsualization, searching-social-media)이 설치돼 있는지 확인하는 `scripts/check_equipment.py` (없으면 해당 단계만 `UNVERIFIED`, 설치 자동 실행 금지)
- [ ] **3. 워크플로 지시 변경안** — `/home/declan/.agents/DEVELOPMENT-WORKFLOWS.md`의 "Content production" 문단 교체안을 diff로 작성. **적용은 사용자 승인 후**
- [ ] **4. 롤백 절차** — 링크 제거 + 지시 원복 2단계 문서화
- [ ] **5. 릴리스** — `manifest.json` 1.0.0, `CHANGELOG.md`, 태그는 사용자 승인 후
