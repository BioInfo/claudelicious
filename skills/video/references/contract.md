# Engine contract and renderer traps

`engine/README.md` documents the reference implementation of these verbs (`engine/bin/mvid`).
This file is the contract any engine honours, written so you can also build your own. Where
the reference engine's README and this file disagree on a flag or a default, the README
describes what the code does. If you build your own, write your binding contract down in your
engine repo and let it win over this file.

## The verbs

| Verb | Input | Output (the artifact a gate checks) |
|---|---|---|
| `new <slug> --mode` | slug, mode | `films/<slug>/film.json`, kit linked in |
| `scene <slug> <ids...>` | scene ids from the storyboard | `scenes/<id>/index.html` from the kit template, ids appended to `film.json` |
| `voice <slug> [<id>]` | `scenes/<id>/narration.txt`, one spoken line per cue | per-line wavs, `narration.wav`, `cues.json` (word and line timestamps, `total`), `cues.js` for the page. Layout: lead 0.35s, gap 0.7s, tail 0.5s, overridable per film |
| `render <slug> [<id>]` | scene HTML + narration | `renders/<id>.mp4`, duration within 0.1s of `cues.total` |
| `critic <slug> [--scene <id>]` | renders | `critic/<video>/packet.md` listing contact sheets, full-size transition frames, transcript, frozen-time and loudness measurements, a text read-time table (text that left the screen before it could be read), a mid-film black-frame check, and a scene timeline table |
| `assemble <slug>` | renders + music | `out/<slug>/<slug>-v<N>.mp4` + `-music.wav`, never overwriting a prior version |

Every verb gates on its artifact and fails loudly; none reports success on an exit code.

## Scene shape

- One film = `films/<slug>/`; one scene = `scenes/<id>/index.html`, which is also the renderer project dir.
- Root: `<div id="root" data-composition-id="<id>" data-width data-height data-duration="<cues.total>">`.
- Exactly one `gsap.timeline({paused:true})`, registered at `window.__timelines["<id>"]` by a small kit harness.
- Every animated value is a function of timeline time. The harness also answers `?t=<sec>`, so any headless browser can render the same file as a fallback renderer.
- Scenes are silent. `render` muxes narration; `assemble` adds music.
- Renderer: pin one version and call it with telemetry, update checks and auto-install disabled (HyperFrames reads `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_AUTO_INSTALL=1 HYPERFRAMES_SKIP_SKILLS=1`). Verbs: lint, check, snapshot, render only.

## Film-level finish

- `film.json` `"mblur": N` renders each scene at N x fps and blends N sub-frames per frame (`tmix`). Use 8; 4 strobes on fast moves. Skip it for draft renders. Per-scene renders do not apply it, so scene agents never see its ghosting: any fast move (a large camera drop, a scale-in, falling objects) becomes 6-8 stacked copies. Fast moves become cuts or dips, or keep per-frame displacement small.
- `film.json` `"grain": S` adds seeded temporal grain in ffmpeg (S around 6). Never add grain in the page.
- `narration.txt`: a line ending in `[[hold 1.5]]` gets that much extra silence after it (a reveal beat). Not spoken. In narrated films use it once, about 0.5s, before the single peak reveal (see `audio.md`).
- `narration.txt`: a line `[[tail 4.0]]` on its own sets the scene's closing silence; use it on the last scene to make room for the end card.
- `film.json` `"outro": 4.0`: the bed swells about +7 dB into the final N seconds and resolves on a long fade.
- Reserved class: `.stage` (the kit's tokens give it an opaque background). Name wrappers `.stg`, `.cam`, `.wrap`.
- Clips: never ship `data-playback-rate` < 1; motion-interpolate slow clips to the output fps first (see lessons).

## Renderer traps

Each of these fails quietly: the render exits 0 and the frame is wrong. Found on HyperFrames
0.8.x; most apply to any headless HTML-to-video renderer.

| Trap | Rule |
|---|---|
| Hidden initial state flashes or never hides | Set hidden states with `gsap.set(...)` OUTSIDE the timeline |
| Element invisible after its entrance | `fromTo` destinations include the visible opacity (`opacity: 1`) |
| Wrong font in the render | Use fonts you ship as local woff2 files in the kit, or the generic stacks in `kit/theme.css`. A named system font, `@import` or web-font CDN gets a fetched substitute |
| Fonts 404 | Load the kit through a symlink inside the scene dir, never through `../` paths |
| Zoom lands off target or drifts | Zoom with scale plus counter-translate on two nested wrappers; measure targets with `getBoundingClientRect` after `document.fonts.ready` |
| Label clipped by the frame or player UI | Labels and anything essential above y=993 at 1080p |
| Text unreadable on a phone | Readable text at least 22px at 1080p |
| Blank frames at shard boundaries | Render with one worker (parallel workers drop frames) |
| Elements drop out for a frame or two | Disable static-frame dedup (`HF_STATIC_DEDUP=false`) with one worker |
| Scaled text renders blurry | No `will-change: transform` on text that scales |
| Silent render | Every `<audio>` needs an `id` |
| GSAP missing, timeline frozen | The reference engine loads GSAP from a CDN, so rendering needs network. For offline or reproducible renders, vendor GSAP into the kit and point the script tags at it |
| Nothing moves (still frame) | `window.__timelines` key must equal the composition id; register after the build finishes |
| Non-deterministic frames | No `Date.now`, `performance.now`, `requestAnimationFrame`, unseeded `Math.random`, CSS transitions or animations, `setTimeout`, `repeat:-1`, `tl.play()` |
| GSAP fights CSS | Never set a CSS transform and tween the same property with GSAP |
| Clip vanishes | Never tween `visibility`/`display`/`autoAlpha` on a clip; animate a child |
| `<video>` freezes | Do not animate width/height/top/left on `<video>`; wrap it |
| `check` reports "0 samples" | A lint error skipped the browser audits. That is a failure, not a pass |
| `<video>` silently vanishes (render PASSES) | Never put CSS `filter: blur()` on a video's wrapper or any ancestor; pre-blur the clip in ffmpeg (`gblur=sigma=5`) |
| `<video>` silently vanishes behind an overlay (render PASSES) | A full-frame `inset:0` overlay that starts empty and is filled by JS can hide the video; size overlay containers to their content |
| Heavy blur or backdrop-filter | Falls back to slow screenshot capture; keep blurs small and few |

## Gate on the artifact

A render passes when ffprobe duration is within 0.1s of `data-duration` and the frames are
present and non-blank. Snapshot the cue times and look at them full size. Never gate on `$?`.
