# mvid kit

Every film links to this folder: `films/<slug>/_kit -> <engine>/kit`, and each scene reaches it through
`scenes/<id>/_kit -> ../../_kit`. Scenes reference `_kit/...`, never `../` paths, because the renderer
serves only the scene dir.

## Files

| File | What |
|---|---|
| `theme.css` | The file you edit. Colours, the one accent, font stacks. Loaded after `tokens.css`, so it overrides it. Dark `:root` plus a `.cream` light variant |
| `tokens.css` | Defaults: palette, type scale, spacing, HUD and section-label styles |
| `harness.js` | `MV.scene(build)` registers the paused timeline at `window.__timelines[<data-composition-id>]`, builds after `document.fonts.ready`, pads to `data-duration`, `?t=` seeks. Helpers: `MV.cue(i)`, `MV.cueEnd(i)`, `MV.word(i, n)`, `MV.wordOf(i, 'word')` (each takes a fallback as its last argument for unvoiced scenes), `MV.tok('accent')`, `MV.rng(seed)`, `MV.hud(tl)`, `MV.timecode(t)` |
| `templates/scene.html` | Blank scene: HUD, lower-right section label, cues.js hook |
| `patterns/` | 15 motion patterns, listed below. Open one in a browser with `?play=1` to watch it |

## GSAP

GSAP and its plugins load from `cdn.jsdelivr.net/npm/gsap@3.15.0/dist/` at a pinned version. Nothing is
vendored here. GSAP ships under its own license (https://gsap.com/standard-license), not this repo's.
Rendering needs network access as a result. To render offline, download the same files into
`kit/vendor/` and point the `<script src>` lines at `_kit/vendor/...`.

## Fonts

None ship with the kit. The default stacks are generic (`sans-serif`, `serif`, `monospace`), so the face
depends on the machine that renders. For the same face everywhere, put woff2 files in `kit/fonts/`,
declare them with `@font-face` in `theme.css`, and give the family a name no system font has. Never
`@import` or a web-font CDN.

## Rules for a scene

- Keep `window.__timelines = window.__timelines || {};` in the inline script: `hyperframes lint` reads it statically.
- Colours in tweens come from `MV.tok(...)`, never hex literals, so `theme.css` and `.cream` apply.
- Every value in a pattern's `P` object marked `// DEMO VALUE` gets replaced from the film's `KIT.md`.
- When you paste a pattern into a scene, change its `../` asset paths to `_kit/`.
- A scene with no narration (reel, loop) drops the `audio/cues.js` script tag, or `hyperframes check` fails on the 404.

## Patterns

| # | File | Use it for |
|---|---|---|
| 01 | `kinetic-headline` | A line said verbatim; words at speech pace, one italic-serif emphasis word turns accent when spoken |
| 02 | `number-counter` | One real metric as the hero: ticker, mono unit, dated source stamp |
| 03 | `bar-reveal` | 2-6 values compared; bars grow, the winner alone takes the accent |
| 04 | `self-drawing-diagram` | Architecture or flow; nodes pop as named, edges draw in |
| 05 | `packet-along-path` | Data moving through a system; hubs pulse on arrival |
| 06 | `focus-zoom-camera` | Dense slide, camera pushes to what is being said (hold, short move, hold). `check` warns `panel_out_of_canvas` on the cropped neighbours; expected |
| 07 | `spotlight-dim-blur` | Same job as 06 without moving; the others dim and blur |
| 08 | `section-label` | Lower-right chapter chip; seeded scramble swap at a chapter change |
| 09 | `quote-card` | Verbatim quote in the italic serif, accent highlighter sweep, source last |
| 10 | `before-after-split` | Old vs new with one measured number per side |
| 11 | `list-checkmarks` | Steps or requirements; ticks draw themselves, one per narration line |
| 12 | `title-outro-card` | Opening title or closing lockup (the outro echoes the title) |
| 13 | `hero-morph` | One shape carried across beats, changing form (MorphSVG) |
| 14 | `corner-hud` | Frame furniture: chapter index rolls, timecode and progress bar are functions of time |
| 15 | `word-slam` | Slot-machine word swap (`slot`) or one-word slams (`slam`) for reel and launch beats |

`kit/music/` is not shipped; bring your own bed. A relative `--music` path is tried against the film folder, the work root (`MVID_ROOT` or the current directory), and then the engine dir.
