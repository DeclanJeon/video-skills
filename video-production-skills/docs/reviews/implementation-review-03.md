# Independent implementation re-review 03

## Scoped verdict: REVISE

**N1 and the original N2 reproductions are fixed. One important residual defect remains in consumed-reference revalidation (N3): an actually selected optional source can become unusable, yet its consumer can be restored to current acceptance while skipping both source-file and source-approval checks.** This also permits a conditional defect affecting an imported attribute to bypass the stated retention policy.

This verdict concerns the accepted goal's local implementation, not an imagined live provider. No provider connection, genuine watching/listening, artistic-quality certification, installation or deployment is required or certified here. The goal/R12 was not edited.

## 1. Checked revision and scope

Project: `/home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-production-skills`.

| Checked input | Before review | After review |
|---|---|---|
| `qa/implementation/review-scope.sha256` SHA-256 | `06562c806b58c9389f18abe5f1ead80f28949205f015e8cd18a2e16073bee1b7` | Identical |
| Current source/spec manifest verification | **75/75 OK** | **75/75 OK** |
| Active goal SHA-256 | `46699997c3c1d50fc4798f66248f1d6685f0da3be0adb96216a40f1f5b28d2e4` | Identical |
| Frozen `qa/implementation/review-goal-03.md` SHA-256 | `46699997c3c1d50fc4798f66248f1d6685f0da3be0adb96216a40f1f5b28d2e4` | Identical |
| Archived `review-scope-02.sha256` file SHA-256 | `e8c69e74a078ec0b25a5b6f13b68946023298a4ef17a016137795d8f76c23928` | Identical |

The archive's file hash was verified; its historical entries are **not** claimed to match intentionally revised sources.

Continued as the same authorized independent reviewer. Read the goal and remediation 02 rather than trusting checkboxes. Reviewed current recovery/adoption code, new and modified tests, operations/design recovery contract, changed skill instructions and schema changes; compared current/prior manifests and retained the previous whole-package review context for unchanged files. Rechecked approval, binding, DAG/fingerprint, scope amendment and G5 code in addition to the newly changed seams. All 75 declared files, including six design documents, remained frozen during review.

## 2. N1/N2 disposition and prior fixes

### N1 — Historical observations blocked by missing current inputs: resolved

`production/store.py:153–181` implements a narrow `record_observation(attempt_id, receipt, expected_revision)` route. It accepts neither a replacement State nor a callback/skip-validation flag. It retains model validation, lock/CAS, original packet digest, receipt request/job matching and lifecycle checks. The fact is published and fsynced before mutable-input diagnostics; a second publication records diagnostics. A failed second publication cannot undo the first saved job ID.

Evidence independently checked:

- The original input-loss reproduction now saves a recovered terminal job ID successfully while current preparation remains blocked.
- Seventeen observation-recovery cases cover acknowledgement/terminal facts under missing/hash-changed inputs, unrelated dependency and missing coverage; other unknown reservations remain occupied.
- Real filesystem tests cover interrupted diagnostics, failure of the second `os.replace`, and a detected noncooperating writer update without clobbering that update.
- Wrong request, stale revision, corrupt recorded packet and known-job/nonreceipt contradictions are rejected. The historical endpoint refuses local submitting/downloaded claims.
- `status`/`read_recorded` expose recorded identities, not new-submission permission; ordinary reserve/adoption/handoff gates remain separate.
- Recovered first running/terminal receipts can skip unobserved intermediate statuses without inventing those events.
- Self-pinned mutable coverage/origin storage is rejected by initialization and checked ordinary publication.

The two-publication revision behavior and error recovery via status are documented. No unresolved important N1 issue was found in this pass.

### N2 — Initial generated admission omitted consumed-source checks: original failure resolved, related gap N3 remains

`production/quality.py:36–44` now supplies the original prepared bindings to `_sources_current` during generated admission. With distinct candidate/source approval files, required and actually selected optional source **byte/approval drift** is rejected; an explicitly justified optional history not selected in the request remains omittable. All six new consumed-approval cases pass. Independently reran the previous distinct-upstream-approval reproduction and observed the expected `hash` blocker.

However, the new helper's treatment of an **unusable** selected optional source differs from its treatment of a usable source with drifted bytes. That is N3 below; the initial N2 negative tests do not exercise it because their source selection stays usable.

### Earlier F1–F5 fixes

The previously reviewed G5 source-pin checks, upstream closure/export preservation, explicit ApprovedConfig, own-approval checks, corrected T-case mappings, reuse/scope paths and namespaced reference keys remain in place. Their regressions pass in the current full run. No need for external execution or blanket dependency uploads was inferred. The remaining actionable issue is N3, not a reversal of those earlier corrections.

## 3. N3 — Important: a chosen optional source can bypass currentness and pin checks during revalidation

**Locations:**

- `production/quality.py:12–23`, particularly line 19 and the guarded file checks at lines 21–23.
- The generated revalidation path at `production/quality.py:36–44,108–113`.
- Contract contradicted: `docs/operations.md:49–51` and `take-reviewer/SKILL.md` step 5 explicitly require current source media/approval/decision checks for actually selected optional history, distinct from unconsumed optional history.

### Cause

The helper correctly computes `bound` and only skips a justified optional reference if it was not bound. But once a selected optional reference reaches the validation body:

```python
if not (current and usable(source, ref.imports)) and (ref.required or not ref.omission_evidence):
    raise ContractError(...)
if source is not None and usable(source, ref.imports):
    verified_file(...source.take.asset...)
    verified_file(...source.approval.evidence...)
```

`bound` is missing from the refusal condition. For an optional reference with omission evidence, an invalid/rejected/import-incompatible source therefore does not raise. Because it is unusable, the subsequent media/approval checks are skipped too. During explicit revalidation, the caller can provide the new fingerprint, and the consumer is restored to current acceptance.

This is not a demand to make every declared optional reference mandatory. The request in the reproduction **actually selected the source**; the historical binding remains unchanged. The correct positive path is the already tested genuinely unselected optional source.

### Executed public-CLI reproduction

1. Use the existing `linked_running(..., separate_approval=True, optional_reference=True)` helper to prepare/reserve C3 with a real selected C1 history binding and a distinct valid C3 approval.
2. Record synthetic C3 success and admit its real local decoded media normally.
3. Persist the state, then invoke the actual `invalidate` CLI on C1 with a reported defect affecting imported identity/pose. This correctly invalidates C1 and C3.
4. Delete C1's original media and its approval evidence file. C3's own media and approval stay unchanged.
5. Invoke the actual `revalidate` CLI on C3 with its reported review and the current fingerprint.

Observed:

```json
{
  "exit": 0,
  "response": {"revalidated":"C3"},
  "source_valid": false,
  "source_media_exists": false,
  "source_approval_exists": false,
  "consumer_current": true,
  "progress": {
    "required":3,
    "accepted":1,
    "conditional":0,
    "coverage_required":3,
    "coverage_fulfilled":1,
    "joins_required":2,
    "joins_passed":0
  }
}
```

The same required-reference control case correctly blocks with `dependency`.

### Additional conditional/import reproduction

Without deleting any files, explicitly re-review C1 through `revalidate_take` as conditional with defect `pose`, valid post-fix/receiver/policy fields, while C3's selected optional binding imports `("identity","pose")`. The source's current conditional decision is thus **not usable for these imports**. Revalidate C3 with the current fingerprint.

Observed:

```json
{
  "chosen_optional":true,
  "imports":["identity","pose"],
  "source_defects":["pose"],
  "source_usable_for_imports":false,
  "consumer_revalidated":true
}
```

This contrasts with the intended positive case: a valid conditional source whose unrelated background defect does not affect the imported attributes.

### Impact and minimal fix

- R07/R08: unresolved/import-incompatible consumed history is restored as current consumer acceptance.
- R09 accounting inherits the incorrect current selection: the public progress command counts it accepted, as shown above. This is not a claim that the entire batch's G5 passed in this reproduction.
- Historical remote facts are not the issue; they should remain unchanged.

**Minimal correction:** Once the helper determines a reference must be checked—required, actually bound, or lacking a justified omission—require both currentness and `usable(source, imports)` before proceeding to its pin checks. An actually bound optional source must not fall through the unusable-source branch. Keep the existing unselected-optional positive path and unaffected-conditional positive path. If changing a retained result to a new omission contract is desired, it must be an explicit reviewed/current binding rather than silently treating an old selected input as unselected.

Add regressions for:

1. Selected optional source invalidated, with missing media/approval: CLI revalidation blocks and consumer stays non-current.
2. Selected optional conditional source with defect intersecting imports: revalidation blocks.
3. Required invalid source still blocks; genuinely unselected optional and unaffected conditional sources still retain the existing allowed behavior.

No source fix or new test file was made by this reviewer.

### Compact repeatable harness

Run from the package root; all writes are to a temporary project. Provider/semantic evidence remains fixture data, while the helper creates actual local technical video.

```python
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "tests")
import conftest
from test_quality import linked_running
from test_cli import cli
from production.models import Phase, Receipt
from production.execution import observe
from production.quality import accept_take
from production.contracts import fingerprint
from production.store import ProjectStore

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    seed = conftest.seed.__wrapped__(root)
    cap = conftest.capability.__wrapped__(root)
    auth = conftest.authority.__wrapped__(root, seed, cap)
    state, source, take, review, packet = linked_running(
        seed, cap, auth, root,
        separate_approval=True, optional_reference=True)
    assert any(b.source_clip == "C1" for b in packet.bindings)
    state = observe(state, "ATT-C3", Receipt(
        phase=Phase.SUCCEEDED, job_id="fixture-C3",
        evidence="synthetic successful receipt",
        request_hash=packet.request_hash))
    state = accept_take(state, take, review, take.fingerprint, root)
    store = ProjectStore(root / "ledger.json")
    initial = state.model_copy(update={
        "attempts":(), "selections":(), "history":(),
        "join_reviews":(), "revision":0})
    store.initialize(initial)
    with store.transaction(0) as tx:
        tx.state = state
    assert cli("invalidate", root/"ledger.json", "C1",
               "reported defect affects imported identity/pose", 1).returncode == 0
    (root/source.take.asset.path).unlink()
    (root/source.approval.evidence.path).unlink()
    report = root/"review.json"
    report.write_text(review.model_dump_json())
    result = cli("revalidate", root/"ledger.json", "C3", report,
                 fingerprint(store.read(), "C3"), 2)
    print(result.returncode, result.stdout)  # Currently 0 / revalidated.
    print(cli("progress", root/"ledger.json").stdout)  # Accepted count is 1.
```

## 4. R01–R11 assessment

| Rubric | Assessment | Current evidence |
|---|---|---|
| R01 — skills/package | **PASS, metadata scope** | Five roles, disabled automatic/external execution, linked contracts and 12 public schemas pass checker. Documented examples independently initialize/validate/prepare offline in a temporary project. No agent-behavior certification. |
| R02 — coverage/reuse/scope | **PASS, local contract scope** | Existing coverage, full supported upstream closure/export, explicit local reuse and exact approved scope amendment regressions pass. Unknown history/slot preservation remains intact. Original upstream validation is still required as documented. |
| R03 — DAG/order/multi-reference | **PASS for scheduling/preparation** | Cycle/dangling/optional-rationale and independent-node tests pass. Multiple source roles and tuple-key collision negatives remain valid. N3 concerns subsequent retained acceptance, not a new generation request. |
| R04 — native binding/authority | **PASS for scoped request preparation** | Exact source/range/revisions/imports/excludes/native readiness and transfer hashes; explicit clip/configuration/output approvals remain enforced. Unsupported video/role and over-limit negatives execute. No live conditioning proof. |
| R05 — lifecycle/slots | **PASS** | Eleven execution cases plus historical-observation tests; exact request/job/digest checks, unknown reservation, terminal release, external occupancy and recovered statuses remain conservative. |
| R06 — persistence/recovery | **PASS, cooperating-writer contract** | Twelve recovery and seventeen observation cases; fact-first durability, diagnostic interruptions/second-write failure, actual lock/CAS/restart/conflict and immutable source/origin rules. N1 reproduction independently fixed. No arbitrary noncooperating-writer or remote exactly-once guarantee. |
| R07 — revisions/currentness | **REVISE** | Existing range/import/acceptance fingerprints, running-source replacement and CAS tests pass. N3 restores a consumer against unusable actually consumed optional history. |
| R08 — QA/conditional adoption | **REVISE** | Real technical decode, reported semantic/narrative checks and six distinct consumed-approval cases pass. N3 bypasses the conditional import/currentness rule during retention. |
| R09 — delivery/progress | **REVISE through N3 accounting** | Own G5 source/approval/flow/coverage checks and actual CLI missing/replaced-source negatives remain effective. Public progress nonetheless counts N3's incorrectly restored consumer accepted; do not infer valid completion from it. |
| R10 — existing seams | **PASS, local adapters only** | Existing Ledger, request auditor and representative project_index closure tests pass without provider calls; all three protected upstream source hashes match recorded baseline. |
| R11 — acceptance trace/integration | **PASS for mapped scenarios; not exhaustive correctness** | T01–T34 execute as 42 cases with structural/reported-semantic classifications. Full suite 146 passes and type check clean. Those scenarios omit N3; green execution cannot override the adversarial result. |

R12 remains the parent's responsibility. This review supplies **REVISE**, not permission to mark independent final acceptance or 100%.

## 5. Commands and actual results

| Command/check | Independent result |
|---|---|
| `sha256sum -c qa/implementation/review-scope.sha256` before/after | **75/75 OK** each time |
| Manifest/archive/goal/frozen-goal SHA-256 before/after | Exact supplied values, unchanged |
| `python3 -m pytest -q` | **146 passed in 32.56s** |
| `python3 -m pytest -q tests/test_execution.py tests/test_observation_recovery.py tests/test_consumed_approval.py tests/test_recovery.py` | **46 passed in 10.52s** |
| `basedpyright production` | **0 errors, 0 warnings, 0 notes** |
| `python3 scripts/check_package.py --json` | **5 skills; findings []** |
| `python3 scripts/check_acceptance.py --json` | **valid true; 34 IDs; 42 executed cases**; live/perceptual flags false |
| Original N1 temporary recovery reproduction | Known terminal ID saved with input deleted; readiness remains false |
| Original N2 temporary distinct-source approval reproduction | Correctly blocked by hash check |
| New chosen-optional retention reproductions | Defect reproduced through real CLI and conditional/import API path |
| Documented examples in temporary project | init, validate, prepare all pass; no submission |
| Three protected originals against baseline | All hashes match |

The adversarial commands ran successfully as reproductions; the observed N3 behavior is a failed implementation invariant, not a passing product assertion.

## 6. Constraints and limitations

**Reviewer constraints: PASS.** Same reviewer, same goal; no children, delegation or restarted workflows. No implementation/source/doc/goal/test/schema/fixture edits, installation, Git command/staging/commit, network/provider call, external asset transfer, paid or provider media generation, deployment or publication. Temporary local technical media/projects, standard caches and the allowed checker's generated `qa/implementation/acceptance-{junit.xml,pytest.txt,results.json}` outputs were used. Only this report was written to the authoritative routed output location. Checked source/spec and frozen/current goal hashes remained unchanged.

**Implementation completion/currentness constraint: REVISE.** Unknown remote facts and slots remain conservative, but N3 can count an incorrectly restored current consumer. Earlier reports remain preserved; no prior REVISE was rewritten into a PASS.

Approval/rights/receiving/semantic observations remain supplied assertions. Byte pins and typed grants establish local consistency, **not authentic issuer consent, actual provider success, watching/listening or artistic fidelity**. Technical ffprobe/full-decode/render output is real but local and non-perceptual. Unsupported nonzero reviewed handles, mixed-format/VFR conform and concurrent legacy writes must remain explicit limitations. No installation/release/deployment readiness is certified.

**Recommended next step:** Correct the narrow selected-optional refusal condition and add the N3 negative/positive retention regressions; rerun checks and obtain an authorized continuation review of a new frozen snapshot. The reviewer made no implementation changes and did not update the goal.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed the same authorized independent reviewer's read-only re-review; no implementation, external actions or delegation. Scoped implementation verdict is REVISE."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Report includes N1/N2 dispositions, one important residual defect with exact ranges and executed reproductions/minimal fix, R01-R11 assessments, commands, constraints and before/after snapshot/goal hashes."
    }
  ],
  "changedFiles": [
    "/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/222157d0-3bfe-4594-a855-da9a27552d3d/reviews/production-implementation-final-review-03.md",
    "qa/implementation/acceptance-junit.xml (generated output)",
    "qa/implementation/acceptance-pytest.txt (regenerated output)",
    "qa/implementation/acceptance-results.json (regenerated output)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {"command":"sha256sum supplied manifests and goals; sha256sum -c qa/implementation/review-scope.sha256 before/after","result":"passed","summary":"All supplied hashes match; 75/75 current files unchanged."},
    {"command":"python3 -m pytest -q","result":"passed","summary":"146 passed in 32.56s."},
    {"command":"python3 -m pytest -q tests/test_execution.py tests/test_observation_recovery.py tests/test_consumed_approval.py tests/test_recovery.py","result":"passed","summary":"46 passed in 10.52s."},
    {"command":"basedpyright production","result":"passed","summary":"0 errors, 0 warnings, 0 notes."},
    {"command":"python3 scripts/check_package.py --json","result":"passed","summary":"Five skills, findings []."},
    {"command":"python3 scripts/check_acceptance.py --json","result":"passed","summary":"34 mapped IDs, 42 cases; live/perceptual verification false."},
    {"command":"Inline temporary-project original/new boundary reproductions, example smoke and protected-input comparisons","result":"passed","summary":"N1/original N2 fixed; N3 reproduced; examples pass; all three protected hashes match."}
  ],
  "validationOutput": [
    "REVISE: selected optional history can become unusable and skip its currentness/media/approval checks during explicit consumer revalidation.",
    "Manifest SHA256 06562c806b58c9389f18abe5f1ead80f28949205f015e8cd18a2e16073bee1b7; 75/75 OK before and after.",
    "Goal/frozen-goal SHA256 46699997c3c1d50fc4798f66248f1d6685f0da3be0adb96216a40f1f5b28d2e4, unchanged."
  ],
  "residualRisks": [
    "One important N3 adoption/currentness defect remains; no source fix was made.",
    "No provider/perceptual/approval-authenticity/installation/deployment certification."
  ],
  "noStagedFiles": true,
  "diffSummary": "Routed report and permitted generated QA artifacts only; checked sources/spec/goal unchanged.",
  "reviewFindings": [
    "important: production/quality.py:12-23,36-44 - selected optional unusable source skips refusal and both pin checks during consumer revalidation"
  ],
  "manualNotes": "Acceptance statuses describe completion of the review assignment, not implementation acceptance. Parent alone may update the goal/R12; this snapshot remains REVISE."
}
```
