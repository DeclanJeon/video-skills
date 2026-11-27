# Stock sound sourcing — approved design and implementation plan

> For agentic workers: execute inline; read writing-skills and verification-before-completion. QA delegation only; one source writer.

**Goal:** Sound design in preproduction must actually search listed sources, compare by listening, clear rights, acquire selected files and hand off scene-linked assets—not return a website directory.
**Spec / approval:** User confirmed the preceding preproduction→post design and explicitly requested touring sites to find appropriate audio.
**Architecture:** Keep the root CSV as the one discovery catalog (all rights claims unverified). Extend the existing sound-designer entry with a disclosed sourcing recipe and two CSV record templates; extend SND for actual cue/file/rights handoff. No new crawler, player, license-verification service or postproduction implementation.
**Tech:** Markdown and CSV templates; existing browsing, media and project-ledger tools when available.

## Scope and constraints
- Own only sound-designer/SKILL.md, sound-designer/assets/SND-template.md, sound-designer/references/stock-audio-sourcing.md, two source/search CSV templates, and orchestrator references/phase-contract.md sound-handoff pointer.
- Preserve source catalog bytes, existing role metadata, SND/APR anchors, IDs and phase schemas. No post changes, commits, paid service, bulk download or runtime install.
- Real selection requires listening and item-level rights for the intended platforms/monetization/ads. Access failure or lack of listening is a truthful blocker, not an excuse to list links as acquired assets.
- Text-only scope stays text-only. Actual project media/logs belong to the work, not shared skills.

## Tasks
- [x] Baseline decision test with existing instructions: qa/sound-sourcing-baseline.md. Design can proceed but no source-search/acquisition route exists.
- [x] Add stock-audio recipe: cue briefs, category-specific multi-site search, candidate comparison, preview/full-file listening, rights evidence, authorized acquisition, decode/metadata and actual handoff.
- [x] Add search/source record templates and SND completion fields; connect catalog and recipe through the existing sound-designer entry.
- [x] Review changed instructions against baseline scenarios, including blocked sites, absent audition, unknown rights, Content ID, prompt-only and no match.
- [x] Run actual CSV/template/path/package checks and entire existing preproduction suite. Validate symlinked registration resolves same new instructions. Record runtime audition/download as UNVERIFIED (no work brief or real source-selection run).

## Completion and QA focus
Source catalog and homepage are neither chosen assets nor license proof. Search progress, candidate/cleared/downloaded/auditioned/accepted states and sources actually tried must be distinguishable. Required acquired assets must have real local files, hash/metadata, hearing evidence, explicit cue usage and rights/credits evidence. Missing required assets keep acquisition partial even when the sound plan is complete. Timing/mixing decisions are handed to post; no fake post receipt.
