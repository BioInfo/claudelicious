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

## 4. The judgment budget

The second half of this cookbook adds a fourth idea, and it is the first three read one level up.

When you run one harness, the scarce resource is the model's attention, and idea 2 is how you spend it. When you run several at once, unattended, the scarce resource becomes yours. Every question a lane escalates costs operator attention on the day it lands. A fleet that escalates everything has re-created the exact problem the attention budget solves, one floor higher: the signal drowns, and now it drowns in your inbox instead of the model's context.

So the answer is the same answer, aimed at the human this time. Progressive disclosure of the operator. The harness governs the model's attention with a short standing context and detail one layer down. The [charter](docs/20-the-autonomy-charter.md) governs your judgment with a written boundary: the lane decides what it can, surfaces only what it must, and loads you only when the moment calls for it. Attention is what you protect at level one. Judgment is what you protect at level five.

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

There is a second way into the same loop once lanes run on their own. When an autonomous lane escalates something its [charter](docs/20-the-autonomy-charter.md) should have handled, the fix is a charter edit at the source, the same move a corrected skill gets. Escalations feed the flywheel the way corrections do.

Two supporting commitments make the loop trustworthy:

**Files are ground truth.** The vault is the canonical store: human-readable markdown, version-controlled, not locked to any model or any vendor. Embeddings are downstream of the files, never a replacement for them. You can read everything the harness knows with `cat`.

**Determinism where it matters.** A written rule loses to habit under load. The things that must happen every time, never delete recursively, inject the current date, scan for secrets before a push, get a hook, not a sentence. Prose persuades; hooks enforce.

---

The whole practice reduces to four words you can apply at GPU scale or at strategy scale:

**Change. Measure. Decide. Repeat.**
