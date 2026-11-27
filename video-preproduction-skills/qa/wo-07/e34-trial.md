# EX-02 — Production design for S01

**Standalone text design.** Sole story source: `evals/design/fixtures/SCR-ex02.md` (unversioned), S01 / D001–D011. The brief is a 34-second, Korean-language, 9:16 realist scene in an old small-town laundry after closing. The design keeps the counter as the divide between the siblings, with the garment rail and ironing station behind it as evidence of the work the sister describes. The storefront sign matters because it names her place in the town; the audience never needs to read it. All layout and finish details not stated in the script are proposals, not claims about a real site.

## `tmp:LOC-01` — Old laundry storefront and workroom

### plan

Use shop-relative directions: **south** is the street front, **north** the rear work wall, and **west/east** the siblings’ left/right as seen from the front looking in. These are design labels, not surveyed bearings.

- **South:** One glass customer door centered on the storefront; the front glazing is the only proposed exterior opening. A fixed shop sign sits above the door, facing the street. The warm streetlamp is outside, just east of the entrance. No second entrance or rear window is established.
- **Center:** The counter sits between the brother on the west/left and the sister on the east/right. The customer route runs from the glass door to the counter; leave the east end open as a working route to the rear. This is circulation, not an instruction for either sibling to move in S01.
- **North:** The plastic-covered hanging row runs along the rear wall. The steam ironing board stands in front of the row toward the east, beyond the counter, outside the working route. The cold fluorescent fixture is on the ceiling above the counter/work area. These are source positions only; direction, intensity and exposure belong to lighting.

### layers

From the storefront side: **foreground**, the glass-door jamb if present, then a clear entry floor; keep visual clutter low. **Midground**, the siblings and the worn counter, with an uncluttered top so the sister’s right hand can read against it without the receipt competing. **Background**, vertical folds of garment plastic and the flatter silhouette of the ironing board against the rear wall. Keep those shapes identifiable but their details subdued; depth of field is not prescribed.

### Four orientation descriptions

These describe the same proposal, not shots or tested sightlines.

| View | Visible design elements | Set elements screened or turned away |
|---|---|---|
| `#view-front` — from the south threshold, looking north | Counter between brother left and sister right; garment row beyond; ironing board toward the right; ceiling fluorescent above. | Counter front screens low workroom detail; exterior sign face is behind this view. |
| `#view-reverse` — from the rear, looking south | Back of counter and glass door beyond; warm street source outside on the door’s east side. | Rear rack is largely behind this view; outward sign face does not face the interior. |
| `#view-left` — from the west, looking east | Near counter end, with the ironing station in the north-side portion of the room; storefront remains on the south side. | Low details on the far side of the counter are subordinate to its solid body; streetlamp stays exterior. |
| `#view-right` — from the east, looking west | The side of the ironing board and the staff route sit near the rear; counter across the center, storefront to the south. | Counter body screens low far-side detail; the rear rail is only partly revealed past the ironing station. |

## `tmp:SET-01` — Laundry fit-out

**Location:** `tmp:LOC-01@draft`. Narrow single-storefront shell with the old fit-out still in use: dulled aluminum door frame, scuffed lower wall, matte floor, a waist-high laminate counter rubbed at the customer edge, an above-waist hanging rail fixed to the north wall, and a waist-high steam ironing board with a clean but worn cloth pad. Keep wear concentrated where hands and work repeat; no abandonment dressing, packed boxes or sale notices. Mount a faded, unlit sign above the glass door; retain its silhouette, but give its face no legible lettering or logo. It stays attached throughout. The south glass door is closed at start and stays closed as a design default; no door or shutter action is scripted. The shutter can remain undesigned and out of frame.

## `tmp:ENV-01` — One after-hours state

**Location:** `tmp:LOC-01@draft`. **Script:** late autumn, night, business closed; cold ceiling fluorescent against warm streetlamp light outside the glass door. **Design default (not in SCR):** dry, still weather and clear near-street visibility through the door, with the farther exterior dark and indistinct. No precipitation, fog, visible steam, or light-state change is designed across S01. Do not change the set or environment to visualize the past shifts the sister describes. No lit/open sign or new street activity.

## Props — Initial state and continuity

The dialogue IDs below locate design beats, **not** approved cuts. No `CNT` was supplied; exact visibility and any cut assignment remain open.

| ID | Initial state and home | Hand, custody and movement | Intended visibility by script beat |
|---|---|---|---|
| `tmp:PRP-01#state-a` — Receipt | One plain receipt lies face-down on the counter, off to the side of the clear center. The exposed back has no legible print. | Shop dressing; neither sibling handles it. No movement or transfer. | May register incidentally in counter coverage; never turned or featured as a readable insert. Do not attach a second narrative action to D001 or D008. |
| `tmp:PRP-02#state-a` — Hanging garments and covers | A short row of muted garments in clear worn plastic on the rear rail, without visible customer labels. | Shop custody; no hands, transfers, or change in order. | Background where the rear is included; not required to enter frame on a specific line. |
| `tmp:PRP-03#state-a` — Iron (proposed dressing) | A plain, unbranded steam iron at rest on the board’s rest; no visible steam or lit indicator. | Shop equipment; untouched by both siblings and held in place throughout. | Incidental workroom detail only; no iron insert at D006–D007 and no implication that this particular iron caused the mark. |

**Beat continuity:** At D006–D007, let the already marked **back of the sister’s right hand** be the visible evidence; it is not a prop and needs no object pickup. At D009–D010 the sister is offscreen as scripted, not necessarily out of the shop or moved to a new mark. The sign is fixed dressing: D010 refers to taking it down, but does not require an insert, a readable face, or removal. Nothing changes hands or position for D011.

**Unassigned / excluded:** The account ledger (D005) and the shutter (D003) are verbal references to past routines; neither is assigned an appearance, a hand, or a move. No contract, cash, or keys are introduced for the proposed sale. The right-hand mark is a script detail for makeup continuity, not a PRP ID. Exact prop-to-cut visibility is unassigned pending coverage, not a requirement to create cuts for this delivery.

## Text delivery packet

```yaml
dlv_for: null
artifacts:
  - {id: 'tmp:LOC-01@draft', changed: [plan, layers, four_views]}
  - {id: 'tmp:SET-01@draft', changed: [structure, materials, dressing]}
  - {id: 'tmp:ENV-01@draft', changed: [time, season, weather, visibility]}
  - {id: 'tmp:PRP-01@draft', changed: [state-a]}
  - {id: 'tmp:PRP-02@draft', changed: [state-a]}
  - {id: 'tmp:PRP-03@draft', changed: [state-a]}
consumed: ['evals/design/fixtures/SCR-ex02.md (unversioned), S01 / D001–D011']
assumptions:
  - 'One south storefront opening; sign and exterior lamp positions, finishes, and working route as proposed.'
  - 'Dry, still exterior; face-down receipt; inert iron as proposed dressing.'
conflicts: []
checks:
  - 'Text design entries use the same named door and light sources; no measured geometry or sightline verification.'
  - 'Receipt and sign are unreadable by design; every assigned prop has a home and an unchanged custody state.'
  - 'The marked right hand and the offscreen lines D009–D010 remain as scripted.'
missing_inputs:
  - 'WLD not supplied; no era, town identity, or shop brand asserted beyond the script.'
  - 'CNT not supplied; exact visibility by cut remains unassigned and does not block this text delivery.'
self_verdict: complete
```

## Action log

1. Read `production-designer/SKILL.md`, the LOC/SET/ENV/PRP templates, `docs/design/02-crew-roster.md`, `docs/design/03-artifact-index.md`, the handoff/direct-delivery section of `docs/design/01-pipeline-and-gates.md`, and `production-director/assets/DLV-template.yaml` for procedure and format, not story material.
2. Read `evals/design/fixtures/SCR-ex02.md` as the only story input. No other evaluation or fixture files were opened.
3. Drafted text only. No scene-specific spatial verification, site search, measurements, blocking test, render, prompts, media generation, tool/provider calls for production, or external action. No project files or ledger were written, and no staging was performed. The only write was this requested local session artifact.
4. The read-only Git index check was unavailable: the working directory is not a Git worktree.
