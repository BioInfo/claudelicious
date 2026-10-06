# House style

Sources: a teardown of 13 viral Claude/Opus-made code-rendered videos (2026-09-30, frames
tiled and cut-detected), the motion-video-kit motion principles (echris6/motion-video-kit,
MIT; full notice in `../THIRD-PARTY.md`), and the owner's own rulings. The kit's patterns implement most of this; see
the kit README.

## Signal density (applies to every film)

- **Say it in the time it needs.** A point worth 10 seconds gets 10 seconds, never 30. Cut any visual that only illustrates a sentence already understood.
- **The point lands in the first 10 seconds.** The opening states why this matters to the viewer, not a scene-setting news recap. Incidents and background are evidence for a claim, never the opener on their own.
- **One idea per scene, 8-15s per scene.** A scene that needs more is two scenes or a cut.
- **Narration: short spoken sentences, about 150-175 wpm** (Kokoro `speed` 1.15-1.2). No preamble lines ("So what happened next?", "Put that together and..."). The film's length is whatever the content needs, never a target to fill; an explainer that runs long is a draft.
- **Gate 1 check:** for each narration line, ask "what does the viewer learn here that they did not know one line ago?" If nothing, cut it.

## Pace per mode

| Mode | Change rate | Cuts | Notes |
|---|---|---|---|
| explainer / paper | new element or state every 1.5-2.5s | rare, 0-9 per minute | continuous camera; holds are deliberate, joined by short eased moves |
| demo | one action every 3-5s | on a real UI state change | cursor dwell 800ms on targets, centered targets, click produces a visible result |
| reel | new state every 0.9-1.5s | on the beat (120 BPM puts cuts on x.0 and x.5) | something happens on every beat; no frozen stretch over 0.6s |
| loop | as reel | as reel | last frame equals first frame |

Frozen-time bar (reels only): under about 1s per 30s of frame-diff stillness, no single hold
over 0.6s except the end card. Explainers hold on purpose so the viewer can read.

## Hook (first 3 seconds)

- Frame 0 is a finished composition that is already moving. Never a half-entered word, a logo, a black fade-in or a title card.
- The message or the hero object is readable by about 2.5s.
- Good openers: a strange true fact from `KIT.md`, a line of copy typed word by word, a cursor doing something, the hero object mid-motion.

## Hero object

One object carries the story across the whole piece and keeps its identity: a dot, a
token, a card, a cursor, a shape, a zoom target. Transitions are morphs or match-cuts
through that object, not crossfades between unrelated layouts. When it crosses a cut,
pre-position the destination so it lands on the same pixels.

**Scene joins in `film.json`.** Between scenes that carry no shared object, use `slideleft` (a hard push) or `fadeblack` (a dip). Never `fade`, `dissolve` or the `smooth*` family between busy layouts: they blend both scenes, so text prints over text. The first proof film (2026-09-30) showed doubled HUD labels and headline-over-card ghosts with `fade` and `smoothleft`; `slideleft` cleared it.

## Palette

- Neutral ground plus ONE accent, occasionally a second for contrast. Grounds: near-black (#0F0F10-ish), warm cream (#ECE9E0-ish), white.
- The accent carries meaning: the answer, the new value, the keyword. Everything else stays neutral.
- Flipping the ground between chapters (black to cream to accent) marks sections.
- Tokens live in the kit's token file; brand swaps happen there, never inline.
- Text contrast WCAG AA (4.5:1) on all settled text.

## Type trio

1. Heavy grotesk display for 1-3 word slams.
2. Italic serif accent for the emphasized word or tagline ("motion *designer*").
3. Small monospace for HUD, numbers, units, timecodes, labels.

Words on screen: 1-3 for a slam, about 8 maximum for a headline. Paragraphs only in the
paper lane, 3-4 short lines. Text enters word by word, slams in, or swaps like a slot
machine; never a whole block fading in. Readable text is at least 22px at 1080p.
Local woff2 fonts or generic stacks only (see `contract.md`).

## HUD and frame furniture

- Tiny mono corner labels: chapter index ("01 / THE WAIT"), timecode or progress bar, crop-mark corners.
- Section label lower-right, above y=993.
- A data HUD may advance with the story: a date stamp, a counter, a log-scale ruler.

## Numbers and diagrams

- Numbers are hero elements and always animate: count up to the real `KIT.md` value, then settle and hold long enough to read. Big number plus a small mono unit label.
- Charts draw on: lines trace, bars grow from zero, value labels land last.
- Diagrams draw themselves; packets travel along paths; formulas get underbrace annotations.
- UI is real (screenshots, recordings) or real-looking components driven by a visible cursor.

## The 8 motion principles (motion-video-kit)

1. The thing in front of the shot becomes the transition: a title, logo or object moves toward camera while the next scene already waits underneath.
2. One object carries the story across shots and keeps its identity.
3. One main movement leads, smaller ones layer under it, all overlapping. The frame never stops and starts all at once.
4. Speed always changes: land slowly enough to read, leave fast, slow into the next arrival. No linear motion. Under film-level motion blur, a fast move ghosts into stacked copies; make it a cut or a dip instead.
5. Cuts only when size, direction and subject match on both sides.
6. Every action produces a visible result: a scan makes findings, a tap makes a new state, a request makes a confirmation.
7. Type is motion too: big words enter from opposite sides, reveal the next scene, and never sit over busy picture without a backing.
8. Vary the scale: close, wide, overhead, full-frame type. Never repeat a layout, like a heading over three cards.

Composition rules that follow: the lead subject fills 60-85% of the frame in feature
beats; one or two reading targets at a time; equal spacing and shared left edges in lists.

## The owner's rulings that shape the look

- Text never jiggles. Still holds joined by short eased moves; no slow continuous zoom over text.
- Focus follows the voice: zoom or spotlight to what the line names, dim and blur the rest.
- Show the real thing moving. Recordings of the real app beat invented UI.
- Real infographics, not words on a page. Never put the narrated sentence on screen.
- Springs with at most a small overshoot.

## Ending

Bookend: the last frame echoes the first (the hook's object or line returns, resolved).
Launch and reel pieces end on wordmark, one-line tagline, URL, and two or three tiny mono
stats, readable at phone size for at least 1.5s. No fade to black end card.

## Banned looks

- Centered text on a gradient background.
- Whole-block fade-ins of text.
- Glows, lens flares, particle bursts.
- Bouncy or elastic easing.
- Slow zoom over text.
- Multi-stop gradients on UI chrome.
- Heading over three cards, repeated.
- Mismatched icon strokes; stock-looking icons.
- Dead time, and anything that looks like a template.
- 3D (Three.js) as decoration; use it only when the idea is spatial.
