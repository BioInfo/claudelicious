# grill-me — how to use it

A skill that interrogates you about a plan or design one question at a time, recommends an answer for each, and walks the decision tree branch by branch until every open decision is settled. It runs before a plan solidifies. The output is a short Resolved-decisions summary you can drop straight into a plan or an implementation.

Built because the expensive failure mode for fast builders is committing to an under-specified plan and discovering the branch you skipped three files into the work. Plan mode explores and proposes. A premortem imagines failure after you have roughly decided. Neither forces you to resolve the open decisions, in order, before you start. This does.

## Credit

Adapted from **Matt Pocock's** [`grill-me`](https://github.com/mattpocock/skills) skill. The interrogation pattern is his. This version adds a model pin, user-invoked-only loading, a stop condition, and the Resolved-decisions closing artifact.

## Install

```bash
git clone https://github.com/BioInfo/claudelicious.git
cp -r claudelicious/skills/grill-me ~/.claude/skills/
```

The skill is **user-invoked only** (`disable-model-invocation: true`) — it will not auto-fire. You trigger it on purpose.

## How a run goes

You say one of:
- `/grill-me`
- `Grill me on this migration plan.`
- `Stress-test this design before I start.`

Then it:

1. Asks **one question at a time** and waits for your answer before the next. No question dumps.
2. Gives its **recommended answer** to every question with a one-line reason, so you are reacting to a position, not staring at a blank.
3. **Reads the code instead of asking** when the answer is discoverable there. It does not make you look up what it can look up itself.
4. Walks the decision tree branch by branch, resolving dependencies in order, so each settled decision constrains the ones downstream.

It stops when every branch is resolved and you both share the same picture of the plan. Then it emits:

- **Resolved decisions** — one bullet per settled choice (the answer, not the deliberation).
- **Open / deferred** — anything you punted, so it does not get silently lost.

## When to use it

- Before a non-trivial migration, refactor, schema change, or new service.
- When you have a vague intent and need it sharpened into decisions before plan mode or implementation.
- When you want to be argued with, not agreed with.

## When not to use it

- Small, reversible edits — the ceremony is not worth it.
- After you have already decided and want failure modes surfaced — that is a premortem, not a grilling.
- Pure exploration where you do not yet have a plan to interrogate.

## Design notes

- Pinned to a high-capability model and runs in the main session, because it is a live back-and-forth, not a one-shot generation. It is not delegated to a subagent — a subagent cannot hold the conversation.
- Kept deliberately short. It is a behavioral prompt, not a multi-phase procedure. The value is the discipline (one question, recommend an answer, read the code, resolve the tree), not the word count.
