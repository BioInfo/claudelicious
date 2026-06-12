# 04 — Memory

A model has no memory between sessions. The harness gives it one, and the design choice that makes it work is almost boring: the memory is a folder of plain markdown files, one fact per file, with a one-line index. No database, no embedding required to read it, nothing you cannot open with `cat`.

Memory is the boring superpower. A harness that remembers what you decided last week outperforms a smarter one that starts cold every morning. This doc is the schema and the discipline that keeps it from rotting into noise.

---

## The shape

```
memory/
  MEMORY.md            # the index: one line per memory, loaded every session
  MEMORY-archive.md    # older index lines, moved here when MEMORY.md fills
  feedback_*.md        # corrections and lessons
  project_*.md         # current state of a piece of work
  reference_*.md       # stable facts about your tools and systems
  user_*.md            # your preferences and identity
```

Every file carries frontmatter:

```yaml
---
name: <kebab-case slug>
description: <one line that stands alone without the body>
metadata:
  type: feedback | project | reference | user
---
```

The `description` is the signal. It is what a future session reads first to decide whether the file is relevant, so it has to make sense on its own.

---

## Index, not content

`MEMORY.md` is loaded into context at the start of every session. That makes it expensive, so it holds index lines, never content:

```markdown
- [feedback_backup_heartbeat.md](feedback_backup_heartbeat.md) — gate the success
  heartbeat on the whole pipeline, not just the last step. See [[reference_backup]].
```

One line, a link, a hook. The detail lives in the file the line points to, loaded only when a session actually needs it. This is the [attention budget](../PHILOSOPHY.md) applied to memory: the always-loaded layer stays lean, detail loads on demand. When the index grows past its ceiling, old lines move to an archive file. They are never deleted, only moved.

---

## The type taxonomy drives the body

Four types, and the type tells you how to write the body.

| Type | Holds | Body |
|------|-------|------|
| `feedback` | a correction or lesson from a mistake | the rule, then **Why** (the failure that produced it), then **How to apply** (prescriptive steps) |
| `project` | the live state of a piece of work | freeform, organized by phase: what shipped, what is open, where to resume |
| `reference` | a stable fact about a tool or system | dense and factual, present tense, no Why/How needed |
| `user` | a preference or identity fact | a declarative statement |

The `feedback` convention is the one that earns its keep. A correction without a "why" is a sticky note that informs but does not guide. The "why" gives the next session the failure case, so it understands the rule instead of just obeying it. The "how to apply" makes it actionable without the original context.

```markdown
[The rule, in one present-tense paragraph.]

**Why:** [The concrete failure. Date, system, what broke, what the wrong move was.]

**How to apply:** [Numbered steps specific enough to act on cold.]
```

---

## One fact per file

Each file holds one durable lesson or one system's state. Two lessons from the same session become two files. This is not tidiness for its own sake. When a later session resolves or supersedes a claim, you want to retire that one file cleanly, rewrite it to "resolved," update its index line, and move on. A file that crammed three unrelated facts together cannot be retired without invalidating the two that are still true. Multi-fact files are how a memory store starts asserting stale state.

---

## Wikilinks make a graph

Files cross-reference with `[[basename]]` links, by basename so they survive folder moves. A feedback file links to the reference it corrects. An index line links to a sibling for context. Over time this turns a flat folder into a small knowledge graph, and the search layer can walk it: when a hub note surfaces in a search, the system can follow its links and surface the cluster around it (see [08](08-second-brain.md)).

---

## Curation is a real job

Without maintenance, the index bloats, the system truncates it, and your most recent (often most relevant) memories get cut. So curation is a first-class operation, not an afterthought. On a cadence, a pass trims the index: compress verbose lines, archive old ones, never delete content. A dedicated curator routine owns this. The reader-and-router over the whole durable store (the **continuum** pattern) is what lets a session ask "what do I know about X" across memory, learnings, and rules without grepping four folders by hand.

---

## Ship / scrub

- The schema, the taxonomy, the index-not-content rule, the wikilink and curation patterns are all generic. Ship them, with the templates in [`templates/memory/`](../templates/memory/).
- Your actual memories are personal. Do not ship the folder. Ship the schema and two or three sanitized example files so people see the shape.
- A `user_*` file by definition holds personal data. Never publish those.
