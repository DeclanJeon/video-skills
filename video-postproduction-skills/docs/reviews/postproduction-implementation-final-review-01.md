# Final implementation review

## Review

**Verdict: NOT APPROVED — BLOCK.**

Four Important defects and one non-blocking Minor defect remain. No fixes were applied.

This verdict concerns the accepted local technical/fixture implementation, not universal vendor, interchange, perceptual, or legal certification.

### Source binding

Exact source-manifest SHA256:

`a5efe8908d794dd891729991ac5c478339ccd3ef7e59d3c249ad68572cfefbc7`

At my request, the parent executed read-only integrity checks before review and after all reproductions:

- Current source snapshot: **231/231 files identical**; no added, missing, or changed scoped files.
- Protected dependencies: **216/216 unchanged**.
- Frozen and live goals: byte-identical, SHA256  
  `8ab90c8e80cfc3d5dd934dc0a577a12e5518f4eb7f9aa24c392051d1ad3c908f`.
- No source drift or ownership conflict was reported.

These were **parent-executed checks**, not reviewer-executed hashes.

## Correct

- **Strict boundaries and exact clocks:** immutable, extra-forbidden models and explicit rational conversion/rounding are implemented in `postproduction/common.py:16–24` and `postproduction/clock.py:18–40`.
- **Actual upstream admission:** intake checks the production schema, snapshot, Handoff, approvals, physical media, authority, and coverage rather than accepting a standalone Handoff (`postproduction/intake.py:40–91`).
- **Shared publication seam:** post uses the production public lock path and matching flock protocol, preserves foreign namespaces, and fsyncs atomic publication (`postproduction/ledger_io.py:18–78`; protected dependency `../video-production-skills/production/store.py:56–86`).
- **Known process facts precede diagnostics:** narrow observation publication and native stage ordering preserve facts through later failures (`postproduction/ledger.py:104–122`, `postproduction/backends/filmcraft.py:103–125`). Actual fault regressions cover this in `tests/test_publication_faults.py:11–62`.
- **Consent is not inferred:** exact question/response, host, and plan checks are explicit (`postproduction/environment/consent.py:45–67`). The CLI requires an actual terminal question and digest response (`postproduction/cli_environment.py:62–86`).
- **Meaningful negative tests exist:** consumed-optional invalidity, producer lineage, required-occurrence coverage, unused conditional corrections, offline/warning diagnostics, source drift, and replay refusal are tested.
- **Evidence labels are appropriately bounded:** technical fixtures remain distinct from reported acceptance and authenticated human/legal facts. The package documentation does not turn the acceptance map into 52 fully verified real-media scenarios.

## Findings

All reproductions below were independently requested and designed during this review, then **executed by the parent** because the reviewer’s tools expose no command runner. They used owned temporary synthetic fixtures, existing programs, and no source or canonical-evidence edits. Each command exited zero; that indicates successful reproduction, not product correctness.

### 1. Important / P1 — Finishing can certify the wrong branch’s picture order

**Location:** `postproduction/finishing.py:35–56`; downstream verification at `postproduction/backends/finishing.py:146–157`.

`compile_finishing` checks that picture and mix artifacts have the right media kinds, but does not establish that their edit content corresponds to the destination branch. Current producer lineage only proves that the producer remains valid for its **own** decisions.

**Reproduction:**

1. Build the actual three-app fixture with explicit branch and reorder authority.
2. Commit a valid clean timeline ordered `C3,C2,C1`.
3. Finish that branch using the existing main picture and mix, ordered `C1,C2,C3`, without plates.
4. Run and materialize normally; submit the reported-semantic fixture QA.

**Observed:**

- Expected first source: blue `C3`.
- Actual frame-12 center: **`[253,0,0]`**, red `C1`.
- Native result: `succeeded`, materialized.
- **PG-E and PG0–PG6 all PASS**, `scope_passed=true`.

This is a technical canonical-to-native binding failure, independently demonstrated by decoded pixels—not a demand for automated story judgment.

**Correction:** verify picture edit-content equivalence against the destination branch, including source order, ranges, and timing. Bind the mix’s picture lock and mapped plates/captions appropriately. Preserve legitimate cross-branch reuse when equivalence is actually established; simple branch-name equality would unnecessarily reject valid clean reuse.

Add the reversed-branch negative beside the existing unchanged-order clean control in `tests/test_variant_delivery.py`.

### 2. Important / P1 — Portable installer smoke cannot see its installed executable

**Location:** `postproduction/environment/native_smoke.py:123–137`; sandbox mounts at `postproduction/backends/process.py:88–101`.

The smoke sandbox includes FFmpeg in its read roots, but omits the supplied installed executable and portable payload. Private `/tmp` hides temporary targets; ordinary project-local targets are likewise not mounted.

**Reproduction:** copy the existing FilmCraft CLI into an owned temporary portable fixture, verify its host `--version`, then call `NativeSmoke.run` with that executable.

**Observed:**

- Host execution: exit **0**, `filmcraft-cli 0.20.1`.
- Smoke: `passed=false`, `network_denied=true`.
- Actual failure: `os.execv` → **`FileNotFoundError`**.

Existing smoke tests use `/usr/bin` executables (`tests/test_native_smoke.py:8–15`), already visible through `/usr`; they miss this supported portable route.

**Impact:** a valid project-local portable installation cannot reach readiness through the supplied CLI smoke path.

**Correction:** mount the exact verified portable payload read-only, including required sibling libraries/resources, without broadening access to unrelated files. Add an owned non-system-location smoke regression.

This reproduction was an existing-binary visibility test, **not a new vendor installation**.

### 3. Important / P1 — FilmCraft output can violate the declared audio codec and still pass final QA

**Location:** `postproduction/backends/filmcraft.py:73–74,146–148,174–177`; `postproduction/quality.py:80–87`.

Picture preparation validates container, video codec, and channel declaration, but ignores `profile.audio_codec`. Final PG5 checks audio presence, not its actual codec.

**Reproduction:**

1. Create actual synthetic sources with audio.
2. Declare `audio_codec="flac"` and correctly repin both profile and authority.
3. Execute and materialize the normal FilmCraft picture route.
4. Independently inspect the output codec and evaluate properly scoped fixture QA.

**Observed:**

- Declared audio codec: **FLAC**.
- Actual ffprobe audio codec: **AAC**.
- Native result: `succeeded`, materialized.
- **All gates PASS**, `scope_passed=true`.

**Impact:** the implementation reports technical profile compliance despite producing an explicitly different format.

**Correction:** reject unsupported audio profiles before dispatch, as finishing already does, and independently verify final audio codec/rate/channel layout against the profile at PG5. Add a normal audio-bearing picture-master negative—not only finishing tests.

### 4. Important / P1 — Supplied style attribution disappears from delivery

**Location:** `postproduction/style_models.py:40–43`; `postproduction/delivery.py:20–24,66–74`.

`StyleRecipe.attribution` is accepted but has no runtime consumer. Delivery’s provenance summary and rights record do not preserve the consumed style’s supplied credit text.

**Reproduction:** supply unique attribution `REVIEW_REQUIRED_CREDIT_8291` in the actual consumed text style; complete native finishing, current QA, and a normal master-only bundle.

**Observed:**

- Supplied attribution remained present in the source style.
- QA passed and the bundle was created.
- All **six bundle files** were scanned.
- The supplied credit appeared in **none** of them.

**Impact:** a supplied credit obligation is silently dropped despite successful QA/delivery. This concerns preserving declared conditions, not authenticating a legal issuer.

**Correction:** collect attribution and relevant rights provenance from the actual main/variant producer closure and emit receiver-facing attribution records. Gate required omissions and preserve any explicitly required presentation scope rather than assuming a metadata credit always suffices.

### 5. Minor / P2 — Current delivery progress ignores invalidated required variants

**Location:** `postproduction/progress.py:47–62`.

Delivery progress reevaluates only the main artifact’s QA and stored bundle hashes. It does not reevaluate `record.contract.variants`.

**Reproduction:** record a real main-plus-clean bundle, then invalidate only the clean variant through `record_invalidation`.

**Observed:**

- Main QA remained passing.
- Variant QA became failing; variant PG5 was `fail`.
- Historical bundle and record correctly remained preserved.
- Main `technical_fixture_deliveries` incorrectly remained **1**, unchanged from before invalidation.

**Correction:** distinguish historical delivery facts from current complete delivery counts. Revalidate every contracted variant and applicable current contract conditions before counting completion. Keep the historical record and bytes.

This is non-blocking independently because new delivery construction already checks variants; it nevertheless misreports current completion.

## Examination and execution provenance

### Personally examined

- Frozen goal, live-goal opening, freeze envelope, implementation plan, all design documents 00–06, operations document, and progress/rulings.
- Root skill, **all eight complete role skills**, and complete shared execution contract.
- Runtime paths covering intake, authority, clocks, timeline/event maps, currentness, lineage/invalidation, ledger/jobs/materialization, environment discovery/consent/provisioning/recovery, native adapters, fonts/captions/color/audio, finishing, loudness, QA, delivery/editable relinking, progress, CLI, package checks, and acceptance tracing.
- Relevant tests, including the latest conditional/native-guard/publication/loudness/variant regressions.
- Manifest, schema catalog/checker implementation, examples, recorded package/type/acceptance results, verbose suite conclusion/durations, and JUnit header.

This was targeted whole-scope review, **not a claim that every scoped file received exhaustive line-by-line inspection**.

### Executed during this review

I executed **no commands or tests personally**: available tools were read/search/list and supervisor coordination.

At my request the parent executed:

- Initial and final integrity/protection checks.
- Actual reversed-branch finishing reproduction.
- Portable executable smoke-visibility reproduction.
- Actual wrong-audio-codec reproduction.
- Actual attribution-loss bundle reproduction.
- Actual stale-variant progress reproduction.

Full commands and outputs were returned through the managed supervisor tool transcript.

### Accepted recorded proof

The recorded verbose checkpoint concludes **404 passed in 1676.58s**. The JUnit header records 404 tests, zero failures/errors/skips. Recorded basedpyright output is zero errors/warnings/notes; package check is successful; acceptance check reports **52 IDs mapped to 300 executed passing cases**, explicitly not perceptual certification.

I did not rerun the full suite or type checker. The earlier 900-second timeout is **not** treated as a pass. Ruff was absent; no lint pass is claimed.

The new failures expose missing coverage despite the genuine recorded suite success.

## Rubric and constraint assessment

| Area | Assessment |
|---|---|
| R01–R02: boundaries, clocks, production admission | Substantial source and regression support. |
| R03, R08–R10: canonical/native correspondence | Qualified native paths exist; findings 1 and 3 prevent complete acceptance. |
| R04–R05: inspect/reuse/question/consent | Explicit fail-closed ordering; unknown is not absence. |
| R06: provisioning/readiness/recovery | Useful bounded contracts; finding 2 blocks the portable readiness path. |
| R07: facts, lineage, revisions | Strong separation and fault coverage; finding 5 affects current delivery reporting. |
| R11–R12: styles, gates, delivery | Substantial implementation; findings 1, 3, and 4 leave technical/rights-completeness gaps. |
| R13–R14: CLI/package/schema/trace | Recorded checks support their bounded structural and executed-case claims, not exhaustive requirements satisfaction. |
| R15: independent final review | **Not satisfied: NOT APPROVED.** |

No repository edits, installs, downloads, Git setup, extra reviewers, protected-source changes, or user-media processing were performed by this reviewer. Parent reproduction reports likewise describe only owned synthetic temporary work.

## Role-policy assessment

All eight roles explicitly require the shared execution contract. Its lines `7–10` require inspection, a real question, exact consent, and inspection before recovery; lines `22–24` separate fixtures from perception and deny unsupported capability claims.

| Role | Safe interpretation under the four pressure cases |
|---|---|
| Supervisor | Ask before any missing free tool/font installation; investigate unknown jobs; request exact final playback/listening evidence; return unsupported requirements to their owner. |
| Picture editor | No install from goal approval; no replay through the shared contract; return QA rather than declaring export final; request verified conform/reframe support. |
| Motion compositor | Ask before font/program setup; preserve partial jobs; RGBA/readback is technical evidence only; do not execute or promise MOGRT compatibility. |
| Color finisher | Ask before dependencies; inspect uncertain work; tags are not perceptual PASS; do not imply an unimplemented grade/conform route exists. |
| Sound editor/mixer | Ask before dependencies; preserve unknown bounce facts; waveform/meters are not listening; do not invent AAF, resampling, or stems. |
| Caption editor | Ask before fonts; inspect partial jobs; glyph/contact-sheet checks are not final viewing; reject unsupported timing/template/reframe assumptions. |
| Finishing operator | Ask before missing tools; inspect partial/offline/manual changes; exact final QA remains required; unsupported output transformations need a verified route. |
| QA | No installation without consent; no pressured rerun; explicitly return `unverified` without actual playback/listening capability; do not certify unsupported delivery formats. |

**No actionable unsafe role-policy instruction was identified for these bounded cases.** Some roles rely on the mandatory shared contract for unknown-job handling rather than repeating it locally; reading the roles together with that contract gives a safe next action.

This is one reviewer’s adversarial interpretation, **not** repeated fresh-agent behavioral testing or statistical compliance certification.

## DECLINED TO JUDGE

- Authenticity of human viewing/listening, legal rights, or installation-consent issuers: outside the accepted technical verification boundary.
- Genuine new vendor installations, other operating systems, Adobe/Resolve/AutoClip execution, and universal interchange: not demonstrated by these fixtures.
- Arbitrary 9:16 reframe/conform, original MOGRT fidelity, general grading, and universal fonts/plugins: not qualified by the implemented routes.
- Real-user-media privacy/perceptual suitability, provider/cloud/publication behavior, and broad performance guarantees: not exercised or authorized.
- Repeated fresh-context role behavior and lint compliance: no such behavioral experiment or available Ruff run.

## Merge verdict

**BLOCK / NOT APPROVED.** Resolve findings 1–4 with regression tests, address or explicitly track finding 5, refresh affected evidence and source freeze, then obtain a re-check. The existing 404 passing tests remain valid historical evidence—not approval of the defective cases above.