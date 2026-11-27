# A7/R3 local trace preparation

Implemented a separate read-only packet check (`scripts/e2e_trace_check.py`), 54 synthetic/negative tests (`tests/test_e2e_trace_check.py`), and usage/format/trust guidance (`evals/e2e/formal-trace.md`). The checker requires six claimed lanes, exact brief and source bytes, explicit observer/session/clock IDs, and ordered same-clock event markers binding dispatch and reached endpoints to the evidence. It rehashes current S08/QA4 bundles and provider receipts, checks receipt target/capability evidence, and withholds durations on incomplete or incomparable packets. A reached `REVISE`/`RETHINK` is not PASS. No harness launches, provider or other external calls, installs, staging, formal rows, or queue updates. R3 remains blocked.

## Actual validation evidence

| Local invocation (Python tests run with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, and temporary `--basetemp`) | Observed result |
|---|---|
| `python3 -m pytest -q … tests/test_e2e_trace_check.py` before adding the checker | RED: exit 2 on `ModuleNotFoundError: No module named 'e2e_trace_check'`. |
| Same test command after the initial implementation | GREEN: 48 passed. |
| `python3 -m pytest -q … tests/test_e2e_trace_check.py -k claims_match_hashed` before enforcing observer-log binding | RED: six failures (claimed tick, executor, observer, clock, source or endpoint did not match archived event). |
| `python3 -m pytest -q … tests/test_e2e_trace_check.py tests/test_e2e_grade.py tests/test_model_facts.py tests/test_submission_gate.py` after binding | GREEN: 86 passed. |
| `python3 -m pytest -q -p no:cacheprovider --basetemp /tmp/a7-trace.HcyNUt/full` final local suite | **219 passed in 2.32s**. |
| `python3 scripts/e2e_trace_check.py --project . --traces qa/wo-13/readonly-pilot.md` | Exit **2**, `expected JSON trace array`; a simulated blocked QA2 packet also returned **3** `unverified` (test). |
| `python3 scripts/e2e_grade.py --evidence-root qa/wo-13 --runs qa/wo-13/runs.json` | Exit **3** `unverified`: all three scenario pairs missing. |
| Before/after SHA-256 inventory of package files outside caches | All 243 existing files unchanged; only the three requested package files added. `runs.json` SHA-256 `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`. |
| `git rev-parse --is-inside-work-tree`; `git -C ../contents-production-skills diff --cached --quiet` | v2 is not a Git worktree; adjacent v1 index clean. No staged files. |

The positive test is invented, not a real run: six synthetic lane claims are structurally accepted; the X-1/v1 fixture reports 6 wall seconds, 2 conti seconds, and S08 `REVISE`. Negative tests reject mismatched markers, conflicting lane settings and targets, missing/expired/unusable receipts, and post-capture tampering (including source, brief, event log, endpoint and provider files).

## Remaining gate

A custodian must confirm original observer/harness provenance, actual byte-complete snapshots and gate judgments, effective settings, telemetry and isolation, and current exact-request/provider compatibility. A checked packet is not formal eligibility, a QA4 pass, approval, or a rubric score. Resolve the A7 preflight's real-input/authority and instrumentation blockers before scheduling any formal R3 lane; do not populate `runs.json` from this work.
