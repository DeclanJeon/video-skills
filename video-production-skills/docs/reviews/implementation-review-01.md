# Independent final implementation review

## Verdict: REVISE

The scoped local implementation is substantial and its existing checks are genuinely executable, but **five important findings remain**. R12 must not be marked PASS on this snapshot. This is not a demand for live provider integration or perceptual certification: both remain explicitly outside this review.

### Snapshot and review boundary

- Project: `/home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-production-skills`.
- Reviewed the active goal, all six reviewed design documents, independent design review 02, README, operations, five role skills, manifest, implementation plan, every `production/*.py`, `scripts/*.py`, and `tests/*.py`, acceptance map, examples, and runtime/schema correspondence.
- Snapshot manifest: `qa/implementation/review-scope.sha256`.
- **Manifest SHA-256 before and after: `281401bf4972cb5fb12495d66a905a3ac055404e70da6ec2dd5ee40d0c9dff5e`.**
- `sha256sum -c qa/implementation/review-scope.sha256`: **60/60 OK before and after**. This is the supplied implementation scope, not a claim that every contextual document is included in that manifest.
- No project sources, skills, goal, docs, examples, fixtures, schemas, or manifest were edited. Standard caches and the acceptance checker's QA outputs were regenerated. This report is written only to the authorized routed output path.

## Findings

### F1 — High: G5 can successfully hand off missing or modified source media

**Locations:** `production/cli.py:146–152`, `production/render.py:98–107`, `production/handoff.py:71–96`.

The CLI checks the review-render manifest and rendered movie, but never re-verifies the selected original source files at delivery. `verify_render` compares source *records* with `slices(state)` and probes only the montage. `build_handoff` has no project root and checks only in-memory selection validity. Deleting a source after rendering therefore leaves selection/hash checks unchanged and still produces a successful handoff containing that nonexistent source.

**Executed reproducer:** Construct three current selections with real temporary local videos; create the real montage with `render_review`; persist the state with `ProjectStore`; create a matching fixture `FlowReview`; delete `root / state.selections[0].take.asset.path`; run the actual `handoff` CLI. Observed:

```text
{"missing_source":"local-0.mp4","handoff_exit":0,"sources_delivered":3}
```

The semantic/remote reports in this reproduction were fixtures; the source files, montage, deletion, persistence, and CLI were real. The same hole applies to replacing the source bytes without updating the ledger.

**Impact:** A successful G5 result does not establish that its deliverable originals exist and match their pinned hashes. This violates R09 and the source/hash/receiving contract in design 04 §5, independent of any perceptual judgment.

**Minimal fix:** At the delivery boundary, verify every selected source pin against the project root before issuing the Handoff; make the checked library entry point enforce this too, rather than relying on an easily omitted caller step. Add post-render deletion and byte-replacement rejection tests through the CLI. Replaying every source is not necessary merely to detect these two failures.

### F2 — High: the upstream adapter silently drops character identity dependencies

**Locations:** `production/adapters.py:55–59,80–84,132–156`.

The upstream models use `extra="ignore"`, but `Shot` does not retain `character_ids` and `Project` does not retain `characters`. Mandatory asset closure is restricted to `shot.asset_ids` and active LOOK. The actual existing handoff contract additionally follows `shot.character_ids → characters[].identity_sheet_asset_id` (see the existing `../contents-production-skills/video-production-assets/scripts/project_index.py:25–26,83–88`). Thus a source project that assigns a character identity normally through this relation can pass G0 with no corresponding identity pin in its production clip.

**Executed reproducer:** Pin a temporary upstream project with:

```json
{
  "shots": [{"id":"SH1","character_ids":["CHR1"],"asset_ids":[]}],
  "characters": [{"id":"CHR1","identity_sheet_asset_id":"IDENTITY1"}],
  "storyboard": {"panels":[{"id":"P1","shot_id":"SH1","beat_ids":["B1"]}]},
  "asset_registry": ["a real verified IDENTITY1 pin, expressed as an asset record"]
}
```

Use `derive_coverage` to assign all resulting requirements to one clip, with `assets=()`, then call `verify_scope`. **It returns normally**, despite the registered required identity asset being omitted. The quoted array entry above describes the full asset object used in execution, not literal input accepted by the parser.

**Impact:** R02/R10's completeness seam does not preserve a real, existing dependency path; R04 cannot require a native binding for an identity already discarded by the adapter. This is a structural omission, not a demand that software recognize faces.

**Minimal fix:** Retain and resolve the existing character-to-identity relation when deriving mandatory asset uses, preferably reusing the established upstream closure contract. Ensure any generated coverage envelope preserves those mandatory uses rather than emitting only requirement IDs (`production/cli.py:61–65` currently emits only requirements). Add a representative upstream fixture that omits the character identity from the batch and must fail before preparation. Check the other existing dependency paths, such as panel asset-version references, when defining the supported projection; do not silently claim full closure for an incomplete projection.

### F3 — Important: approval cannot bind the requested duration or output format

**Locations:** `production/models.py:187–199`, `production/bindings.py:16–29`.

`Authority` can constrain clip IDs, account/model/transport/mode, hashes, and counts, but has no approved duration, dimensions/aspect ratio, audio setting, scope/configuration fingerprint, or equivalent setting constraint. Preparation checks duration only against the supplied capability, not the approval. The approval evidence file is hash-checked but its contents are not interpreted.

**Executed reproducer:** Starting with the standard 2-second fixture approval, change C1 to 20 seconds and supply a capability supporting `(2,20)` with dimensions changed from 1280×720 to 720×1280. Keep the exact same `Authority`, approval evidence pin, prompt, assets, and allowed hashes. `prepare_request` succeeds:

```text
{"same_authority":true,"duration":20.0,"resolution":[720,1280]}
```

This is not a claim that the fixture authorized any actual external operation. It demonstrates that the local contract cannot express or reject a narrower real approval.

**Impact:** R04's authority comparison cannot satisfy design 01 §5, which explicitly requires approval of length/aspect/settings. A newly valid request hash protects against changing one prepared packet, but does not prevent preparing a different configuration under the same insufficiently scoped approval.

**Minimal fix:** Bind approval to the approved per-clip configuration or equivalent explicit setting constraints, including relevant scope and reference-transfer scope, then check it in both preparation and reservation. Add negative tests showing duration/aspect changes require refreshed approval. Do not infer approval from model capability.

### F4 — Important: acceptance ignores drift in pinned approval evidence

**Locations:** `production/quality.py:13–31,57–63`; compare `production/bindings.py:28–29`.

Preparation/reservation verifies approval evidence, but QA commit does not verify the successful attempt's authority evidence or obtain a current approval binding. Its fingerprint excludes authority. `ProjectStore` only calls `verify_scope` at publication, which also does not inspect approval evidence. Consequently approval pin drift between submission and acceptance is not detected at the current-validity boundary.

**Executed reproducer:** Use `tests/test_quality.py::candidate` to create an actually decodable candidate and fixture successful receipt; overwrite `root / authority.evidence.path` with `APPROVAL REVOKED / REPLACED`; call `accept_take(state,take,review,take.fingerprint,root)`. Observed:

```text
QA accepted = accepted
```

The original authority SHA no longer matches the on-disk file. Remote history must remain historical, but this is not a valid current approval check.

**Impact:** R07/R08's commit gate omits the design 03 §3a requirement to compare current design/authority validity immediately before acceptance. Detecting byte drift in an explicitly pinned local approval artifact is within scope; authenticating who revoked it is not required to detect this mismatch.

**Minimal fix:** Before publishing current acceptance, validate the applicable approval pin/current approval revision under the same transaction. On mismatch preserve remote facts and leave the candidate non-current pending explicit revalidation/approval. Add both initial-admission and revalidation tests. Preserve historical request data rather than rewriting it to the new approval.

### F5 — Important: the acceptance map reports several different scenarios as the specified cases

**Locations:** `docs/acceptance-map.json:5–11,23,28–30`; relevant assertions in `tests/test_bindings.py:55–62`, `tests/test_quality.py:83–89`, `tests/test_handoff.py:52–59`, and `tests/test_revisions.py:14–24`.

The runner really executes pytest nodes, but node existence/execution does not establish scenario fidelity. Concrete mismatches include:

- **T05:** The mapped test has no accepted predecessor and stops at `dependency`; it does not exercise an otherwise-ready request whose required video role/modality is unsupported. Removing the subsequent video-support check would not make this mapped T05 test fail.
- **T10:** The mapped test is reaction-first reveal order, not an approved `time_elision` with changed prop state. It is also reused for T31. No mapped assertion exercises T10's allowed state change.
- **T27:** The two mapped tests separately change a global scope before admission and replace a synthetic selected source. They do not run the specified linked attempt while its consumed source changes and then deliver its late remote success.
- **T29:** The mapped test covers range change only, not the specified imports/conditional acceptance changes.
- **T22:** The test checks request `excludes` preservation, not the reported-result contract for unwanted action/dialogue repetition. A fixture semantic report would be an acceptable local test; it is not necessary or authorized to perform actual perceptual QA here.

**Impact:** R11 is only partially met. The output's 34 `passed` labels overstate the scenarios actually exercised, despite correctly disclosing that semantics are fixtures. These gaps help explain why the additional boundary failures above coexist with a green acceptance result.

**Minimal fix:** Add focused, executable fixture-level tests for the missing local scenarios and map each T ID to its actual scenario. Separate structural coverage from reported semantic-contract coverage and genuinely out-of-scope perceptual validation. Include regressions for F1–F4. Do not substitute live generation or real artistic QA for this local test work.

## Per-rubric assessment

| Rubric | Assessment | Independent evidence |
|---|---|---|
| R01 — five roles/package | PASS, scoped | Five skill files have role inputs/outputs and ownership boundaries; invocation is disabled. Package checker reports `skills:5, findings:[]`. All ten supplied schemas match runtime schemas (seven in checker, three independently compared). This is not behavioral certification. |
| R02 — approved coverage | REVISE | Existing shot/panel/beat/speech/cue omissions and reduced denominator tests pass. Mandatory identity closure can be discarded before that comparison: F2. Existing suite has no positive approved pre-existing-source reuse/exclusion workflow proving the full wording of R02. |
| R03 — references/DAG/order | PASS, scoped | Four dependency tests pass; code validates sources/imports, detects cycles, separates edit order from reference readiness, and requires omitted optional-reference rationale. Two-history-source preparation is exercised. No live conditioning claim accepted. |
| R04 — native binding/authority | REVISE | Thirteen binding tests and the CLI preserve distinct native IDs, source/range/revisions/imports/excludes and enforce allowlisted hashes. F2/F3 leave required identity and setting approval gaps. |
| R05 — attempts/slots/duplicates | PASS, scoped | Nine execution tests pass; reservation precedes observation, unknown remains active, known terminal receipts free remote slots, external occupancy is counted, unknown occupancy blocks, duplicate attempts and mismatched request/job receipts fail. These are supplied-receipt contracts, not provider exactly-once guarantees. |
| R06 — persistence/restart | PASS, scoped | Ten recovery tests pass; real flock contention/restart and failed `os.replace` are exercised. Existing ledger fields survive. Concurrent noncooperating legacy writes remain unsupported and documented; no claim of arbitrary-writer safety accepted. |
| R07 — revisions/CAS/stale | REVISE | Three revision tests plus QA/recovery checks demonstrate range fingerprints, conservative descendant invalidation, independent-node preservation, and revision CAS. Current authority validity is missing at admission: F4. T27–T29 coverage is incomplete: F5. |
| R08 — G0–G5/QA | REVISE | Fourteen quality tests really decode/probe local fixtures and reject missing playback/audio/requirements, metadata mismatch, unsupported timing, short ranges, and invalid conditional admission. These gates still accept stale approval evidence: F4. Semantic observations remain fixture assertions, not machine perception. |
| R09 — full flow/handoff/progress | REVISE | Ten handoff tests and the complete CLI integration exercise required reports, exact take/range revisions, real montage lineage, zero certified handles and separate conditional accounting. F1 permits a G5 success when delivered source bytes are absent. |
| R10 — existing seams | REVISE | Nine adapter tests pass, including the real preproduction Ledger and existing `prepare_generation_request.audit_call` in temporary/offline use. Upstream identity closure is incomplete: F2. The real auditor test does not prove provider connectivity. |
| R11 — 34 cases/integration | REVISE | Runner executes 33 distinct cases for T01–T34; full suite is 87 passing; type check is clean. Several mappings are not the specified scenarios: F5. Green output is not sufficient evidence of full acceptance. |

### Additional revalidation observation

A local experiment also showed that, after invalidating required source C1 and its consumer C3, `revalidate_take(C3, ..., fingerprint(current_state,"C3"))` can restore C3 to current acceptance while C1 remains invalid; a further C3 consumer can then become ready. The function checks the new fingerprint and a supplied full review, but does not require usable upstream selections. I have **not used this alone as a blocking finding**: the design allows explicitly reviewed retention of stale results, and retention may legitimately establish that the upstream defect did not propagate. This policy should be made explicit and tested with an affected-import case versus an unaffected-import case; it must not be confused with permission to submit a new dependent generation from invalid required inputs.

## Validation performed

| Command/check | Result |
|---|---|
| `sha256sum qa/implementation/review-scope.sha256` before/after | Exact supplied hash both times |
| `sha256sum -c qa/implementation/review-scope.sha256` before/after | 60/60 OK both times |
| `python3 -m pytest -q` | **87 passed in 17.34s** |
| `python3 scripts/check_package.py --json` | Five skills, no findings |
| `python3 scripts/check_acceptance.py --json` | `valid:true`, 34 mapped IDs, 33 executed cases; scenario-fidelity reservations above |
| `basedpyright production` | 0 errors, 0 warnings, 0 notes |
| Independent equality checks for Authority/Capability/Bindings JSON Schemas | All three match runtime |
| Five temporary-project adversarial Python checks described in F1–F4/additional observation | All reproduced the described current behavior; no project-source edits |
| Recorded protected-input hashes against current files | All three match the recorded baseline |

### Reproduction setup

The adversarial checks ran as inline `python3` commands from this package root, used `tempfile.TemporaryDirectory`, and imported existing fixture helpers without creating or editing test files:

```python
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "tests")
import conftest

# For each independent temporary case:
root = Path(temp_directory)
seed = conftest.seed.__wrapped__(root)
capability = conftest.capability.__wrapped__(root)
authority = conftest.authority.__wrapped__(root, seed)
```

Specific repeatable steps:

- **F1:** `test_handoff.all_selected(seed,root)`; replace its three source pins with `test_media.make_video` outputs and update playback hashes; set `joins_for(state)`; call `render_review(state,root,"qa/review.mp4")`; use its proof in `flow_for(state)`; initialize a clean store and persist the test state via `transaction(0)`; unlink the first source; call `test_cli.cli("handoff",ledger,flow_file,"post","rights-fixture")`. Expected safe behavior is a nonzero blocked result; observed result was exit 0 and three delivered records.
- **F2:** Use `conftest.pin` for the identity, prompt, and project JSON described above; derive coverage; build a one-clip State assigning every requirement but with `assets=()`; `verify_scope(state,root)` incorrectly succeeds.
- **F3:** Set `seed.batch.clips[0].duration_s=20` using immutable copies and set capability `durations=(2,20), width=720, height=1280`; call `prepare_request(changed_state,"C1",changed_capability,authority,(test_bindings.native(seed),),root)`. The same authority succeeds.
- **F4:** `state,take,review=test_quality.candidate(seed,capability,authority,root)`; overwrite `root/authority.evidence.path`; call `accept_take(state,take,review,take.fingerprint,root)`. It returns an accepted selection rather than blocking on the stale pin.
- The revalidation experiment admitted real temporary C1/C3 media via preparation, reservation, successful fixture receipts and `accept_take`, then called `invalidate_selection(C1,...)` and `revalidate_take(C3,...)`. Observed C1 invalid/C3 current; this is separated from the definite findings above.

## Constraints verdict and residual limitations

- **Review mutation/execution constraints: PASS.** No install, Git command, commit/staging, provider call, external service, external asset transfer, deployment, publication, delegation, or child launch was performed. The directory has no `.git`; no staged files were created.
- Standard test caches/artifacts were allowed. Running the requested acceptance checker regenerated `qa/implementation/acceptance-{junit.xml,pytest.txt,results.json}`. The checked source snapshot remained unchanged.
- All three recorded protected input files currently match their baseline SHA-256 values. This verifies those named files, not an independent historical audit of every earlier implementer action or every upstream project.
- **Product safety/completion constraints: REVISE.** Unknown and ordinary stale accounting are conservative, but current authority and actual G5 source availability are not fully enforced (F1/F4); mandatory upstream input preservation is incomplete (F2).
- Provider receipts/native IDs, rights, receiving declarations, and semantic playback observations are operator-supplied evidence. Their authenticity is not certified by this offline package or this review.
- The real ffprobe/full decode/render checks establish technical local-media behavior only. No live provider success, actual watching/listening, artistic quality, installation, release, or operational deployment is certified.
- Complete positive workflows for approved reuse/exclusions, explicit retry rationale, nonzero reviewed handles, mixed-format/VFR conform, or concurrent legacy writers were not established. Some are explicitly unsupported; they must not be promoted to demonstrated outcomes.
- Reviewer made no implementation changes. Recommended next step: parent addresses F1–F5 with focused local regressions, reruns checks, and obtains authorized review of the resulting new snapshot. Do not mark 100% or reuse this snapshot's review as a future PASS.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed the requested independent read-only review without implementation, installation, external service calls, Git work, or delegation; wrote only the routed report plus allowed generated test artifacts. Product verdict is REVISE."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Report provides five actionable findings with exact source ranges, executed reproduction steps/results, minimal fixes, R01-R11 assessments, command results, constraints and before/after snapshot verification."
    }
  ],
  "changedFiles": [
    "/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/0e76a4e7-5dcc-444c-b7c0-43f36b69fc76/reviews/production-implementation-final-review.md",
    "qa/implementation/acceptance-junit.xml (generated check output)",
    "qa/implementation/acceptance-pytest.txt (regenerated check output)",
    "qa/implementation/acceptance-results.json (regenerated check output)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {"command":"sha256sum qa/implementation/review-scope.sha256; sha256sum -c qa/implementation/review-scope.sha256 (before and after)","result":"passed","summary":"Supplied manifest hash matches; all 60 source entries unchanged before and after."},
    {"command":"python3 -m pytest -q","result":"passed","summary":"87 passed in 17.34s."},
    {"command":"python3 scripts/check_package.py --json","result":"passed","summary":"Five skills, findings []."},
    {"command":"python3 scripts/check_acceptance.py --json","result":"passed","summary":"34 mapped IDs, 33 executed cases; scenario fidelity is qualified in F5."},
    {"command":"basedpyright production","result":"passed","summary":"0 errors, 0 warnings, 0 notes."},
    {"command":"Inline temporary-project adversarial checks and schema/protected-input hash comparisons","result":"passed","summary":"Executed safely; reproduced F1-F4 behavior and the separately qualified revalidation observation. Schema and protected-input comparisons matched."}
  ],
  "validationOutput": [
    "Verdict: REVISE; F1 missing-source handoff, F2 dropped upstream identity dependency, F3 unbound approval settings, F4 stale approval accepted, F5 acceptance scenario mismatches.",
    "Snapshot manifest SHA256: 281401bf4972cb5fb12495d66a905a3ac055404e70da6ec2dd5ee40d0c9dff5e; 60/60 entries OK before and after."
  ],
  "residualRisks": [
    "Five important implementation/evidence findings remain; no implementation fixes were made.",
    "Provider and semantic receipts are fixtures/operator assertions, not live provider or perceptual QA certification.",
    "Non-Git project: no staging/commit operation was performed; source snapshot, not Git diff, establishes preservation."
  ],
  "noStagedFiles": true,
  "diffSummary": "Read-only implementation review; only routed report and allowed generated check artifacts, no checked source changes.",
  "reviewFindings": [
    "blocker: production/cli.py:146-152 and production/render.py:98-107 - missing source media can pass G5 handoff",
    "blocker: production/adapters.py:55-84,132-156 - required upstream character identity dependency discarded",
    "important: production/models.py:187-199 and production/bindings.py:16-29 - authority cannot constrain approved duration/output format",
    "important: production/quality.py:13-31,57-63 - acceptance ignores approval evidence hash drift",
    "important: docs/acceptance-map.json:5-11,23,28-30 - scenario mappings overstate executed acceptance coverage"
  ],
  "manualNotes": "Acceptance statuses above describe completion of this review assignment, not acceptance of the implementation. The implementation verdict is REVISE. No new tests or source edits were authorized or made."
}
```
