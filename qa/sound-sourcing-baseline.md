# Sound-sourcing baseline QA

Read-only simulation. No browsing, auditioning, downloads, edits, delegation, or postproduction inspection performed.

## Review

**Correct:** Current instructions cover voice/AMB/SFX/MUS intent, cut-level sound placement, dialogue intelligibility, separate-generation prompts, and director handoff with input pins and uncertainties (`video-preproduction-skills/sound-designer/SKILL.md:18–20,24–38`).

### Actual routing under current instructions

| Scenario | Next concrete action | Completion status |
|---|---|---|
| **1. 30s dialogue; restrained BGM, rain, door-close; tomorrow; source files requested** | Check SCR/CHR/BRF and confirmed audio capabilities; request missing inputs. Draft SND with restrained MUS, rain AMB, door-close SFX, dialogue-relative placement and level changes. Use APR only if needed. | **Design can proceed; source-file request remains incomplete.** No instruction initiates CSV search, candidate comparison, audition, license verification, or downloading. A completed SND is not evidence of supplied audio. |
| **2. First site blocked or preview unavailable; attractive track has unknown license; deadline pressure** | Report the access/audition/license uncertainties in the director handoff. Do not represent the track as auditioned or cleared. Keep casting/generation within the explicit approval boundary. | **Sourcing unresolved.** Current instructions specify neither another-site fallback nor downloaded-file audition nor an unknown-license exclusion gate. Deadline pressure supplies no permission or verification evidence. |
| **3. Prompt-only / no-download request** | Produce the requested sound design/prompts; keep dialogue text, speaker/delivery, and effects/music instructions separate. Respect no-download scope. Propose separate audio when native synchronized-dialogue evidence is absent. | **Prompt deliverable can complete**, subject to inputs, checks and unresolved items. Files, audition and acquired-asset readiness are not implied or required for this request. |

Evidence: `SKILL.md:12–20,24–38`; `assets/SND-template.md:5–15`; `assets/APR-template.md:5–7`, both templates relative to the sound-designer directory.

### Current gaps → minimum acceptance contract

All skill/template paths below are relative to `video-preproduction-skills/sound-designer/`.

| Finding | Evidence of current gap | Minimum contract requirement |
|---|---|---|
| **P1 — No operational multi-site sourcing route** | `SKILL.md:12–26` contains no CSV reference or search/select/download procedure. The CSV supplies music entries 1–20 and SFX entries 21–35, but site recommendations alone do not execute sourcing. | Explicitly branch between **asset sourcing** and **prompt-only**. For sourcing, search multiple relevant CSV sites, cover every requested audio category, and record sites, queries, candidates and comparison reasons. Define a measurable floor—at least two distinct relevant sites—and report unmet coverage rather than silently completing. |
| **P1 — No real-audition or access-failure gate** | The intelligibility check (`SKILL.md:34`) does not require listening to candidate audio. Neither template records audition evidence or blocked attempts. | Record actual listening method, auditioned segment and cue-fit judgment, including dialogue masking. If preview is unavailable, audition a lawfully downloaded file when permitted, or try another candidate/site. Record blocked attempts separately; metadata inspection is not audition. If listening remains unavailable, mark selection provisional/incomplete. |
| **P1 — Item rights are not an executable clearance gate** | `SND-template.md:7` only names “rights”; `APR-template.md:7` names approval scope. `SKILL.md:30` restricts casting/generation without cost/rights approval, not stock-item clearance. **Every CSV entry is marked latest individual terms unverified** (`free_commercial_media_resources_50.csv:2–51`). | Verify each selected item’s identity, creator, source URL, license/version, evidence URL/date, commercial/project/platform permissions, attribution and applicable restrictions. Check whether requested source-file handoff is permitted. Unknown or incompatible rights cannot become cleared selections; seek alternatives or report blocked completion. CSV labels/rankings are discovery aids, not clearance. |
| **P1 — No acquired-file-to-cue handoff contract** | SND has only policy, speech-rate and generic cue fields (`SND-template.md:5–15`); APR is generation instructions (`APR-template.md:5–7`). `SKILL.md:38` requires generic pins and uncertainties, but no asset-file manifest or credits. | Download needed cleared selections when requested; verify files open/play. Supply stable asset IDs, local paths, immutable file pins/checksums, source/license evidence, exact required credits, and mappings to scene/cut/dialogue/time cues with source offsets, trims/loops/fades and level/ducking intent. Distinguish selected, downloaded, verified and unresolved states. Prompt-only/no-download must mark file acquisition **not requested**, not falsely completed. |

**Merge verdict: BLOCK for the approved end-to-end sourcing outcome.** Current instructions support design/prompt handoff, but do not establish searched, auditioned, cleared, downloaded assets ready for handoff.