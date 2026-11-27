# Sound sourcing validation

## Scope
Approved skill/template update, not source selection for an actual film. No websites searched, music previewed, files downloaded, rights cleared, new dependencies installed, media generated or postproduction source modified in this change.

## Baseline and authoring checklist
- [x] Existing instructions decision-tested: qa/sound-sourcing-baseline.md (design-only procedure had no actual acquisition route).
- [x] Existing skill name/description/disabled flag preserved; no new public skill.
- [x] Root CSV is the only catalog; no duplicated list or invented rights status.
- [x] Real multi-site search → candidates → listening/comparison → item rights → authorized acquisition → source/cue/rights handoff prescribed.
- [x] Independent status fields distinguish rights/download/listening/selection; design and acquired-source completion are separate.
- [x] Blocked sources, absent audition, no-match, Content ID, restricted redistribution and text-only scope have explicit branches.
- [x] Existing role IDs, SND anchors, APR and writer ownership preserved.
- [x] Post implementation and package registrations untouched.
- [x] Independent after-state review completed: all six behavior simulations passed; one registered-path defect reproduced and corrected by parent. No independent re-review claimed; targeted actual read-tool regression passed after correction.

## Exercised checks — PASS
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider` in preproduction: **224 passed**, qa/sound-sourcing-tests.txt.
- `python3 scripts/check_skills.py --json`: 20 skills, no findings; description-token estimate unchanged (612).
- CSV SHA-256 unchanged: e0a36c886e4795e00e8ec3808ac6c348854f931fc51010fb32c43f1dba493433. 50 sources, 35 in audio categories.
- Both new CSV templates parse with unique/nonempty headers and no fictional rows (search 15 fields, source manifest 47 fields).
- Initial pathlib.resolve path check was insufficient: actual read tool normalized the registered alias's ../../ catalog escape before resolving symlinks. This gave ENOENT and was reproduced in the session.
- Corrected the three catalog pointers to the one canonical absolute source; documented canonical resolution and the registered video-skills/<catalog> fallback. No catalog copy added.
- Actual read-tool after-state checks: all three documents in each of six directly registered phase aliases lead to readable canonical catalog (**18 reads PASS**); all six registered coordinator catalog fallbacks also read successfully (**6 reads PASS**).
- Shared Agents, Pi, Codex, Claude, Gemini and OpenCode aliases retain the same edited entry and recipe. Full pre suite and package structure check rerun after correction (224 passed / no findings).

## Limits / UNVERIFIED
- Live source search, preview/final-file listening, per-item rights, actual downloading, real project asset registration and end-to-end post handoff are UNVERIFIED. A real work brief and supported tools/authority are required; local tests do not certify those capabilities.
- CSV templates are record formats for the skill workflow, not a newly implemented runtime gate or general crawler.

## QA execution incident
Retained baseline run resume returned `Async run not found` for cd3c345d-1ea0-484c-bed2-48303a8080cf. Reported in session, checked changed-file/backup state, then made one fresh read-only reviewer launch through the same subagent tool (0e10d699-6a42-4826-bb5a-ee6a69c99439). No alternate CLI orchestration used.

Backup: /home/declan/.local/state/video-skills/sound-sourcing-xo9rnQqT.
