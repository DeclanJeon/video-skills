# Video skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Install one shared video orchestrator with scoped sequential routing and a reserved postproduction interface.
**Architecture:** One discoverable root SKILL.md reads the two existing phase entry files in their original package context. Existing phase packages remain unchanged; external equipment remains registered. Post is explicitly unconfigured.
**Tech Stack:** Markdown, JSON, filesystem symlinks, local validation.
**Spec:** docs/design.md

## Global Constraints
- No postproduction implementation, edits, relocation or installation.
- No external generation, spending, publication, package installation or git push.
- Preserve phase packages and legacy source. Back up registrations and workflow pointers.
- Existing roots only: shared Agents, Pi, Codex, Claude, Gemini, OpenCode.

## Review Focus
- Pre-only must stop before generation; both must proceed past phase boundary.
- Final target with post absent is blocked, not a completed final video.
- Existing ledgers and unknown remote jobs must resume without duplicate generation.
- Retained equipment must not override new routing.
- Shared and explicit discovery must not create multiple public routers.

## Task 1: Design QA and failing baseline
- [x] Independent reviewer reads design, checks actual dependencies and captures missing-orchestrator baseline.
- [x] Integrate important findings in design and implementation.
- [x] Record static missing entry/registration baseline before authoring.

## Task 2: Orchestrator
Create SKILL.md, references/phase-contract.md, references/postproduction-slot.md, README.md, qa/scenarios.md.
- [x] Author the routing matrix and requested-target/actual-state completion contract.
- [x] Define explicit phase file entry points, handoff validation and one-writer transitions.
- [x] Reserve post role with no invented entry name/path or completion promise.
- [x] Validate links/frontmatter and exercise scenario matrix in fresh review context.

## Task 3: Safe shared cutover
- [x] Snapshot settings, workflow pointer files, symlink inventory and protected package hashes outside discovery.
- [x] Retire legacy planning/router symlinks in existing agent roots; retain equipment and unrelated skills.
- [x] Add unique video-skills links; clean Pi explicit old planning entries and update workflow pointer via exact edits.
- [x] Run real Pi discovery plus target/absence/hash checks; record results and rollback instructions.

## Task 4: Acceptance
- [x] Fresh read-only reviewer checks implementation and routing scenarios.
- [x] Resolve actionable findings and rerun validation.
- [x] Report installed roots, checks and postproduction limitation.

## Execution rulings
This is a filesystem registration migration, not a branch implementation. Work directly in the user-specified root and back up mutable global state; no worktree or git commits. The user's 'QA then proceed, leave post space' authorizes continuous execution of this bounded plan. No runtime behavior or real media generation is claimed from structural validation.
