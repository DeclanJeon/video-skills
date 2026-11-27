## Actual user response

**[P3 콘티 회의 결정 | S01 | `tmp:RUL-01`]**

창 쪽 역광은 유지하고, **마지막 동작 전에는 얼굴에 정면 키라이트를 쓰지 않습니다.** 손은 동작이 읽히도록 손에만 제한한 보조광으로 살립니다. 조명 취향보다 확정 DNT의 이야기 요구가 우선입니다. 같은 화면에서 **누구인지는 알 수 없고, 손이 무엇을 하는지는 보여야** 합니다. 신원 노출이 필요한 경우에도 마지막 동작보다 앞당기지 않습니다.

1. **촬영팀 먼저:** S01 콘티 초안의 카메라 레이어에서 마지막 동작이 시작되는 컷·비트를 표시해 주세요. 그 전까지 얼굴 식별 단서는 가려지고 손동작은 프레임 안에서 읽히는 앵글과 구도를 정리해 조명팀에 넘겨 주세요.
2. **조명팀 다음:** 그 카메라 안을 기준으로 S01 조명 레이어만 수정해 주세요. 창 역광을 유지하고 손 쪽에만 약한 측면광이나 반사광을 제안해 주세요. 얼굴에 빛이 새거나 창·소품 반사로 신원이 먼저 드러나지 않는지, 같은 컷에서 손동작이 읽히는지 확인해 돌려주세요.

**다음:** 두 팀은 자기 레이어만 수정하고, 남는 충돌은 상대 레이어를 고치지 말고 회신해 주세요. P3 마감 전에 수정된 두 레이어를 함께 대조해 신원 노출 시점·손동작 가독성·컷 간 빛 연속성을 확인합니다.

## Tool log

1. `read production-director/SKILL.md` — loaded the director routing and conflict-handling instructions.
2. Parallel `read` calls (directly routed references only):
   - `docs/design/05-conti-collaboration.md` — camera-to-lighting dependency, Director ruling priorities, affected layers only.
   - `docs/design/01-pipeline-and-gates.md` — P3 scope, crew handoff and stopping rules.
   - `production-director/assets/RUL-template.yaml` — ruling fields.
   - `production-director/assets/CALL-template.yaml` — work assignment and stop conditions.
   - `production-director/assets/DLV-template.yaml` — return and conflict reporting.
3. `git diff --cached --name-only --` — read-only staging check failed (exit 129; Git treated the directory as outside a work tree).
4. `pwd; git rev-parse --is-inside-work-tree` — confirmed the task directory and that it is not in a Git work tree (exit 128).
5. `write`, then `edit` — recorded and refined this response and log at the requested output path, outside the project.

No evaluator materials or production project records (such as a live DNT, CNT or ledger) were opened. No project files were changed. No message was sent to either team, no work was delegated, and no external action or downstream phase was executed.
