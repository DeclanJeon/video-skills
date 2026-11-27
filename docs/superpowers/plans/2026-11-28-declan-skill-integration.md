# Declan Skill Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Track steps below.

**Goal:** Integrate only the approved attention/order/look-comparison guidance into existing crew skills.
**Architecture:** film-editor owns A/B in its existing edit layer; concept-benchmark owns conditional C in BRF/BMK/BOR. Preserve current role boundaries and other in-flight changes.
**Tech Stack:** Markdown; existing preproduction package checker and pytest.
**Spec:** [Approved design](../specs/2026-11-28-declan-skill-integration-design.md); user approved implementation in this session.

## Global Constraints
- Direct canonical source update requested; in-place changes, no worktree migration/commit/push.
- No new skill, schema, gate, ledger, renderer, dependency, external generation or installation.
- Preserve original disabled flags/descriptions and all unrelated edits.
- No delegation authorized. Reference audits and author walkthroughs are not fresh-context behavioral tests or actual media QA.

## Review Focus
- Normal dialogue and single emphasis: no new required form.
- Approved simultaneous emphasis and result-first explanation: preserve intent.
- Planned timings: never fabricate measured speech timestamps.
- Already locked visual style: do not restart selection.
- Missing samples/unsupported effects: no unauthorized generation or support claims.

### Task 1 — Film editing guidance
**Files:** video-preproduction-skills/film-editor/SKILL.md.
**Consumes/produces:** Existing CNT/sound/edit layer; no new interface.
- [x] Snapshot actual current instructions and audit missing explicit A/B contract (source audit, not behavioral baseline).
- [x] Merge existing approved explanation timing with conditional attention/diagram guidance once.
- [x] Author review of A1–B3 and unsupported-backend boundary; preserve normal cuts and phase ownership. Fresh-context behavior remains unverified.

### Task 2 — Conditional look comparison and verification
**Files:** video-preproduction-skills/concept-benchmark/SKILL.md; video-preproduction-skills/CHANGELOG.md; qa/declan-skill-integration.md; approved design status.
**Consumes/produces:** Existing BRF/BMK/BOR; change record and evidence.
- [x] Audit C source baseline; add only controlled-comparison and authorization gaps.
- [x] Author review of C1–C3; package checker 20 skills/findings=[]; pre pytest 273 pass; registration checks 8 pass.
- [x] Review exact before/after diffs, local links/frontmatter unchanged, other 18 pre SKILL hashes preserved.
- [x] Record actual checks and behavioral/media verification limits in qa/declan-skill-integration.md. No compliance PASS from phrase checks.
