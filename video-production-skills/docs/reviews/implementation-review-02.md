# Independent implementation re-review 02

## Verdict: REVISE

The first-pass fixes are substantial and mostly effective. F1, F2, F3 and F5 are resolved for the explicitly scoped local contracts. **F4 remains incomplete for consumed upstream approvals, and a separate important recovery defect prevents durable remote observations when local inputs become unavailable.** These two actionable findings prevent final PASS/R12 completion.

This review does not require live providers, genuine perceptual QA, installation, or deployment. None was performed or accepted as proven. All provider/semantic receipts below remain synthetic; technical decoding/rendering and filesystem operations were real local operations.

## 1. Snapshot and independence

Project: `/home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/video-production-skills`.

| Item | Before | After |
|---|---|---|
| Current `qa/implementation/review-scope.sha256` SHA-256 | `e8c69e74a078ec0b25a5b6f13b68946023298a4ef17a016137795d8f76c23928` | Same |
| Current manifest entries | **67/67 OK** | **67/67 OK** |
| Archived `review-scope-01.sha256` manifest SHA-256 | `281401bf4972cb5fb12495d66a905a3ac055404e70da6ec2dd5ee40d0c9dff5e` | Same |
| Active goal SHA-256 | `87ec1c8879ac43673def29870ff24d643a7d687d4d0ef9acda41b32111a18f3d` | Same |

The archived manifest's **file hash** was checked; its original entries are not claimed to match the intentionally revised implementation. The active goal was read, not accepted from its checkboxes. Its active status and unchecked R12 remain appropriate.

Reviewed the previous report and remediation disposition, goal, design 00–05, README, operations, five skills, manifest, all current production modules and tests, check scripts, acceptance map, examples and schema/runtime checks. Compared old/current manifest entries to identify new and changed seams. No children or prior workflows were started. No implementation/source/doc/goal/schema edits were made.

## 2. First-pass finding dispositions

| Finding | Disposition | Evidence from actual code and rerun tests |
|---|---|---|
| **F1: missing/replaced original media could pass G5** | **Resolved** | `production/handoff.py:75–86` now requires root, rechecks scope, every delivered source pin and selection approval evidence. CLI supplies root. Parameterized library regressions reject deletion/replacement; actual CLI regressions render real media first, then reject both mutations. Existing montage does not excuse missing originals. |
| **F2: character identity closure silently discarded** | **Resolved for supported projection** | `production/upstream.py` retains character IDs, identity/SSOT, panel pins/images/sheets, LOOK, voice/spatial, cue/caption and source/master/artifact closure. `export_coverage` preserves asset uses and origin; `verify_scope` checks origin equivalence and mandatory local pins. Actual existing `project_index.build_index` is compared on a representative project. Conflicting panel versions and missing identities fail. `Clip.dependencies` preserves local lineage without treating the whole closure as an upload grant, as explicitly approved in the goal. |
| **F3: duration/output approval not representable** | **Resolved** | `ApprovedConfig`, `clip_configuration_hash` and `validate_config` bind source/scope/configuration, duration, dimensions and requested audio. Preparation/reservation use these checks. Duration/aspect/scope regression negatives pass. Capability is no longer treated as setting consent. |
| **F4: approval evidence drift ignored by acceptance** | **Partially resolved; remains important** | Own-candidate approval evidence is now checked on initial admission and revalidation, and explicit new approval can bind retained output without rewriting the old request. However, the generated initial-admission branch omits the consumed-source checks used by reuse and revalidation. Separate upstream approval drift still permits current acceptance: **N2 below**. |
| **F5: scenario mapping overclaimed several T cases** | **Resolved for local scenario fidelity** | T05 now reaches role/modality refusal with an accepted predecessor; T10 has approved/unapproved time-elision prop changes; T22 adds reported repetition rejection; T27 runs a dependent job, replaces its source, then supplies late success; T29 separately covers range/imports/conditional acceptance. Runner executes 42 cases for 34 IDs and classifies structural versus reported-semantic evidence; live/perceptual verification flags remain false. |

### Previously qualified revalidation policy

The goal now explicitly chooses a policy: unresolved required upstream sources block retention; an unaffected conditional source can permit retention after explicit review. `revalidate_take` calls `_sources_current`; its two new negative/positive tests exercise that distinction. That resolves the policy ambiguity noted in report 01. It does **not** resolve N2's different initial-admission path.

## 3. Remaining/new actionable findings

### N1 — High: local input loss prevents recording known remote job IDs and terminal receipts

**Locations:**
- `production/store.py:93–109`, especially unconditional `verify_scope` at lines 105–106.
- `production/upstream.py:242–265`, especially validating every clip's local assets/dependencies at lines 258–260.
- `production/cli.py:88–95` (`observe` uses the ordinary transaction path).

Every transaction, including a historical remote observation, must pass current mutable input validation before publishing. If any local input disappears or changes after reservation, a correct remote acknowledgement cannot be saved. This is not merely blocking new generation or adoption: the durable job identity itself is discarded from the transaction.

**Executed real CLI reproducer:**

1. Initialize a temporary store and persist a normal C1 reservation at revision 1.
2. Delete the pinned local `face.txt` input after reservation.
3. Supply an exact synthetic `submitted` receipt for the original request hash and job ID `fixture-confirmed-remote-id`.
4. Invoke the actual `observe` CLI with revision 1.
5. Inspect the ledger JSON directly, since even normal `store.read()` now fails its current-input check.

Observed:

```json
{
  "exit": 2,
  "output": {"status":"blocked","error":"path: missing regular file face.txt","submitted":false},
  "revision": 1,
  "phase": "submitting",
  "job_id": null,
  "ledger_unchanged": true
}
```

The slot is conservatively retained, so this does not create an immediate duplicate submission. It does, however, fail the requirement to promptly and durably preserve the known job ID. The same transaction gate prevents recording known success/failure/cancellation and corresponding slot reconciliation while unrelated local inputs are broken. Repairing/restoring local design files should not be a prerequisite for saving an already observed historical remote fact.

**Contract impact:** R05/R06/R07; design 03 §3 and §3a distinguish preserving remote observations from opening current acceptance. The new broader dependency validation exacerbates the coupling, but this review does not claim the entire coupling was newly introduced.

**Minimal fix:** Keep locked/CAS/model/receipt identity and transition validation for observations, but decouple recording historical attempt facts from mutable current-scope/media readiness. Current invalidity must still block reservation/acceptance and remain visible; do not permit new submission or fabricate failure to work around this. Persist observations in the same authoritative namespace, not a competing ledger. Add subprocess regressions for acknowledged job IDs and terminal receipts after input deletion/hash drift, including an unrelated clip dependency and unchanged unknown reservations.

### N2 — Important / F4 remainder: generated initial admission accepts drifted consumed-source approval

**Locations:** `production/quality.py:12–20,23–51,88–110`.

`_sources_current` checks both referenced media and approval evidence. It runs for approved reuse and explicit revalidation, but **not for the `generated` initial-admission branch**. That branch checks the candidate's own approval only. A source approval file's on-disk drift does not alter the serialized selection or its fingerprint, so fingerprint equality does not close this gap.

**Executed adversarial scenario:**

1. Admit C1 using normal preparation/reservation, successful fixture receipts, real decoded local media, and its own pinned approval.
2. Prepare/reserve C3 consuming required C1, with a **separate** valid C3 approval evidence file. The source's approval is still valid at preparation.
3. Record C3's original job success.
4. Replace C1's approval evidence bytes with `UPSTREAM APPROVAL REVOKED / REPLACED`, leaving C3's own approval file and both media files unchanged.
5. Admit the C3 candidate with the original/current fingerprint and reported fixture QA.

Observed:

```json
{
  "own_C3_approval_pin_valid": true,
  "C1_approval_pin_drifted": true,
  "C3_accepted": "accepted",
  "C3_valid": true,
  "C3_fingerprint_current": true
}
```

This does not depend on authenticating who revoked approval. It is a deterministic mismatch against a specifically pinned local approval artifact. The same current-pin check is already considered necessary at preparation, revalidation and handoff; initial generated acceptance omits it.

**Contract impact:** R07/R08, F4's required current approval/consumed-input check immediately before adoption. Historical remote success must remain preserved, but the candidate must not become current merely because its own separate approval still matches.

**Minimal fix:** Apply the same appropriate consumed-source currentness/media/approval checks to generated current-admission commits as to reuse/revalidation, respecting documented optional-omission policy. Keep late remote facts immutable and leave the result non-current pending explicit remediation. Add a regression with distinct source and candidate approval files; tests that share one approval file only exercise the own-approval check and mask this omission.

## 4. Reproduction details

Both findings were reproduced by inline Python from the package root, importing existing test helpers and using `TemporaryDirectory`. No new test/source file was written.

### N1: compact repeatable harness

```python
import sys, tempfile, json
from pathlib import Path
sys.path.insert(0, "tests")
import conftest
from test_execution import reserved
from test_cli import cli
from production.store import ProjectStore
from production.models import Phase, Receipt

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    seed = conftest.seed.__wrapped__(root)
    cap = conftest.capability.__wrapped__(root)
    auth = conftest.authority.__wrapped__(root, seed, cap)
    state, packet = reserved(seed, cap, auth, root)
    ledger = root / "ledger.json"
    store = ProjectStore(ledger)
    store.initialize(seed)
    with store.transaction(0) as tx:
        tx.state = state
    (root / seed.batch.clips[0].assets[0].path).unlink()
    receipt = root / "receipt.json"
    receipt.write_text(Receipt(
        phase=Phase.SUBMITTED, job_id="fixture-confirmed-remote-id",
        evidence="synthetic exact acknowledgement",
        request_hash=packet.request_hash).model_dump_json())
    result = cli("observe", ledger, "ATT-1", receipt, 1)
    persisted = json.loads(ledger.read_text())["production"]
    print(result.returncode, result.stdout)
    print(persisted["attempts"][0]["job_id"])  # None, incorrectly not saved
```

### N2: exact setup/mutation needed

Use `test_dependencies.linked(seed)` and `test_quality.candidate` to admit C1 with `accept_take`. Construct its C3 `Binding` from `selection_for(state,"C1")`, as `test_quality.linked_running` does. Before calling `prepare_request` for C3, copy its authority with:

```python
a3 = auth.model_copy(update={
    "evidence": conftest.pin(root, "approval-C3.txt", "separate current C3 fixture approval"),
    "allowed_hashes": (*auth.allowed_hashes, source.take.asset.sha256)
})
```

Prepare C3 with `(test_bindings.native(state), source_binding)`, reserve `ATT-C3`, and observe its submitted/succeeded fixture receipts using the packet's request hash. Use `test_media.make_video(root,"candidate-C3.mp4",color="red")` for the C3 candidate; copy its clip/attempt/fingerprint and reported fulfilled ID to C3/ATT-C3/packet fingerprint/R3. Then:

```python
(root / source.approval.evidence.path).write_text("UPSTREAM APPROVAL REVOKED / REPLACED")
verified_file(root, a3.evidence)  # Still succeeds: C3's approval did not drift.
updated = accept_take(state, t3, r3, t3.fingerprint, root)
assert selection_for(updated, "C3").valid  # Current code incorrectly admits it.
```

The executed setup used only legitimate transition helpers before the file mutation, not forged persisted requests or patched runtime functions.

## 5. R02 additions and other affected seams

- Six reuse/scope tests now cover positive approved reuse, refusal without reuse permission, exact approved exclusion, missing exclusion refusal, and actual CLI persistence for both additions.
- Independently exercised a scope amendment **with an existing unknown attempt**: the entire attempts tuple stayed unchanged, available capacity stayed at one of two, and exact old/new source history was retained. Thus scope changes do not silently free unknown reservations.
- Independently changed only the approved reuse range while keeping the real source/report unchanged: admission correctly failed with `authority`.
- Scope amendment invalidates retained selections and clears joins rather than carrying current acceptance into a changed denominator. Removed selection history is retained. Approval authenticity remains a supplied-evidence assumption, not a proven fact.
- Namespaced source/role identity regression uses tuple keys, avoiding colon-concatenation collisions in required-reference accounting.
- Upstream closure is explicitly **not** a replacement for the original full preproduction validators. That is a truthful supported-projection boundary, not approval for unvalidated arbitrary upstream projects or blanket external upload.
- Library handoff checks source/approval pins; the documented public CLI additionally calls `verify_render` for technical montage validation. Library callers must preserve that documented separation if using the pieces directly. No perceptual truth is inferred from either function.

## 6. Per-rubric assessment

| Rubric | Assessment | Evidence / qualification |
|---|---|---|
| **R01** five roles/package | **PASS, local metadata scope** | Five roles have input/output/ownership boundaries; invocation and external execution disabled. Package checker validates all 12 public schemas and links without findings. No agent-behavior certification claimed. |
| **R02** coverage/reuse/exclusions | **PASS, scoped contract** | Coverage tests, identity/closure regressions, six reuse/scope tests, plus independent unknown-preservation and exact-range negatives. Approved-source pins and explicit deltas anchor the denominator. Requires original upstream validation as documented. |
| **R03** DAG/multi-reference/order | **PASS** | Four dependency tests; separate edit/DAG checks; accepted multi-source roles and optional omission rationale; tuple-key collision negative. No live conditioning claim. |
| **R04** native binding/settings/transfer | **PASS for scoped preparation contract** | Sixteen binding cases and config regressions; source/range/revisions/imports/excludes/native IDs and allowlisted transfer hashes retained; per-clip settings are explicitly approved. N2 affects later adoption, not the exercised preparation check. |
| **R05** lifecycle/slots/duplicates | **REVISE** | Nine pure execution tests pass, and unknown preservation survives scope changes. N1 prevents durable acknowledgements/terminal reconciliation after local input loss. |
| **R06** persistence/restart | **REVISE** | Ten existing lock/restart/atomic-failure tests pass; fields and cooperating single-writer/CAS behavior remain intact. N1 is an untested cross-boundary recovery failure. |
| **R07** revision/currentness/CAS | **REVISE** | Five revision cases and actual running-source-replacement test pass. Revalidation policy is explicit and tested. N1 fails historical-fact preservation; N2 misses current consumed approval at generated admission. |
| **R08** QA/conditional/narrative | **REVISE** | Nineteen quality cases use real local decode with explicit reported semantics; own approval drift and conditional retention tests pass. N2 leaves an acceptance-validity hole. |
| **R09** flow/handoff/progress | **PASS for scoped delivery gate** | Twelve handoff tests, actual complete CLI montage, and source deletion/replacement negatives at library/CLI resolve F1. Exact joins/ranges, full reported flow, rights/receiver fields and zero certified exterior handles remain distinct. |
| **R10** existing seams | **PASS, local adapters only** | Nine adapter tests exercise the actual legacy Ledger and existing auditor offline; representative closure compared to actual `project_index`. No invented provider API, source mutation, or live service success claim. |
| **R11** trace/integration execution | **PASS for mapped local scenarios, not exhaustive correctness** | 34 IDs map to 42 executed cases; named F5 mismatches corrected; full suite 119 passed and type check clean. N1/N2 demonstrate missing cross-boundary regressions; green output cannot override those findings. |

The overall verdict remains REVISE even where individual mapped scenarios pass. R12 requires no unresolved important findings, not simply green existing tests.

## 7. Commands and independent results

| Command/check | Result |
|---|---|
| `sha256sum` of current manifest, archived manifest and goal before/after | All match the supplied hashes |
| `sha256sum -c qa/implementation/review-scope.sha256` before/after | **67/67 OK** each time |
| `python3 -m pytest -q` | **119 passed in 26.94s** |
| `python3 scripts/check_package.py --json` | **5 skills; findings []** |
| `basedpyright production` | **0 errors, 0 warnings, 0 notes** |
| `python3 scripts/check_acceptance.py --json` | **valid true; 34 IDs / 42 executed cases**; live/perceptual flags false |
| Temporary N1 actual CLI reproduction | Reproduced receipt persistence failure; exit 2, no job ID saved |
| Temporary N2 distinct-approval reproduction | Reproduced current C3 acceptance after C1 approval pin drift |
| Temporary scope amendment with unknown attempt | Attempts unchanged, slot retained, exact scope history retained |
| Temporary wrong-range reuse grant | Correctly blocked by authority |
| Recorded protected-input baseline comparison | All three current hashes match |

The reported command successes are execution results, not a PASS on the defective behavior reproduced by the adversarial checks.

## 8. Constraints and remaining limitations

**Reviewer constraints: PASS.** No installation, Git command/staging/commit, network/provider operation, external transfer, publication/deployment, delegation, or child launch occurred. This is the same authorized reviewer continuing the same goal. No sources/docs/goal/fixtures/schemas were edited. Only normal caches, the checker's generated `qa/implementation/acceptance-{junit.xml,pytest.txt,results.json}` outputs, temporary local projects, and this routed report were written.

**Implementation safety/completion constraints: REVISE.** No observed automatic resubmission or fabricated remote execution; unknown slots remain conservative. However, N1 loses durable reconciliation opportunities and N2 can classify an approval-stale dependency's generated consumer as current. Do not claim final implementation acceptance or 100% from this snapshot.

Approval/rights/receiving declarations and semantic playback reports are unverified operator assertions within this offline contract. Matching pins prove consistency, not issuer authenticity, actual consent, watching/listening, identity fidelity, or artistic merit. ffprobe/decode/render prove technical local-media behavior only. Actual provider conditioning, paid/Unlimited generation, perceptual QA, installation, release and deployment remain unperformed/out of scope. Nonzero exterior handles, mixed-format/VFR conform and concurrent legacy writing remain unsupported rather than silently certified.

**Recommended next step:** Address N1 and N2 with narrow local negative/positive regressions, rerun existing checks, create a new snapshot, and obtain an authorized continuation review. Preserve this report and the earlier REVISE record; no implementation fixes were made by this reviewer.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Completed the same authorized reviewer's read-only re-review of the specified goal and fixes without implementation, installation, Git, network/provider operations or delegation. Implementation verdict is REVISE."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Report supplies F1-F5 dispositions, two concrete remaining findings with source ranges, executed reproductions and minimal fixes, R01-R11 assessments, safe check results and unchanged before/after hashes."
    }
  ],
  "changedFiles": [
    "/home/declan/.pi/agent/sessions/--home-declan--/subagent-artifacts/outputs/1abed98c-ee47-4d26-b5e5-ab4c1d1184f0/reviews/production-implementation-final-review-02.md",
    "qa/implementation/acceptance-junit.xml (generated output)",
    "qa/implementation/acceptance-pytest.txt (regenerated output)",
    "qa/implementation/acceptance-results.json (regenerated output)"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {"command":"sha256sum manifest/archive/goal; sha256sum -c qa/implementation/review-scope.sha256 (before/after)","result":"passed","summary":"All supplied hashes match; 67 current entries unchanged."},
    {"command":"python3 -m pytest -q","result":"passed","summary":"119 passed in 26.94s."},
    {"command":"python3 scripts/check_package.py --json","result":"passed","summary":"Five skills, no findings; 12 public schemas checked."},
    {"command":"basedpyright production","result":"passed","summary":"0 errors, 0 warnings, 0 notes."},
    {"command":"python3 scripts/check_acceptance.py --json","result":"passed","summary":"34 mapped IDs, 42 executed cases; live/perceptual verification false."},
    {"command":"Inline temporary-project adversarial and preservation checks","result":"passed","summary":"Safely reproduced N1/N2; approved scope retained unknown attempts/slots; wrong-range reuse blocked; three protected hashes match."}
  ],
  "validationOutput": [
    "Implementation verdict REVISE: N1 historical receipt persistence blocked by local input failure; N2 generated initial admission omits consumed-source approval checks.",
    "Current manifest SHA256 e8c69e74a078ec0b25a5b6f13b68946023298a4ef17a016137795d8f76c23928; 67/67 OK before and after.",
    "Goal SHA256 87ec1c8879ac43673def29870ff24d643a7d687d4d0ef9acda41b32111a18f3d unchanged."
  ],
  "residualRisks": [
    "N1 and N2 remain unresolved; F4 only partially resolved.",
    "No live provider, perceptual-quality, approval-authenticity, installation or deployment certification."
  ],
  "noStagedFiles": true,
  "diffSummary": "Routed review report and allowed generated QA artifacts only; no checked implementation changes.",
  "reviewFindings": [
    "blocker: production/store.py:93-109 and production/upstream.py:258-260 - unavailable local input prevents durable known remote observations",
    "important: production/quality.py:12-20,23-51 - consumed source approval drift bypasses generated initial admission"
  ],
  "manualNotes": "Acceptance statuses describe completion of the review assignment, not acceptance of the implementation. Implementation remains REVISE."
}
```
