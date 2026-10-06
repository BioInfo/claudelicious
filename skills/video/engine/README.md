# mvid engine

A small CLI that turns HTML scenes into a narrated MP4. You write each scene as an HTML page with one
paused GSAP timeline; `mvid` voices the narration locally with Kokoro, renders the page with a pinned
HyperFrames, checks the result, and assembles the film with ffmpeg. It implements the contract in
`../references/contract.md`.

Everything runs on your machine. The network is used for three things only: installing packages,
Kokoro's one-time model download, and loading GSAP from its CDN at render time.

## Requirements

| Tool | Why | Notes |
|---|---|---|
| Node 22+ | the renderer | HyperFrames `0.8.62`, pinned in `hf/package.json`. Without a local install `mvid render` falls back to `npx --yes hyperframes@0.8.62` |
| ffmpeg + ffprobe | every audio and video step | captions also need an ffmpeg built with libass (the `ass` filter); set `MVID_FFMPEG_ASS` if your default build lacks it |
| uv | the Python tools | Python 3.11 or 3.12, dependencies in `lib/pyproject.toml` |
| Chrome or Chromium | `critic`'s read-time check and the fallback renderer | found automatically, or set `CHROME_PATH` |
| ImageMagick (optional) | timestamps on critic contact sheets | without it the sheets are unlabelled and the packet lists tile times |

Kokoro (82M parameters, CPU) downloads its weights from Hugging Face (`hexgrad/Kokoro-82M`) the first
time you run `mvid voice`. Its English front end can fall back to espeak-ng for unknown words, so
install `espeak-ng` too if your package manager has it.

## Install

```bash
cd engine
(cd hf && npm ci)                  # pinned renderer + puppeteer-core
(cd lib && uv sync)                # Kokoro, numpy, soundfile
(cd lib && uv sync --extra asr)    # optional: local transcript for critic WER and assemble --captions
ln -s "$PWD/bin/mvid" ~/.local/bin/mvid   # or add bin/ to PATH
```

`mvid` finds its engine dir from its own path (override with `MVID_HOME`). Films go under
`./films/<slug>` and cuts under `./out/<slug>` of the directory you run it from; change that with
`--root DIR` as the first argument or `MVID_ROOT`.

## Quickstart

```bash
mvid new hello --title "Hello"            # films/hello/film.json, STORYBOARD.md, KIT.md, _kit link
mvid scene hello s01-hook                 # films/hello/scenes/s01-hook/index.html from the template
echo "Every film starts with one idea." > films/hello/scenes/s01-hook/narration.txt
mvid voice hello && mvid render hello     # narration + cues, then renders/s01-hook.mp4
mvid assemble hello --music pad && mvid critic hello   # out/hello/hello-v1.mp4, then critic/hello-v1/packet.md
```

Edit `scenes/<id>/index.html` between `scene` and `render`: paste a pattern from `kit/patterns/`, key
each beat to the narration with `MV.cue(i)` and `MV.word(i, n)`. Change the look in `kit/theme.css`.

## What each verb produces

| Verb | Writes | Gate |
|---|---|---|
| `new <slug> [--mode explainer\|paper\|demo\|reel\|loop] [--title T]` | `films/<slug>/film.json`, `STORYBOARD.md`, `KIT.md` (the only source of on-screen numbers and names), `_kit` link to `kit/` | refuses an existing film |
| `scene <slug> <id>...` | `scenes/<id>/index.html` from `kit/templates/scene.html`, an empty `narration.txt`, ids appended to `film.json` with a default transition | leaves an existing `index.html` alone |
| `voice <slug> [id...] [--voice V] [--speed S] [--force]` | `scenes/<id>/audio/`: `line_NN.wav`, `narration.wav` (-16 LUFS), `cues.json` and `cues.js` (line and word times, `total`); sets `data-duration` on the scene root | only changed lines are re-synthesized |
| `render <slug> [id...] [--draft] [--no-check] [--jobs N]` | `renders/<id>.mp4`: `hyperframes lint` + `check`, a one-worker render, narration muxed in; `renders/<id>.log` | duration within 0.1s of `data-duration`, checked with ffprobe; a failed render leaves the last good one in place |
| `critic <slug> [--scene ID] [--video P] [--strict]` | `critic/<video>/packet.md` + `packet.json`: contact sheets, transition strips, a frame per narration cue, frame 0, transcript and WER, frozen time, loudness, silent windows, black frames, text read time | measurements only; the packet ends with instructions for a fresh reviewer. `--strict` exits 1 on any FAIL |
| `assemble <slug> [--music P\|pad\|none] [--captions] [--formats L] [--out P] [--version N]` | `out/<slug>/<slug>-vN.mp4`, `-music.wav`, `poster.png`, optional `-captioned.mp4` and `-square`/`-vertical`/`-x`/`-linkedin` variants | duration measured on the output; never overwrites a prior version |

Narration markup in `narration.txt`, never spoken: a line ending in `[[hold 1.5]]` adds 1.5s of silence
after it; a line `[[tail 4.0]]` on its own sets the scene's closing silence.

`--music pad` synthesizes an ambient chord bed (`lib/pad.py`). A music file loops on a beat-aligned seam
when it is shorter than the film (`lib/bedloop.py`). Either way the bed ducks under the voice.

Transcription for `critic` and `assemble --captions` is local only: stable-ts (the `asr` extra) or
faster-whisper, whichever is installed, model from `MVID_WHISPER_MODEL` (default `base`). With neither,
`critic` marks the WER check N/A and says why.

## Layout

```
bin/mvid              the CLI (bash)
hf/package.json       pinned renderer
kit/                  theme.css, tokens.css, harness.js, templates/scene.html, patterns/
lib/                  render.py (stdlib only), tts.py, assemble.py, critic.py, pad.py, bedloop.py,
                      readcheck.mjs, capture-frames.mjs (fallback renderer), tests/
```

`node lib/capture-frames.mjs <scene_dir> -o out.mp4` renders a scene by seeking its timeline frame by
frame in headless Chrome. Use it to cross-check a suspicious HyperFrames render.

## Tests

```bash
cd lib && uv run pytest
```

Tests that need a missing tool (Kokoro model, a transcriber, a libass ffmpeg, the local renderer) skip
and print the reason.

## Licenses

GSAP and its plugins load from `cdn.jsdelivr.net/npm/gsap@3.15.0` and are not part of this repo. They
are free to use under GSAP's own license, https://gsap.com/standard-license. HyperFrames, Kokoro and the
Python packages carry their own licenses.
