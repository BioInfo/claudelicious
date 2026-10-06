# Audio

Audio makes strong visuals feel amateur faster than anything else. Numbers here match
the engine contract (`contract.md`); the contract wins on conflict.

## Narration

- Default voice: Kokoro `af_heart`, run locally, via `<engine> voice`. Word timestamps come from Kokoro tokens; no ASR needed for cues.
- Layout per scene: lead 0.35s, gap 0.7s between lines, tail 0.5s (overridable per film). With a 0.4s crossfade a cut carries about 1s of audible gap. Longer defaults read as a pause between every scene. Measure it from `cues.json` (first word start, and `total` minus last word end), not by ear. Only the end-card scene gets a long tail (`[[tail 4.0]]`). `narration.txt` holds one spoken line per cue.
- Speed: Kokoro `speed` about 1.15-1.2, which lands near 150-175 words per minute.
- To use another voice, add a backend to `BACKENDS` in `engine/lib/tts.py`.
- Writing: plain spoken sentences, one per cue, numbers written as spoken. Narrate like a university professor. No Claudisms: no staccato fragments, no stat dumps, no "it isn't X, it's Y". Narration stays high level; the screen carries the detail.
- The owner's own voice or brand: run the script past their voice spec.

## Mastering

- Strip the TTS onset, 10ms fade-in and 25ms fade-out per line.
- Narration mastered to -16 LUFS.
- Final mix: `loudnorm I=-16 TP=-1.5 LRA=11`. Reels may go to -14 LUFS; calm explainers stay at -16.
- No silence over about 1s inside a scene. The lead/gap/tail layout enforces it; there is no `silenceremove` pass.
- One exception per film: a voice pause of about 0.5s before the single peak reveal, `[[hold 0.5]]` on the line before it. The duck releases in that gap, so the bed rises rather than drops; a true music drop-out needs an assemble feature of its own. One only; a second reads as slow. (Pause research: about 0.5s helps comprehension, 4s hurts. Fors, Gothenburg 2015.)
- Verify every beat by transcription (stable-ts on the rendered audio) plus `volumedetect` per window. LUFS alone cannot hear a dropped word or a silent clip. Tool exit codes lie here: a TTS tool has exited 1 on success, and silent clips have exited 0.
- Back up the previous `out/` file before re-rendering over it.

## Music bed

- Bring your own instrumental bed, with a license that allows your use: `--music <path>`. Offer the bed choice in the storyboard defaults.
- Until a bed is approved: `"music": "pad"` (a synthesized ambient pad).
- Never MusicGen (non-commercial weights), YuE, Stable Audio Open, or scripted Pixabay downloads.
- Level: about 0.15-0.16 under the voice (`music_volume` in `film.json`).
- Ducking: `sidechaincompress threshold=0.03 ratio=8 attack=20 release=400`, keyed on the narration.
- Loop the bed on its own rhythm: seam it where the onset pattern matches the bed's opening, with a crossfade of a few seconds, after trimming the bed's own fade-out and trailing near-silence. Gate: `silencedetect=noise=-50dB:d=0.5` on the master returns nothing. No near-silent intro; do not let it die before the ending. If the music resolves on the end card, add no separate sting.
- Avoid: vocals or humming, vinyl crackle, ukulele or whistling stock, trailer hits, EDM drops, risers, anything "epic".

## Sound effects

Keep them sparse. That is supported by evidence as well as taste: added music and sounds lowered recall in narrated animations (Moreno & Mayer 2000). If your engine has no effects layer yet, the rules below are the spec for when one is built.

- One short, soft, rumble-free whoosh per real scene change. Nothing boomy (little energy below 150 Hz, rise about 80-400ms).
- Small clean UI sounds only on real actions: a click on a cursor click, a tick on a label, one soft chime on a confirmation.
- Level effects in their own frequency band against a music-only render: about +3-4 dB in band, never more than about 4 dB lift at 2-8 kHz. Soften sounds that cluster within 0.15s.
- When in doubt, fewer. Effects copied from punchy launch films onto a calm score read as annoying.

## Reels and loops

- Music only, no narration, no captions.
- Cut on beats: time-stretch the bed to a tempo where every cut lands on a beat (120 BPM puts cuts on x.0 and x.5). Measure onsets rather than trusting the grid.
- Groove arrives on the hero moment; 5ms fade-in on the first sample; the track's own final hit on the end card.
- For a loop, the audio seam must be inaudible at the wrap point.

## Captions

- Off for explainers. `--captions` for every social cut (feeds autoplay muted), always burned in, because most posting paths upload no caption track.
- Cut captions from the RENDERED audio (stable-ts), never from the script: TTS reads numbers and units differently from how they are written.
- Keep captions inside the safe area (about 10% margins; bottom 20% on 9:16 is covered by platform UI).

## Deliverables

- `out/<slug>/<slug>-v<N>.mp4` and always a music-only export `out/<slug>/<slug>-v<N>-music.wav`, so a complaint about "that whoosh" can be traced to the right layer.
- Keep previous versions; never overwrite v<N>, write v<N+1>.
