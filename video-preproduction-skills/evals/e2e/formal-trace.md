# WO-13 claimed trace check (local only)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/e2e_trace_check.py \
  --project /path/to/local/wo13-evidence --traces traces.json
```

Use a frozen evidence root, not a live run directory. This is a read-only pre-registration check, separate from `scripts/e2e_grade.py`. Exit **0** (`trace_checked`) reports wall/conti seconds and the claimed gate verdict for each lane; **3** (`unverified`) reports missing or incomparable evidence without metrics; **2** is a CLI/input error. None of these registers a run or evaluates quality.

## Packet format

`traces.json` is a JSON array containing exactly one row for each `X-1`–`X-3` × `v1`/`v2`. A **file reference** is `{ "path": "relative/path", "sha256": "<lowercase hex SHA-256>" }`. All referenced files must be nonempty and resolve inside `--project`; no absolute paths or `..` components. Hashes are checked against the files as they exist at validation time.

| Row fields | Meaning |
|---|---|
| `scenario`, `variant`, `session_id`, `observer_id` | Unique executor session per lane; no observer ID may be an executor ID anywhere in the packet. |
| `model`, `reasoning` | Effective **evaluator** model ID/version and effort, identical in all six lanes. |
| `brief`, `source` | File references. Brief is a byte-identical copy of the corresponding frozen WO-13 brief. Source is an archive of the exact source used (including working-tree bytes), not just a commit ID or `SKILL.md`. Freeze one source snapshot per variant. |
| `timing_protocol`, `clock_id`, `event_log`, `events` | Protocol `wo13-preflight-v1` (below), one same-clock ID per lane, a file reference to the UTF-8 observer event log, and four marker objects with `event`, integer `tick_ns` and 1-based `line`. |
| `endpoint` | `{gate, verdict, artifact}`: `S08` for v1, `QA4` for v2, and `PASS`, `REVISE` or `RETHINK`. `artifact` is a file reference to the frozen review bundle containing the exact would-be request, attachments/references, options and review evidence. Input-blocked, skipped or text-only review is not a reached endpoint. A reached nonpassing verdict remains nonpassing. |
| `provider`, `provider_receipt` | Intended **media** target (`transport`, `model`, `endpoint` strings), identical within each scenario pair; file reference to a matching provider receipt. |

The ordered markers are `wall_start` (initial prompt dispatch), `conti_start` (v1 S06 first shot breakdown on locked screenplay/bible; v2 P3/R0 after locked SCR/bible and DNT), `conti_end` (v1 finalized cut/timing/continuity handoff; v2 R7 recheck, rulings and CNT/CTY handoff), then `formal_endpoint` (reached pre-submit review, before any video generation). Include in-slice revisions/tool work, not prior authoring, DNT, or subsequent panel/prompt work. Wall time ends at the reached gate, excluding scoring/archival. Use actual observed transitions; an inseparable conti slice or an estimated duration is not evidence. Ticks are nonnegative integer nanoseconds, strictly increasing. Each referenced log line is a JSON object reproducing `event`, `tick_ns`, `clock_id`, `session_id`, `observer_id`; `wall_start` also has `brief_sha256` and `source_sha256`, and `formal_endpoint` has `gate`, `verdict`, and `artifact_sha256`. Preserve the original harness record alongside any normalized event log.

A provider receipt is JSON using the [model-facts registry shape](../../model-facts/_schema.md) plus matching `transport` and a `source_evidence` file reference to the archived provider documentation, experiment or user-supplied evidence. It must contain currently verified, sourced `max_duration_s` (positive finite), `aspects` (nonempty ratios), `reference_images_max` (positive integer), `native_audio` (boolean), and, when native audio is supported for X-1/X-2, `dialogue_languages` (nonempty strings). Expiry is checked as of the local current date using `ttl_days` (default 30). A verified language list does not itself establish support for the requested language or audio path.

## Trust boundary

Matched hashes and log fields detect inconsistencies, not fabrication. The checker does not authenticate the observer/harness, prove that archived source ran or that snapshots are complete, inspect media or verify gate judgments, validate the exact request against provider capabilities, or verify evaluator metadata, isolation, scoring, or token telemetry. A custodian must compare these claims to raw evidence and confirm equivalent inputs, settings, timing boundaries, gate contents, and authority under the [A7 preflight](../../qa/wo-13/formal-preflight-a7.md). No provider calls, formal eligibility, or submission approval follow from `trace_checked`. Passing test packets are synthetic only, not formal evaluation evidence.
