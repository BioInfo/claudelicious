# Model & Agent Selection (example rule file)

<!-- An example rules/*.md. It auto-loads alongside the global AGENTS.md and owns
     one topic so the global file stays a short index. Scrub to your own models,
     agents, and thresholds. See docs/01 and docs/02. -->

Pick the model by task type, and pass it explicitly. An unpinned skill or
subagent defaults to your most expensive model and leaks cost on every call.

## By task type

1. **Writing in your voice** (emails, posts, anything you'll send/publish) → top model. Non-negotiable.
2. **Research / synthesis / multi-source verification** → top model.
3. **Architectural judgment, hard tradeoffs** → top model.
4. **Code writing, analysis, multi-step reasoning** → mid model.
5. **Status / audit / fleet checks** (long output) → mid model minimum (cheap models cap output low).
6. **Log / file / diff summarization** → cheap model.
7. **Simple CLI dispatch, file discovery** → cheap model.

## Inline vs delegate

Don't reflexively fork. A large context window makes inline the right default
for reasoning-heavy work. Fork to a subagent when the work is **discovery or
scanning** — reading many files, grepping a codebase, dumping large logs — where
holding raw content in the main context is the worse trade. Hard fork triggers:

- reading more than ~5 files for exploration
- grepping a codebase for more than one pattern
- any "audit the codebase" / "find all X" task
- reading a large file when you only need a summary

## Output ceilings matter

Cheap models cap output low. If a task will produce long output (a system audit,
a large generation, a transcript), use a mid or top model even if the task type
would normally route cheap.

## Content on your behalf = top model

Anything that generates content you will send or post must be drafted by the top
model. A cheap model can orchestrate and dispatch (run the CLI), but the drafting
is the expensive, voice-sensitive part. Pattern: top model drafts → you approve →
the dispatch skill shells out the send command.
