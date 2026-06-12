# 02 — Skills as a centerpiece

A skill is a repeatable procedure the harness invokes by name. Said plainly: a skill is a business process, encoded. And like any business process, the win is not in having more of them. It is in having the right ones, kept sharp.

This is the doc most "here is my setup" repos get backwards. They treat the skill list as a trophy case: look how many I have. A large skill library is not a strong one. A library of 134 skills where half never fire, three pairs overlap, and two contradict each other is slower to reason over and harder to trust than a library of 48 that all earn their place.

The reduction from 134 to 48 was not cleanup. It was the work.

---

## More is not better

Run the comparison you would run on any process inventory:

- **Does it fire?** If a skill has not been invoked in months, it is dead weight in the description space the model has to match against on every routing decision.
- **Does it overlap?** Two skills that do almost the same thing make the model guess. Merge them.
- **Does it contradict?** A skill whose instructions fight a rule or another skill produces nondeterministic behavior. Resolve it.
- **Does it earn its triggers?** A skill that fires when it should not is worse than no skill, because it derails good work.

The discipline is the same one a healthy org applies to its processes: **prune, consolidate, extend, retire.** Adding is the easy half. The half that compounds is subtraction.

---

## Dissect your most-used skills

Before you build another skill, look at the ones you actually reach for. The pattern in the winners is consistent. Your highest-use skills almost always do one of three things:

1. **They collapse a recurring friction.** A morning-orientation skill that gives you "done, now, next" in three sentences replaces ten minutes of re-reading. The value is the friction removed, measured in the gap between curiosity and action.
2. **They encode a process you would otherwise do by hand every time.** A commit skill, a triage skill, a research-sweep skill. The procedure was always the same; the skill makes it one word.
3. **They are dispatch points for a tool you do not want to hand-drive.** A skill that drafts in your voice, gets your approval, then shells out the send command. The judgment stays with you and the model; the mechanics get automated.

If a skill does none of these, it is a candidate for the cut list. The skills you build next should aim squarely at one of the three.

---

## Anatomy of a skill

A skill is a `SKILL.md` file with YAML frontmatter and a body. The frontmatter is where the routing and safety live.

```yaml
---
name: commit
description: >
  Create well-formatted commits with conventional-commit format. ALWAYS invoke
  when the user says "commit", "commit this", "make a commit", or asks to save
  work to git. NOT for pushing or for staging review.
model: sonnet            # or: agent: <subagent>   (one of these is mandatory)
allowed-tools: Bash, Read, Grep
disable-model-invocation: false
---

# Commit

[The body: the procedure, in the order it should run.
 Reference files for detail the model loads only when needed.]
```

Four things matter in that block:

- **`description` is the trigger surface.** This is what the model matches a user request against. It is not marketing copy. Front-load the verbs and exact phrases that should fire it, and name what should *not* fire it. A vague description is the number-one cause of the wrong skill firing or the right one staying silent.
- **`model` or `agent` is mandatory.** An unpinned skill silently runs on your most expensive model every time. Pin judgment and voice work to your strongest model, code to a mid model, dispatch and summarization to a fast one. (See model pinning below.)
- **`allowed-tools` is the permission surface.** Give a skill the tools it needs and no more. A dispatch skill that only sends does not need write access to your whole filesystem.
- **`disable-model-invocation`** marks a skill as user-invoked only (`/skill-name`), which you want for anything destructive or expensive that should never auto-fire.

### Progressive disclosure inside a skill

A skill body should be short. Detail goes in reference files the model reads only when the task reaches that branch:

```
skills/research-sweep/
  SKILL.md              # the routing + the spine of the procedure
  references/
    sources.md          # the per-source query patterns
    synthesis.md        # the two-pass synthesis spec
```

The same attention-budget logic that governs the top-level config governs the inside of a skill. Load the minimum; branch into detail on demand.

### The dispatch-only contract

For any skill that posts, sends, or publishes on your behalf, the content must be drafted in the main session, shown to you, and approved *before* the skill runs. The skill is the hands, not the author. Encode this as a contract at the top of the skill body so it cannot be invoked with raw "post a tweet about X" instructions. The judgment stays where it belongs.

---

## Model pinning

| Task type | Pin to |
|-----------|--------|
| Voice, drafting, anything you will send or publish | your strongest model |
| Research, synthesis, multi-source verification | your strongest model |
| Architectural judgment, hard tradeoffs | your strongest model |
| Code writing and multi-step reasoning | a mid model |
| Status, audit, long-output dispatch | a mid model (small models truncate) |
| Log and file summarization, simple CLI dispatch | a fast model |

The rule of thumb: anything that produces content you put your name on is drafted by your best model. Fast models orchestrate and dispatch; they do not author.

---

## Keeping the library refined

A skill is not done when it ships. It drifts: the API it wraps changes, the trigger turns out too broad, a correction reveals a gap. The cookbook treats skill maintenance as a first-class loop with four tools, each doing a different job.

**Mechanical linting.** A `lint-skill` pass checks the structural invariants: is the frontmatter valid, is a model or agent pinned, are protected blocks balanced, does the description actually contain trigger phrases. This is the cheap, always-run gate.

**The learning loop.** When you correct the agent, the [learning loop](05-learning-loop.md) attributes the failure to a root cause and edits the skill *at the source*. The attribution is what makes the fix land in the right place:

| If the failure was... | The fix lands in... |
|-----------------------|---------------------|
| right skill fired, instructions wrong | the SKILL.md **body** |
| wrong skill fired, or right one stayed silent | the `description:` **triggers** |
| wrong tool access | the `allowed-tools` / `model` **frontmatter** |
| external (API down, missing dep) | nowhere in the skill. Log it; fix the environment. |

That last row is the one most loops get wrong. An external failure logged as a skill bug makes a later pass "fix" a skill that was never broken.

**Guarded optimization.** Over many corrections, a skill body accumulates edits. Two guardrails keep it from rotting:

- **Protected blocks.** Load-bearing invariants (a dispatch-only contract, a NEVER rule, a model pin) get fenced so the loop cannot erode them:

  ```
  <!-- protected:start reason="dispatch-only contract" -->
  ...content the loop may never auto-edit...
  <!-- protected:end -->
  ```

- **A rejected-edit buffer.** When you veto a proposed change, it gets logged so no future session re-proposes the same dead end. Before promoting any edit, the loop checks the buffer first.

And one anti-pattern to enforce: **delta edits, not section rewrites.** When a correction lands, change the one line or append the one bullet. Do not regenerate the whole section to "incorporate" it. Letting a model rewrite a doc each iteration drives it toward shorter, blander, lossier versions. Patch; do not regenerate.

**Periodic consolidation.** On a cadence (weekly works), a consolidation pass reviews the library as a whole, not one skill at a time: what overlaps, what has gone stale, what two skills should become one, what should be retired. This is the subtraction work that the per-correction loop cannot see, because it only ever looks at one skill. It is the difference between a library that compounds and one that just grows.

---

## Ship / scrub

- The anatomy, the dispatch-only contract, the model-pinning table, and the four-tool maintenance loop are all generic. Ship as-is.
- The specific skill names in your library are personal. Share the *pattern* of a skill, and a few genuinely generic example skills (see [`skills/`](../skills/)), not your whole list.
- If a skill body references a private path, host, or system, genericize it before sharing the skill file.
