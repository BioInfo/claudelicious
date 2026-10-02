# STORYBOARD.md template

Copy into `films/<slug>/STORYBOARD.md` and fill it. This file is gate 1: the owner reads it
and edits any line he disagrees with. State every default inline so no question is needed.

```markdown
# <Working title> (<mode>)

## Brief
- **Audience:** <who watches, and what they already know>
- **Length:** <target, e.g. ~2:40> (mode range <90-180s>)
- **One takeaway:** <the single sentence a viewer should be able to repeat>
- **Sources:** <doc / paper / repo / URL, each with date read>; facts in KIT.md
- **Voice:** Kokoro af_heart (default) | --clone (the owner's cloned voice)
- **Music:** pad (default until beds are auditioned) | kit/music/<bed>.wav
- **Destination:** none yet (watch locally) | <platform, with its duration cap>
- **Format:** 1920x1080, 30fps (reel/loop: 60fps, 16:9 or 1:1)
- **Captions:** off (explainer default) | on, burned in (social cut)
- **Hero object:** <the one thing that persists and transforms across scenes>
- **Palette:** <ground> + <one accent>; accent means <what>

## Question (at most one, only on a genuine fork)
<The single question, or "None: defaults above stand.">

## Scenes

| id | label | narration (one line per cue) | asset | focus move | secs |
|---|---|---|---|---|---|
| s01-hook | <lower-right label> | 1. <spoken sentence> | <pattern / screenshot / recording> | <what the camera or spotlight goes to, on which cue> | <n> |
| s02-... | ... | 1. ...<br>2. ... | ... | ... | ... |

Rules for the table:
- Narration lines are plain spoken sentences, numbers written as spoken, no Claudisms.
- The screen never shows the narrated sentence; the asset column says what it shows instead.
- Every number that will appear on screen has a KIT.md row.
- Asset names a kit pattern (see the kit README), a real screenshot, or a click-through recording.
- Focus move names the cue it lands on ("zoom to the p99 bar on line 2").
- Secs are estimates; `<engine> voice` makes cues.json the truth.

## Three signature moments
1. **<time>** <the moment people remember, e.g. counter runs to the real figure while the diagram draws>
2. **<time>** <...>
3. **<time>** <...>

## Opening and ending
- **Frame 0:** <what is already moving; no logo, no title card>
- **Last frame:** <how it echoes the opening>

## Prototype scene (gate 2)
<scene id> because <it is the most representative: narration, focus move, label, HUD>.
```

## Mode defaults to state inline

| Mode | Length | Voice | Music | fps / aspect | Captions | Gate 2 |
|---|---|---|---|---|---|---|
| explainer | 90-180s | Kokoro af_heart | pad or bed | 30 / 16:9 | off | yes |
| paper | 120-300s | Kokoro af_heart | pad or bed | 30 / 16:9 | off | yes |
| demo | 30-120s | Kokoro af_heart | pad or bed | 30 / 16:9 | off | yes |
| reel | 15-25s | none | bed, beat-locked | 60 / 16:9 or 1:1 | none | skipped |
| loop | 8-15s | none | bed, seamless | 60 / 1:1 | none | skipped |

For reel and loop, replace the narration column with a beat column (bar and beat where
each state change lands).
