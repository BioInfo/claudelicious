# 14 — Subagents and workflows

A single conversation has one context window, and that window is the scarcest thing in the harness.
Fill it with raw file dumps, log output, and exploratory dead ends, and the model gets worse at the
actual task. Subagents exist to keep the main thread clean: hand the messy or parallel work to a
forked worker, and let it return only the conclusion. This doc is about when to fork, what model the
fork should run, and the newer pattern where the harness writes its own orchestration.

---

## Fork or stay inline

The first decision is whether to delegate at all. With a large context window the reflex to delegate
everything is wrong, because a fork has a real cost: it cannot see the conversation so far, and you
pay latency spinning it up. The rule is about what kind of work it is, not how big.

**Stay inline** when the work needs the conversation you already have: voice-sensitive drafting,
multi-step reasoning where you refine each step, anything where the context already loaded is the
point. Reasoning work stays where the reasoning context lives.

**Fork** when the work would pollute the main context more than it would benefit from it:

- Scanning many files for discovery, where holding the raw contents in the main thread is the worse trade.
- Grepping a codebase for several patterns at once.
- Reading a large PDF or a log dump you need summarized, not retained.
- Genuinely parallel, independent subtasks.

A useful set of hard thresholds: reading more than a handful of files for exploration, grepping across
a codebase for more than one pattern, or any "find all X" / "audit the codebase" task. When one of
those trips, fork instead of inlining. The forked worker burns its own context on the mess and hands
you back a paragraph.

---

## Pick the model for the job

A subagent should not default to the most expensive model, and it should not default to the cheapest
either. Match the model to the task:

| Task | Model tier |
|------|-----------|
| Writing in your voice, research synthesis, hard tradeoffs | the strongest |
| Code, analysis, multi-step reasoning, long status output | the middle |
| Log and file summarization, simple dispatch, file discovery | the fast one |

Two traps worth naming. First, a fast model usually has a low output ceiling, so any task that
produces long output (a fleet audit, a big code generation, a transcript) needs a middle or strong
model even if the work itself is simple. Match the model to the *output size*, not just the
difficulty. Second, content you will send or publish on your own behalf, an email, a post, a draft,
is drafted by the strong model in the main context, then dispatched. A cheap worker can run the send
command. It does not write the words.

---

## Two ways a subagent dies

Both are common enough to name, and you will hit them in the first week of forking real work.

First, every forked worker has a hard ceiling on how much it can produce in one response, and the
ceiling is lower than you expect. The worse part is that the model's own reasoning counts against that
same ceiling. A worker set to think hard on a hard task can spend the whole budget thinking and die
before it writes a word. The worker is not broken. It thought itself out of room. The fix is to bound
what you ask for: chunk a large write into smaller pieces, and do not run a producing worker at maximum
reasoning effort when the job is mechanical.

Second, do not ask a worker to hand a large file back inside its reply. A fork told to paste a rewritten
file into its response hits that same ceiling and returns having applied nothing. Tell it to edit the
file in place and reply with a short summary and a command you can run to check the result. The big
content stays on disk where it belongs, and you get back a paragraph, which is the reason you forked.

The ceiling itself is a fixed number: 8,000 output tokens per response, and it holds for every subagent
regardless of which model runs it or what type of worker it is. The main session loop is not subject to it
at all, only the forked workers are. This was measured directly, across roughly 640,000 responses, and it
is consistent enough that it has been filed upstream as a harness issue (anthropics/claude-code#78460).
Knowing the exact number turns "the worker died" from a mystery into arithmetic: add up what you asked it to
produce plus what a hard reasoning effort will spend thinking, and see if it fits.

---

## The archived folder that still loads

An underscore prefix does not mean "ignored." If you retire a subagent by renaming its folder to something
like `_archived-agent-name` but leave it inside the same directory the harness scans for agents, it still
loads. The tool only skips a directory that sits outside the folder it treats as the agent config tree, not
one that merely looks archived by name. One self-audit found 21 dead agents loading into every session,
sitting alongside the live ones, because they had been "retired" this way for months. Retire an agent by
moving its file out of the config tree entirely, not by renaming it in place. A naming convention is not an
exclusion rule.

---

## The dispatch-only contract

A specific, reusable pattern: a skill that posts or sends something (to chat, social, email) forks to
a cheap worker, but the worker is forbidden from composing the content. The main thread drafts in your
voice, you approve it, and only then is the approved text handed to the dispatcher. The skill's own
body carries a short contract that says exactly this, so a future session cannot shortcut it by asking
the dispatcher to "write a post about X." Drafting discipline survives because the contract is in the
skill, not in your memory.

---

## When the harness writes the workflow

The newest layer up is orchestration the model designs itself. Instead of you forking workers by hand,
the harness can write a script that fans out parallel subagents, runs them, and then runs adversarial
verifiers over their findings before returning a synthesized answer. This is the right shape for work
that is genuinely wide: auditing a whole codebase, migrating a framework across many files, or
generating several independent attempts and judging between them.

It is powerful and it is expensive, in two distinct ways that you have to hold together.

**Cost.** A fan-out can spawn many workers and burn quota fast. The sane default is off. Turn it on
per session for real fan-out work, and leave it off for everyday editing, where one careful pass beats
fifty parallel guesses.

**Permission surface.** This is the part people miss. Workers inside an auto-written workflow run with
file edits auto-approved and inherit your tool allowlist, regardless of the session's permission mode.
So enabling the fan-out is a permission decision as much as a budget one. Treat "let the harness
orchestrate itself" with the same care you treat any broad grant: know what the workers can reach
before you let them run.

The honest irony worth admitting: a cookbook like this one was itself assembled by fanning out a set
of discovery agents across the whole install in parallel, each summarizing one subsystem, then
synthesizing. The pattern documents itself.

---

## Ship / scrub

- The fork-or-inline decision, the model-to-task table, the output-size trap, the dispatch-only
  contract, and the cost-plus-permission framing for self-written workflows are all generic. Ship them.
- Scrub the specific model names and any per-agent routing table that encodes your own subscriptions
  or gateway. The *shape* of the decision is the lesson; your exact routing is yours.
- Keep the default for self-orchestrating workflows set to off in anything you share. An on-by-default
  fan-out in someone else's hands is a surprise quota bill and a wider permission surface than they meant to grant.
