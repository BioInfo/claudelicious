# Lessons ledger

One row per ruling or trap. Append when the owner rules on something or a render fails in a
new way, in the same session. Date is when the ruling was recorded; source is where it came
from. This file is the point of the skill: it is how the next film starts higher than the last.

Sources: `prior-skill` = an earlier explainer-video skill the owner used and approved
(2026-09-29); `notes` = past video rulings and memories from the owner's notes;
`teardown` = a 2026-09-30 teardown of viral model-made explainer videos. Film slugs
(`science-film`, `leadership-film`, `first-film`) name the film where the lesson was learned.

## Rulings

| Date | Ruling | Source |
|---|---|---|
| 2026-10-02 | A flash-tier image model was good enough for plates; the pro tier is not the default | owner |
| 2026-10-02 | The painted-overlay recipe works (second film approved after one fresh-critic round). What got it there: a per-scene shot spec giving every line a code-drawn event over the plate, scene agents resumed with the critic's list rather than rebuilt, and a grain-proof freeze detector to find dead stretches. Two assembled cuts against nine for the first film | owner |
| 2026-10-02 | Plates approved, but a painted plate with a slow camera move and voice over it is not an explainer; two talking scenes over a backdrop do not make one. Every line needs code-drawn action over the plate (simulation, particles, in-world type) filling 60-85% of frame | owner, leadership-film excerpt |
| 2026-10-01 | Look chosen: science film = cinematic molecular (Drew Berry, lit 3D, shallow DoF, haze, orange rim on navy); leadership film = painted editorial (Goodsell watercolour, paper texture). Prompts kept as JSON sidecars beside each plate | owner |
| 2026-10-01 | Cinematic films drop the HUD furniture (corner crops, timecode, channel label); it reads as motion graphics, not film. Keep only the section label if anything | owner, science-film |
| 2026-10-01 | Judged too basic: a typographic/data scene is not a film. Do look-dev FIRST: 2 directions x 2 shots as Gemini Pro stills, the owner picks the world, then prototype an IMAGE-LED shot (plate + motion + code overlay), never a text-only scene | owner, science-film s01 |
| 2026-10-01 | Spectacular over templated: research current standout Opus videos + subject explainers before each storyboard; Gemini plates OK for physical subjects; fold what we learn back into the skill after every film | owner, leadership-film + science-film |
| 2026-09-30 | First film from this lane approved (first-film v3: 67s, Kokoro af_heart, calm-tech bed, slideleft joins, HUD on film time, two critic rounds) | owner |
| 2026-09-29 | Narration and music are required for explainers; without them it reads as a web page revealing itself a piece at a time | prior-skill |
| 2026-09-29 | Section label lower-right | prior-skill |
| 2026-09-29 | Text never jiggles: holds plus short eased moves, no slow zoom over text | prior-skill |
| 2026-09-29 | Focus follows the voice: zoom or spotlight what the line names, dim and blur the rest | prior-skill |
| 2026-09-29 | Show the real thing moving: click-through recordings of the real app | prior-skill |
| 2026-09-29 | Cool animation like viral Claude explainers: kinetic type, counters to real numbers, self-drawing diagrams, packets on paths | prior-skill |
| 2026-09-29 | Real numbers, dated, from the KIT.md truth section | prior-skill |
| 2026-09-29 | Kokoro af_heart approved as the narration voice | prior-skill |
| 2026-09-30 | Master every audio deliverable: strip TTS onset, 10ms/25ms fades, loudnorm I=-16 LRA=11 TP=-1.5 | notes |
| 2026-09-30 | Verify audio for known artifacts by transcription, not by LUFS | notes |
| 2026-09-30 | Narration high level, plain English, no stat dumps | notes |
| 2026-09-30 | Real screen footage beats text cards | notes |
| 2026-09-30 | Graphics must be real infographics, not words on a page | notes |
| 2026-09-30 | Never ship out-of-sync lipsync | notes |
| 2026-09-30 | An act that runs too long or goes silent gets tightened | notes |
| 2026-09-30 | Publishing gated on an explicit yes naming the destination | notes |
| 2026-09-30 | Subtitles off by default; --captions for muted autoplay | notes |
| 2026-09-30 | Open mid-work, not on a title card | notes |
| 2026-09-30 | Music bed about 0.15 under voice; music taste still open | notes |
| 2026-09-30 | Narrate like a university professor; avoid Claudisms (staccato fragments, stat dumps) | teardown |
| 2026-09-30 | Caption off the rendered audio, never the script | teardown |
| 2026-10-04 | Too slow, low signal, across most films to date: a point that needs 10 seconds gets 10 seconds, not 30. Point lands in the first 10s; one idea per 8-15s scene; no news-recap opener; Kokoro speed 1.15-1.2; length is whatever the content needs. Spec: house-style.md "Signal density" | owner |
| 2026-10-05 | The first film cut under the signal-density rule passed gate 3 on first viewing: under two minutes, nine scenes of 8-15s, the point by 0:12, two critic rounds. Keep that shape: a why-now hook, the substance in the middle, an end card | owner |
| 2026-10-05 | Treatment discipline: three candidate structures with the reason for the pick, a reason on every focus move, and a "differs from the last film" table where four of six rows must differ. The first idea for a subject is its cliché | owner |
| 2026-10-01 | Endings are a home run, never a cut-off: the last section wraps the thesis, builds to the final line, lands a visual climax on its last word (a bookend to frame 0), then a title end card while the music swells and resolves (`film.json "outro": N`). A hard cut on the last word read as a cut-off | owner, science-film v7 |

## Traps

| Date | Trap | Source |
|---|---|---|
| 2026-10-04 | `"mblur": 8` turns any fast move (a 600px camera drop, a scale-in, falling cards) into 6-8 stacked ghost copies. The per-scene render does not apply it, so scene agents never see it. Fast moves become cuts or dips, or keep per-frame displacement small; the critic checks a full-size frame mid-move | critic rounds |
| 2026-10-05 | Two defects no still frame shows: on-screen text that leaves before it can be read, and black frames mid-film. The critic packet now carries a text read-time table and a black-frame check, and the critic rules on every row | critic rounds |
| 2026-10-02 | Scene cuts felt slow on every film, with a noticeable pause between scenes. Dead air at a cut = scene tail + next lead + the TTS's own ~0.25s clip padding at each end, minus the crossfade: 2.5+0.8+0.5-0.6 = about 3.2s. Defaults are now lead 0.35, gap 0.7, tail 0.5, crossfade 0.4, about 1.0s audible. Only the end-card scene keeps `[[tail 4.0]]`. Measure from `cues.json`, not by ear | owner |
| 2026-10-02 | Parallel scene agents share one scratch area: generic temp names (`p2.js`) collided between two scenes. The scene brief requires temp files under a per-scene temp dir (`films/<slug>/tmp/<scene-id>/`), and the parent greps each assembled `index.html` for other scenes' labels | scene agents |
| 2026-10-02 | A scene agent ran the renderer's snapshot inside ANOTHER scene's directory to read its end frame. Read a sibling's end frame from `renders/<id>.mp4` with ffmpeg instead | scene agents |
| 2026-10-02 | Kokoro misread a product name as an ordinary word. Check every brand or product name via KPipeline phonemes before voicing; respell it in `narration.txt` (split a compound into two words) and key the animation on the first word. When ASR "mishears" a word, check the phonemes first: often the transcriber was wrong and the voice was right | scene agents |
| 2026-10-03 | Frame 0 of a film that opens mid-motion on real footage is a raw, unframed frame (tool output, temp paths). It went out as a thumbnail. Make any thumbnail or card from a deliberate frame (`ffmpeg -ss <end-card time> -frames:v 1`) and look at it first | owner |
| 2026-10-02 | The critic's freeze check was blind under film grain: `noise=allf=t` changes every pixel every frame, so freezedetect on the full frame reported 0.00s on every grained scene since grain shipped. Fixed in `lib/critic.py`: downscale to 160px + gblur before freezedetect (control: 3s still under grain, old 0 hits, new 3.0-6.0; slow pan not flagged). A zero from an instrument that cannot fail is not a pass | leadership-film s04 agent |
| 2026-10-02 | LTX on a plate with a single accent-colour mark (one thin orange stroke) swept it into a near-full orange ring, so the 'judged good' colour was on screen before its cue. Grade the accent out of the clip (`huesaturation=saturation=-1:colors=r+y:strength=4`) and let code draw the only accent | leadership-film s01 |
| 2026-10-01 | Gemini Pro plates: adding 'full bleed, no white border' pushed look B toward photographic; crop inside the painted border instead. A requested count of objects came back about half again too many, and the aspect came back square: never trust a count or aspect in a plate, draw counted objects in code | leadership-film |
| 2026-10-01 | LTX i2v on painted (watercolor) plates: architecture and sky hold; abstract matter does not. Loose particles melted into a cartoon blob, and particles told to align into a line sprouted wires. Use LTX for camera and light on solid subjects; draw particle behaviour in code over the still plate | leadership-film |
| 2026-10-01 | Music beds: the synthesized pad has 3s fades and duck_music added another 3s; the film ended on 2.5s dead air. Fades are now 0.5 in / 1.5 out | science-film critic r1 |
| 2026-10-01 | Diagram scenes over a dimmed plate shrank the lead subject to 5-25% of frame; the cinematic look needs diagrams at 70-80% width with 60-150px glyphs, or they read as HUD | science-film critic r1 |
| 2026-10-01 | Intermediate counter values (2/200, 7/200, 'min 7') imply a measured time course the source never gave: a P0 even when the end value is right. Animate the build-up, print only the sourced end value | science-film critic r1 |
| 2026-10-01 | One lower-third pattern (bold sans + orange italic word + mono caps over a bottom gradient) reused 8x read as template. Vary label treatment per scene: in-world callouts with leader lines, depth-placed numbers, chips | science-film critic r1 |
| 2026-10-01 | Typing text under `mblur`: quantizing the length did NOT work (critic r2 still saw doubled glyphs, a re-centring line and a truncated string). What works: lay the FULL string out once, left edge fixed, and reveal it with a stepped clip-path (`inset(0 100% 0 0)` → `inset(0 0% 0 0)`, `ease: steps(N)`) on an inline-block. No glyph ever moves, so sub-frames cannot ghost. Verified on s01 v4 frames | science-film critic r2 |
| 2026-10-01 | Music bed: two separate faults. (1) `music_volume` 0.16 on a −20 LUFS bed plus a ratio-8 duck measured −46 dB in narration gaps; 0.4 is the starting point. (2) `prepare_bed` loops a short bed with a crossfade, but beds end on their own fade-out plus seconds of near-silence, so a 2s crossfade left a ~5s hole at the seam (about six seconds of silence at the seam). The loop now trims to the audible body (`bed_body_end`, −40 dB) and crossfades 6s. Gate: `silencedetect=noise=-50dB:d=0.5` on the master returns nothing. Read the whole audio path before patching one function (a duplicate loop was first added in `duck_music`, then reverted) | science-film critic r2–r3 |
| 2026-10-01 | A critic's fix is a hypothesis about the science, not an order: a fix that redescribed what an experiment did was relayed to a scene agent as written, and it contradicted a sourced fact in KIT. Check every relayed fix against KIT before dispatch | science-film critic r3 |
| 2026-10-01 | LTX-2.3 image-to-video via ComfyUI: 1376x768, 121f@24, 8 steps = about 3.5 min per clip; the subject's shape held across the clip | science-film look-dev |
| 2026-10-01 | Motion blur: `"mblur": 4` strobes into 4 discrete ghosts on fast text moves (~50px/frame); `8` smears cleanly. Cost ~2 min render per 20s scene at 8. Keep fast text moves >=1.2s | science-film s01 |
| 2026-10-01 | Science films: check the brief against the primary source before storyboarding. A headline figure came from a different experiment than the one the brief named, and a scene had attributed it to the wrong source | science-film |
| 2026-10-01 | Research subagents hit the 30-turn ceiling before writing: brief them to write the report file FIRST as a skeleton and append, and cap searching at ~20 tool calls | leadership-film |
| 2026-09-29 | `gsap.set` outside the timeline for hidden states | prior-skill |
| 2026-09-29 | `fromTo` must include the visible opacity | prior-skill |
| 2026-09-29 | Local woff2 fonts only; named system fonts get fetched substitutes | prior-skill |
| 2026-09-29 | Zoom via scale plus counter-translate on two wrappers, measured after fonts.ready | prior-skill |
| 2026-09-29 | Labels above y=993; text at least 22px | prior-skill |
| 2026-09-29 | Element dropouts: HF_STATIC_DEDUP off and -w 1 | prior-skill |
| 2026-09-29 | Gate: duration within 0.1s of cues.total, contact sheet at fps=9/dur, full-size frames, 1fps dropout sample, cue-timed focus check, numbers vs KIT truth, stillness PSNR >= 65dB | prior-skill |
| 2026-09-30 | Verify audio per beat (volumedetect, transcribe each window) | notes |
| 2026-09-30 | Never trust exit codes: a TTS tool has exited 1 on success; silent clips exit 0 | notes |
| 2026-09-30 | Back up --out before a re-render | notes |
| 2026-09-30 | Count-up stats: wait for the settled value before snapshotting | notes |
| 2026-09-30 | Cursor dwell 800ms, centered targets, occlusion check, hover link CTAs | notes |
| 2026-09-30 | Visual change every 3-5s in demos; demos crater past about 3 minutes | notes |
| 2026-09-30 | Stage voiceover per beat, resumable | notes |
| 2026-10-01 | Slow-motion clips stutter: a 24fps clip at `data-playback-rate` 0.4 changes frame every 2.5 output frames (3-2-3-2 cadence), and mblur does not hide it (it reads as a shuffle). Before the full render, retime each slowed clip with ffmpeg: `setpts=PTS/<rate>,minterpolate=fps=30:mi_mode=mci` (about 30s per clip), then set the tag's `data-playback-rate` to 1. New `<video>` tags should never carry a rate < 1 | owner, science-film v7 |
| 2026-10-01 | Kokoro misreads Latin names and abbreviations. Use the misaki inline override in narration.txt: `[word](/phonemes/)`. Check with `KPipeline(...)` → `.phonemes` before re-voicing | owner, science-film v7 |
| 2026-10-01 | Never give a scene element the class `stage`: the kit's token CSS styles `#root,.stage` with an opaque `background:var(--bg)`, so a `.stage` wrapper paints a navy sheet over every layer beneath it (one scene lost all its footage and overlays; the browser preview looked fine). Bisect a vanished layer with `hyperframes snapshot --at` plus `display:none` overrides, positive-controlled on a scene whose footage renders | science-film s06 rebuild |

## Legacy (do not follow)

| Date | Superseded rule | Why |
|---|---|---|
| 2026-09-30 | Video work goes through a template-picker app and the owner picks a template | No templates in the HTML lane; the storyboard and the mp4 are the window |
| 2026-09-30 | Narration audio only via a remote voice pipeline | Kokoro runs locally; another voice is a new entry in `BACKENDS` in `engine/lib/tts.py` |
| 2026-09-30 | A one-shot film command and React-based long-explainer comps | Replaced by the new/voice/render/critic/assemble verbs |
| 2026-09-30 | `silenceremove` caps dead air | No such pass; the lead/gap/tail layout keeps silence under about 1s |
| 2026-09-29 | About 3 minutes for an explainer, as a target | Superseded 2026-10-04: 3 minutes is a ceiling; length is whatever the content needs |
| 2026-09-30 | Narration lead 0.8s, tail 2.5s | Superseded 2026-10-02: lead 0.35s, tail 0.5s |
