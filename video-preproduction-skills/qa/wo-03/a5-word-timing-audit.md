# WO-15 A5 — Read-only Korean word/reaction timing audit

**Disposition: BLOCKED for actual speech timing; X-3 is not applicable.** No eligible real Korean recording paired with registered word times was found in package `qa/`, `tests/`, or X-3’s own files. Do not advance A5/R1 on this audit. The completed EX-02 board-pin work is separate. No TTS, recording, external service, installation, project/ledger/code change, or staging was performed. Only this managed report was written.

## What was checked

- `docs/work-orders/WO-03-prompt-lint.md` (local CLI contract), WO-02 and `production-ledger/references/ledger-schema.md` (timeline contract), DES-07 §§3/6/7, and the implementation in `scripts/timeline_check.py`, `scripts/prompt_lint.py`, `scripts/cp2/ledger.py`. WO-03’s older implementation step mentions proportional word-position estimation; that is **not** the current in-cue behavior and is not evidence.
- Scope: package `qa/` (75 files), `tests/` (52, including existing Python bytecode), `/home/declan/Documents/Media_Studio/wo13-x3-storyboard` (569, including hidden files; no symlinks). The X-3 root is cited in `qa/wo-10/e62-trial.md`. Filename and MIME checks found no audio/video or alignment file in those trees. Two package QA tarballs were listed, not extracted; the X-3 entries exposed no audio/video/word timing candidate. No other project’s contents were read for media. The lone compressed X-3 `.blend` was opened read-only with auto-execution disabled: no sound datablocks, sequencer strips or speaker objects. PNGs are stills, not speech evidence.
- The only `word_events`/`stimulus_source` hits were the generated JSON in `tests/test_prompt_lint.py::test_registered_word_end_distinguishes_reaction_order`. It registers a made-up `D001`/`기다려` boundary and tests `error`, `None`, `unverified` directly in `reaction_order`; it has neither a registered screenplay in that test nor source audio. EX-02 `speech-timing` blocks under `tests/fixtures/` are scripted cue windows for rate/coverage tests, not token alignments. `qa/wo-08/e41-retry.md` marks the EX-02 windows as estimated; `qa/wo-07/e35b-trial.md` explicitly says text only, no measured utterances. The X-3-local `async-qa4-repair/registered-board/evidence/ex02-test-ledger` registers the EX-02 **evaluation screenplay** for a board-pin test (`registered-inputs/SCR.provenance.md`); the `VOC` inputs are text. A board-pin pass does not turn a rehearsal or timing assumption into measured media.
- X-3’s brief `evals/e2e/X-3.md` requires no dialogue. The actual current ledger pins resolved and their bytes matched registration:

  | Pin | Path under X-3 | SHA-256 |
  |---|---|---|
  | `SCR@v1` | `06_prompt/SCR.md` | `7f121ee2acbe269874647907a8facf995a4e164ce6d770acb19515017ee1f4e9` |
  | `CNT@v2` | `03_conti/CNT-v5.md` | `0f7ecd0598d18aef1111b8bd04e1252c8816d67ba1e5ab90a077dfc109dda408` |
  | `APR-01@v1` | `06_prompt/APR-01.md` | `e0492f6bc2d65140bc71d1b3ae52e2e08a15b1d8f8c9a4e3456b329ae84ce60b` |

  The registered SCR has no `Dnnn` lines and `speech-timing` is `[]`; CNT marks dialogue/VOC/reaction-to-dialogue N/A and timing as intended, not measured. The APR explicitly excludes speech/vocals (separate rain and action effects only). Both v6 packet maps (`GEN-01`, offset `0`; `GEN-02`, offset `8`) have zero dialogue entries, zero reaction links, and no `stimulus_source`. Both prompt lints and the timeline checker exited 0 with `[]`: **L9 was not exercised**, not a timing pass.

## What the verifiers establish

- `timeline_check.py` reads index cut/beat ranges and optional SCR `speech-timing` JSON (`ids`, `start`, `end`, `text`, `lang`; optional `pauses`/`mode`). It checks cue allocation, coverage, overlap/L-cut notation and rate estimates. Missing timing on assigned dialogue is a TL05 warning; exit 0 does not rule out warnings. It does not read audio, authenticate cue text/timestamps, or infer word timing. Korean rate is estimated from Hangul syllables and cue duration, with a 0.3 s allowance per specified pause; shipped thresholds are marked `uncalibrated-default`. This is distinct from timing a word in an audible take.
- `prompt_lint.py` L2 matches B5 quoted utterances to registered SCR text. L9 expects `reaction_to` (or `stimulus`) with `dialogue` and `word`; the word must occur in a known SCR line and there must be exactly one local cue for that dialogue. Before cue start is L9 error; at or after cue end skips the word lookup. For a within-cue check, `stimulus_source: CNT@vN` must be *current* and byte-identical to the ledger hash at an in-project path. Its JSON object (or one `prompt-evidence` fence) must name the same `screenplay: SCR@vN` and `gen: GEN-nn` as the sidecar. There must be exactly one matching `word_events` row `{dialogue, word, start_s, end_s}` in project-global seconds. It subtracts `global_offset_s`; the resulting nonempty interval must fit inside the cue. A reaction strictly before the word’s end is L9 error; equality or later is ordered. Missing, ambiguous, unresolvable or out-of-cue evidence is `unverified`. Prompt CLI exits `0` (no errors/unverified), `1` (errors), `2` (bad input), or `3` (unverified without errors). Neither CLI measures media or checks a recording hash/provenance; that association must be checked independently.
- **Full-prompt limitation:** `lint()` takes the reaction timestamp from the linked segment’s **start**, not an independent point. With L1’s nonoverlapping partition and one dialogue segment, another segment cannot start strictly inside that cue. A same-segment link exercises the within-cue branch at cue start, where any valid nonempty word ending later correctly gives L9 error. Marking a following segment alone can pass without reading the word map. Use the direct helper to verify an independently measured *interior* reaction timestamp; do not use overlapping beats to manufacture a full-CLI positive. If acceptance requires full-prompt positive verification of a truly interior reaction, the maintainer must approve how to represent that event; this audit did not change the schema.

## Read-only reproduction run

From the package root:

```bash
X3=/home/declan/Documents/Media_Studio/wo13-x3-storyboard
export PYTHONDONTWRITEBYTECODE=1
find qa tests "$X3" -type f -print0 | xargs -0 file -b --mime-type | sort | uniq -c
find qa tests "$X3" -type l -print
rg --hidden -n 'word_events|stimulus_source|speech-timing' qa tests "$X3"
for a in qa/wo-13/*.tar.gz; do
  tar -tzf "$a" | grep -E '/x3-v(1|2)(\.|/)' | grep -Ei '\.(wav|mp3|ogg|opus|flac|aac|m4a|aiff?|caf|amr|wma|mp4|mov|mkv|avi|webm|vtt|srt|textgrid|praat|zip|gz|zst|7z|bin|pcm|mxf|mpeg|mpg|m4v|3gp|mts|m2ts|au)(/|$)' || :
done
blender --background --factory-startup --disable-autoexec "$X3/previs-v1/X3-previs.blend" --python-exit-code 1 --python-expr 'import bpy; print("SOUNDS", [(x.name, x.filepath) for x in bpy.data.sounds]); print("SCENES", [(s.name, [(a.name,a.type) for a in s.sequence_editor.strips_all] if s.sequence_editor else [], [x.name for x in s.objects if x.type == "SPEAKER"]) for s in bpy.data.scenes])'
python3 -B scripts/timeline_check.py --index "$X3/04_board/index.csv" --runtime 20 --script "$X3/06_prompt/SCR.md" --json
for f in ex02-defect-30s:30 ex02-fixed-34s:34; do
  x="tests/fixtures/${f%:*}"
  python3 -B scripts/timeline_check.py --index "$x/index.csv" --runtime "${f#*:}" --script "$x/SCR.md" --json
  printf '%s exit=%s\n' "$f" "$?"
done
PYTHONPATH=scripts python3 -B - "$X3" <<'PY'
import json, subprocess, sys
from hashlib import sha256
from pathlib import Path
from cp2.ledger import Ledger
from prompt_lint import pinned_bytes, screenplay
from timeline_check import read_speech
x = Path(sys.argv[1]); book = Ledger.load(x)
for pin in ('SCR@v1', 'CNT@v2', 'APR-01@v1'):
    record = book.resolve(pin)
    print(pin, record['status'], record['path'], sha256(pinned_bytes(x, pin, pin.split('@')[0])).hexdigest())
print('SCR dialogue:', screenplay(x, 'SCR@v1'), 'timing:', read_speech(x / book.resolve('SCR@v1')['path']))
for p in json.loads((x / '06_prompt/seedance-review-v6/batch.json').read_text())['packets']:
    side = json.loads((x / p['map']).read_text()); segs = [s for sh in side['shots'] for s in sh['segments']]
    print(side['gen'], side['global_offset_s'], sum(len(s.get('dialogue', [])) for s in segs),
          sum(bool(s.get('reaction_to', s.get('stimulus'))) for s in segs), side.get('stimulus_source'))
    result = subprocess.run([sys.executable, '-B', 'scripts/prompt_lint.py', '--kind', 'video', '--prompt', str(x / p['prompt']), '--map', str(x / p['map']), '--project', str(x), '--json'], capture_output=True, text=True)
    print(result.returncode, result.stdout.strip(), result.stderr.strip())
PY
```

EX-02 defect exit 1: TL04 for D001, D002, D009+D010; TL05 warning for D004+D005. EX-02 fixed exit 0: `[]`. These are synthetic contract controls only. The focused existing helper unit test was inspected, not run here because its `tmp_path` fixture writes test artifacts. No Git worktree/index was available in either checked root (`git rev-parse --show-toplevel` exit 128); no staging commands took place.

## Exact unblock and local replay — not run (inputs missing)

**Decision or supplied file:** Authorize one isolated *voiced* R1/WO-03 fixture (EX-02 is an option only if the recorded line matches the chosen canonical version), or supply an already registered fixture that meets the same conditions. Provide a rights-cleared real Korean take as a local WAV (PCM preferred), and a verifiable alignment of that exact take to the selected `SCR@vN` dialogue ID and exact Korean token/string. Do not add dialogue to X-3, substitute an unrelated take, or use TTS. If the video reaction is claimed to be actual rather than planned, also supply synchronized picture/audio or a reviewed measured onset marker tied to the picture version. Audio alone does not prove a reaction time. A maintainer, not this read-only audit, must provide/register the isolated SCR/CNT and the matching VPR/index artifacts if they do not already exist.

Pair the WAV’s SHA-256, take ID, origin (WAV sample or clip zero → project-global second), sample rate/channel, and reviewed word onset/offset (sample index or time relative to that origin) with one unambiguous `(Dnnn, exact Korean text)` occurrence in `SCR@vN`. Record annotator/method, time precision and the measured or planned status of reaction onset. Use a unique token or exact unambiguous phrase; recording the same `(dialogue, word)` twice for one CNT is unverified. Use a word ending **strictly inside** a cue for the positive interior test, ideally with a nonzero GEN offset. Store converted global seconds as `word_events[].start_s/end_s` in the current `CNT@vN` object along with exact `screenplay` and `gen`; sidecar `stimulus_source` points at that pin. The time basis must include any trim/lead-in; no char-count interpolation. Review the recording against the full SCR utterance and listen to the annotated window, not just the file metadata. Preserve audio digest and review notes beside the alignment; the CLI’s registered CNT hash alone does not cover audio.

For a reproducible, no-write verification, set these variables to supplied **absolute** paths/values: `project_root`, `INDEX`, `RUNTIME`, `SCR` (the ledger path for the sidecar SCR), `PROMPT`, `sidecar_path`, `audio_path`, `AUDIO_SHA` (expected supplied digest), `dialogue_id`, `spoken_token`, and `REACTION_GLOBAL_S` (independent observed or explicitly planned onset). From the package root:

```bash
export PYTHONDONTWRITEBYTECODE=1
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of json "$audio_path"
sha256sum "$audio_path"
python3 -B scripts/timeline_check.py --index "$INDEX" --runtime "$RUNTIME" --script "$SCR" --json
python3 -B scripts/prompt_lint.py --kind video --prompt "$PROMPT" --map "$sidecar_path" --project "$project_root" --json
PYTHONPATH=scripts python3 -B - "$project_root" "$SCR" "$sidecar_path" "$audio_path" "$AUDIO_SHA" "$dialogue_id" "$spoken_token" "$REACTION_GLOBAL_S" <<'PY'
import json, sys
from hashlib import sha256
from pathlib import Path
from cp2.ledger import Ledger
from prompt_lint import canonical_json, interval, reaction_order, screenplay
from timeline_check import read_speech, seconds
root, scr, side_path, wav, audio_sha, line, word, reaction_g = sys.argv[1:]
root, scr, side = Path(root).resolve(), Path(scr).resolve(), json.loads(Path(side_path).read_text())
assert sha256(Path(wav).read_bytes()).hexdigest() == audio_sha.lower(), 'Audio differs from alignment source'
r = Ledger.load(root).resolve(side['screenplay']); assert r and (root / r['path']).resolve() == scr
text = screenplay(root, side['screenplay'])[line]; assert word and text.count(word) == 1
segments = [s for shot in side['shots'] for s in shot['segments']]
windows = [interval(s) for s in segments if line in s.get('dialogue', [])]; assert len(windows) == 1
start, end = windows[0]; off = seconds(side['global_offset_s'])
[c] = [c for c in read_speech(scr) if line in c['ids']]
assert c['ids'] == [line] and c['text'] == text and c['lang'] == 'ko'
assert (seconds(c['start']), seconds(c['end'])) == (start + off, end + off)
m = canonical_json(root, side['stimulus_source'], 'CNT')
assert (m['screenplay'], m['gen']) == (side['screenplay'], side['gen'])
[e] = [e for e in m['word_events'] if (e['dialogue'], e['word']) == (line, word)]
left, right = (seconds(e[k]) - off for k in ('start_s', 'end_s'))
assert start <= left < right < end, 'choose an interior stimulus for both controls'
def probe(t, packet=side):
    return reaction_order(root, packet, line, word, t, (start, end))
assert probe((left + right) / 2) == 'error'
assert probe(right) is None
assert probe(right, {k: v for k, v in side.items() if k != 'stimulus_source'}) == 'unverified'
reaction = seconds(reaction_g) - off
assert start <= reaction < end, 'external reaction timestamp must exercise the word lookup'
verdict = probe(reaction)
print('verified join', side['screenplay'], side['stimulus_source'], side['gen'], line, word)
print('GEN-local word', left, right, 'reaction', reaction, 'observed verdict', verdict or 'ordered')
assert verdict is None, 'the supplied reaction does not pass the timing comparison'
PY
```

This probe intentionally chooses a singleton cue with the same global window as the GEN-local map plus offset. Do not `set -e` around intentional failures or treat a shell exit alone as sufficient evidence: retain the TL and L9 findings, the offset/word and reaction coordinates, the byte-checked pins and the audio review. `None` from the helper is an order pass only after the explicit inside-cue guard. If only timing is supplied (no picture), report a real-word vs **planned** reaction comparison, not observed playback. One take can close a specific word-order case; it cannot establish a calibrated rate distribution (`calibrate_speech_rate.py` asks for ≥30 usable samples per language), provider/model support, or broader R1 completion.
