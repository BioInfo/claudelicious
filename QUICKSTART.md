# Quickstart: your first week

The mistake is building all of this at once. You read the map, see twenty boxes, and try to wire them in a weekend. Then nothing compounds because nothing is load-bearing yet.

Build it in order instead. Each step below works on its own and makes the next one worth doing. A week of this puts the spine in place. The autonomy layer (agents, multi-provider, the fleet) can wait until the spine is real.

If you want the why before the how, read [the story](STORY.md). If you want the wiring diagram, read [the map](docs/00-the-map.md). This page is just the order.

---

## The spine, in order

**1. Write your `AGENTS.md`.** ([doc 01](docs/01-rules-and-context.md))
One file at the project root. Who you are, how you work, what this repo is, the two or three constraints that actually matter. Keep it short. Every line here is paid for on every turn, so a long file is a worse file. This is the one step that changes every session that follows, which is why it goes first.

**2. Write one skill.** ([doc 02](docs/02-skills.md))
A skill is a named procedure the agent can reach for. Write the one you'd explain to a new teammate first. Resist writing ten. The whole discipline of this cookbook is that a small, sharp set beats a big one, and you learn that fastest by living with a single skill before you add the second.

**3. Add one hook.** ([doc 03](docs/03-hooks.md))
Rules persuade; hooks enforce. Start with time injection: the model has no clock, so put the real date into every prompt. It is five lines and it removes a whole class of wrong answers. Once you trust the mechanism, the safety hooks (block recursive deletes, scan for secrets before a push) are the same shape.

**4. Turn on memory and write one fact.** ([doc 04](docs/04-memory.md))
Point the harness at a memory directory and let it write a single durable note the next session can read. One fact proves the loop. The value shows up the third time you start fresh and the agent already knows the thing you told it last week.

**5. Add a `CONTINUITY.md`.** ([doc 06](docs/06-continuity.md))
A long session gets summarized, and the detail you cared about can fall out. A continuity file is where tactical state lives so it survives that. Goal, current phase, the decision you just made, what is next. You write it once and update it as you go.

**6. Close the learning loop.** ([doc 05](docs/05-learning-loop.md))
This is the step that makes the rest compound. When you correct the agent, two things should happen: memory writes the sticky note so the next session does not repeat the mistake, and the loop writes a work order naming the exact file to edit so it cannot recur. Without this, you re-teach the same lesson forever. With it, the harness gets better while you sleep.

---

## What to ignore for now

Everything past the spine is real and worth having, later. Skip it this week:

- **Subagents and workflows** ([14](docs/14-subagents-and-workflows.md)). Forking work out. You don't need it until one context gets crowded.
- **Multi-provider** ([09](docs/09-multi-provider.md)). Running on a non-Anthropic model. A swap, not a foundation.
- **Crons and always-on agents** ([10](docs/10-crons-and-scheduling.md), [11](docs/11-always-on-agents.md)). Unattended work. Stand these up after the spine you supervise is solid.
- **The fleet** ([16](docs/16-the-fleet.md)). Many machines. One machine is plenty to learn on.
- **Second brain and session search** ([08](docs/08-second-brain.md), [07](docs/07-session-search-mneme.md)). Retrieval over everything. These pay off once the vault has enough in it to search.

---

## How you know it's working

By the end of the week the test is simple. Start a brand-new session and ask it to pick up where the last one left off. If it reads your continuity file, knows the facts you taught it, reaches for the skill you wrote, and respects the constraints in your `AGENTS.md`, the spine is real. Now you add to it.

The harness is something you wear, not something you open. The first week is where it starts to fit.
