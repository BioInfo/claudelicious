---
name: video
model: opus
description: "Makes a finished, watchable explainer MP4 from a topic, doc, paper, app URL or launch brief: narration, music and kinetic motion graphics authored as HTML scenes and rendered headless. ALWAYS invoke on 'make a video', 'make an explainer video', 'explainer video', 'hype reel', 'launch video', 'turn this paper into a video', 'demo this app on video', 'loop for X', 'video of this'. NOT short branded clips (quote cards, audiograms), and NOT posting: nothing leaves the machine without the owner's explicit yes naming the destination."
# Runs INLINE in the main context: the three gates are conversations with the owner.
# Scene building and the critic run as subagents with the model passed explicitly.
---

# video

The orchestration pattern for making explainer films with Claude Code. One skill, one
pipeline; modes only change defaults. The owner touches it three times: the storyboard
(gate 1), one prototype scene (gate 2), and watching the mp4 (gate 3). Everything between
gate 2 and the mp4 runs without questions.

## What this published version is, and is not

This is the **orchestration layer**: the gates, the agent briefs, the critic, the house
style, and the lessons ledger. A generic reference engine ships beside it in `engine/`
(`engine/bin/mvid`, verbs `new`, `scene`, `voice`, `render`, `critic`, `assemble`; local
Kokoro TTS; films under `./films/<slug>`). Read `engine/README.md` for its install steps
and exact flags. Every `<engine> <verb>` call below is one of those verbs; the contract each
verb must honour is in `references/contract.md`, so you can also build your own in whatever
stack you like.

The patterns worth stealing even if you never render a frame:

- **Storyboard gate.** A written STORYBOARD.md with every default stated inline, so the owner overrules by editing one line instead of answering ten questions.
- **Look-dev before the storyboard is final.** Two visual directions x two key shots as stills; the owner picks the world before any scene is built.
- **Voice-first timing.** Narration is synthesized first and word timestamps become `cues.json`. Every scene is a function of cue times, so a voice swap is re-align plus re-render, not a rebuild.
- **Parallel scene agents** with strict ownership: one agent per scene directory, the parent owns the storyboard, the prototype, the film-level gates and the review.
- **A fresh critic agent** every round, told nothing about what was fixed.
- **A self-evolving lessons ledger** (`references/lessons.md`): every owner ruling and every new failure becomes a dated row in the same session, so the next film starts higher.

## The standard (owner rulings, one line each)

- Explainers carry narration AND music. Without both it is "just a website that comes in a piece at a time".
- Text never jiggles: still holds joined by short eased moves. No slow zoom over text.
- Focus follows the voice: when a line names a thing, the camera or a spotlight goes to it; the rest dims.
- Show the real thing moving: real app click-throughs and real screenshots beat invented UI.
- Real numbers, dated, from `KIT.md` only. Private business numbers never go on screen.
- About 3 minutes is a ceiling, not a target. Say each point in the time it needs: the point lands in the first 10s, one idea per 8-15s scene, no preamble lines. Spec: `references/house-style.md` "Signal density".
- Graphics are real infographics (counters, self-drawing diagrams, packets on paths), never words on a page.
- Open mid-motion on the idea. Never a logo, a black fade-in or a title card.
- Section label lower-right, above y=993.
- Captions off for explainers; on for social cuts, burned in, cut from the rendered audio.
- Master every audio deliverable and verify it by transcription, not by LUFS alone.
- Nothing is published without an explicit yes that names the destination.
- Spectacular, not templated. Every film opens with a research pass on current standout model-made videos and on the best explainers in its subject, and the storyboard names the borrowed techniques. Generated image plates are allowed where the subject is physical or spatial. After each film, the new techniques and the owner's rulings go back into `references/` so the next film starts higher.

Full style spec: `references/house-style.md`. Dated ledger: `references/lessons.md`.

## Modes

| Mode | Length | Narration | fps / aspect | Pace |
|---|---|---|---|---|
| `explainer` (default) | 90-180s | TTS | 30 / 16:9 | continuous camera, new element every 1.5-2.5s, mono HUD labels, numbers animate |
| `paper` | 120-300s | TTS | 30 / 16:9 | explainer plus self-drawing diagrams and formulas with annotations |
| `demo` | 30-120s | TTS | 30 / 16:9 | real click-through recording plus focus zoom |
| `reel` | 15-25s | none | 60 / 16:9 or 1:1 | beat-locked, new state every 0.9-1.5s, one hero object morphs across every shot, bookend ending |
| `loop` | 8-15s | none | 60 / 1:1 | reel rules, and the last frame equals the first |

Pick the mode from the ask: "paper" or an arXiv link -> `paper`; an app URL or "demo" ->
`demo`; "hype reel" or "launch video" -> `reel`; "loop" -> `loop`; anything else -> `explainer`.
State the mode in the storyboard; do not ask about it.

## The flow

### 0. Scaffold (no questions)

```
<engine> new <slug> --mode <mode>
<engine> scene <slug> s01-hook s02-problem ...
```

One film directory per slug, one scene directory per scene, the shared kit linked in, a
`film.json` holding mode, scene order and film-level finish settings. Colour and type come
from a CSS token file; scenes use tokens (`--bg`, `--ink`, `--accent`, ...) and never a raw hex. Read
every source (doc, paper, repo, URL). Write `films/<slug>/KIT.md`: every number, name and
claim that may appear on screen, each with its date and source. If a number has no source,
it does not go in `KIT.md` and it does not go on screen.

### 0.5 Look-dev (before the storyboard is final)

Generate 2 visual directions x 2 key shots as stills with an image model and let the owner
pick the world. Optional motion for stills: an image-to-video model,
used for camera and light on solid subjects, not for abstract matter (see
lessons). The gate-2 prototype must be an image-led shot, not a text-only scene.

### 1. GATE 1: STORYBOARD.md

Write `films/<slug>/STORYBOARD.md` from `references/storyboard-template.md`: brief block,
three candidate structures with the reason for the pick, scene table (one narration line per
cue), three signature moments, a "differs from the last film" table, mode defaults stated
inline. Show the owner the file path and a five-line summary.

Treatment discipline, before the owner sees it (adapted from lemo-opuscar's `DIRECTOR.md`, MIT; see `THIRD-PARTY.md`):
- The first structure that comes to mind for a subject is usually its cliché. Write three, pick one, and say why it fits this subject and takeaway. Take the opening image, the ending and the score shape from the subject too.
- Every focus move names its cue and its reason ("zoom to the p99 bar on line 2, because the line names it").
- At least four of six aspects (structure, opening, signature moment, camera path, score shape, ending) differ from the last film made in this mode. Rethink the ones that match.
- Signal-density pass: for each narration line, ask what the viewer learns that they did not know one line ago. If nothing, cut it.

Ask at most ONE question, and only on a genuine fork (audience or takeaway unclear, two
real angles). Every other default is stated inline ("16:9, TTS voice X, pad bed, no
captions, ~2:40") so the owner can overrule by editing one line. Wait for the go.

Narration draft rules:
- Plain spoken sentences, one per cue. Narrate like a university professor explaining to a smart colleague.
- Avoid Claudisms: no staccato punchy fragments, no stat dumps, no "it isn't X, it's Y", no rhetorical triplets.
- Numbers written as spoken ("four point five percent", "twenty twenty-six").
- Never put the narrated sentence on screen. The screen shows the thing; the voice explains it.
- Narration in the owner's own voice or for their brand: run it past their voice spec first.

`reel` and `loop` may skip the question entirely.

### 2. GATE 2: one-scene prototype (explainer, paper, demo)

Build the most representative scene end to end: narration, ducked bed, section label,
HUD, its focus moves. 15-20s, about 5 minutes wall.

```
<engine> voice <slug> <id>
<engine> render <slug> <id>      # lint + check + render + narration mux
```

Look at its full-size frames yourself, then hand the owner the path to the rendered mp4.
On their yes, this scene becomes the house-style reference every scene agent copies.
A wrong direction dies here at 5 minutes instead of at 30. `reel`/`loop` skip this gate.

### 3. Build (no questions)

```
<engine> voice <slug>            # every scene: line wavs, narration.wav, cues.json, cues.js
```

Then fan out scene agents, one per scene, in parallel (brief below). The parent does not
write scene HTML; it owns the storyboard, the prototype, the film-level gates and the
review. When all agents report:

```
<engine> render <slug>           # every scene, a few in parallel; gates on the artifact, not $?
```

Each scene runs the renderer's lint and check first (a scene with no timeline renders a
blank video without error, so never skip them), then ffprobe duration must match
`data-duration` within 0.1s. A failing scene goes back to its owner agent with the failing
output pasted.

### 4. Critic

```
<engine> critic <slug>           # contact sheets, dense transition frames, transcript, frozen-time, text read time, black frames, loudness -> packet.md
<engine> critic <slug> --scene <id>
```

Then dispatch a FRESH critic agent (brief below). P0s go back to the owning scene agent.
One round by default, two at most. After fixes, re-render only the touched scenes and send
a new fresh critic the previous report to verify.

### 5. Assemble, then GATE 3

```
<engine> assemble <slug> [--captions] [--formats square,vertical] [--music <bed>|pad|none]
```

Joins on cuts, narration acrossfade, bed ducked, loudnorm, poster baked as frame 0.
Output: `out/<slug>/<slug>-v<N>.mp4` plus a music-only `-music.wav`. Look at the full-size
frames and read the transcript first, then hand the owner the path.

GATE 3 is the owner watching it. Take notes by timestamp, fix, re-assemble as v<N+1>.
The skill ends at the mp4. Approval of a cut is not approval to send it anywhere.

Any thumbnail or card made from the film uses a deliberate frame (the end card, or a frame
picked by time), never frame 0: a film that opens mid-motion on real footage has a raw,
unframed frame 0. Look at it before using it.

## Scene-agent brief

Dispatch with the Agent tool, `model: opus` passed explicitly, one agent per scene.
The brief carries:

- **Ownership:** you own `films/<slug>/scenes/<id>/` and nothing else. Do not touch the kit, other scenes, `film.json` or `STORYBOARD.md`.
- **Temp files and siblings:** parallel agents share one scratch area, so temp files go only under a per-scene temp dir (e.g. `films/<slug>/tmp/<scene-id>/`) (generic names like `p2.js` collide). To see a sibling's frame, extract it from `renders/<id>.mp4` with ffmpeg; never run the renderer inside another scene's directory. The parent greps each scene's `index.html` for other scenes' labels.
- **Motion blur:** the film-level blur is applied after your render, so you will not see it. Under it, any fast move (a large camera drop, a scale-in, falling objects) becomes stacked ghost copies. Make fast moves cuts or dips, or keep per-frame displacement small.
- **Read first, in order:** the kit README (its patterns), `references/contract.md`, the prototype scene's `index.html` (the house-style reference), `KIT.md`, your `audio/cues.json`, and the pattern files your row names.
- **Your row:** paste the scene's storyboard row, its narration lines and the cue times the focus moves must land on.
- **Rules:** start from the kit's scene template; copy a pattern before inventing one; every number from `KIT.md`; `data-duration` equals `cues.total`; animation keyed to cue times.
- **Fill the frame and keep it moving:** the narrated element fills 60-85% of the frame on its line, and its action spans the whole line. A thin playhead inside a small card is dead screen (first proof film: 0.12% of pixels changed over 5s in a card at 17% of frame width). No glyph leaves the frame on a zoom (keep a 120px margin).
- **Narrow gate, yours only:** renderer check clean, snapshots at each cue time that you have looked at, render duration within 0.1s of `cues.total`, and the per-scene critic packet read for its longest freeze (anything over ~2.5s that is not a deliberate reading hold gets motion). The film-level suite belongs to the parent; do not run it.
- **Output cap:** state the per-response token cap. Write the skeleton first, then append in chunks of 150 lines or fewer. Never echo a file back.
- **Report:** under 250 words: files touched, gate output (pasted), the frames you looked at, anything you could not do.

## Critic brief

A FRESH agent (`model: opus`), told nothing about what was fixed or what you believe.
Prompt: `references/critic.md`. It reads the critic packet, opens every image listed there
(sheets AND full-size frames), and reads the transcript against the storyboard narration.

Its first question is: does this look like the default model-made template look, yes or
no, and why. If subagents cannot write files in your setup, the critic replies with the
report and the parent saves it. Then P0 (ship blocker), P1 (visible defect), P2 (polish),
each with a timestamp and screen region, ending in SHIP or ONE MORE PASS.

## Hard gates

- **Artifact, never exit code.** A render passes on ffprobe duration and frames present; audio passes on transcription per beat.
- **Duration:** each scene within 0.1s of its cues; the film inside the mode's length and under the destination's cap.
- **Look at full-size frames**, not only contact sheets. Sheets hide clipped text, collisions and 22px violations. With motion blur on, look at a full-size frame mid-move as well.
- **No mid-film black frames**, and no on-screen text that leaves before it can be read. Neither shows in a still frame; the critic packet measures both.
- **Numbers only from `KIT.md`**, dated. A number on screen with no `KIT.md` row is a P0.
- **Nothing leaves the machine** (upload, post, publish, share link) without the owner's approval naming the destination.
- **Renderer verbs:** lint, check, snapshot, render only, with telemetry and auto-update disabled. Install the renderer once (see engine/README.md) before the first render; the npx fallback installs on first use, which is slow mid-film. Never let the renderer scaffold, publish or upgrade itself mid-film.

## Voice, music, captions

- **Voice:** a local TTS (Kokoro's `af_heart` was the approved default, speed about 1.15-1.2) with word timestamps. Per-scene layout: lead 0.35s, gap 0.7s between lines, tail 0.5s, so a cut carries about 1s of audible gap. Scenes are functions of `cues.json`, so a voice swap is re-align plus re-render.
- **Music:** generated or licensed instrumental beds, auditioned by the owner. Until one is approved, a synthesized ambient pad. Check model weight licences: some music models are non-commercial.
- **Captions:** off for explainers; on for any social cut, burned in, cut from the rendered audio by forced alignment, never from the script.

Details: `references/audio.md`.

## References

| File | Read when |
|---|---|
| `references/house-style.md` | writing the storyboard; briefing scene agents |
| `references/contract.md` | building or debugging any scene; wiring your own engine |
| `references/storyboard-template.md` | step 1 |
| `references/critic.md` | step 4 |
| `references/audio.md` | voice, bed, mix, captions |
| `references/lessons.md` | before starting; append a row when the owner rules on something or a render fails in a new way |

Research passes (standout model-made videos, subject explainers) are written as dated files
per film in your own working tree; the originals are not published here.
