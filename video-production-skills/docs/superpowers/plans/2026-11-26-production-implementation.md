# Video Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. One parent implementer and one authorized final read-only reviewer. No other children.

**Goal:** Implement the reviewed production contracts as five skills plus local typed batch/continuity/execution/QA tooling with truthful offline adapters.
**Architecture:** Frozen Pydantic boundary models; pure contract functions; atomic locked transactions on a `production` namespace inside the existing project ledger (other fields preserved). CLI prepares auditable requests and imports observed receipts; it never performs uploads or generation. Existing sequence/ledger contracts are consumed read-only through explicit adapters.
**Tech Stack:** Python 3.14, installed Pydantic 2.14, Typer, pytest; stdlib fcntl/atomic replace; no installation.
**Spec:** docs/design/00-overview.md through 05-validation-decisions.md.

## Global Constraints
- No external mutations, media generation, package install, Git operations or changes to preproduction/shared projects.
- No artificial budget; one final independent reviewer authorized. Tests use temporary projects.
- Native capabilities/rights/actual playback remain supplied evidence, never fabricated by code.
- All time ranges are explicit [in,out); unknown occupies a slot; no automatic retry.

## Review Focus
- Untrusted/malformed JSON and path traversal/symlinks: boundary parse, safe-file and CLI error tests (Tasks 1/3/5).
- Remote success arrives after source acceptance revision changes: commit CAS and stale tests (Task 2/4).
- Crash before/after submit receipt and external account work: durable reservations/recovery tests (Task 3).
- Conditional findings touch imported identity or mandatory action: QA/handoff refusal tests (Task 4).
- Local adapters silently dropping existing project fields or assuming native roles: real contract fixture and roundtrip tests (Task 5).

## Task 1 — Typed inputs, coverage and DAG
Files: production/{models,contracts}.py, tests/{conftest,test_coverage,test_dependencies}.py.
Interfaces: frozen Batch, Clip, Pin, Reference, Take, Evidence, State; `validate_batch(batch)->None`, `ready_clips(state)->tuple[str,...]`, `fingerprint(state,clip_id)->str`.
- [x] Write failing tests for complete coverage, missing/duplicate IDs, multi-shot omissions, cyclic/dangling refs, blocked dependency and independent ready.
- [x] Run pytest on the two suites; preserve RED output (missing implementation).
- [x] Implement parse-at-boundary models and pure coverage/graph/ready/fingerprint functions.
- [x] Rerun the suites; GREEN and evidence log.

## Task 2 — Bindings and revisions
Files: production/{bindings,revisions}.py, tests/{test_bindings,test_revisions}.py.
Interfaces: `prepare_request(state,clip_id,capability,authority)->Prepared`; `replace_take(state,take)->State`; accepted current range/QA revision pins; affected descendants blocked.
- [x] RED: missing/native wrong roles, over-capacity, forbidden transfer, stale hashes and same-byte range/acceptance changes; running replacement, irrelevant revision retention.
- [x] Implement final immutable prepared packet, per-input fingerprint, revision propagation.
- [x] GREEN and evidence.

## Task 3 — Execution and persistence
Files: production/{execution,store}.py, tests/{test_execution,test_recovery}.py.
Interfaces: `reserve(state,prepared,attempt_id,external_active)->State`, `observe(state,attempt_id,receipt)->State`; `ProjectStore.transaction(expected_revision)` context manager reads/writes the existing JSON namespace with flock, revision check, fsync/replace.
- [x] RED: unknown keeps slot, duplicate submit, terminal releases slot, unconfirmed cancel, foreign account jobs, illegal transition, persistent lock/process/atomic failure.
- [x] Implement pure lifecycle transitions and durable transaction; no network transport.
- [x] GREEN, including real subprocess lock/restart tests.

## Task 4 — QA, commit and handoff
Files: production/{quality,handoff}.py, tests/{test_quality,test_handoff}.py.
Interfaces: `accept_take(state,take,review,expected_fingerprint)->State`, `check_join(state,join)->None`, `build_handoff(state,flow,received)->Handoff`, progress projection.
- [x] RED: missing playback/listening, wrong/range-mismatched evidence, invalid conditional imports, non-linear reveal, late CAS, missing requirement, missing join, fake full flow, invalid denominator.
- [x] Implement G2–G5 checks with explicit media evidence and current revision bindings; atomic publication through store.
- [x] GREEN and evidence.

## Task 5 — Offline adapters and CLI
Files: production/{adapters,cli}.py, scripts/production.py, tests/{test_adapters,test_cli}.py, tests/fixtures/*.
Interfaces: read-only preproduction ledger and sequence projection readers; typed native prepared-call receipt adapter; CLI validate/ready/prepare/reserve/observe/accept/invalidate/handoff persisted transactions; no execute command.
- [x] Read actual existing contracts, create representative fixtures with provenance.
- [x] RED: preserve other ledger fields, reference selection mismatch, missing current provider contract, path safety, success/error CLI cases and durable restart.
- [x] Implement adapters/CLI; GREEN via subprocess invocation, not mocks of internal functions.

## Task 6 — Five role skills, examples, checkers and acceptance trace
Files: five role dirs/SKILL.md, manifest.json, examples/, scripts/{check_package,check_acceptance}.py, tests/test_package.py, docs/acceptance-map.json, docs/operations.md.
- [x] RED: package metadata/paths/links/schema and acceptance IDs must resolve to real pytest nodes; no prose assertion snapshots.
- [x] Write role procedures that use tested CLI, explicit operator transport and gate evidence; scope to offline package without installation.
- [x] Map T01–T34 to exercised behavior tests; execute check_acceptance which runs actual nodes and records outcomes (not count-only).
- [x] Full pytest and real CLI smoke; snapshot protected preproduction inputs unchanged.

## Task 7 — Independent finish
- [x] Fresh current verification for R01–R11; record actual evidence and constraints in goal. After review 03/N3: full 154, type/package/acceptance and protected input hashes pass.
- [x] Hash review scope; launch one authorized read-only reviewer with goal, scope and commands. Same retained reviewer only; reports 01/02/03 remain preserved REVISE records.
- [x] Correct known actionable findings with RED/GREEN; do not infer review PASS after code changes. Reviewer authorization is one child; same retained reviewer may recheck only if its continuation is permitted; otherwise request remaining permission.
- [x] Mark done on current evidence + independent review 04 PASS. 76-file scope unchanged, 154 tests and all checks independently pass; goal 12/12 done. External/provider/perceptual/install/release claims remain excluded.

## Execution ledger
Goal file is the canonical completion record. Per-task evidence lives in qa/implementation/. No commits or Git-dependent worktree scripts; nonGit workspace exception recorded in the goal.
