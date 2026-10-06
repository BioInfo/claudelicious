# 06 — Continuity

Two things end a working context whether you want them to or not. A session stops, and you come back tomorrow cold. Or the window fills and gets summarized mid-task, and the model loses the thread it was holding. A harness has to treat both as normal events and design for them, because they happen every day.

The pattern here is a session journal plus two hooks: one that hands off the last session's open items when a new one starts, and one that re-injects state when the window compacts. The result is that you almost never have to re-explain where you were.

---

## The session journal

Every session writes one markdown file. It starts as frontmatter only, created the moment the session begins:

```yaml
---
session_id: <host>-<YYYYMMDD-HHMMSS>-<uuid8>-<thread>
host: <host>
thread: <thread>
cwd: <project path>
started: <ISO timestamp>
status: active
---
```

The body gets filled at the end, by hand or by a wrap routine, in a fixed shape:

```markdown
## Done
- what shipped this session

## Now
- the state of the thing in flight

## Next
- the first move for whoever picks this up
```

That `## Next` block is the load-bearing part. It is the handoff.

When the session ends, the file moves from a `live/` folder to an `archive/` folder. Nothing is deleted; the journal is a permanent record, and (see [07](07-session-search-mneme.md)) a searchable one.

---

## Threads

A thread is a workstream, keyed by the git-root basename of where you are working. `project-a`, `project-b`, `claudelicious`. Outside a repo it falls back to the directory name; at home it is `general`.

The journal id combines host, timestamp, a short slice of the session UUID, and the thread:

```
<host>-<yyyymmdd>-<hhmmss>-<uuid8>-<thread>
```

That combination is collision-proof. Two sessions on the same machine, the same project, at the same time, on different machines syncing to the same folder, none of them collide and none of them write the same mutable file. So the journals are safe to sync across a fleet without a lock.

---

## The handoff (SessionStart hook)

When a new session starts, a `SessionStart` hook does four things:

1. mints the journal id and writes the frontmatter-only file to `live/`
2. sweeps stale `live/` journals to `archive/` (by transcript age plus a liveness check, so a crashed session does not leave a ghost)
3. finds the most recent finalized journal for this thread
4. extracts that journal's `## Next` section and injects it as context

So the new session opens already knowing the last one's open items, with zero effort from you. You sit down, and the harness says "here is where you left this."

---

## Surviving compaction (PostCompact hook)

When the context window fills, Claude Code summarizes it. Anything held only in the live conversation, current task state, decisions made an hour ago, can get flattened. A `PostCompact` hook re-injects what has to survive:

- the head of the project's `CONTINUITY.md`
- the head of the project `CLAUDE.md`
- the active journal's `## Next` / `## Now` section
- standing behavioral rules

It emits a "context restored" marker so the model knows it just happened. What survives a compaction is exactly what you wrote down; what you kept only in the conversation is what you lose. That is the argument for writing state to a file as you go, not holding it in your head or the window.

---

## The project ledger: CONTINUITY.md

Per project, a `CONTINUITY.md` holds the tactical state that has to outlive any single session:

```markdown
# CONTINUITY

Goal: <the one-line objective>
Phase: <where we are>

## Decisions
- <decision> — <why> — <date>

## Current focus
- <the thing in flight right now>
```

This is the project's short-term memory, distinct from the [durable memory store](04-memory.md), which is cross-project and permanent. The ledger answers "what is the state of this project," updated as you work. A small skill keeps it current on "continue."

---

## The principle

Compaction and session boundaries are not failures to work around. They are events to design for. Write state to files as you go, key it by thread, and let two hooks move it across the boundaries automatically. The payoff is the thing every workshop demo opens with: you sit down and get oriented in three sentences instead of ten minutes.

---

## Ship / scrub

- The journal schema, the thread-keying scheme, the handoff and post-compact hooks, and the `CONTINUITY.md` shape are all generic. Ship them, with the template in [`templates/CONTINUITY.md.template`](../templates/).
- The hooks reference a journals directory and a vault path. Genericize those to a single configurable variable before sharing.
- Your actual journals are a record of your work. Do not ship them.
