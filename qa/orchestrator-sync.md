# Canonical orchestrator sync — 2026-11-28

## Symptom and repair
The current postproduction entry existed, but the orchestrator connection contract and shared agent instructions still said it was unavailable. The public description/routing also omitted post-only work.
Layer: stale routing reference/cache. Repair: use current package instructions as the authority, wire post-only/final routes to the real entry, and replace shared cached package status with canonical pointers.

## Changed paths
- SKILL.md: request routing, stage owners, explicit endpoint, continuous execution, truthful completion.
- references/phase-contract.md and references/postproduction-slot.md: actual G5 → IntakeRequest → work/QA/local-delivery connection, current schema/runtime pointers.
- README.md, docs/design.md, qa/scenarios.md: current documentation; historical evidence retained and labeled.
- /home/declan/.agents/DEVELOPMENT-WORKFLOWS.md: canonical pointers for all agent consumers. Claude/Codex/Gemini/OpenCode instruction files are existing symlinks to this file.
- qa/routing-contract.test.mjs: static contract, link, flag and installed registration-byte checks.

## Evidence
- RED: `node --test qa/routing-contract.test.mjs` before edits: 8 tests, 2 pass, 6 fail. Existing post-only/final routes, availability, connection contract and shared pointer failures reproduced. Output: /tmp/video-routing-red.txt.
- GREEN: same command after edits: 8 pass, 0 fail, 0 skipped. Includes six roots (.agents, .codex, .claude, .pi/agent, .gemini, .config/opencode), canonical public/phase realpaths and all reachable canonical SKILL.md bytes.
- Boundary: `python3 -m pytest qa/boundary-check.py -q`: 3 passed.
- Pre package: `python3 -m pytest -q`: 273 passed (/tmp/video-sync-pre-tests.txt).
- Production package: `python3 scripts/check_package.py --json`: 5 skills, findings []; `python3 -m pytest -q`: 154 passed (/tmp/video-sync-production-{package,tests}.txt).
- Post package: `python3 scripts/check_package.py --json`: ok=true, 8 roles, issues=[] (/tmp/video-sync-post-package.txt). CLI root and inspect-env help executed without installation.
- Post whole-suite: `python3 -m pytest -q`: 438 passed in 843.49s, exit 0 (/tmp/video-sync-post-full-tests.txt; /tmp/video-sync-post-full-exit.txt). The first invocation hit the 210-second tool limit with no reported failure; this is the completed full rerun.
- Protection: 1,316 existing phase-package files hashed before edits; all matched immediately after the routing edits. Final comparison after the 14-minute post suite: 1,315 matched; story-writer/SKILL.md changed separately during the session (this executor never edited it). Its current pitch-selection instruction was preserved, not overwritten. Pre tests and registered-byte checks rerun on current files. Cache/venv/tracking/Git internals excluded.
- `git diff --check`: passed.

## Limits and scope decisions
No department runtime/skill file changed. Correct symlinks were retained, not replaced with independently drifting copies. Existing unrelated untracked plans/specs were preserved. Direct in-place canonical changes follow the user's overwrite request; no worktree merge, commit or push performed.
No agent delegation, independent review, repeated fresh-context behavior tests or actual end-to-end video production performed. Static checks prove reference/registration consistency, not automatic model compliance, human audiovisual QA or all-agent session loading.
Current sessions may retain old prompt metadata; Pi needs /reload and other agents need their supported reload/new session to rediscover updated descriptions.
