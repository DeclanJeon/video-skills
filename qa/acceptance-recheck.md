# Acceptance recheck

**Result: PASS — all three previous findings are resolved at the contract/schema level.**

Read-only recheck limited to those findings and scenario 4. No commands or tests were run. No postproduction package was inspected or changed. Parent-reported test results are not independently certified here.

## Review

### Correct

The direct `CoverageEnvelope` route is supported by the existing implementation:

- `Requirement` accepts distinct string keys, shot/panel ownership, modality, and locators (`video-production-skills/production/models.py:50–55`).
- Envelope coverage and asset uses pass through the supported derivation branches; export pins their immutable origin (`video-production-skills/production/upstream.py:103–115,151–157,237–239`).
- Downstream allocation validates unique requirement keys and their shot assignments without requiring the old `speech:<dialogue>` naming (`video-production-skills/production/contracts.py:11–46`).

### Fixed — verified corrections

1. **Cross-cut dialogue:** `references/phase-contract.md:24–30` now selects an explicit envelope for repeated canonical dialogue IDs. Per-cut requirement keys retain both obligations without renaming canonical dialogue. Locators preserve source/range information; a separate immutable provenance sidecar avoids forbidden envelope metadata. Complete asset closure and source reconciliation remain mandatory, with G0 blockage if unfinished.

   `qa/boundary-check.py:91–133` now contains a two-cut envelope/export case asserting both scoped speech requirements, canonical `D001` locators, shared asset pins, and origin-derived coverage/asset-use equality. This verifies test contents, not execution results.

2. **Separate-audio prerequisite:** `SKILL.md:26` distinguishes video generation from pre-QA4 audio work. `references/phase-contract.md:13–17` assigns the orchestrator a bounded sequence: APR → authorized executor → actual files/measurement/listening evidence → retiming and pin updates → timeline validation → VPR → QA4. This matches the required ordering in preproduction `docs/design/07-video-prompt-spec.md:181–189` without prematurely initializing the production batch.

3. **Resource paths:** `references/phase-contract.md:7,56` now names the correct root-relative operating-contract and handoff paths. Both were opened successfully.

## Scenario 4 repeated — decision simulation

| Variant | Result | Selected phase and next action | Completion status |
|---|---|---|---|
| Combined with L-cut dialogue | **PASS** | Director validates actual upstream work and QA4. Author the immutable envelope with both per-cut dialogue obligations, complete asset uses, source/range locators, and pinned provenance sidecar; export coverage, then enter the supervisor once for G0/allocation validation. | Not executed or complete. Unreconciled mapping/closure blocks G0; the former unavoidable duplicate-ID projection failure is avoided. |
| Combined with separate audio | **PASS** | Director retains design ownership while the orchestrator obtains authorized prerequisite audio and returns measured results for retiming. Complete timeline/pin validation, VPR and QA4 before the production handoff. | Not executed or complete. Missing executor, authority, or evidence blocks the audio prerequisite—not a circular wait for post-QA4 production. |

### Findings

No issues found.

### Merge verdict: **OK**

The three reviewed findings no longer block registration cutover. This scoped approval does not certify test execution, installed discovery, registration preservation, or real media delivery.