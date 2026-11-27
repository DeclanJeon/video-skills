# Retained-reviewer remediation re-check — review02

## Review

**Verdict: NOT APPROVED — BLOCK.**

Findings 3–5 are resolved within the accepted technical scope. Findings 1 and 2 are partially corrected but retain reproduced Important defects. No project, source, goal, or evidence files were edited by this reviewer.

This is the same retained reviewer’s bounded re-check, not a second review panel. The original report remains historical evidence and is not superseded for its original snapshot.

## Current source binding

Source manifest: `qa/implementation/review01-test-scope.json`

**SHA256:**  
`a538f078e86f759a603128bcb7f430f649407017acc717f9cfa8526d0f657792`

Goal snapshot SHA256:  
`a577981d162b136f66de6267d3f772dc7ea2114da66e37516b07e5e9f5220cd0`

At my request, the parent performed read-only verification before and after the reproductions:

- **239/239 scoped files identical** to the current manifest; no additions, removals, or drift.
- Live goal equals frozen goal bytes.
- **216/216 protected files unchanged**.
- Current XML/scope aliases are byte-identical to their versioned review01 artifacts.

These are **parent-executed checks**, not personally executed reviewer hashes.

## Resolution inventory

| Original finding | Status |
|---|---|
| 1. Wrong-branch finishing content | **Partially fixed; Important residual remains.** |
| 2. Portable smoke visibility | **Partially fixed; Important driver-wiring residual remains.** |
| 3. Declared audio profile ignored | **Resolved within qualified scope.** |
| 4. Supplied attribution lost | **Resolved within qualified scope.** |
| 5. Invalidated variant still counted complete | **Resolved.** |

## Remaining findings

### F1 — Important / P1: Raw finishing reservations still bypass destination-branch binding

**Locations:**  
`postproduction/backends/finishing.py:52,60–71`  
`postproduction/materialization.py:92–97`

The new content, mix-lock, and plate checks correctly validate the timeline selected by `FinishingRecipe.branch`. However:

- `prepare` binds `recipe.branch` to `order.branch`.
- `plan_for`, used by execution of an existing typed reservation, does not repeat that binding.
- Current artifact verification recompiles the payload recipe without checking that its branch is the reserved work’s branch.

Consequently, the new guards can validate **main content against main**, while QA attributes that output to a **reverse work order**.

**Reproduction, parent-executed at my request:**

1. Build actual native fixtures with explicit branch/reorder authority.
2. Commit a reverse timeline `C3,C2,C1`.
3. Construct a fresh typed `RequestPacket`:
   - work order branch: `reverse`;
   - correctly computed reverse-order fingerprint;
   - original main finishing recipe/inputs;
   - fresh owned workspace and identity.
4. Use normal reservation, native execution, materialization, and current QA—without editing the ledger or mocking validation.

**Observed:**

| Property | Result |
|---|---|
| Payload recipe branch | `main` |
| Reserved work branch | `reverse` |
| Expected first source | Blue C3 |
| Actual frame-12 center | **`[253,0,0]`**, red C1 |
| Native execution | `succeeded` |
| Materialization | Accepted |
| Current QA | **PG-E and PG0–PG6 all PASS** |

This remains the original technical canonical-to-native binding defect, reachable through the public typed reservation seam.

**Smallest correction:** share the finishing packet/order consistency checks across preparation, execution, and current artifact verification. Bind the payload recipe pin and branch to the reserved order and validate its required consumed artifacts against that order. Current QA must reject already-materialized mismatched packets while preserving historical facts and bytes.

Add a raw-reservation regression alongside the existing ordinary-prepare and legacy-proof cases.

### F2 — Important / P1: Real portable driver still supplies only the CLI, omitting required payload files

**Locations:**  
`postproduction/environment/portable.py:80`  
`postproduction/environment/craft_installer.py:64,72–76`  
`postproduction/environment/portable_audit.py:78–81`  
`postproduction/environment/native_smoke.py:124–127`

`NativeSmoke` now correctly mounts every supplied file. But its comment that the installer supplies the complete verified payload is contradicted by the actual callers:

- Extraction returns only `(target/relative_cli,)`.
- `CraftPortableDriver.install` returns that tuple unchanged.
- Recovery inspection likewise returns only the matching CLI.
- `CraftPortableDriver.smoke` forwards the tuple unchanged.

The new sibling-resource test manually supplies `(cli, actual_binary, resource)` (`tests/test_review_portable_smoke.py:21–22`), bypassing this wiring gap.

**Reproduction, parent-executed at my request:**

Using the owned copied-CLI wrapper/resource fixture, invoke the actual driver’s smoke callback with:

1. `(cli,)` — the real install/recovery return shape;
2. `(cli, actual_binary, resource)` — the manually complete test shape.

**Observed:**

- Host `--version`: exit **0**, FilmCraft 0.20.1.
- Actual driver, CLI-only tuple: **smoke failed**, missing sibling `resources/required.txt`.
- Same driver, complete tuple: **smoke passed**, network denied.

No installation, extraction, download, or vendor readiness receipt was performed.

**Impact:** resource-dependent portable payloads still cannot reach readiness through the actual driver/recovery path despite passing the helper-level remediation test.

**Smallest correction:** produce and propagate the exact verified payload inventory, CLI first, through install and recovery into smoke. Keep unrelated files excluded; do not replace exact mounts with a broad home/target mount. Handle unsupported link/dependency layouts explicitly.

Add an integration regression using the actual driver-produced/recovered inventory, not a manually expanded smoke argument.

## Verified corrections and strengths

### F1: Ordinary preparation and historical same-branch checks improved

`postproduction/finishing_binding.py:15–47` now compares actual edit content rather than incidental branch/cut names, checks the selected picture lock and mix extent, and checks consumed-source timing for plates.

The new tests cover wrong picture, wrong mix lock, old caption mapping, correct blue-first reverse output, and unchanged-content clean reuse.

I examined the legacy fixture carefully: only historical fixture construction bypasses the missing guard; the current QA evaluation runs after restoration. That is useful regression evidence. It does not cover the different raw-packet mismatch reproduced above.

### F3: Audio/profile enforcement resolved

`postproduction/profile_checks.py:37–73` provides:

- fail-closed container-brand matching;
- qualified MP4/H264/stereo-AAC dispatch restrictions;
- independent actual video/audio codec, rate, and channel checks.

The guard is called at picture/finishing preparation and packet execution. Both observers and PG5 independently inspect encoding (`postproduction/quality.py:82`).

`tests/test_review_audio_profile.py` covers actual audio-bearing output, unsupported declarations, codec/rate/layout negatives, unknown brand, and raw-packet dispatch refusal.

### F4: Attribution preservation and presentation scope resolved

`postproduction/delivery_attribution.py:34–58` collects supplied credits and exact provenance from actual main/variant consumption. Delivery writes the receiver-facing attribution record into the hashed inventory.

Explicit `on_screen` requirements fail closed rather than becoming metadata-only fulfillment. Both current QA and delivery enforce this (`postproduction/quality.py:101–103`; `postproduction/delivery_scope.py:46`).

The schema exposes the presentation distinction, and the new tests exercise main/variant credits and on-screen denial.

### F5: Current delivery progress resolved

`postproduction/progress.py:55–57` now preflights the main artifact and every contracted variant before counting current completion.

The actual invalidation regression checks count reduction to zero while retaining the historical delivery record and bundle. This addresses the goal-specific current-completion semantics, irrespective of the original report’s lower severity classification.

## Evidence and execution provenance

### Personally inspected

- Freeze02, current goal snapshot, remediation journal/rulings, updated operations/README.
- All added remediation modules and tests.
- Changed finishing, materialization, encoding, sandbox, smoke, delivery, attribution, progress, and fixture seams.
- Adjacent portable install, recovery inventory, provisioner, and smoke wiring.
- Updated schema field and acceptance-map references.
- Recorded full-suite conclusion, type/package results, and selected actual RED/GREEN logs.

The earlier whole-scope review remains background; this was a bounded current-source remediation re-check, not another exhaustive review.

### Parent-executed at my request during this re-check

- Initial/final manifest, goal, protected-file, and alias verification.
- JUnit parsing: **423 testcases, zero failures/errors/skips**.
- Default acceptance and package checkers.
- Actual driver-to-smoke residual reproduction.
- Actual raw-reservation finishing residual reproduction.

I personally ran **no commands, hashes, pytest, or type checks** because no command runner is available.

### Accepted recorded proof

- Entire pytest: **423 passed in 669.66s**, exit zero.
- Basedpyright: zero errors/warnings/notes.
- Package checker: successful, eight roles.
- Default acceptance checker: **52 IDs → 319 executed passing cases**.
- No lint pass: Ruff remains unavailable.

The older 404-case run and first verdict remain historical. The current passing suite is genuine but does not cover the two reproduced residuals.

## Rubric, roles, and constraints

- R03/R12 remain incompletely satisfied because F1 still permits wrong canonical branch content to receive current technical QA.
- R06 remains incompletely satisfied because F2 leaves the actual portable readiness path disconnected from its required payload inventory.
- The reviewed F3/F4/F5 gaps in R07/R08/R11/R12 are corrected within their stated technical boundaries.
- R13/R14 have current structural/executed-case evidence, not proof of exhaustive scenario satisfaction.
- **R15 remains unsatisfied: current verdict is NOT APPROVED.**

The eight role skills and shared execution contract are unchanged according to the manifest comparison. My prior bounded safe interpretation therefore stands: inspect/reuse first, ask before installation, inspect unknown jobs before replay, do not call previews full viewing/listening PASS, and return unsupported conform/9:16/MOGRT requests accurately. No repeated fresh-context behavioral certification is claimed.

No source edits, additional reviewers, installations/downloads, Git actions, user-media work, or user-process actions were performed in this re-check. Integrity corroboration found no drift or ownership conflict.

## DECLINED TO JUDGE

Unchanged qualified exclusions:

- Authentic human viewing/listening, legal-rights, or consent-issuer certification.
- Genuine new vendor installations, other OS/vendor execution, and universal interchange.
- Arbitrary 9:16/conform, original MOGRT fidelity, general grading, and universal font/plugin compatibility.
- Real-user-media privacy/perceptual suitability, provider/cloud/publication behavior, and broad performance guarantees.
- Repeated agent behavioral compliance and unavailable Ruff lint verification.

These exclusions do **not** excuse the reproduced local contract failures.

## Merge verdict

**BLOCK / NOT APPROVED.**

Resolve the remaining F1 packet-to-order binding and F2 driver-to-smoke inventory gaps, add their integration regressions, and refresh the affected validation/freeze evidence. F3–F5 need not be reopened without contrary evidence.