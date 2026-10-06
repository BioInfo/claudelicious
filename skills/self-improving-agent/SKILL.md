---
name: self-improving-agent
description: "Logs corrections, errors, bugs, feature requests, and learnings into a learnings log, then queues a promotion target (a skill's SKILL.md, an agent's SOUL/SCOPE, a rules file) so a future session applies the fix at the source. Invoke when the user (1) corrects behavior or output ('no', 'wrong', 'actually', 'don't do that', 'next time'), (2) reports a bug or unexpected output, (3) requests a capability that does not exist yet, (4) flags an outdated assumption, (5) confirms a non-obvious approach worked, or (6) asks to promote a learning. Runs in PARALLEL with the memory system: memory writes the next-session sticky note, this skill writes the structured entry that edits the broken skill/agent/rule. Both fire on the same trigger."
disable-model-invocation: true
model: opus
---

# Self-improving agent

Logs structured learnings, errors, and feature requests to markdown so the broken skill, agent, or rule can later be fixed at the source. This is the work-order half of the [learning loop](../../docs/05-learning-loop.md); the [memory](../../docs/04-memory.md) system is the sticky-note half. Both fire on the same trigger.

## Why this exists alongside memory

The memory system captures a correction as a note the harness reads next session. That stops the same mistake recurring **for a session or two**, but the skill, agent, or rule that produced the mistake stays broken, so the same correction is needed again until someone edits the source.

This skill closes that loop. Same trigger, different output:

| | Memory | self-improving-agent |
|---|---|---|
| Output | a per-fact memory file | a learnings-log entry + a promotion target |
| Lifetime | loaded every session | a resolve / promote / wont-fix lifecycle |
| Action | inform the next session | edit the broken skill / agent / rule |

Memory is fast capture. This skill produces the structured entry with a named **promotion target**, the exact file that needs to change, so the next maintenance pass can do the real fix.

## Procedure (when invoked)

1. **Detect the signal.** Correction → the learnings log. Error or bug → an errors log. Feature request → a feature log. Vetoed edit (you proposed a change, the user rejected it) → a rejected log.
2. **Decide scope.** Cross-project (voice, tools, conventions, infra) → the global learnings dir. Project-specific → the project's own `.learnings/`.
3. **Attribute the cause** (the step that makes the loop work). Classify the failure into exactly one root cause before naming a target:
4. **Pick the promotion target from the cause** (not from a guess).
5. **Append the entry** in the format below, including the source (which conversation, which memory file).
6. **Check the guardrails before promoting.** Grep the rejected log for the target and topic; a prior veto means stop and surface it, do not re-propose. If the fix would land inside a `<!-- protected:start -->` fence, do not write it; surface and ask.
7. **Optionally promote now.** If the fix is mechanical (a wording change, a missed config line, a banned phrase), passed both guardrails, and you have the file open, make the edit and mark the entry `promoted`.
8. **Confirm in one line:** "Logged to the learnings log, promotion target = X. [Promoted / Pending review.]"

## Attribution taxonomy

The loop's weak point is guessing the promotion target. Attribution makes the cause pick the fix location. Classify into exactly one:

| Cause | What it means | Fix lands in |
|---|---|---|
| `skill-body` | The right skill fired, but its instructions are wrong, stale, or incomplete. | the skill's SKILL.md **body** (mechanical → promote now) |
| `skill-trigger` | The wrong skill fired, or the right one did not. A routing miss. | the skill's **`description:` frontmatter** (trigger phrases), not the body |
| `skill-permission` | The skill ran with the wrong tool access (too broad, or missing a tool). | the skill's **`allowed-tools` / `model:` / `agent:`** frontmatter |
| `environment` | Skill and trigger were both correct; the failure was external (API down, missing dep, stale state). | **no skill edit.** Log to the errors log, fix the environment. |

The `environment` row is the one the loop gets most wrong: it logs an external failure as a skill learning, and a later pass "fixes" a skill that was never broken. Naming `environment` as a terminal cause stops that.

**Validation gate (for `skill-body` and `skill-trigger`).** Before marking `promoted`, generate a one-line executable check from the skill's own `description:` and confirm the fix passes it after and failed or was absent before. That is the held-out gate the loop otherwise lacks, scoped to a single hand-written assertion.

## Promotion targets

A learning can have more than one.

- Global learnings → the global rules file or a topic rules file (`rules/<topic>.md`).
- Project learnings → the project's own context file.
- Skill or agent fixes → that skill's `SKILL.md`, or that agent's `SOUL.md` / `SCOPE.md` / `HEARTBEAT.md`.
- If the learning concerns a documented system, also edit that system's doc page and bump its `last_compiled:` date in the same pass. Otherwise the docs rot while the skills stay current, and the loop dies at the documentation layer.

## Logging format

Append to the learnings log:

```markdown
## [LRN-YYYYMMDD-XXX] category
**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Cause**: skill-body | skill-trigger | skill-permission | environment | n/a

### Summary
One line: what was learned.

### Details
What happened, what was wrong, what is correct.

### Suggested Action
The specific fix, and the promotion target it lands in.

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file
- See Also: LRN-YYYYMMDD-001 (if related)
---
```

Errors, feature requests, and vetoes follow the same shape with `ERR-` / `FEAT-` / `REJ-` ids. The rejected log is the negative-feedback buffer: when the user vetoes an edit, record the dead end so no future session re-proposes it. See `examples.md` for worked entries.

## Detection triggers

- **Corrections** ("no, that's not right", "actually it should be", "that's outdated") → a learning.
- **Feature requests** ("can you also", "I wish you could", "is there a way to") → a feature entry.
- **Knowledge gaps** (the user provides information you did not have; docs you referenced are stale) → a learning.
- **Errors** (non-zero exit, a stack trace, unexpected output) → an error entry.
- **Vetoes** ("no, leave that", "we decided against that", "we already tried that") → a rejected-edit entry.

## Resolving entries

When an issue is fixed, change `Status: pending` to `resolved` and append a resolution block (date, commit or PR, a one-line note). Never delete an entry; the audit trail is the point. Other statuses: `in_progress`, `wont_fix` (with a reason), `promoted`.

## Why this is a good example

It is the engine that makes the whole harness compound. Without it, corrections pile up as sticky notes and the underlying skill stays broken. The non-obvious parts, attributing the cause before picking the fix, treating `environment` as terminal, and buffering vetoes so dead ends do not get re-proposed, are what keep the loop from rotting as it runs.
