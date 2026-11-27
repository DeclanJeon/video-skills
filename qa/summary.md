# Cutover acceptance — 2026-11-27

## Delivered
- Public entry: `SKILL.md`, automatically discoverable.
- Same canonical root registered in shared Agents, Pi, Codex, Claude, Gemini and OpenCode skill directories.
- 89 legacy planner/resource registrations removed (symlinks only); 64 old equipment/history registrations retained.
- Six resource-only auditor aliases preserve `video-production-assets/scripts` without exposing its old SKILL.
- Pi explicit paths and the one shared workflow source updated. Claude/Codex/OpenCode/Gemini instruction symlinks already point to that shared source.
- Postproduction reserved/unconfigured. No implementation, move, registration or invocation of that package.

## Evidence
- Design QA: `design-review.md`; important findings integrated.
- Fresh decision review: `acceptance-review.md`; 9/10 initially passed, combined-route findings corrected.
- Targeted independent recheck: `acceptance-recheck.md`, PASS for L-cut, prerequisite separate-audio sequence and resource locators.
- Existing phase suites after cutover: preproduction **224 passed**, production **154 passed**; logs `preproduction-tests-after.txt`, `production-tests-after.txt`.
- Synthetic boundary suite **3 passed**: `python3 -m pytest qa/boundary-check.py -q -p no:cacheprovider`.
- Package structure checks: 20 pre skills and 5 production skills, no findings.
- Installed Pi skill loader across all six roots: exactly one public canonical video-skills, no creative-production/video-production-assets advertisement and no new diagnostics (`discovery-after.json`).
- Three existing unrelated raw-loader diagnostics remain: malformed frontmatter in kr-yt-hook and kr-yt-series-packaging, and flucto-media-research collision between shared/Claude roots. They predate this cutover; not changed.
- Registration checks PASS: `registration-check.json`; exact original link targets and config copies in migration snapshot.
- Original protected snapshot equality **FAIL**: 14 preproduction files changed during this session outside migration writes. The new 2026-11-27 continuity changelog and later mtimes corroborate concurrent work. Preserved those changes and reran current pre suite (224 passed); did not restore old bytes. Production source comparison has no differences. Post was not inspected during cutover verification.

## Limits
These are routing contracts, structural checks, decision simulations and local tests—not actual video generation, media artistic QA, paid-provider certification or full end-to-end final-master delivery.
Only installed Pi's filesystem loader was exercised. Other harness skill registrations and common pointers were checked on disk; Claude/Gemini executables are not on this shell PATH. Existing live sessions need reload/new session.
No pushes, runtime installation, external transfers, generation or publication were performed.

## Backup / rollback
See `migration.json` for exact removed/created link inventory and backup location. See `../docs/rollback.md` for conflict-aware restoration. No existing phase-package source should be rolled back by this migration.
