# Orchestrator sync implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Track execution below.

**Goal:** Replace obsolete routing with contracts from the current canonical video-skills packages.
**Architecture:** One public entry reads existing phase instructions directly. Shared agent instructions point to the canonical entry instead of caching package availability.
**Tech Stack:** Markdown; Node built-in test runner (no installs).
**Spec:** User-approved four-part design in this session: routing, post intake, shared instructions/README, regression checks; latest instruction requires canonical-source identity.

## Global constraints
- Preserve all department package files, disabled flags, runtime implementations and existing untracked work.
- No install, paid generation, upload, publishing, commit or push.
- Existing registrations already resolve to canonical source; replace only divergent content, not correct symlinks.
- User requests direct update of the actively registered canonical path; use in-place edits, not a disconnected worktree.
- No delegation authorized. Static reference/registration checks are not agent-compliance or real-video tests.

## Review focus
- Pre-only/nonstop must retain the explicit endpoint.
- Production-only missing inputs must remain G0-blocked.
- Post-only must use real Handoff and IntakeRequest, not arbitrary source admission.
- Final-video route must reach the existing post entry without inventing receiver, approvals or QA.
- All six discovered registration roots must resolve to byte-identical canonical skills.

### Task 1: Canonical routing and reference regression
**Files:** SKILL.md, references/phase-contract.md, references/postproduction-slot.md, README.md, docs/design.md, qa/scenarios.md, qa/routing-contract.test.mjs.
**Interfaces:** Consumes existing production Handoff and post IntakeRequest/execution contract; produces routing references only, no new API.
- [x] Write static contract/link/registration regression checks.
- [x] Run `node --test qa/routing-contract.test.mjs`; observe obsolete route/availability failures (6 fail, 2 pass).
- [x] Rewrite root entry and post connection contract; update active design/README/scenarios and phase pointer.
- [x] Rerun checks (8 pass); compare 1,316 package hashes: initial match; final 1,315 matched, separately changed story-writer/SKILL.md preserved and current pre tests rerun.

### Task 2: Shared instruction sync and verification
**Files:** /home/declan/.agents/DEVELOPMENT-WORKFLOWS.md, qa/orchestrator-sync.md.
**Interfaces:** Consumes canonical routing from Task 1; shared agent symlinks keep one source.
- [x] Replace stale package status with canonical entry and runtime-gate pointer.
- [x] Run static checks (8), boundary tests (3), production/post package checks (clean) and local test suites (pre 273, production 154, post 438 passed).
- [x] Record evidence/limits in qa/orchestrator-sync.md, inspect diff, preserve unrelated work. Self-review only; no independent agent review performed.

## Execution record
- Design/scope approved by user. Direct canonical overwrite requested.
- No independent agent review or behavioral pressure testing authorized/performed; static checks do not establish model compliance.
