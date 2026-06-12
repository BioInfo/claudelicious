# Philosophy

Three ideas hold the whole system together. If you take nothing else from this repo, take these. Everything in `docs/` is an application of one of them.

---

## 1. A system, not a chat box

There is a ladder of how people work with these models:

```
Chatbot  →  Copilot  →  Agent  →  Harness  →  Dark Factory
```

Level 2, Copilot, is where most people stop, and it is the most dangerous level. You feel transformed. What you actually adopted was a faster keyboard. That is better tooling, not a different way of working, and it is easy to mistake one for the other.

This cookbook is about levels 3 through 5: the model inside a harness that knows you, that holds your context, that runs without you in the room. The shift it describes is the one where AI stops being something you open and starts being something you wear.

Move one level from where you are. Not five.

---

## 2. The attention budget

Every standing instruction you put in front of the model costs attention on every single turn, whether or not that turn needs it. Context is finite. A rule that helps one task in fifty is paid for by the other forty-nine.

So the architecture is **progressive disclosure**:

- The always-loaded file at the top stays short.
- Detail lives one layer down, in `rules/*.md`, in a skill's reference files, in a doc the agent reads only when the task calls for it.
- You prune by relevance-per-turn and by conflict, not toward a line count.

The top-level config file is a contract, not a dumping ground. The moment it tries to hold everything, it holds nothing, because the signal drowns.

---

## 3. More is not better

Compounding does not mean accumulating. It means keeping the ones that work and ruthlessly cutting the ones that do not.

A skill library is a set of business processes, encoded. Nobody runs a healthy organization by only ever adding processes and never retiring one. The same discipline applies here: a library of 134 skills is not stronger than a library of 48 if half of them never fire, overlap, or contradict each other. The reduction is the point. A smaller, sharper set is faster to reason over, cheaper to maintain, and easier to trust.

This is why [skills](docs/02-skills.md) are the centerpiece of the cookbook, and why the [learning loop](docs/05-learning-loop.md) is built to refine existing skills at the source rather than spawn new ones.

---

## The loop underneath all of it

These three ideas connect through one flywheel. It is the thing that makes the harness compound instead of just accumulate.

```
You correct the agent once
   │
   ├─►  memory writes a durable note          (the sticky note)
   ├─►  the learning loop writes a work order  (names the file to edit)
   │
   ▼
the broken skill / rule / agent gets edited at the source
   │
   ▼
all of it lands in the vault as plain markdown
   │
   ▼
the vault gets embedded and becomes semantically searchable
   │
   ▼
the next session starts already knowing what this one learned
```

Two supporting commitments make the loop trustworthy:

**Files are ground truth.** The vault is the canonical store: human-readable markdown, version-controlled, not locked to any model or any vendor. Embeddings are downstream of the files, never a replacement for them. You can read everything the harness knows with `cat`.

**Determinism where it matters.** A written rule loses to habit under load. The things that must happen every time, never delete recursively, inject the current date, scan for secrets before a push, get a hook, not a sentence. Prose persuades; hooks enforce.

---

The whole practice reduces to four words you can apply at GPU scale or at strategy scale:

**Change. Measure. Decide. Repeat.**
