---
name: learn
description: >
  Takes any external artifact you link (a repo, a paper, a tool, a blog post, a
  thread) and decides what to lift from it into your own stack. Resolves the
  artifact, maps it against what you already have (your notes, skills, rules,
  memory), extracts only the genuine deltas, red-teams each delta against your
  real setup, and returns a per-delta decision: borrow, build, install, or skip.
  ALWAYS invoke when the user shares a link and asks "should we adopt this",
  "what do we take from this", "what do we lift from X", or "is this worth
  stealing". NOT a review of the artifact on its own merits (that is a different,
  grade-it-in-isolation skill); this one grades the artifact against YOUR systems
  and outputs a lift plan.
model: opus
allowed-tools: Read, Grep, WebSearch, WebFetch
disable-model-invocation: false
---

# learn

Turn an external artifact into an adoption decision. The output is not a summary
and not a grade. It is a short list of the things worth lifting into your own
stack, each with a decision attached. The judgment that makes this skill useful is
that it reads the artifact **against what you already run**, not in a vacuum, so
it never recommends something you already do under a different name.

## What this is NOT

- Not a review or a decode. Those grade an artifact on its own merits. This grades
  the artifact against your systems and outputs a lift plan.
- Not a full re-implementation. It decides *whether* and *how* to adopt; the
  building happens after the decide-gate says so.
- Not a summarizer. If it hands you a description of the artifact and stops, it
  did the wrong job. Every run ends in decisions.

## Procedure

1. **Resolve the artifact.** Fetch and read the link closely enough to know what
   it actually claims, not just its headline. A repo means the README plus the
   parts that carry the real idea; a paper means the method, not the abstract; a
   thread means the argument, not the first post.
2. **Map against what you already have.** Search your own stack for overlap: your
   notes, the skills folder, your rules, your memory. The goal of this step is to
   separate a genuinely new idea from one you already run. Skip it and you will
   recommend things you already do.
3. **Extract the deltas.** Keep only what the artifact does that you do not.
   Discard everything you already cover. A short list of real deltas beats a long
   list padded with things you already have.
4. **Red-team each delta against your real setup.** For every surviving delta,
   ask not "is this good in the abstract" but "does it survive contact with how I
   actually work, and what breaks if I adopt it." A delta that fails this step is
   a skip, and saying so is a result.
5. **Decide, per delta.** Attach one of four calls to each surviving delta:
   **borrow** the idea and adapt it, **build** your own version, **install** the
   thing directly, or **skip** it with the reason.

## The decide-gate

Close with a single gate rather than an open recommendation. For the deltas worth
acting on, offer three exits: **plan it further** (the change is real but needs a
design pass), **borrow it now** (small enough to lift in place), or **implement
it** (start building against the decision). The user picks the exit. The skill
does not silently start building.

## Notes

- Weight what red-teaming survives, not what sounds clever. A delta that reads
  well but breaks against your setup is the weakest kind of recommendation.
- Be willing to conclude "nothing to lift here." An artifact you already cover is
  a valid, useful answer, and it is faster than a padded lift plan.
- Keep the deltas honest to the source. If a capability is not actually in the
  artifact, it does not go in the plan.
