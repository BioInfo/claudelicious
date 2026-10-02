# Lessons ledger

One row per ruling or trap. Append when the owner rules on something or a render fails in a
new way, in the same session. Date is when the ruling was recorded; source is where it came
from. This file is the point of the skill: it is how the next film starts higher than the last.

Sources: `prior-skill` = an earlier explainer-video skill the owner used and approved
(2026-09-29, "its awesome"); `notes` = past video rulings and memories from the owner's notes;
`teardown` = a 2026-09-30 teardown of viral model-made explainer videos. Film slugs
(`phage-art`, `agents-and-good`, `how-this-was-made`) name the film where the lesson was learned.

## Rulings

| Date | Ruling | Source |
|---|---|---|
| 2026-10-02 | Plates approved ("I like those backdrops"), but a painted plate with a slow camera move and voice over it is not an explainer: "just two scenes with people talking over it... doesn't make it a cool explainer video". Every line needs code-drawn action over the plate (simulation, particles, in-world type) filling 60-85% of frame | owner, agents-and-good excerpt |
| 2026-10-01 | Look chosen: science film = cinematic molecular (Drew Berry, lit 3D, shallow DoF, haze, orange rim on navy); leadership film = painted editorial (Goodsell watercolour, paper texture). Prompts in films/phage-art/assets/lookdev/*.json sidecars | owner |
| 2026-10-01 | Cinematic films drop the HUD furniture (corner crops, timecode, channel label); it reads as motion graphics, not film. Keep only the section label if anything | owner, phage-art |
| 2026-10-01 | 'Pretty basic': a typographic/data scene is not a film. Do look-dev FIRST: 2 directions x 2 shots as Gemini Pro stills, the owner picks the world, then prototype an IMAGE-LED shot (plate + motion + code overlay), never a text-only scene | owner, phage-art s01 |
| 2026-10-01 | Spectacular over templated: research current standout Opus videos + subject explainers before each storyboard; Gemini plates OK for physical subjects; fold what we learn back into the skill after every film | owner, agents-and-good + phage-art |
| 2026-09-30 | First film from this lane approved: "awesome!" (how-this-was-made-v3: 67s, Kokoro af_heart, calm-tech bed, slideleft joins, HUD on film time, two critic rounds) | owner, watching v3 |
| 2026-09-29 | Narration and music are required for explainers; without them it is "just a website that comes in a piece at a time" | prior-skill |
| 2026-09-29 | Section label lower-right | prior-skill |
| 2026-09-29 | Text never jiggles: holds plus short eased moves, no slow zoom over text | prior-skill |
| 2026-09-29 | Focus follows the voice: zoom or spotlight what the line names, dim and blur the rest | prior-skill |
| 2026-09-29 | Show the real thing moving: click-through recordings of the real app | prior-skill |
| 2026-09-29 | Cool animation like viral Claude explainers: kinetic type, counters to real numbers, self-drawing diagrams, packets on paths | prior-skill |
| 2026-09-29 | Real numbers, dated, from the KIT.md truth section | prior-skill |
| 2026-09-29 | About 3 minutes for an explainer | prior-skill |
| 2026-09-29 | Kokoro af_heart approved as the narration voice | prior-skill |
| 2026-09-30 | Master every audio deliverable: strip TTS onset, 10ms/25ms fades, loudnorm I=-16 LRA=11 TP=-1.5 | notes |
| 2026-09-30 | Verify audio for known artifacts by transcription, not by LUFS | notes |
| 2026-09-30 | atempo 0.9 for the cloned voice | notes |
| 2026-09-30 | Narration high level, plain English, no stat dumps | notes |
| 2026-09-30 | Real screen footage beats text cards | notes |
| 2026-09-30 | Graphics must be real infographics, not words on a page | notes |
| 2026-09-30 | Never ship out-of-sync lipsync | notes |
| 2026-09-30 | An act that runs too long or goes silent gets tightened | notes |
| 2026-09-30 | Publishing gated on an explicit yes naming the destination | notes |
| 2026-09-30 | Revenue and subscriber numbers never on frame; privacy masked at capture | notes |
| 2026-09-30 | Subtitles off by default; --captions for muted autoplay | notes |
| 2026-09-30 | Open mid-work, not on a title card | notes |
| 2026-09-30 | Music bed about 0.15 under voice; music taste still open | notes |
| 2026-09-30 | Narrate like a university professor; avoid Claudisms (staccato fragments, stat dumps) | teardown |
| 2026-09-30 | Caption off the rendered audio, never the script | teardown |
| 2026-10-01 | Endings are a home run, never a cut-off: the last section wraps the thesis, builds to the final line, lands a visual climax on its last word (a bookend to frame 0), then a title end card while the music swells and resolves (`film.json "outro": N`). A hard cut on the last word read as "cutting off" | owner, phage-art v7 |

## Traps

| Date | Trap | Source |
|---|---|---|
| 2026-10-02 | The critic's freeze check was blind under film grain: `noise=allf=t` changes every pixel every frame, so freezedetect on the full frame reported 0.00s on every grained scene since grain shipped. Fixed in `lib/critic.py`: downscale to 160px + gblur before freezedetect (control: 3s still under grain, old 0 hits, new 3.0-6.0; slow pan not flagged). A zero from an instrument that cannot fail is not a pass | agents-and-good s04 agent |
| 2026-10-02 | LTX on a plate with a single accent-colour mark (one orange star trail) swept it into a near-full orange ring, so the 'judged good' colour was on screen before its cue. Grade the accent out of the clip (`huesaturation=saturation=-1:colors=r+y:strength=4`) and let code draw the only accent | agents-and-good s01 |
| 2026-10-01 | Gemini Pro plates: adding 'full bleed, no white border' pushed look B toward photographic; crop inside the painted border instead. A '17 stones' count comes back as ~25 and 1:1: never trust a count or aspect in a plate, draw counted objects in code | agents-and-good |
| 2026-10-01 | LTX i2v on painted (watercolor) plates: architecture and sky hold (tower, star trails); abstract matter does not. Sediment melted into a cartoon blob, 'grains align to a line' sprouted copper wires. Use LTX for camera and light on solid subjects; draw particle behaviour in code over the still plate | agents-and-good |
| 2026-10-01 | Music beds: the synthesized pad has 3s fades and duck_music added another 3s; the film ended on 2.5s dead air. Fades are now 0.5 in / 1.5 out | phage-art critic r1 |
| 2026-10-01 | Diagram scenes over a dimmed plate shrank the lead subject to 5-25% of frame; the cinematic look needs diagrams at 70-80% width with 60-150px glyphs, or they read as HUD | phage-art critic r1 |
| 2026-10-01 | Intermediate counter values (2/200, 7/200, 'min 7') imply a measured time course the source never gave: a P0 even when the end value is right. Animate the build-up, print only the sourced end value | phage-art critic r1 |
| 2026-10-01 | One lower-third pattern (bold sans + orange italic word + mono caps over a bottom gradient) reused 8x read as template. Vary label treatment per scene: in-world callouts with leader lines, depth-placed numbers, chips | phage-art critic r1 |
| 2026-10-01 | Typing text under `mblur`: quantizing the length did NOT work (critic r2 still saw doubled glyphs, a re-centring line and a truncated string). What works: lay the FULL string out once, left edge fixed, and reveal it with a stepped clip-path (`inset(0 100% 0 0)` → `inset(0 0% 0 0)`, `ease: steps(N)`) on an inline-block. No glyph ever moves, so sub-frames cannot ghost. Verified on s01 v4 frames | phage-art critic r2 |
| 2026-10-01 | Music bed: two separate faults. (1) `music_volume` 0.16 on a −20 LUFS bed plus a ratio-8 duck measured −46 dB in narration gaps; 0.4 is the starting point. (2) `prepare_bed` loops a short bed with a crossfade, but beds end on their own fade-out plus seconds of near-silence, so a 2s crossfade left a ~5s hole at the seam (phage-art 1:07–1:13). The loop now trims to the audible body (`bed_body_end`, −40 dB) and crossfades 6s. Gate: `silencedetect=noise=-50dB:d=0.5` on the master returns nothing. Read the whole audio path before patching one function (a duplicate loop was first added in `duck_music`, then reverted) | phage-art critic r2–r3 |
| 2026-10-01 | A critic's fix is a hypothesis about the science, not an order: "route the reruns to miss the find" was relayed to a scene agent as written, and it contradicted KIT ("sampled ART loci"). The reruns reached the genes; they just didn't read upstream. Check every relayed fix against KIT before dispatch | phage-art critic r3 |
| 2026-10-01 | LTX-2.3 image-to-video via ComfyUI: 1376x768, 121f@24, 8 steps = 3.5 min on `<gpu-host>`, phage morphology held across the clip. stopping the host's resident local-LLM service freed enough GPU headroom | phage-art look-dev |
| 2026-10-01 | Motion blur: `"mblur": 4` strobes into 4 discrete ghosts on fast text moves (~50px/frame); `8` smears cleanly. Cost ~2 min render per 20s scene at 8. Keep fast text moves >=1.2s | phage-art s01 |
| 2026-10-01 | Science films: check the brief against the primary source before storyboarding. The 8% ART figure was from Staph phage SA1 data, not the E. coli experiment; a scene had put it in the wrong host | phage-art |
| 2026-10-01 | Research subagents hit the 30-turn ceiling before writing: brief them to write the report file FIRST as a skeleton and append, and cap searching at ~20 tool calls | agents-and-good |
| 2026-09-29 | `gsap.set` outside the timeline for hidden states | prior-skill |
| 2026-09-29 | `fromTo` must include the visible opacity | prior-skill |
| 2026-09-29 | Vendored fonts only; named system fonts get fetched substitutes | prior-skill |
| 2026-09-29 | Zoom via scale plus counter-translate on two wrappers, measured after fonts.ready | prior-skill |
| 2026-09-29 | Labels above y=993; text at least 22px | prior-skill |
| 2026-09-29 | Element dropouts: HF_STATIC_DEDUP off and -w 1 | prior-skill |
| 2026-09-29 | Gate: duration within 0.1s of cues.total, contact sheet at fps=9/dur, full-size frames, 1fps dropout sample, cue-timed focus check, numbers vs KIT truth, stillness PSNR >= 65dB | prior-skill |
| 2026-09-30 | Verify audio per beat (volumedetect, transcribe each window) | notes |
| 2026-09-30 | Never trust exit codes: the voice-clone tool exits 1 on success; silent clips exit 0 | notes |
| 2026-09-30 | Back up --out before a re-render | notes |
| 2026-09-30 | Count-up stats: wait for the settled value before snapshotting | notes |
| 2026-09-30 | Cursor dwell 800ms, centered targets, occlusion check, hover link CTAs | notes |
| 2026-09-30 | Visual change every 3-5s in demos; demos crater past about 3 minutes | notes |
| 2026-09-30 | silenceremove caps dead air | notes |
| 2026-09-30 | Stage voiceover per beat, resumable | notes |
| 2026-09-30 | The GPU host is shared: preflight it before --clone | notes |
| 2026-09-30 | Hero films render on one fixed host; fonts diverge across hosts | notes |
| 2026-09-30 | YouTube API uploads land private and embeddable=false | notes |
| 2026-09-30 | Substack Note video fails silently | notes |
| 2026-09-30 | LinkedIn native video needs a separate API login in the posting tool | notes |
| 2026-09-30 | Posting-tool duration gates: X 140s, LinkedIn 600s, Bluesky 60s, Instagram 90s; pair render with publish and an artifact check | notes |
| 2026-10-01 | Slow-motion clips stutter: a 24fps clip at `data-playback-rate` 0.4 changes frame every 2.5 output frames (3-2-3-2 cadence), and mblur does not hide it (owner: "shuffles"). Run a retime step before the full render: it motion-interpolates each (clip, rate) to 30fps (`minterpolate` mci, ~30s per clip) and rewrites the tag to rate 1. New `<video>` tags should never carry a rate < 1 | owner, phage-art v7 |
| 2026-10-01 | Kokoro misreads Latin binomials ("E. coli" → "ee KOH-lee"). Use the misaki inline override in narration.txt: `[E. coli](/ˌi kˈOlI/)`. Check with `KPipeline(...)` → `.phonemes` before re-voicing | owner, phage-art v7 |
| 2026-10-01 | Never give a scene element the class `stage`: the kit's token CSS styles `#root,.stage` with an opaque `background:var(--bg)`, so a `.stage` wrapper paints a navy sheet over every layer beneath it (s06 lost all footage, trails and ember; the browser preview looked fine). Bisect a vanished layer with `hyperframes snapshot --at` plus `display:none` overrides, positive-controlled on a scene whose footage renders | phage-art s06 rebuild |

## Legacy (do not follow)

| Date | Superseded rule | Why |
|---|---|---|
| 2026-09-30 | Video work goes through a template studio and the owner picks a template | No templates in the HTML lane; the storyboard and the mp4 are the window |
| 2026-09-30 | Narration audio only via the GPU-host voice pipeline | Kokoro runs locally; the clone stays on the GPU host behind --clone |
| 2026-09-30 | A one-shot film command and React-based long-explainer comps | Replaced by the new/voice/render/critic/assemble verbs |
