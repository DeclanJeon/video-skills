# Sound-sourcing acceptance QA

**Verdict: FAIL — one verified registered-path defect.** The sourcing decisions otherwise satisfy the six acceptance scenarios.

Read-only review of the baseline, approved plan, named skill/reference/templates, catalog headers/status, and phase-contract sound paragraph. No browsing, downloads, edits, delegation, or postproduction inspection.

**Real-web search, acquisition and audition results: UNVERIFIED.** Tests were not run; parent owns test execution.

Paths below use `S = video-preproduction-skills/sound-designer/`.

## Review

### Correct

- Actual sourcing is mandatory when requested—not a directory of homepages (`S/SKILL.md:21–22`).
- Each required audio type requires searches on at least two distinct relevant catalog sites, with blocked attempts distinguished from successful searches (`S/references/stock-audio-sourcing.md:17–22`).
- Listening requires actual hearing evidence; metadata, waveforms and playback clicks do not qualify (`S/references/stock-audio-sourcing.md:26–28`).
- Item-level clearance covers commercial use, advertising, platforms, editing, credits and source-file redistribution. Content ID is checked separately (`S/references/stock-audio-sourcing.md:32–37`).
- Completion requires every required cue to link to cleared, technically checked, finally auditioned local files. Design completion cannot conceal missing acquisition (`S/references/stock-audio-sourcing.md:41–53`).
- Search/source CSV headers support independent access, rights, download, audition and selection records, including evidence, hashes, cue timing and recipient conditions (`S/assets/audio-search-log-template.csv:1`; `S/assets/audio-source-manifest-template.csv:1`).
- SND preserves cue intent, file pins, rights/credits and explicit missing-work resume points. Director registration and post editing remain separate responsibilities (`S/assets/SND-template.md:17–48`; `references/phase-contract.md:21`).

### Finding: P1 — Catalog links fail from directly registered package paths

**Locations:** `S/SKILL.md:14`, `S/references/stock-audio-sourcing.md:5`, `S/assets/SND-template.md:24`.

The catalog references climb above the preproduction package. They work from the canonical repository and coordinator-root aliases, but this runtime normalizes those paths outside the directly registered package alias.

Verified read results:

| Entry/reference used | Result |
|---|---|
| Canonical repository catalog | Readable |
| `/home/declan/.pi/agent/skills/video-preproduction-skills/sound-designer/../../free_commercial_media_resources_50.csv` | **ENOENT**, normalized to `/home/declan/.pi/agent/skills/free_commercial_media_resources_50.csv` |
| Equivalent `.agents/skills` skill catalog link | **ENOENT**, normalized to that skills root |
| `.claude/skills` recipe’s `../../../free_commercial_media_resources_50.csv` | **ENOENT**, normalized to that skills root |
| `.pi/agent/skills` SND’s `../../../free_commercial_media_resources_50.csv` | **ENOENT**, normalized to that skills root |
| Catalog through registered `video-skills/video-preproduction-skills/...` paths in Pi, Agents and Claude roots | Readable |

The directly registered skill and recipe themselves are readable in all three roots; the defect affects their catalog escape path, not skill loading. Package-local recipe/template links remain accessible.

**Impact:** A legitimate registered entry cannot follow the supplied discovery-catalog reference using the available read tool. The mandatory multi-site workflow starts with a missing input despite the catalog being installed.

**Smallest fix:** Add explicit canonical-root resolution guidance before following catalog-relative paths, with the registered `video-skills/free_commercial_media_resources_50.csv` route as a fallback. Apply consistent guidance to the recipe and SND catalog pointer. Keep one catalog; do not duplicate it.

**Re-check:** Read the catalog starting from each directly registered package entry using the documented resolution procedure, not only through the coordinator alias.

### Fixed

None; review-only.

## Decision simulations

These describe required next actions, not executed sourcing. They assume the catalog-path issue above is corrected or the canonical entry is used.

| Scenario | Next actual action | Completion status |
|---|---|---|
| **1. 30s dialogue, restrained BGM, rain and door; files required tomorrow** | Use existing SCR/CHR/BRF and confirm only missing platform/advertising/recipient permissions. Write distinct BGM, rain AMB and door SFX cue briefs. Search at least two relevant catalog sites per type, follow individual item pages, audition and compare candidates, clear rights, then acquire only required selected files. Record hashes, decode evidence, final-file listening and cue/credit handoff. Dialogue generation remains separately approved work. | **Not complete yet.** Completion requires evidence for every required source; tomorrow’s deadline does not lower the gates. Design may complete independently. |
| **2. First site blocked; preview/listening unavailable; unknown license; deadline pressure** | Log the blocked attempt and move to another relevant site. Do not download the unknown-license candidate. If preview alone is unavailable, establish rights/download permission before acquiring a file for listening. If actual listening remains unavailable, record `audition_status=unverified` and the precise reviewer/tool resume condition. | **partial/blocked** while required rights, listening or files remain unresolved. No deadline-based clearance or invented audition. |
| **3. Text-only / no-download** | Record the scope in SND and produce design/prompts or permitted candidate descriptions without acquisition. Keep generated dialogue/effects/music instructions separate as applicable. | Requested text deliverable **can complete**. Acquisition is **not requested**, not “acquired”; no download or audition readiness is implied. |
| **4. Multiple relevant sites; no matching candidates** | Search at least two distinct relevant sites per required type; revise terms/filters and expand to further relevant catalog sources when no meaningful candidate appears. Record queries, exclusions and uncovered scope. After exhausting relevant sources, report “no suitable source acquired”; if interrupted earlier, preserve the next site/query. | **partial/blocked** for required unmatched cues. Do not silently substitute generated/paid audio or label missing sound intentional silence. |
| **5. Preview differs from final file** | Identify and pin the downloaded final file, run technical checks, then audition that final file and record its exact listening range, method and observations. Reassess cue fit and applicable item/version rights before acceptance. | **Not ready** until final-file evidence supports selection. Preview evidence alone cannot complete acquisition. |
| **6. Commercial license, but Content ID or redistribution unclear** | Record Content ID separately as unverified and resolve certificate/channel/claim requirements. Check recipient/source-file delivery permissions against the intended handoff. Seek clarification or another candidate rather than accepting commercial permission as blanket clearance. | **Selection/handoff blocked** until applicable requirements are resolved; no unrestricted source-file transfer. |

**Evidence:** Scenario 1: recipe lines 7, 13, 17–21, 41–53; scenario 2: lines 20, 28, 37; scenario 3: line 9 and SND lines 22, 43–44; scenario 4: lines 17–22; scenario 5: lines 28, 43, 53; scenario 6: lines 32–37, 51.

## Merge verdict

**BLOCK / acceptance FAIL** pending the catalog-link correction and targeted registered-path re-check.

No additional concrete contract gaps found in the six simulations. This review does not certify live websites, acquired files, listening results, or separately run tests.