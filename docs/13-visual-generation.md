# 13 — Visual generation

A harness should make its own pictures. Logos, hero images, infographics, the diagrams in these docs: all generated from a text prompt by a skill, not hand-drawn and not pulled from stock. This page is both the how and a worked example, because the [logo](../assets/) and the visual assets in this repo were made exactly this way.

The skill here wraps a Gemini image model. The pattern generalizes to any image API.

---

## The skill, not a one-off script

The rule is: image generation goes through one skill, never a hand-rolled `curl` each time. The skill knows the things you would otherwise re-learn every time:

- **Which model.** Two tiers: a fast model for drafts and iteration, a high-quality model for anything published. Default to the quality model for finished work; drop to the fast one only when you are explicitly sketching.
- **How to route.** Through your gateway with a dedicated virtual key, so image spend is tracked like everything else, not billed to a raw provider key.
- **Where output lands.** A known assets directory, or the relevant project's image folder.

One skill, one place to fix when the model IDs change or the routing moves.

---

## Generate in the background

Image calls take ten to ninety seconds. Blocking the session on each one is wasteful, so the pattern is to fire the generation as a background job and keep working:

```bash
<image-cli> "PROMPT" -m <quality-model> -o /path/to/out.png &
```

This matters more than it sounds. When you are iterating on a logo (and you will iterate), backgrounding lets you generate a batch of variations in parallel, or write a doc while the pixels render, instead of staring at a spinner. This whole repo was built that way: docs written while logo concepts rendered.

---

## Prompt discipline

Two rules save the most rework.

**The anti-chrome rule.** When the image will be wrapped by a page that supplies its own headline (a blog hero with an overlaid title, a doc with its own `H1`, a card with a caption), do not bake a title, header band, or footer into the image. You get duplicated text and a cramped composition. Strip the framing; generate the visual, let the page provide the words. Keep text that belongs in the world of the image (a sign, a label on a device in the scene); strip text that is really UI.

**Say what to avoid, in the negative.** Image models drift toward clichés: glowing orbs for anything AI, neon gradients, 3D renders, generic robots. Naming the avoids in the prompt ("flat vector, no glow, no 3D, no photorealism") does more than describing the thing you want. The logo prompts in this repo's history are mostly a list of what not to do.

---

## What it is good for

- Logos and brand marks (iterate in batches, pick, refine)
- Blog and social hero images
- Infographics and schematic diagrams for docs
- Slide decks with consistent branding

What it is not for: editing or cropping an existing image (that is ImageMagick, as the square and transparent cuts of this repo's logo were made), code-driven charts (that is a plotting library), or screenshots.

---

## The meta-point

The cookbook documents a harness that generates its own visuals, and it used that exact capability to make its own logo and figures. That is the tell of a real system rather than a demo: the tools are good enough that you reach for them on the actual work in front of you, including the work of building the system itself.

---

## Ship / scrub

- The pattern (one skill, two model tiers, gateway routing, background generation, the anti-chrome and negative-prompt rules) is generic. Ship it.
- Scrub the gateway host and the virtual-key path. The model IDs are public, but treat the routing as personal.
- The output directories are yours; genericize them.
