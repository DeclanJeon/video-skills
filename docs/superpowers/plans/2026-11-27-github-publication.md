# GitHub Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Parent inline execution only; no delegation authorized for this request.

**Goal:** Publish the current video-skills source tree publicly with a truthful GitHub README.

**Architecture:** Root monorepo snapshot with explicitly staged ordinary files; preserve the embedded preproduction repository locally. Ignore private/local-only material without deleting it.

**Tech Stack:** Git, existing GitHub CLI authentication, GitHub Markdown/Mermaid, existing Python checks.

**Spec:** `docs/superpowers/specs/2026-11-27-github-publication-design.md`

## Global Constraints
- Public `DeclanJeon/video-skills`; main branch; no forced push, install or global registration.
- Preserve internal Git history/index and approved postproduction source bytes.
- Exclude secrets, caches, external symlink, reference originals and scratch archives.

## Review Focus
- Embedded repository becoming a gitlink: staged mode160000 must be absent.
- Credential or private bundle leakage: inspect candidate/index paths and secret indicators before remote creation/push.
- Misleading README: distinguish local recorded tests and reserved post integration from live CI/end-to-end completion.
- Local-only reference inputs: document exclusions instead of claiming every public-clone test is self-contained.
- Remote mismatch: verify public visibility and remote HEAD equals local main.

## Tasks
- [ ] Finalize README, ignore policy and public scope documentation; inspect local links.
- [ ] Initialize root Git, preserve nested HEAD/index, stage explicit ordinary files and audit staged content.
- [ ] Run existing package/boundary checks, verify frozen post source, create atomic source/docs commits.
- [ ] Create public remote, push main without force, verify remote visibility/HEAD/README and remaining status.
