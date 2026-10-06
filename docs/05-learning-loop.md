# 05 — The learning loop

[Memory](04-memory.md) keeps a session from repeating yesterday's mistake. It does not fix the thing that caused the mistake. A sticky note that says "do not do X" sits there forever; the skill or rule that produced X is never touched. Pile up enough sticky notes and the harness looks like it is learning while the underlying behavior never changes.

The learning loop closes that gap. Every correction fires two systems in parallel, and the second one is the difference between accumulating notes and actually improving.

| | Memory | The learning loop |
|---|--------|-------------------|
| Writes | a durable note | a work order |
| Says | don't repeat this | here is the exact file to edit so it cannot recur |
| Metaphor | the sticky note | the fix |

Memory is fast capture. The loop names a **promotion target**, the specific skill, rule, or agent file to change, so the correction lands at the source. Without the work order, the notes pile up and the source never moves.

---

## The entry

A learning is one structured entry. The fields that do the work are the cause and the promotion target:

```
## [LRN-YYYYMMDD-NNN] <type> | <one-line rule>
Status: pending | promoted | resolved
Cause:  skill-body | skill-trigger | skill-permission | environment
Summary: what happened and the durable rule
Promotion target: <exact file + what to change>   (or DONE: <the edit made>)
Related: <source memory file>
```

---

## Attribution: name the cause before you touch anything

Most loops get this wrong by editing the first plausible file. The fix is to classify every failure into exactly one root cause, because the cause names the file *and the field*.

| Cause | What happened | The fix lands in |
|-------|---------------|------------------|
| `skill-body` | right skill fired, its instructions were wrong or stale | the SKILL.md **body** |
| `skill-trigger` | wrong skill fired, or the right one stayed silent | the `description:` **triggers**, not the body |
| `skill-permission` | wrong tool access, too broad or missing | the `allowed-tools` / `model` **frontmatter** |
| `environment` | skill and trigger were fine, the failure was external | **nowhere in the skill.** Log it, fix the environment. |

That last row is the one that quietly corrupts a system. An API outage or a missing dependency, logged as a skill bug, makes a later pass "fix" a skill that was never broken. When the failure is external, the discipline is to stop, write it to an errors log, and leave every skill alone.

---

## Three guardrails so the loop does not rot

A loop that edits its own skills over many corrections needs brakes, or it erodes the very files it maintains.

**A rejected-edit buffer.** When you veto a proposed change ("no, leave that"), log the veto. Before promoting any future edit, the loop checks the buffer first and does not re-propose a dead end. Without this, corrections re-litigate decisions you already made.

**Protected blocks.** Fence the load-bearing invariants so the loop can never auto-edit them:

```
<!-- protected:start reason="dispatch-only contract" -->
...content the loop may not touch...
<!-- protected:end -->
```

A NEVER rule, a model pin, a safety contract: fenced, invisible in rendered markdown, greppable, and off-limits to automatic edits. They change only when you say so.

**Delta edits, not rewrites.** When a correction promotes, change the one wrong line or append the one bullet. Do not regenerate the section to "incorporate" it. Letting a model rewrite a doc each iteration drives it toward shorter, blander, lossier versions as detail gets summarized away. Patch; never regenerate. A promotion that would rewrite more than its own few lines is a signal to stop and review, not to auto-apply.

---

## Promotion order

When the fix is mechanical and the cause is clear, promote in the same session. In priority:

1. the SKILL.md whose triggers or body produced the behavior
2. the agent's identity or scope file
3. a cross-cutting rule file
4. the top-level config, only as a last resort

And resolve the old note. When this session's work resolves a claim asserted in a memory file, rewrite that file to "resolved" and update its index line in the same pass. Stale "pending" language is what makes a future session re-do finished work.

---

## Where it connects

This is the loop that makes [skills](02-skills.md) a refined set instead of a growing pile. It is why the answer to "the agent did X wrong" is usually an edit to one existing file, not a new skill. And every artifact it produces, the note, the learning, the edited skill, lands in the [vault](08-second-brain.md) as plain markdown, where it gets embedded and becomes searchable. The next session starts already knowing what this one learned.

---

## Ship / scrub

- The dual-loop design, the attribution table, the three guardrails, and the promotion order are generic and are the most valuable part of this repo to copy. Ship them.
- The learnings log itself is personal (it names your skills, your failures, your systems). Ship the schema and the templates in [`templates/learnings/`](../templates/learnings/), not your log.
