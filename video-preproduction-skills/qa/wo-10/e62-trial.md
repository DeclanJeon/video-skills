# X-3 fresh image prompt trial — S01-C02-P2

**Result: draft delivered; image lint exit 3 (unverified).** The project index and design pins support the shot, but X-3 has no registered sheet baseline or rendered reference images. This is not an approval or a generation-ready packet.

## Source decision and chosen still comparison

The `S01-C02` index row lists one visible performer (`CHR-01@v1`, `WRD-01a@v1`), `CAM-02@v1`, both props and no sheet assignment. The STB places P2 at **7.4 s global**, the end panel in the **5.0–8.0 s** second segment. This is a single held image of the first step toward screen right: the teal canopy is already fully open above the right hand, the leading charcoal toe points out to the rain, and neither recess in the central rack is occupied. The frame stays on the original low three-quarter axis. The identity block reproduces the registered Korean character and wardrobe sections; the surrounding direction is English. The Korean is canonical source text, not dialogue, signage or an added note; its wardrobe continuity wording is retained verbatim.

I opened the actual local chosen `production-look-v5/panels/S01-C02-P2.png` (540×960, SHA-256 `1a8e58cbc0ea98ddc0041cfa88861a5cf9afb96bf7d9c8d88c39e4201600fc2a`) for comparison only. It reads as a low vertical composition with the shelter to the left, a central empty two-slot rack, a teal canopy held above an ochre sleeve, and a dark cropped shoe/leg toward the rain side, without showing a face or readable text. It also shows a brown rack and dimensional, CG-like shading rather than the pinned dark-gray rack and paper-textured 2D cels. The sleeve and shoe look detached from the performer at this crop, the umbrella hook is not clearly legible, and the far-right shoe crop makes the toe direction harder to verify. The fresh text follows the design pins and asks for a connected cropped silhouette, readable rightward toe, hooked grip and dense rain at the shelter edge. No pixel feature from the still was used to override a pin, and the still is not a reference input or sheet baseline.

## Exact prompt — `IMG-S01-C02-P2.md`

```text
[style]
Hand-drawn 2D cel animation still on subtly textured paper. Deep slate-blue shelter shadows and blue-gray wet surfaces, with muted ochre, plum and teal reserved for their established designs. Matte color, crisp contours at points of contact, no glossy highlights.

[framing]
Vertical 9:16. Keep the open canopy, gripping hand, empty rack slots and leading toe legible together inside the central 80 percent of the frame; leave the outer margin for stray drops. Keep the head out of frame without making the passerby stoop.

[shot]
Fixed low, waist-height three-quarter medium shot, with a 35 mm lens feel and moderate depth of field. Hold the canopy edge, hand, rack recesses and leading toe in readable focus; soften the far wall and pavement.

[identity]
30대 성인, 좁은 어깨, 둥근 턱, 짧은 검정 머리. 오른손 엄지 밑 점 하나; 우산 손은 오른손.
황토색 무광 방수 우비, 넉넉한 일자 소매에 좁은 단추 없는 커프, 검회색 고무창 신발; 짧은 검정 머리, 무분장, 가방 없음. 소매 밑단에 물방울; S02에서도 같은 핏과 습기.

[action]
Freeze the first step into the rain: the lead charcoal shoe points right, the elbow is extended, and the grip is relaxed but secure under a fully open teal canopy. Individual drops hang just beyond its outer edge. The release of tension shows in the wrist and sleeve, not the face.

[composition]
Visible people: 1
Axis: Shelter on screen left, rack at center, wet sidewalk on screen right; the passerby departs toward screen right without crossing the axis.
Show enough of the cropped coat and leading lower leg to read the sleeve, gripping hand and shoe as parts of one passerby. The wrist and toe carry the direction; no face or direct eyeline is visible.

[setting]
An anonymous roadside shelter on an overcast late-spring day: matte gray awning and soft wall on the left, a dense vertical drip line at the eave, wet blue-gray sidewalk and shallow puddle on the open right. Heavy rain falls outside the shelter only; under cover, show residual drops. Diffuse daylight from screen right leaves a soft blue-gray reflection across the wet pavement and teal cloth, with faint bounce under the awning and no separate rim light.

[props]
The passerby's right hand holds the teal hooked handle, the shaft upright and the plain teal canopy fully open overhead. The other hand stays out of frame. Center the waist-high dark-gray manual sharing rack with its drip tray and two umbrella-shaped vertical recesses clearly empty: the borrowed umbrella is out of the left slot, and the right has stayed empty.

[negative]
No text, no readable signage, no captions, no lettering, no watermark, no logo, no panel labels, no speech bubbles, no extra person or background traffic, no oversized umbrella, no electronic lock or controls, no photorealism or glossy rendering.
```

## Exact sidecar — `IMG-S01-C02-P2.map.json`

```json
{
  "id": "IMG-S01-C02-P2",
  "panel": "S01-C02-P2",
  "moment": "7.4 s global, end panel, S01-C02.b2",
  "block_markers": {
    "style": "[style]",
    "framing": "[framing]",
    "shot": "[shot]",
    "identity": "[identity]",
    "action": "[action]",
    "composition": "[composition]",
    "setting": "[setting]",
    "props": "[props]",
    "negative": "[negative]"
  },
  "sheet_baseline": null,
  "identity_sources": ["CHR-01@v1#anchor", "WRD-01a@v1#prompt"],
  "references": [],
  "sources": {
    "style": ["LOOK-01@v1", "WLD@v1#palette"],
    "framing": ["BRF@v1", "STB@v1", "CAM-02@v1"],
    "shot": ["CAM-02@v1"],
    "identity": ["CHR-01@v1#anchor", "WRD-01a@v1#prompt"],
    "action": ["STB@v1", "CNT@v1#S01-C02.perf", "DNT@v1#S01"],
    "composition": ["STB@v1", "CTY@v1#axis-01", "CAM-02@v1"],
    "setting": ["LOC-01@v1#layers", "LOC-01@v1#plan", "SET-01@v1", "ENV-01@v1", "LGT-01@v1", "WLD@v1#rules"],
    "props": ["PRP-01@v1#state-b", "PRP-02@v1#state-b", "CTY@v1#state-01"],
    "negative": ["WLD@v1#forbidden", "BRF@v1", "common:no-text"]
  },
  "model": null,
  "prompt_language": "en+ko"
}
```

## Actual lint result

Working directory: `/home/declan/Documents/Projects/Products/04_Skills/Skills-and-Automation/contents-production-skills-v2`.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/prompt_lint.py --kind image --project /tmp/cp2-wo13-followup.CZUrco/x3-v2 --prompt /tmp/wo15-image-close-task2.rM7sym5h/IMG-S01-C02-P2.md --map /tmp/wo15-image-close-task2.rM7sym5h/IMG-S01-C02-P2.map.json --json
```

**Exit: `3`. Stderr: empty. Stdout:**

```json
[
  {
    "code": "I2",
    "message": "registered sheet baseline not supplied",
    "severity": "unverified"
  },
  {
    "code": "I3",
    "message": "registered sheet baseline not supplied",
    "severity": "unverified"
  },
  {
    "code": "I7",
    "message": "registered sheet baseline not supplied",
    "severity": "unverified"
  }
]
```

The tool emitted no I1/I4/I5/I6 findings. The separate local check confirmed exact identity against the two pinned source sections and one performer against the index. These checks do not verify a sheet roster, a common style hash across the sheet, or a canonical per-panel axis line. I2, I3 and I7 remain unverified; the manual count and axis review do not substitute for the missing evidence. Lint did not verify actual image/reference inputs, visual fidelity or endpoint compatibility.

## Delivery packet (DLV)

```yaml
dlv_for: X-3 fresh image prompt trial / S01-C02-P2
artifacts:
  - /tmp/wo15-image-close-task2.rM7sym5h/IMG-S01-C02-P2.md
  - /tmp/wo15-image-close-task2.rM7sym5h/IMG-S01-C02-P2.map.json
consumed:
  - STB@v1 and 04_board/index.csv plus 04_board/index-header.json
  - BRF@v1, DNT@v1, CNT@v1, CAM-02@v1, CTY@v1
  - CHR-01@v1, WRD-01a@v1, LOOK-01@v1, WLD@v1
  - LOC-01@v1, SET-01@v1, ENV-01@v1, LGT-01@v1, PRP-01@v1, PRP-02@v1
assumptions:
  - Provider-neutral draft; no model dialect or ratio adaptation applied.
  - The chosen still was inspected for comparison only, not consumed as a generation reference.
conflicts:
  - Chosen still differs from the design pins in rack color and apparent rendering style; the prompt follows the pins.
checks:
  - Image prompt lint exit 3 with unverified I2, I3, I7.
  - Nine populated source-mapped blocks; exact pinned identity; one visible performer per board row.
missing_inputs:
  - No registered SHT baseline containing a panel roster, shared style hash and per-panel axis line.
  - No registered rendered REF records for the shot. Ledger IMG-REF records are text prompt records, not rendered reference inputs.
  - No selected model or endpoint, so reference attachment and native 9:16 support are unverified.
self_verdict: partial
```

For any later QA/generation decision, the director should supply and register the real sheet baseline and reference assets (at least the first passerby and the shelter angle; wardrobe, open umbrella/rack and look where applicable). Re-run lint against the registered baseline before treating the draft as verified. No approval, upload, submission, spend or media generation was performed.

## Actual tool log

| Tool | Inputs/actions | Observed result |
|---|---|---|
| `read` | `image-prompt-engineer/SKILL.md`, `docs/design/06-image-prompt-spec.md`, `image-prompt-engineer/assets/IMG-template.md`, `image-prompt-engineer/assets/IMG-map-template.json`, `docs/design/03-artifact-index.md`, `production-director/assets/DLV-template.yaml` | Confirmed the nine content blocks, exact identity, local markers/map and delivery format. |
| `read`, `ls` | X-3 `04_board/index.csv`, `04_board/STB.md`, `04_board/index-header.json`; listed the X-3 root | Located the 7.4 s P2, index row and 9:16 frame; no sheet assignment on the row. |
| `read` | `/home/declan/Documents/Media_Studio/wo13-x3-storyboard/production-look-v5/panels/S01-C02-P2.png` | Tool returned the PNG for direct viewing; comparison above. |
| `read` | `scripts/prompt_lint.py` image branch and CLI, `scripts/cp2/prompt_parse.py`, `production-ledger/references/ledger-schema.md`, `production-director/references/qa4-submit.md` | Confirmed identity parser, registered baseline requirements and nonzero-exit handling. Did not run broader submission or generation checks. |
| `bash` | Read registry keys and selected design pins via `python3`; checked pinned-file SHA-256 matches and the chosen PNG dimensions/hash | `STB`, `BRF`, `CHR-01`, `WRD-01a`, `CAM-02`, `CNT`, `CTY`, `DNT`, `WLD`, `LOOK-01`, `LOC-01`, `SET-01`, `ENV-01`, `LGT-01`, `PRP-01`, `PRP-02` all current at v1, with matching hashes. Registry prefix queries returned `SHT- NONE`, `REF- NONE`, and existing `IMG-REF-` text records. Existing panel prompt contents/maps and evaluator materials were not opened. |
| `bash` | `git status --short`, `git diff --cached --name-only`, then `LC_ALL=C git rev-parse --is-inside-work-tree` | Package CWD was not in a Git work tree; no staging performed. |
| `bash` | `mktemp -d /tmp/wo15-image-close-task2.XXXXXXXX`; `sha256sum` of ledger, index, header and STB | Created `/tmp/wo15-image-close-task2.rM7sym5h` and saved pre-lint checksums there. |
| `write` | The fresh prompt and map, both in scratch | Both writes succeeded. |
| `bash` | The image lint command above; `sha256sum` of prompt and map; `sha256sum -c` for project inputs | Exact stdout above, exit 3, empty stderr; all four project input checks returned `OK`. |
| `bash` | Parsed scratch prompt/map; checked block order, source-map coverage, pinned identity and X-3 board row | Exact validation output below. |
| `bash` | Assembled this managed report directly from the scratch prompt, map and captured JSON, verifying the report embeds the same text | Prompt, map and findings reproduced without transcription. |

```text
Nine nonempty blocks in spec order; all nine source mappings populated.
Identity equals the two pinned source sections.
Manual board-row check: S01-C02, one CHR-01 performer, CAM-02, no sheet assignment.
```

Linted artifact SHA-256:

```text
59600bed0a5e76bfaef64b2c944b60aaafa6bdb53fde27dea826fa18d406846e  IMG-S01-C02-P2.md
c05617e317584ec578873abf14fe67eb148ed8ac16b0ee7570886402e8c54786  IMG-S01-C02-P2.map.json
```
