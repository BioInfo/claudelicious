---
name: grill-me
description: "Interrogate the user about a plan or design one question at a time, walking the decision tree branch by branch and recommending an answer for each, until every decision is resolved and understanding is shared. User-invoked only via explicit phrases like 'grill me', 'interrogate this plan', 'stress-test this design', or '/grill-me'. Never auto-fires. Distinct from plan mode (explores and proposes) and a premortem (runs after a rough decision); grill-me runs before a plan solidifies, to extract and resolve the open decisions."
disable-model-invocation: true
model: opus
---

# grill-me

Interview the user relentlessly about a plan or design until every branch of the decision tree is resolved and understanding is shared.

Runs BEFORE a plan solidifies: extract the open decisions, resolve them. This is not plan mode (which explores and proposes without forcing per-decision resolution) and not a premortem (which runs after a rough decision: "imagine it failed, why"). Grill first, then plan or implement.

## Trigger

User-explicit only: "grill me", "interrogate this plan", "stress-test this design", "/grill-me". Never auto-invoke. The `disable-model-invocation: true` in the frontmatter is what enforces "never auto-fires": the skill is invocable by the user but the model cannot reach for it on its own.

## Mechanics

- Ask **one question at a time**. Wait for the answer before the next.
- For **every** question, give your recommended answer with a one-line reason.
- If a question is answerable from the codebase, **go read the codebase** instead of asking.
- Walk the decision tree branch by branch. Resolve dependencies between decisions in order, so a settled decision constrains the ones downstream of it.

## Stop condition

Stop when every branch is resolved and you and the user share the same picture of the plan.

## Closing artifact

When done, emit a short **Resolved decisions** summary:

- One bullet per settled decision (the answer, not the deliberation)
- A short **Open / deferred** list for anything punted

Keep it a bullet list, not a template. It should drop straight into a plan or implementation.

## Why this is a good example

It is tiny, it is dispatch-disabled so it never fires by accident, and it does one thing the model is bad at on its own: forcing a decision tree to resolve before code is written, one question at a time, instead of dumping a wall of questions or quietly assuming defaults. The whole skill is the discipline.

## Credit

Adapted from **Matt Pocock's** `grill-me` skill (github.com/mattpocock/skills). The interrogation pattern is his; this version adds a stop condition and the Resolved-decisions artifact.
