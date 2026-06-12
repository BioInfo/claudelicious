# 01 — Rules and context

This is the layer that loads every session, before you type anything. It is the standing instruction set: who the agent is working with, how it should behave, what the house style is. Get it right and every session starts aligned. Get it wrong, specifically, make it too big, and you pay for it on every single turn.

The whole design of this layer is one tension: you want the agent to know a lot, and you cannot afford to tell it everything up front.

---

## The attention budget

Every standing instruction costs attention on every turn, whether the turn needs it or not. This is not a metaphor. A long context file does not just sit there harmlessly; it competes with the actual task for the model's focus, and a rule that helps one task in fifty is a tax on the other forty-nine.

So the top-of-stack file stays short. It is a contract and an index, not a knowledge base. The moment it tries to hold everything, the signal drowns and it effectively holds nothing.

The corollary: you prune by relevance-per-turn and by conflict, not toward a target line count. A rule earns its place in the always-loaded layer by being relevant most of the time. Everything else moves down a layer.

---

## The hierarchy

Context is layered, most general at the top, most specific at the bottom, each inheriting from the one above:

```
user-global     applies everywhere you work
   │            (who you are, how you write, your defaults)
   ▼
machine-local   per-host facts
   │            (this box's role, paths, what runs here)
   ▼
project         per-repo
                (this codebase's conventions, commands, gotchas)
```

The canonical filename at every layer is `AGENTS.md`, with `CLAUDE.md` as a symlink to it for tools that still look for the older name. One file, two names, no divergence.

A project file overrides a machine file overrides the global. The agent assembles the stack for wherever it is working, so a session in one repo gets that repo's conventions on top of your global defaults, automatically.

---

## Progressive disclosure

The short top file is made possible by pushing detail down into files that load only when relevant:

- **The global file** is a short hub: your identity in a few lines, your hard defaults, and an index of the rule files below it. Topics longer than a couple of lines do not live here; they live in their own file and get a one-line pointer.
- **Rule files** (`rules/*.md`) each own one topic: how you write, your security posture, your model-selection logic, your scraping strategy. They auto-load, but they are separate, so the global file stays an index instead of a wall.
- **Skills** push it further: a skill's body is short and its reference files load only when the task reaches that branch (see [02](02-skills.md)).

The principle repeats at every level of the harness: load the minimum, branch into detail on demand. The top file is the table of contents, not the book.

---

## What belongs where

A quick test for where a piece of guidance goes:

- True everywhere, every session, and short → the global file.
- A real topic with depth (voice, security, model routing) → its own rule file.
- True only on this machine (a path, a host role) → the machine file.
- True only in this repo (a build command, a convention) → the project file.
- A specific fact you learned once → [memory](04-memory.md), not a rule.

That last line matters. A rule is a standing behavior; a fact is a memory. Putting facts in the always-loaded rules is how that layer bloats. The rules say how to behave; memory holds what you know.

---

## Why short wins

The instinct is to write more rules, because each one seems to help. The discipline is the same as with [skills](02-skills.md): more is not better. A focused set of standing instructions that the agent actually follows beats an exhaustive one it cannot hold in focus. When a rule stops earning its turn-by-turn cost, move it down a layer or cut it.

---

## Ship / scrub

- The hierarchy, the `AGENTS.md`/`CLAUDE.md` convention, the progressive-disclosure pattern, and the what-belongs-where test are all generic. Ship them, with the template in [`templates/AGENTS.md.template`](../templates/).
- Your actual global file is personal (it holds your identity and defaults). Ship the structure and a sanitized skeleton, not your file.
- A few of your rule files are generic enough to share as examples (model selection, a security posture, a scraping strategy). Scrub the host-specific details first.
