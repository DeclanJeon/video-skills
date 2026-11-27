# Orchestrator acceptance review

## Scope and method

Fresh-context, read-only decision simulation against `qa/scenarios.md`. Read the five requested documents and verified relevant phase instructions, schemas, implementation seams, and canonical legacy resources.

No commands, tests, generation, writes, delegation, installation, or external actions were performed. **The postproduction package was not inspected.** Scenario inputs are stipulated, not verified project evidence.

PASS below means the routing decision satisfies the scenario—not that production work completed.

## Scenario results

| # | Result | Selected phase | Next action | Completion status |
|---|---|---|---|---|
| 1. Prompt-only pre | **PASS** | Director; requested prompt endpoint only | Read the relevant crew instructions and supplied material; return only the requested prompts without generation or unwanted scaffolding. | Not executed; no deliverable completion claimed. `SKILL.md:11–15`; `references/phase-contract.md:11`. |
| 2. Image-inclusive pre | **PASS** | Director; P5/QA3 | Verify image-executor availability and authority; require actual references, panels, PNG sheets, cell mappings, and image-review evidence. | Pending actual media and QA; prompts alone cannot complete it. `SKILL.md:16`; preproduction `docs/design/06-image-prompt-spec.md:16–22`. |
| 3. Production-only, missing coverage | **PASS** | Supervisor; G0 | Locate validated upstream inputs and derive coverage when possible; otherwise report the exact missing source/coverage prerequisite. Do not invent preproduction. | **G0 blocked**, not production-ready. `SKILL.md:17`; production `production-supervisor/SKILL.md:9–14`. |
| 4. Combined | **FAIL** | Director → verified handoff → supervisor | Resume actual preproduction, validate the inputs, author the projection, preserve immutable coverage, then enter the supervisor once without routine phase approval. | The ordinary sequence is specified, but the L-cut mapping and separate-audio prerequisite routes remain unresolved; see findings. `references/phase-contract.md:17–23`. |
| 5. Nonstop, deadline, no post/receiver | **PASS** | Authorized pre/production; reserved post boundary | Continue independently executable authorized work. Preserve final-master target and record the receiver, integration, and restart blockers. | Final delivery blocked; absent genuine receipt also blocks G5. No fake master, receiver, or legacy P7 fallback. `references/postproduction-slot.md:18`. |
| 6. Combined ledger, script revision | **PASS** | Recorded production status first; preproduction revision blocked | Read recorded jobs/reservations; prohibit legacy writes until a preservation migration exists. Do not initialize again or resubmit unknown jobs. | Revision blocked; existing production facts preserved. `references/phase-contract.md:29–33`. |
| 7. Equipment packet | **PASS** | Assigned equipment under its phase owner | Consume the call sheet; verify live schema, selected inputs, rights, transmission, and cost gates; return results without a `creative-production` callback. | Pending actual execution evidence. `SKILL.md:30`; `references/phase-contract.md:40–45`. |
| 8. Approved model/transfer range | **PASS** | Current phase/operator | Reuse applicable approval; request only genuinely missing spend authority before submission. | Submission blocked if required spend authority is absent; supplied approvals are not re-requested. `SKILL.md:36`. |
| 9. Post directory exists, entry unconfigured | **PASS** | Reserved slot only | Report the unconfigured integration; do not inspect, adopt, install, or mutate the package. | Post remains unavailable. `references/postproduction-slot.md:3–9`. |
| 10. “프리만 논스톱” | **PASS** | Director; explicit pre endpoint | Continue within the requested preproduction scope only. | No expansion to production/final delivery. `SKILL.md:22`. |

## Six original P1 defects

| Original defect | Acceptance assessment |
|---|---|
| Phase-boundary precedence | **Addressed.** `SKILL.md:26–30` expressly supersedes imported generation/P7 routing and equipment callbacks while preserving safety gates. Separate-audio ordering still needs clarification below. |
| Pre-to-production bridge | **Partially addressed.** `references/phase-contract.md:15–25` defines an honest agent-authored projection—not an automatic CSV converter—and requires provenance, closure, validation, and immutable origin. L-cut dialogue remains unrepresentable by the prescribed mapping. |
| Destructive legacy writer | **Addressed procedurally.** Separate mutable ledgers and a historical-combined-ledger write prohibition are explicit (`references/phase-contract.md:29–33`). This accurately accommodates the unchanged destructive serializer at preproduction `scripts/cp2/ledger.py:39–47`; it is not a runtime guard added to that writer. |
| Transitive dependency keep map | **Addressed in the contract.** History, equipment, resource-only auditor compatibility, and canonical legacy-root correction are explicit (`references/phase-contract.md:8,35–45`). Actual registration preservation remains a separate machine check. |
| Equipment callback to old coordinator | **Addressed.** The new overlay explicitly suppresses it (`SKILL.md:30`). The canonical retained executor still contains the old instruction at `../contents-production-skills/higgsfield-generate/SKILL.md:33`, making transmission of the overlay important. |
| Post absence blocking G5 | **Addressed honestly.** Source readiness, G5 handoff, and final-master completion are separated; no placeholder receipt is allowed (`SKILL.md:42–46`; `references/phase-contract.md:49`). |

## Schema and resource verification

- Production actually accepts `Project` or `CoverageEnvelope`, not the preproduction artifact ledger: `video-production-skills/production/upstream.py:88–112`. The new handoff contract correctly recognizes this.
- Coverage preserves shot, panel, beat, speech, and cue obligations; mandatory asset closure is separately derived. The contract correctly warns that extra provenance metadata is not automatically validated (`references/phase-contract.md:18–23`).
- The immutable-origin warning is accurate: `export_coverage` uses `path.name` (`video-production-skills/production/upstream.py:237–239`). The contract requires checking the real project-relative location.
- Actual `Handoff` contains selections, joins, flow, receiver, rights evidence, and handle policy (`video-production-skills/production/models.py:322–332`). The builder requires current coverage/flow and nonempty recipient/rights evidence, and certifies zero exterior handles (`production/handoff.py:75–104`). These fields do not authenticate a recipient’s identity; actual receipt remains an observational obligation.
- Director/supervisor entry paths, preproduction validators, canonical history entry, and retained continuity/sequence-execution resources resolve. Two root-relative operating-contract locators are incorrect; see Finding 3.
- `qa/boundary-check.py` was read. It covers a single-cut, single-dialogue, LOOK-only projection and a missing-asset negative case. It does not cover the failures below. **No test result is asserted.**

## Review

### Correct

The orchestrator substantially improves scope ownership, approval reuse, safe resume behavior, and truthful completion reporting. The reserved post slot respects the prohibition against inspecting or implementing postproduction.

### Fixed

None; this review was read-only.

### Finding 1 — P1: L-cut dialogue cannot cross the prescribed projection boundary

**Location:** `references/phase-contract.md:18–23`.

Preproduction explicitly supports dialogue continuing across cuts. Its timeline validator requires the dialogue ID in **every intersected cut**, with the L-cut annotation (`video-preproduction-skills/scripts/timeline_check.py:90–94`).

The new mapping preserves each cut and maps its dialogue IDs into `speech[].id`. Production then creates globally keyed `speech:<id>` requirements and rejects duplicates (`video-production-skills/production/upstream.py:125–135`).

**Deterministic source-level example, not executed:** `D001` spans `S01-C01` and `S01-C02`. Both projected shots contain `Speech(id="D001")`. Derivation produces two `speech:D001` requirements and raises `duplicate upstream coverage IDs`.

**Impact:** This preproduction-supported combined route cannot reach production using the documented unchanged-ID projection. Silently removing or renaming an occurrence would change its obligations.

**Smallest remedy:** Specify and validate an L-cut-aware mapping preserving canonical dialogue identity and both cut obligations. If unavailable within the protected-package constraint, explicitly identify this case as unsupported/G0-blocked and narrow the combined-route claim. Add a cross-cut dialogue boundary case.

### Finding 2 — P1: Separate-audio production has no pre-QA4 owner/return path

**Location:** `SKILL.md:26`; `references/phase-contract.md:11`.

The overlay assigns actual generation to the supervisor **after QA4**, with preproduction owning generation-before-design completion. However, the imported separate-audio contract requires:

1. APR preparation;
2. approved audio generation;
3. measured-duration retiming;
4. only then VPR preparation.

That ordering is explicit in `video-preproduction-skills/docs/design/07-video-prompt-spec.md:181–189`.

**Impact:** Even with an authorized, supported audio executor, the documented sequence has no defined route to obtain the audio required before VPR/QA4. Following the inherited director-generation route contradicts the overlay; waiting until the supervisor boundary reverses the required order.

**Smallest remedy:** Define a bounded pre-QA4 audio-prerequisite owner and return path through measured retiming and renewed validation. Alternatively, explicitly report this route unsupported. Do not silently switch to native audio or invoke legacy postproduction.

### Finding 3 — P2: Required operating-contract paths contradict the declared root basis

**Location:** `references/phase-contract.md:5–7,49`.

The document declares paths relative to the orchestrator root, but names `docs/operations.md` and `production/docs/operations.md`; neither is the actual operating-contract path. Likewise, `production/handoff.py` omits the phase-package prefix under that declared basis.

**Smallest remedy:** Use explicit root-relative paths:

- `video-production-skills/docs/operations.md`
- `video-production-skills/production/handoff.py`

The supervisor’s own relative operations link is correct, so this is recoverable rather than a standalone cutover blocker.

### Merge verdict: **BLOCK**

Hold registration cutover until the two combined-route contract gaps are resolved or explicitly bounded as unsupported, then repeat scenario 4 with those cases. Static tests, discovery/collision checks, protected-source checks, and registration verification remain separate acceptance evidence.

Postproduction implementation or inspection is **neither required nor authorized** to resolve these findings.