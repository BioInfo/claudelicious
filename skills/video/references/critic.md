# Fresh critic

Adapted from `critic-prompts.md` and `quality-bar.md` in echris6/motion-video-kit
(github.com/echris6/motion-video-kit, MIT License), with Deedy's screenshot-plus-transcript critic.

## Rules for the dispatcher

- Dispatch a NEW agent every round, `model: opus`. It has seen none of the building.
- Never tell it what you fixed, what you believe about the references, or what you are worried about. It pulls its own frames and measures for itself.
- Run `<engine> critic <slug>` first so `films/<slug>/critic/<video>/packet.md` exists and lists every sheet, frame, transcript and measurement.
- Fix the biggest problem first. P0s go back to the owning scene agent with the timestamp and region.
- The verification round is another fresh agent given the previous report and asked item by item.

## Full-film prompt

Fill the `<>` slots and send verbatim.

```
You are an independent, harsh film critic. You did NOT build this. Judge rendered pixels
and measured audio, not intentions.

Artifact: <films/<slug>/renders or out/<slug>/<slug>-vN.mp4> (<duration>s, <WxH>, <fps>fps).
Brief: <audience, one takeaway, mode, destination>, from films/<slug>/STORYBOARD.md.
Facts file: films/<slug>/KIT.md. Every number, name and claim on screen must appear there.
Packet: films/<slug>/critic/<video>/packet.md. Read it, then open EVERY image it lists: the contact
sheets AND the full-size frames. Sheets hide clipped text; check full-size frames for it.
Read the transcript of the rendered audio against the storyboard narration.

Answer these first:
1. Does this look like the default Opus / template look? Yes or no, and name the specific
   frames that make it so.
2. On mute, can a first-time viewer say what this is about and the one takeaway?

Then check:
- Frame 0 is a finished composition already in motion; no logo, title card or black fade.
- Text never jiggles; no slow zoom over text; no whole-block text fade-ins.
- Focus follows the voice: when the narration names a thing, is that thing where the eye goes?
- No text collisions, including mid-transition. No clipped text. Text >= 22px at 1080p.
  Labels above y=993. WCAG AA contrast on settled text.
- Equal spacing, shared left edges, lead subject fills 60-85% of the frame in feature beats.
- Transitions carry an object or matched direction; no unrelated slide-in after slide-in.
- Numbers on screen match KIT.md exactly; flag any number not in KIT.md.
- The narrated sentence is not printed on screen.
- Audio: transcript matches the script (missing words, garbled numbers, cut-off lines);
  music audible but under the voice; no clicks, no dead air over 1s; loudness from the packet.
- Banned looks: centered text on a gradient, glows, particle bursts, bouncy easing, repeated
  heading-over-three-cards.
- For reel/loop only: frozen time under ~1s per 30s, no hold over 0.6s except the end card.

Report (under 700 words), also written to films/<slug>/critic/<video>/report-<round>.md:
- Template look: yes/no with frames.
- Give every timestamp as film time AND scene time (scene time = film time minus that scene's
  film start in the packet's Scene timeline table), and check a word-timing claim against the
  scene's audio/cues.json before asserting it. Round 1 on the first film misplaced a cue by 1.5s.
- P0 (ship blocker), P1 (visible defect), P2 (polish). Each with timestamp, screen region,
  and a fix that can be implemented in code.
- Separate "measured" from "needs a human" (taste, music fit).
- End with exactly one line: SHIP or ONE MORE PASS.
A video with no bugs is not the same as a good video. Would this sit next to the viral
references without looking weaker? Be blunt; no padding.
```

## Verification prompt

```
You are an independent critic; you did NOT build this. Artifact: <new render>.
Previous report: <films/<slug>/critic/<video>/report-<N>.md>. Section timings may have moved by
about <x>s. Read films/<slug>/critic/<video>/packet.md and open every image it lists.

For every P0 and P1 in the previous report give FIXED / PARTLY / STILL PRESENT with a
timestamp. Then list any NEW defects: glitch frames, overlaps, clipped text, awkward
transitional frames, audio regressions.

Write the report (under 500 words) to films/<slug>/critic/<video>/report-<N+1>.md, ending with
SHIP or ONE MORE PASS (at most 3 fixes).
```

## Storyboard critic (optional, for high-stakes films)

```
Review films/<slug>/STORYBOARD.md for a <length>s <mode> for <audience>. You did not write
it. Check: does the chronology match how the real thing works; is every claim in KIT.md;
does each scene have a distinct composition and a job; which scenes are filler; is the
takeaway unmistakable on mute; does any narration line read as a Claudism (staccato
fragments, stat dump, "it isn't X, it's Y")? Return a ranked list of problems with one
concrete fix each.
```

## Quality bar (ship only when all hold)

| Check | Target |
|---|---|
| Duration | each scene within 0.1s of cues; film inside the mode length and destination cap |
| Loudness | integrated -16 LUFS, true peak <= -1.5 dBFS (reels may master at -14) |
| Contrast | WCAG AA on settled text |
| Determinism | same frame rendered twice gives identical pixels |
| Frame 0 | finished composition |
| Facts | every on-screen number traces to a dated KIT.md row |
| Audio | transcript of the render matches the narration, beat by beat |
