# `tmp:WLD` — The laundry after closing

**Chat draft · S01 only · 34 seconds · Korean-language, 9:16 realism**

**Source pin:** `evals/design/fixtures/SCR-ex02.md` (EX-02 working screenplay; no registered `@v` or lock status supplied). SHA-256: `da771243e857f2bb36ca7fb609759ab2e5117fe13ac230806c7989ab3ab94b5f`. This is the only story source. **Script** below means established within the fiction, not independently verified fact; **Testimony** means a character’s account; **Draft choice** means a proposed visual treatment; **Unverified** means the screenplay does not settle it.

## rules

| Rule | Applies / evidence | World rule and limit |
|---|---|---|
| R1 · After closing | `S01`, opening description | **Script:** One late-autumn night in an old laundry in a provincial small town. Business is already closed. The siblings’ conversation takes place in the work space; the exterior streetlight reaches it through the glass door. **Limit:** The opening and closing hours in `D003` are remembered, not time shifts in S01. No named town, year, or jurisdiction is established. |
| R2 · A shop run by hand | `S01`, opening and action; `D003`, `D005–D007` | **Script:** The counter separates the siblings (brother on the left, sister on the right); plastic-covered hanging clothes and the steam-ironing station establish the work behind it. The sister’s iron mark is on the back of her **right** hand; she draws attention to it in `D006–D007`. **Testimony:** The shutter and ledger belong to the routine and family history she recounts. Mention does not require either object to be shown in use, nor does it establish that this is a paper-only business or a particular decade. |
| R3 · The threatened sale | `S01`, scene description; `D001–D005`, `D008` | **Script:** The brother argues for closing and selling; the sister distinguishes his possible payout from what she would lose. **Testimony:** He reports a deposit increase next month; she says she raised the shutter at six and lowered it at eleven for twenty years, while he only came at holidays to look through the ledger. These are their accounts, not a lease record or proof of ownership, shares, or a completed sale. |
| R4 · Public identity without readable text | `S01`, opening description; `D009–D011` | **Script:** If visible, the sign and receipt contents are unreadable. **Testimony:** The sister says people call her “세탁소 아줌마,” not by name. Her reference to taking down the sign is hypothetical, not an action. The sign’s function can be understood without being able to read it; `D009–D010` are expressly off-screen speech, and `D011` has no off-screen designation. |
| R5 · Two ordinary light sources | `S01`, opening description | **Script:** The ceiling fluorescents are cold; the exterior streetlight through the glass door is warm. Both qualities must stay distinct. The clothes’ plastic covers and the glass may still reflect light. The script does not specify the lamp technology outdoors, season-specific weather, or a lighting rig. |

**Period / location status:** **Unverified** — the year, exact town, local lease practice, and equipment makes or vintages. The Korean dialogue is specified; the deposit, shutter, ledger, and steam iron are story evidence, not dating evidence. Keep additions time-neutral rather than declaring the world historical or banning all modern objects. No brief or separate location/period constraint was supplied; none is needed to draft the above from S01.

## forbidden

| Applies | Keep off screen | Required presence / exception |
|---|---|---|
| `S01` · R1–R2 | No customers being served, daytime opening/closing inserts, or visible reenactment of the twenty years. No newly introduced people. | Keep the closed shop recognizably a workplace: the scripted clothes, plastic covers and ironing station still belong there. The late-night streetlight outside is not evidence the shop is open. |
| `S01` · R2 | No reversed hand mark, fresh-injury effect, or wardrobe change. Do not replace the narrated shutter/ledger work with a new digital workflow. Avoid added prominent devices, dated logos or signage that imply an unsupported year or town. | The right-hand mark is the evidence shown now; its design need only read as an old iron mark. The script’s gray/navy clothing stays unchanged; the glasses and plastic covers are not excluded by the muted look. |
| `S01` · R3–R4 | No legible store name or receipt details, including in reflections or inserts. No visible sale confirmation, newly displayed ownership paperwork, or actual removal of the sign. | The sign and receipt, if shown, may have recognizable forms. “세탁소 아줌마” and the reference to the sign belong to spoken dialogue, not a readable insert. |
| `S01` · R5 | Do not turn the whole interior uniformly warm, flatten both sources to the same color, or introduce neon/commercial gloss that competes with them. | Preserve the warm light at the entrance and the cold interior fluorescents. Local glass, metal and plastic reflections are compatible with a muted room. |

**Boundary:** This bible gives world constraints, not a floor plan, prop specification, costume design, or shot list. The left/right relation above preserves the script, not a camera axis. The screenplay’s live dialogue and no-music/no-enhanced-effects/no-narration constraints remain as written; this draft adds no sound design.

## palette

| Applies | Color and texture | Basis |
|---|---|---|
| `S01` · R5 | **Cool gray-white inside; restrained amber at the glass door.** Keep facial color legible in both; warmth should not erase the cooler room. | The cool/warm split is **Script**. Gray-white and amber are **Draft choices**, not historical bulb specifications or a locked lighting setup. |
| `S01` · R2 | **Gray and navy cloth**, backed by muted, used work surfaces, translucent plastic and subdued metal. Let seams, scuffs and soft creases suggest years of work, without making the shop look abandoned. | Gray/navy clothes, plastic covers, an ironing station and an old laundry are **Script**. The degree of wear and specific finish are **Draft choices**; no material catalog or date is claimed. |
| `S01` · R2, R4 | **Quiet contrast at small details.** Let the right-hand mark read against natural skin; keep the sign/receipt shapes recognizable without making their contents legible. | The hand detail and text restriction are **Script**. Restraint in contrast and texture is a **Draft choice**. |

**Self-check:** The closed-store look allows an illuminated work interior and warm streetlight; the matte wear treatment allows plastic and glass reflections. An unreadable sign can still represent the sister’s public identity. Neither prior work hours nor a potential sale is depicted as an event. No real-world historical claims were made, and the draft assigns no layout, prop build, or lighting setup.

---

## Tool log (trial only)

1. `read` — `world-designer/SKILL.md`.
2. Parallel `read` — `world-designer/assets/WLD-template.md`, `docs/design/02-crew-roster.md`, `docs/design/03-artifact-index.md`, `production-director/assets/DLV-template.yaml`, and `evals/design/fixtures/SCR-ex02.md`. Only the last file supplied story facts. Standalone delivery uses a temporary ID and a chat draft, not a director/ledger packet.
3. `bash` — `sha256sum -- evals/design/fixtures/SCR-ex02.md` produced the pin above. A read-only staged-file check (`git --no-optional-locks diff --cached --name-only`) could not run because the directory is not a Git worktree; `pwd`, `git --no-optional-locks rev-parse --is-inside-work-tree`, and a `.git` existence check confirmed it.
4. `write`, `edit` — this requested session output only. No project files, ledger, provider calls, or external sources.
5. `bash` — read-only validation of the saved output: required sections, temporary WLD ID, S01 and dialogue references, and the screenplay hash.
