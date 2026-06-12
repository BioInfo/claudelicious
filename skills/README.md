# skills/

Example skills you can read end to end. They are illustrations of the *pattern*, not a
library to install wholesale. The whole point of [doc 02](../docs/02-skills.md) is that more
skills is not better, so this folder stays a curated handful. Copy the shape, not the list.

## The three archetypes

One per archetype from [`docs/02-skills.md`](../docs/02-skills.md):

| Skill | Archetype | Shows |
|-------|-----------|-------|
| `commit/` | encodes a process you'd do by hand | a tight body, a mid-tier model pin, scoped `allowed-tools` |
| `post-update/` | a dispatch point for a tool you don't hand-drive | the **dispatch-only contract** inside a `protected:` fence, an agent pin |
| `research-sweep/` | collapses a recurring friction | **progressive disclosure**: a short body plus `references/` loaded only when the task branches there |

## The flagships

A few real skills, cleaned and scrubbed, to show how the patterns look at full size:

| Skill | What it demonstrates |
|-------|----------------------|
| `grill-me/` | The smallest useful skill. Dispatch-disabled so it never auto-fires, it forces a decision tree to resolve one question at a time before code is written. |
| `council/` | The [subagent fan-out](../docs/14-subagents-and-workflows.md) pattern at its cleanest: blind parallel seats that cannot see each other, a distilled dissent round, then a single synthesis in the main thread. Ships its own lens library. |
| `self-improving-agent/` | The work-order half of the [learning loop](../docs/05-learning-loop.md). It attributes a failure's root cause before picking the file to edit, treats `environment` as a terminal non-skill cause, and buffers vetoes so dead ends are not re-proposed. |
| `dream/` | Memory consolidation. The proof that memory is not write-only: a scheduled pass that prunes, merges, and resolves, with a hard rule against deleting confirmed knowledge. |
| `designing-frontend-uis/` | The [anti-slop](../docs/12-voice-and-antislop.md) discipline applied to UI: vague "be distinctive" advice replaced with a countable pre-flight gate the model cannot pass while shipping the default. |

## The frontmatter is where routing and safety live

Every `SKILL.md` pins a `model:` or `agent:` (mandatory: an unpinned skill runs on your most
expensive model every time), scopes `allowed-tools` to what it needs and no more, and
front-loads `description:` with the exact phrases that should and should not fire it. The
`description` is the trigger surface, not marketing copy. Several of these also set
`disable-model-invocation: true`, which makes a skill user-invocable but unreachable by the
model on its own. That is how you ship a sharp tool without it firing by accident.

## Adapt before you use

The model aliases and any CLI placeholders are examples. Substitute your own models, agents,
and commands. The flagships were scrubbed of real paths, hosts, and brand tokens before they
landed here. If you adapt one, keep that discipline and run a secret scan over `skills/`
before you share it onward.
