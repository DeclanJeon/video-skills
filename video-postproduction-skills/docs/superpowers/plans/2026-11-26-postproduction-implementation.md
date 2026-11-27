# Postproduction Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for proposed native execution after this plan/goal is explicitly armed. Subagent-driven execution is an alternative requiring user selection and delegation authority. Steps use checkbox tracking. No implementation starts while the goal is draft.

**Goal:** Implement the reviewed postproduction design, amended to inspect the system and existing same-program installations first, ask the user if installation is necessary, and install only after explicit plan-bound consent.
**Architecture:** Frozen typed boundaries and exact clocks; one postproduction namespace in the existing project JSON, preserving production/foreign fields through the actual shared lock/CAS seam. Separate pure planning/currentness from bounded native Craft execution and installer side effects; observations never certify current creative QA.
**Tech Stack:** Available Python3.14.4, Pydantic2.14.1, Typer0.29.0, pytest9.1.1, basedpyright; existing FilmCraft/EffectCraft/SoundCraft CLI. No dependency installation assumed.
**Spec:** `docs/design/00-overview.md` through `06-environment-and-installation.md`, including latest explicit ask-before-install amendment. Previous QA report covers the pre-amendment snapshot and is not current implementation acceptance.

## Global Constraints
- Parent is sole code/goal writer for proposed native mode; no old agents/workflows restarted. New final read-only reviewer only after authorization.
- Inspect OS/arch/resources and same app/CLI/package/desktop entry/known location before concluding installation is needed. Unknown is not absent. Reuse adequate existing installations.
- Every new install/download-for-install/upgrade/dependency/model/font/plugin setup requires an actual user question and explicit consent to the exact host/plan/scope. Goal arming, free status, generic policy or `--yes` is not consent.
- Use installed Craft tools first. No real new vendor installation unless separately inspected, proposed and approved. No media provider/upload/payment/publication, credential changes, global app upgrades, user-session takeover, or Git init/commit.
- New package and owned temporary/project QA workspaces only. Preserve templates/CSV/previous production 216-file baseline; raw template binaries must not be bundled.
- Real local synthetic native fixtures are distinct from mock installer receipts and reported semantic review. No real-media/perceptual/consent-authenticity certification from fixtures.
- Source intervals are [in,out); certified exterior handles are zero; no invented stems; no universal round-trip. Missing required input/support/evidence remains blocked/unverified.
- Non-Git workspace: replace suggested commit checkpoints with source hashes/tests/goal records. Do not create a repository/worktree implicitly.

## Review Focus
1. Launcher/PATH missing but same native program exists elsewhere → probe multiple evidence routes; reuse rather than duplicate (Task3).
2. Consent inferred from goal activation, free/project-local policy or an old/different host/plan → side effects0, ask again on changed plan (Task3).
3. Parent/bridge disappears after a native command or installer has acted → known facts durable, unknown preserved, inspect before replay (Task4).
4. Handoff selection survives but mandatory event was trimmed/hidden or actual-consumed optional becomes invalid → current coverage/QA stays closed (Tasks2/9).
5. Native export returns success despite placeholders/font fallback/wrong alpha/missing audio or wrong ID mapping → independent real-file/readback tests fail (Tasks5–9).

## File / Module Map

- `postproduction/models.py`, `errors.py`, `clock.py`: frozen external types, tagged results, rational/frame/tick/sample arithmetic.
- `intake.py`, `timeline.py`, `authority.py`: actual upstream handoff/snapshot projection, edit/event map, scoped decisions.
- `environment/{models,probe,consent,provision,installers}.py`: same-program inventory, install plan/consent, bounded installer drivers and readiness.
- `ledger.py`, `revisions.py`, `jobs.py`: same project JSON/lock seam, currentness, job facts/leases/recovery.
- `backends/{base,filmcraft,effectcraft,soundcraft}.py`: small inspect/prepare/execute/observe Interface, actual native differences and mapping.
- `media.py`, `templates.py`, `captions.py`, `quality.py`, `delivery.py`: independent probe/decode/measurement, recipes/cues, gates and package checks.
- `cli.py`, `scripts/postproduction.py`: typed local CLI; no publish/generate/implicit install command path.
- Eight role directories named by spec, `manifest.json`, `schemas/`, `examples/`, check scripts and tests. These are planned files, not present outputs.

## Task 1 — Typed boundaries and exact clocks

**Files:** create `postproduction/{__init__,models,errors,clock}.py`, project test/config metadata; test `tests/test_models.py`, `tests/test_clock.py`, shared temporary factories in `tests/conftest.py`.
**Interfaces:** frozen `Pin`, `SourceRange`, `ClockRate`, `PostIntake`, `PostTimeline`, `WorkOrder`, `PostState`, `EditAuthority`, `QualityReport`, `DeliveryProfile`, `ArtifactRef`, `JobReceipt`; `map_frame(frame:int, source:ClockRate, target:ClockRate, *, rounding:str)->int` with required `exact/floor/ceil/nearest` policy and `ClockRate(num:int,den:int)`; `ContractError(stage,detail)`.
- [x] Write tests: `test_boundary_rejects_unknown_fields_nonfinite_and_invalid_ranges` asserts malformed/NaN/negative/empty required records reject; `test_clock_exact_fractional_rates_and_48k_offsets` asserts exact 24000/1001 and 30000/1001 mapping and sample bounds under declared rounding.
- [x] Run `python3 -m pytest -q tests/test_models.py tests/test_clock.py`; retain legitimate RED.
- [x] Implement only boundary types and arithmetic; parse untrusted input and reparse model_copy at persistence seams.
- [x] Rerun GREEN; record tests and source-hash checkpoint, not a Git commit.

Task1 ruling: core Pin/SourceRange/ClockRate boundary and clocks are complete; domain-specific intake/environment/job/timeline models are defined and tested immediately before their consuming tasks, not speculative monolithic models in advance. Public names continue through models.py re-exports.

## Task 2 — Actual handoff intake, timeline, coverage and authority

**Files:** create `intake.py`, `timeline.py`, `authority.py`; tests `test_intake.py`, `test_timeline.py`, `test_authority.py`.
**Current implemented interfaces (ruling recorded in progress ledger):** `load_intake(root,request_path,ledger=None)->PostIntake` parses the complete pinned request; `build_timeline(intake,proposal=None,parent=None)->PostTimeline`; `timeline_digest(timeline)->str`; `authorize(intake,root)->None`. External edited `validate_timeline`/state work fingerprint and per-WorkOrder checks integrate at Task4/8 persistence/finishing seams.
- [x] Read actual sibling `production/{models,handoff,store}.py` and schema pins. No copied fake provider or modified sibling code.
- [ ] RED: Handoff alone lacks full coverage/LOOK; wrong scope/hash/missing files/symlink/ranges fail; handles0/no stem inventory enforced; event removed/hidden by trim/overlay fails, no anchors implies retain whole adopted range; approved overlap/nonlinear controls remain allowed.
- [ ] Run `pytest -q tests/test_intake.py tests/test_timeline.py tests/test_authority.py`; preserve RED.
- [ ] Implement versioned projection/edit map and explicit change scope. Respect exact upstream clocks/probe metadata and consumed dependencies.
- [ ] GREEN plus current-source and coverage negative fixtures; P01–P10 mapping checkpoint.

## Task 3 — Inspect, reuse, ask, consent, provision

**Files:** create `environment/` modules; tests `test_environment.py`, `test_install_consent.py`, `test_installers.py`.
**Interfaces:** frozen `ToolRequirement`, `HostSnapshot`, `InstallationPlan`, `InstallConsent`, `InstallAuthority`, `EnvironmentDecision`, `InstallReceipt`; `inspect_host(requirements:tuple[ToolRequirement,...])->HostSnapshot`; `plan_environment(requirements,host)->EnvironmentDecision`; `ensure_environment(requirements,host_snapshot,install_authority)->EnvironmentPreparation` (decision plus exact draft/action/actual-question flag); injected `Provisioner(driver,record).execute(plan,host,authority)->InstallReceipt`, `InstallRecovery(...).resume(plan,host,authority)`, `InstallRollback(...).execute(plan,host,authority)`. Lone InstallConsent cannot prove an actual question; InstallAuthority carries optional concrete plan plus AskedQuestion/response. Ruling and evidence in execution ledger.
- [ ] RED: same app found via package/desktop but missing PATH must not install; ArtCraft launcher alone is not CLI; unknown vs absent distinct; compatible installed tools reused. Current host probe must identify installed launcher+3 Craft apps/CLIs without changes.
- [ ] RED: consent None/no actual question/rejected/goal-only/free-policy/host or plan mismatch causes installer/download side effects0. Changed version/dependencies/rights/network/cost needs a new question. Correct consent permits only exact planned operations.
- [ ] RED: OS/GPU/disk/permissions incompatibility; official artifact/source mismatch; installed exit0 but smoke fails is not ready. Partial install, existing user process and shared package locks are preserved.
- [ ] Run `pytest -q tests/test_environment.py tests/test_install_consent.py tests/test_installers.py`; save RED.
- [ ] Implement safe same-program probes and bounded official Installer Adapters for selected Craft/AutoClip/Resolve/Adobe routes. Use current primary/local docs for actual recipe parameters; unverified or unsupported OS/vendor route returns explicit needs_user_action/unsupported, never fabricated installer success. Separate artifact planning/obtaining/installing/configuring/testing. Actual fresh vendor installation remains unperformed unless later explicitly approved.
- [ ] GREEN against controlled temporary installer drivers; classify those as contract fixtures, NOT vendor-install success. Inspect real host read-only; no program installation for these checks. Cover P41–P52 and P39 pre-media egress gate.

## Task 4 — Shared ledger, host lease, jobs and revisions

**Files:** create `ledger.py`, `jobs.py`, `revisions.py`; tests `test_ledger.py`, `test_jobs.py`, `test_revisions.py`.
**Interfaces:** `PostStore(path:Path).read()/transaction(expected_revision)` and narrow `record_observation(job_id,receipt,expected_revision)`; `reserve_work(state,order)->PostState`; `invalidate_dependents(state,changed_pins)->PostState`; host/tool installer lease uses real package-manager ownership.
- [ ] RED: roundtrip preserves production/foreign fields; shared actual production lock contention; CAS/external-write conflict; atomic replace interruption; facts persist before diagnostic failure; unknown native/installer process not replayed; two projects cannot concurrently mutate one host/tool target.
- [ ] RED: actual-consumed optional invalid/stale/conditional-import conflict blocks, justified unselected optional allowed, unrelated independent work retained. Old job/request facts remain immutable.
- [ ] Run `pytest -q tests/test_ledger.py tests/test_jobs.py tests/test_revisions.py` and retain RED.
- [ ] Implement same lock seam without competing registry or importing unsafe legacy `_save`; scoped immutable snapshots and currentness. Never use whole mutable ledger hash as immutable project source.
- [ ] GREEN with real temp files/processes and no system installer actions.

## Task 5 — Real FilmCraft native path

**Files:** create `backends/base.py`, `backends/filmcraft.py`, `media.py`; tests `test_filmcraft.py`, `test_media.py`.
**Interfaces:** `Backend.inspect()->CapabilitySnapshot`, `prepare(order,capability,authority)->NativePlan`, `execute(plan)->JobReceipt`, `observe(job)->JobObservation`; `probe_and_decode(root,pin)->MediaFacts`. Define shared backend types in `backends/base.py`.
- [ ] Inspect actual `filmcraft-cli describe/inspect` and package docs; no guessed resource IDs/commands.
- [ ] RED: mock process timeout/unknown and readback mismatches; `offlineMedia`/placeholder/allow-offline rejects; wrong source/clock/duration/audio/format cannot adopt.
- [ ] Run targeted tests RED, then implement allowlisted argv/no shell, exact item/clip mapping and isolated data/project/output paths.
- [ ] Run real tiny synthetic source→import→sequence/readback→export→independent full decode fixture with existing binary. Log exact source/commands/result/PID/paths; no private media or install. If unavailable, leave blocked rather than replace native editor with FFmpeg.
- [ ] GREEN + real native evidence. Probe/decode is technical, not artistic certification.

## Task 6 — Real EffectCraft composition path

**Files:** create `backends/effectcraft.py`; tests `test_effectcraft.py`.
**Consumes/produces:** same shared Backend Interface, WorkOrder and artifact mappings.
- [ ] RED: wrong comp/layer/property IDs; fabricated MOGRT compatibility; RGBA/premultiply/color/fps/duration mismatch; partial native apply and duplicated retries.
- [ ] Read actual CLI/command/property metadata, run RED, implement native project/keyframe/render path without executing untrusted template scripts.
- [ ] GREEN with existing EffectCraft on a tiny independently inspectable composition and supported alpha/plate output; verify exact frame/size/alpha behavior via independent inspection/decode. No downloaded fonts/models/plugins or copied template media.

## Task 7 — Real SoundCraft mix path

**Files:** create `backends/soundcraft.py`; tests `test_soundcraft.py`.
**Consumes/produces:** shared Backend Interface; actual track inventory and sample-offset cues; real mix ArtifactRef/measurements.
- [ ] RED: mixed stereo cannot become fake stems; nonexistent AAF import; wrong sample offset/channel/duration, missing required audio, meter-only pass and unknown bounce rejection.
- [ ] Read actual run/script/describe schema and create RED. Implement WAV/cue exchange/native mapping/bounce in isolated no-user-preferences workspace.
- [ ] GREEN with existing binary and tiny synthetic audio + picture reference. Independently decode/measure sync/channel/levels; no microphone/recording/user session or paid sound generation. Artist/listening claims remain unverified fixtures.

## Task 8 — Recipes, captions, color and finishing work graph

**Files:** create `templates.py`, `captions.py` and finishing orchestration functions in `timeline.py`; tests `test_templates.py`, `test_captions.py`, `test_finishing.py`.
**Interfaces:** `load_recipe(path:Path,root:Path)->StyleRecipe`; `map_cues(cues,timeline:PostTimeline)->tuple[CaptionCue,...]`; `prepare_finishing(state,recipe_pin,root)->WorkOrder` over explicit versioned FinishingRecipe(actual materialized picture/plate/mix IDs). Profile alone cannot authorize guessed style or invented audio. StyleRecipe/CaptionCue/typed SourceCaption source and TextRecipe native contracts are defined in their domain models; ruling/evidence in execution ledger.
- [ ] RED: absent actual font/fallback, glyph overflow/safe mask, source-text/speaker/translation changes, no word timestamps, old cues after retime, color assignment vs detection, fake metrics/attribution missing.
- [ ] Run RED, implement conceptual recipe metadata/ref pins and approved replacements; no template binaries redistributed. Font installation routes through Task3 ask/consent.
- [ ] GREEN and real native representative text/plate/mix reintegration where supported. Unsupported template/native/format behavior remains explicit.

## Task 9 — Current QA, conditional resolutions and delivery

**Files:** create `quality.py`, `delivery.py`; tests `test_quality.py`, `test_delivery.py`.
**Interfaces:** `review_artifact(state,report,expected_fingerprint,root)->PostState`; `build_delivery(state,profile,receiver,root)->DeliveryBundle` (DeliveryBundle in models).
- [ ] RED: fix merely scheduled≠resolved; video/listening unverified; final encode differs from reviewed preview; missing/replaced source/approval after render; conditional imports/visible coverage; wrong denominator or missing editable assets/rights/credentials.
- [ ] Run RED, implement PG-E and PG0–PG6 projections/current commit plus final technical validation; supplied semantics labeled reported, not authenticated human consent.
- [ ] GREEN with real CLI/library missing-source negatives and master/variant separation. Build a real local technical final package from Tasks5–8; no live story/perceptual certification.

## Task 10 — Public CLI, 8 roles, schemas/examples and P01–P52 trace

**Files:** create `cli.py`, `scripts/postproduction.py`, eight spec-named `SKILL.md`, manifest/schemas/examples, `scripts/check_package.py`, `scripts/check_acceptance.py`, `docs/acceptance-map.json`; tests `test_cli.py`, `test_package.py`.
**Interfaces:** CLI `inspect-env`, `intake`, `validate`, `plan`, `ready`, `prepare`, `run`, `observe`, `review`, `invalidate`, `progress`, `render`, `deliver`, `install-plan`, `install`. `install` requires current probe and exact external consent; no synthetic `--yes` bypass. Commands are planned until implemented.
- [ ] RED: bad JSON/path/symlink/unknown fields; package links/schema drift; 8 roles; mandatory install QUESTION in role procedure; P IDs must resolve to actual executed cases, not prose/count-only.
- [ ] Run RED, implement CLI over existing modules and metadata-only disabled-auto-invocation roles; no install/publish on import/help/validate.
- [ ] GREEN via real subprocess three-tool/consent-denial/restart/delivery flows; execute mapped cases with structural vs reported-semantic vs native-technical labels.

## Task 11 — Whole-scope verification and acceptance

- [ ] Run `python3 -m pytest -q`, `basedpyright postproduction`, package/acceptance checkers; record actual results and source hashes. P01–P52 are 52 scenarios, not an assumed test count.
- [ ] Recompare original 216 hashes and actual app/version/directory changes. Preserve user-installed programs and previous QA history.
- [ ] Freeze source/spec scope; request one authorized fresh independent final reviewer. Previous design-only APPROVE cannot satisfy this gate, and installation-policy amendments must be considered.
- [ ] Only check goal items with current evidence. Real vendor installs/other OS/live privacy/perceptual success cannot be claimed from mock fixtures; unresolved required proof blocks completion.

## Concrete RED anchors

These are minimal assertion anchors for the owning task, not implemented tests or substitutes for the negative/positive cases above. Factories belong in each task's tests/conftest; they return the public types already assigned to that task.

```python
# Task1 exact clock: 24000 source frames at 24000/1001 is 1001 seconds.
assert map_frame(24000, ClockRate(num=24000,den=1001),
                 ClockRate(num=48000,den=1),rounding="exact") == 48_048_000
# Task2 frozen intake: mutating the original file after pinning is rejected.
with pytest.raises(ContractError, match="hash"):
    import_intake(handoff_with_replaced_source_path, snapshot_path, root)
# Task3 fixture has a completed system probe confirming missing required tools.
decision = ensure_environment(missing_requirements, host_missing_tools, InstallAuthority(consent=None))
assert decision.status == "planned"  # No concrete plan exists: never manufacture an actual question.
assert runner_spy.calls == []
# With an exact bounded install_authority.install_plan but no actual asked receipt: awaiting_consent.
# Task4 compare-and-swap cannot overwrite another writer's namespace.
with pytest.raises(ContractError, match="revision"):
    with store.transaction(stale_revision):
        pass
# Tasks5-7 native fixture contracts use real artifacts rather than declared success.
assert result.status == "materialized"
assert result.backend == expected_backend
assert result.artifact is not None
assert result.native_readback.source_ids == expected_source_ids
assert probe_and_decode(root, result.artifact).frame_count == expected_frames
# Task8 actual source-text/cue mapping, not a paraphrase.
assert tuple(c.text for c in map_cues(cues, uncut_timeline)) == tuple(c.text for c in cues)
# Task9 existing render does not waive replacement-source checks.
with pytest.raises(ContractError, match="hash"):
    build_delivery(state_with_replaced_source, profile, receiver, root)
# Task10 actual subprocess rejects missing consent; no installer marker is created.
assert result.returncode != 0
assert not installer_marker.exists()
```

Task3's public EnvironmentDecision uses a `status` discriminator; a materialized Backend JobObservation exposes `status`, `backend`, `artifact` and `native_readback.source_ids`; media facts expose `frame_count`. Running/unknown observations cannot pretend to provide a materialized artifact. Source/fixture revisions and approval fields must match the frozen boundaries rather than being patched around the public seam. For audio-only fixtures inspect sample_count/channel facts instead of video frame_count. Actual native commands/parameters are learned in each adapter task, not invented here.

## Plan Self-Review / Execution Handoff

- Spec map: 00/roles→Tasks9–10; 01/intake/clock/currentness→Tasks1–2/4/9; 02/native execution→Tasks4–7; 03/craft→Tasks6–9; 04/gates/delivery→Task9; 05/P01–P52→Task10; 06/system-first/ask/consent→Task3/4.
- Public type and Interface definitions are assigned before use; installer side effects and native rendering have separate proof surfaces.
- Five Review Focus cases have owning RED tests above. Planned installer drivers are fixtures; actual native Craft work is separately required.
- Proposed execution: parent implements task-by-task (Native), one new independent final reviewer if user authorizes during goal arming. Alternative subagent-driven execution must be explicitly selected; no delegation inferred.
- Goal remains draft and no product code is created before the user's explicit activation covering this plan, scope and method. Any genuinely needed installation is inspected and asked separately; activation is not installation consent.
