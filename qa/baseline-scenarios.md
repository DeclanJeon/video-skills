# Baseline routing scenarios

Read-only routing simulation: no production, delegation, generation, revision, or postproduction inspection was performed. Only this requested report was written. Scenario inputs are stipulated, not verified project evidence.

## Sources and limits

Read only these source files:
- `video-preproduction-skills/production-director/SKILL.md` — preproduction entry, although its description also claims benchmark-to-final-cut coordination; respects user stop points and prompt-only requests.
- `video-production-skills/production-supervisor/SKILL.md` — approved batch/resume entry; requires source-derived coverage and closes production with reviewed coverage, joins, flow, post receipt, and handoff.
- `video-production-skills/docs/operations.md` — local state/evidence contract, not an execution provider; final editing/publication are separate.

There is no public root entry. Referenced design documents and role skills were not read; neither `docs/design.md` nor `qa/design-review.md` was read. Exact gates defined only in those references cannot be certified in this bounded test.

## 1. “프롬프트만 프리프로덕션 해줘”

- **Selected entry:** `video-preproduction-skills/production-director/SKILL.md`.
- **Phase endpoint:** Requested text/prompt preproduction delivery. Do not generate images or proceed to production. The entry explicitly exempts text/prompt-only requests from actual generation; its image-inclusive P5/QA3 endpoint is not imposed here.
- **Next actual step:** Determine whether the supplied brief and existing material support the requested prompt scope; route only that scope through the director's direct-work procedure. Do not invent project IDs, create an unrequested ledger, or claim unread department instructions have been executed.
- **Completion status:** Routed, not executed. Prompt delivery is feasible in principle; no prompt or QA completion is claimed. The entry delegates exact direct-work/gate details to documents outside this test's read boundary.

## 2. “승인된 설계로 프로덕션만 진행” — no coverage data

- **Selected entry:** `video-production-skills/production-supervisor/SKILL.md`.
- **Phase endpoint:** Production handoff after required coverage, accepted sources, joins, flow review, and post receipt; not a final edited/published master.
- **Next actual step:** Obtain/locate the actual approved project and its preserved source snapshot, then derive coverage from that source. If using the project JSON as the mutable ledger, first prepare an approved immutable version copy and export coverage from it. Do not initialize against a self-invalidating source pin. If the source itself is unavailable, stop and request it.
- **Completion status:** Blocked before production readiness until source-derived coverage is available and validated. “Approved design” alone neither supplies the coverage denominator nor proves execution/transfer/configuration authority or native capability. Missing exported coverage can be derived from a valid source; it must not be invented from batch clip count.

## 3. “프리프로덕션, 프로덕션 한번에 해줘” — preproduction ledger + board CSV

- **Selected entry:** `video-preproduction-skills/production-director/SKILL.md` first, then `video-production-skills/production-supervisor/SKILL.md` at the production boundary. This is the selected bounded sequence, not an existing root router or a claim that an automatic inter-package transfer exists.
- **Phase endpoint:** Validate/finish the requested preproduction first; then production's reviewed handoff. For image-inclusive preproduction, the director requires reference images, individual panels, real PNG sheets, cell mapping, and QA3 evidence. A board CSV alone is not that evidence. Prompt-only scope was not specified here.
- **Next actual step:** Resume from the existing preproduction ledger and actual decisions/evidence; establish the last accepted gate and incomplete work rather than infer completion from ledger/CSV existence. Only after preproduction is ready, provide the actual project source, derive full coverage, and use the existing project's production namespace through the production supervisor. An existing production namespace must be resumed, not initialized again.
- **Completion status:** Routed conditionally; neither phase is demonstrated complete. Ledger + CSV alone do not establish approved preproduction, asset closure, or production readiness. If a legacy preproduction writer would also save the shared ledger, simultaneous writes are blocked: operations warns that legacy `_save` drops unknown namespaces and requires a separate mapping/adapter for concurrent integration.
- **Current routing gap:** The director's broad final-cut remit overlaps the production entry, but the read entries provide no explicit root combined-run router or exact cross-package completion-transfer rule. The legacy read seam does not by itself establish safe two-way integration. Do not silently treat these gaps as implemented automation.

## 4. “오늘 마감이니 질문 없이 최종 영상까지 논스톱” — no post integration or receiver

- **Selected entry:** `video-preproduction-skills/production-director/SKILL.md` for the broad end-to-end request, with production work routed to `video-production-skills/production-supervisor/SKILL.md` when ready. No postproduction entry is selected or inspected.
- **Phase endpoint:** The requested final video is beyond the demonstrated executable boundary. Production can at most reach its reviewed delivery boundary; its handoff requires actual post receipt and rights evidence. The local `render-review` connection is explicitly not a final master.
- **Next actual step:** Report the missing post integration and receiver as blockers, and identify the unmet execution/transfer/rights approvals without assuming them. Do not fabricate receipt, call a technical review render final, or claim uninterrupted completion. No post inspection is needed to state the stipulated blocker.
- **Completion status:** Infeasible as requested under these conditions. Deadline and “no questions” do not supply approval or a receiver. Work before the blocked boundary would still require its normal inputs, authority, tools, and reviews; none are executed in this test.
- **Current routing gap:** The director advertises final-cut orchestration, while the production operations contract explicitly leaves final editing/publication separate. These files do not provide an executable route across the absent post integration.

## 5. Production started, then screenplay revised — production data in `ledger.json`

- **Selected entry:** `video-preproduction-skills/production-director/SKILL.md` for the upstream screenplay revision, and `video-production-skills/production-supervisor/SKILL.md` for production impact control and resumption.
- **Phase endpoint:** Reapproved upstream work and affected source/coverage pins, followed by invalidation/revalidation of affected production descendants and joins; eventual handoff only after all current gates close again. The revision is not an implicit production reset.
- **Next actual step:** Before any legacy screenplay-workflow save, preserve the existing production-bearing ledger and enforce a single safe writer. Read recorded production status/remote IDs and establish the last upstream decision; do not run `init`. Route the revision without allowing legacy `_save` to overwrite the production namespace. If the intended revision workflow requires concurrent legacy writes, stop for the required mapping/adapter. Once a safely recorded approved revision exists, propagate impacts with `invalidate`; use an exact approved `revise-scope` only if requirements/assets/coverage scope change, then explicitly revalidate against current pins.
- **Completion status:** Revision/resumption is not complete. A direct legacy rewrite of this shared ledger is unsafe and blocked under the operations contract. Existing jobs, attempts, unknown reservations, and historical approvals must be preserved; changed inputs do not erase remote facts. New work/adoption/handoff must pass current-input gates, and an invalid required predecessor cannot be bypassed by revalidating descendants.
- **Current routing gap:** The preproduction entry directs work through its legacy ledger procedure but does not expose the production-namespace preservation constraint. Operations documents that constraint and only a read-side `resolve_legacy` seam, not a complete revision-write integration.

## Result

All five requests have routing decisions, but no scenario is marked executed or complete. Explicitly infeasible transitions are: production without validated source-derived coverage; shared-ledger legacy writes without namespace-safe integration; handoff without a receiver; and a claimed final master through a package that ends before final editing/publication. No tests were run, no other files were changed, and no staging commands were used.
