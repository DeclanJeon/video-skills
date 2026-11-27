# Video-skills design QA and no-orchestrator baseline

## Scope and method

Read-only review of `docs/design.md`, both entry skills, manifests, linked operating contracts, relevant implementation seams, and current shared/agent registrations. No files were edited, no commands or generation jobs were executed, and no delegation occurred.

Postproduction was **not inspected, modified, implemented, moved, or installed**. “Post absent” below means no configured, verified integration; a sibling directory’s existence is not installation evidence.

Paths below are relative to the `video-skills` root unless beginning with `~/`.

## Review

### Correct

- **One public entry, disabled departments:** `docs/design.md:7–9,20` correctly chooses explicit file reads rather than automatic invocation of department skills. Both entry skills have `disable-model-invocation: true` (`production-director/SKILL.md:4`; `production-supervisor/SKILL.md:4`). Production’s validator expressly requires these disabled flags and rejects automatic invocation (`video-production-skills/scripts/check_package.py:34–35,47–48`). Do not enable the departments to make orchestration work.
- **Authority is separate from nonstop:** the design preserves spend, transfer, rights, publishing, and tool-availability gates (`docs/design.md:17`). This matches the director’s approval contract (`video-preproduction-skills/production-director/SKILL.md:33`) and production’s actual-executor restriction (`video-production-skills/production-supervisor/SKILL.md:14`).
- **An unavailable post slot is not completion:** `docs/design.md:15,23` correctly retains the final-video target and reports blockage rather than calling a production handoff a final master.
- **Existing work and single artifacts are protected:** `docs/design.md:16` matches the director’s ledger-based resume and no-unrequested-scaffolding rules (`video-preproduction-skills/production-director/SKILL.md:15,37`).

### Fixed

None. This was a read-only review.

### Finding — P1: Explicit phase-boundary precedence is missing

**Location:** `docs/design.md:9,12–15`.

Reading the existing director imports instructions that still claim the entire pipeline:

> “Use for finished-video production … run phases from benchmark to final cut”  
> — `video-preproduction-skills/production-director/SKILL.md:3`

Its referenced “sole routing table” assigns actual generation to `production-director`, take QA to `production-qa`, and post to `film-editor`/`sound-designer` (`video-preproduction-skills/docs/design/01-pipeline-and-gates.md:59–61`). Its waiting rule also excludes unavailable tools from permissible waiting reasons (`…/01-pipeline-and-gates.md:185`), unlike the new contract.

The design names the new owners but does not explicitly explain which imported routing instructions are superseded. Sequentially reading both entries is therefore insufficient to establish a unique owner.

**Smallest remedy:** define an orchestration overlay, without changing either package:

- `production-director`: assigned preproduction scope only; for the combined route, stop after the required prompt/QA4 handoff.
- `production-supervisor`: generation, take/continuity review, production state, and production handoff.
- Post: reserved integration only; never fall back to the director’s legacy P7 route.
- Preserve department safety gates, but make the approved scope boundary and unavailable-capability blockage explicit precedence rules.

### Finding — P1: The preproduction-to-production data bridge is unspecified

**Location:** `docs/design.md:9,13–14`.

The packages do not expose the same upstream representation:

- Preproduction uses an artifact ledger and `04_board/index-header.json` plus `04_board/index.csv` (`video-preproduction-skills/production-ledger/references/ledger-schema.md:3,23`).
- Production’s `derive_coverage` parses only `CoverageEnvelope | Project` JSON (`video-production-skills/production/upstream.py:88–112`). That `Project` requires `shots` and `storyboard`.
- `resolve_legacy` resolves individual current artifact pins; it does not translate the board CSV into production coverage (`video-production-skills/production/adapters.py:36–47`).

Consequently, “validated preproduction inputs” does not yet define an executable handoff from these particular packages. Passing their artifact `ledger.json` directly to `derive_coverage` does not satisfy either supported schema.

**Smallest remedy:** specify an orchestrator-owned handoff procedure that:

1. Runs the existing preproduction validators.
2. Maps current cut/panel/beat/dialogue/cue IDs and mandatory asset dependencies into production’s supported input contract.
3. Preserves original IDs, version/hash pins, and source locators.
4. Creates an immutable coverage snapshot separately from the mutable ledger, as required by `video-production-skills/docs/operations.md:28`.
5. Reports unmapped requirements as G0 blockers instead of substituting example fixtures or inventing completion.

Add one synthetic boundary acceptance case using actual preproduction-shaped outputs.

### Finding — P1: Returning to preproduction can erase the production namespace

**Location:** `docs/design.md:9,16` — preserving authoritative ledgers during resume/rework.

The preproduction writer serializes only:

> `{'schema_version': 1, 'artifacts': artifacts}`  
> — `video-preproduction-skills/scripts/cp2/ledger.py:39`

It then replaces `ledger.json` (`…/ledger.py:47`). Production preserves other fields while adding its namespace (`video-production-skills/production/store.py:72–74`).

Production documents the incompatibility explicitly:

> “legacy cp2.Ledger._save는 알 수 없는 namespace를 보존하지 않으므로…”  
> [The legacy writer does not preserve unknown namespaces.]  
> — `video-production-skills/docs/operations.md:6`

This affects sequential rework, not just simultaneous writers: after production initialization, a later director registration can remove the entire production namespace.

**Smallest remedy:** explicitly prohibit the old writer from writing a ledger containing production state. Define an orchestrator-owned preservation/commit seam for necessary preproduction revisions, or block such revisions until that seam exists. Merely serializing the two writers is not sufficient.

### Finding — P1: Legacy retirement needs an explicit transitive-dependency keep map

**Location:** `docs/design.md:20`.

“Retain provider/equipment skills” does not identify two dependencies that resemble retired legacy infrastructure:

- `recording-production-history` remains an actual dependency of `production-ledger` (`video-preproduction-skills/production-ledger/SKILL.md:21`; `references/ledger-schema.md:29`), despite the old migration table describing it as absorbed (`video-preproduction-skills/docs/design/08-v1-migration.md:28`).
- Retained `higgsfield-generate` requires sibling `video-production-assets` continuity and sequence-execution resources (`~/.agents/skills/higgsfield-generate/SKILL.md:35–37`).
- An existing production compatibility test imports the auditor through the registration slated for possible retirement:

  > `Path.home()/".pi/agent/skills/video-production-assets/scripts"`  
  > — `video-production-skills/tests/test_adapters.py:112`

Removing those registrations indiscriminately would lose required history support, break relative equipment reads, or break the existing compatibility test.

**Smallest remedy:** add an explicit keep/retire/resource-only table. Preserve the history tool and legacy auditor/reference closure without exposing the old planning router. Resolve retained resources from canonical source directories; document how the unchanged compatibility test retains its import path.

**Relocation note — P2:** the preproduction README still points to `../contents-production-skills` (`video-preproduction-skills/README.md:47`). From its current location, the real legacy package is `../../contents-production-skills`. Preserve package bytes, but supply the correct canonical legacy-root mapping in the orchestrator; do not treat that stale README path as a live dependency locator.

### Finding — P1: Retained equipment still routes back to creative-production

**Location:** `docs/design.md:20` — replacing legacy routing while retaining equipment.

The retained executor says:

> “`creative-production` is the sole project-level coordinator…”  
> “Standalone invocation: consult `creative-production` once…”  
> — `~/.agents/skills/higgsfield-generate/SKILL.md:33`

Its no-callback exception specifically names delegation by `creative-production`. Removing the old link and updating the shared workflow pointer does not remove this instruction. Delegation by `production-supervisor` or `video-skills` is not covered expressly.

**Smallest remedy:** specify a bounded equipment-delegation overlay: consume the new coordinator’s call sheet, retain all provider execution/approval gates, and return results without rerouting to `creative-production`. Do not modify legacy sources or resurrect the old coordinator to satisfy that wording.

### Finding — P1: Post absence can block production at G5, before the proposed post boundary

**Location:** `docs/design.md:14–15`.

Production completion itself requires post receipt:

> “모든 필수 coverage, 접합, 전체 흐름과 post 수령을 닫고 handoff를 만든다.”  
> [Close mandatory coverage, joins, whole flow, and post receipt, then create handoff.]  
> — `video-production-skills/production-supervisor/SKILL.md:16`

Its handoff builder rejects a missing recipient:

> `ContractError("handoff", "post recipient and rights record required")`  
> — `video-production-skills/production/handoff.py:98–99`

Therefore an unconfigured post slot may prevent G5 completion even when all production sources are ready. The design does not distinguish that state from a completed production handoff awaiting post execution.

**Smallest remedy:** define separate statuses for source readiness, G5 receipt/handoff completion, and final-master completion. With no genuine recipient, preserve the G5 blocker and exact restart inputs; do not invent receipt. A real explicitly designated external recipient may satisfy the existing contract, but a reserved slot may not.

## Disabled invocation and duplicate discovery

These are verification requirements, **not demonstrated duplicate defects**:

- The new public `video-skills` entry must have valid discovery metadata and must not inherit `disable-model-invocation: true`.
- All shared/agent aliases should resolve to the **same canonical entry file**, not copied variants.
- Pi currently also scans `~/.codex/skills` (`~/.pi/agent/settings.json:32`), so counting one link per directory does not establish unique discovery.
- An installed Pi loader deduplicates identical canonical files and reports same-name collisions between different files (`~/.local/opt/flucto-cli/lib/node_modules/free-pi-cli/node_modules/@earendil-works/pi-coding-agent/dist/core/skills.js:328–350`). Thus multiple aliases alone are not proof of a collision.
- That loader stops recursion when a directory contains `SKILL.md` (`…/skills.js:117`). Ensure the installed link targets the public entry root, rather than a parent lacking its own entry and exposing nested departments.

Acceptance should record one effective public entry per harness, its canonical path, and collision diagnostics. No running-session discovery check was performed here.

## No-orchestrator baseline

This is a **static scenario walkthrough**, not a model-backed execution result.

### Common baseline evidence

Neither phase entry advertises itself automatically:

> `disable-model-invocation: true`  
> — both entry skills, line 4

Production additionally declares:

> `"automatic_invocation": false`  
> `"external_execution": false`  
> — `video-production-skills/manifest.json:6,15`

Current startup routing still says:

> “For video production, use the standalone `creative-production` skill…”  
> — `~/.agents/DEVELOPMENT-WORKFLOWS.md:52–53`

Pi explicitly includes that legacy entry (`~/.pi/agent/settings.json:7`). Therefore the current configuration does **not** automatically route natural-language requests through these two packages as the proposed replacement.

| Request | What existing packages provide when explicitly read | Exact missing routing behavior |
|---|---|---|
| **Preproduction only** | The director supports explicit stopping points, direct artifacts, ledger-based resume, and image-inclusive preproduction. It says not to stop image-inclusive work at text prompts (`production-director/SKILL.md:17`) and not to pass the user’s stop point (`:41`). | No public replacement selects this entry and binds the requested endpoint. The existing director still advertises final-cut ownership. Manual explicit loading can perform the bounded task; automatic replacement routing is absent. |
| **Production only** | The supervisor accepts a project, current preproduction/coverage source, batch, authority, and capability evidence (`production-supervisor/SKILL.md:9`). It resumes existing production instead of initializing again (`:13`). | No public dispatcher selects it directly, validates supplied inputs, and reports exact missing prerequisites without restarting preproduction. Its implementation also does not ingest the preproduction CSV/ledger representation directly. |
| **Both** | Each package has phase-local procedures and resume rules. | No existing entry dispatches director → validated cross-package handoff → supervisor. The director’s own table instead assigns generation and take QA to its old crew. Coverage mapping and safe writer ownership are missing at the seam. |
| **Final video, nonstop; post absent** | The director has a legacy P7 route; production provides reviewed sources and a gated handoff, not final editing. | No shared owner retains the final-master target across these packages, suppresses the old P7 fallback, and records a verified post/G5 restart point. Production cannot supply a final master, and absent receipt may block G5 before post execution even starts. |

The missing component is chiefly **scope ownership and cross-package integration**, not a lack of phase-local instructions. “Nonstop” cannot supply missing authority, tools, receipt, or post implementation.

## Required acceptance checks after design correction

1. Public entry automatically discoverable; department flags and protected package bytes unchanged.
2. Pre-only prompt request stops without generation; image-inclusive preproduction follows its actual image/QA contract.
3. Production-only missing inputs produce exact G0 blockers, not fabricated preproduction.
4. Combined route validates actual preproduction-shaped outputs and enters the supervisor once.
5. Preproduction rework preserves all existing production state.
6. Retained equipment/history resources resolve without invoking the old coordinator.
7. Same canonical public entry discovered across overlapping roots; no new collisions.
8. Final/nonstop with unconfigured post retains the final target and precise G5/post blocker; no invented receipt or final master.
9. Rollback inventory distinguishes removed registrations from preserved source/resource dependencies.

**Merge verdict: BLOCK** pending the integration-contract corrections above. Postproduction implementation is neither required nor authorized to resolve this review.