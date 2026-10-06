# 00 — The map

This is the wiring diagram. Read it once before the rest, so the later docs have somewhere to land.

A harness is built in layers. Each layer does one job, and the layers feed each other. The diagram below is the whole system on one page. Every box has its own doc.

```
                         ┌─────────────────────────────────────────┐
                         │              YOUR SESSION                │
                         └─────────────────────────────────────────┘
                                          ▲
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
   ┌────────┴────────┐          ┌─────────┴─────────┐         ┌─────────┴─────────┐
   │  CONTEXT layer  │          │  CAPABILITY layer │         │ ENFORCEMENT layer │
   │  rules + AGENTS │          │  skills + MCP +   │         │      hooks        │
   │  (01)           │          │  subagents (02)   │         │      (03)         │
   └─────────────────┘          └───────────────────┘         └───────────────────┘
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          ▼
                         ┌─────────────────────────────────────────┐
                         │   MEMORY (04)  +  LEARNING LOOP (05)     │
                         │   durable facts  +  edits-at-the-source  │
                         └─────────────────────────────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────────────┐
                         │             THE VAULT                    │
                         │  every note, memory, learning, journal   │
                         │  written as plain markdown. the hub.     │
                         └─────────────────────────────────────────┘
                              │                          │
                              ▼                          ▼
                  ┌───────────────────────┐   ┌───────────────────────┐
                  │  CONTINUITY (06)      │   │  SECOND BRAIN (08)    │
                  │  journals, threads,   │   │  vault → embeddings → │
                  │  handoff, post-compact│   │  Qdrant hybrid search │
                  └───────────────────────┘   └───────────────────────┘
                              │                          ▲
                              ▼                          │
                  ┌───────────────────────┐              │
                  │  SESSION SEARCH (07)  │──────────────┘
                  │  mneme · LanceDB      │
                  └───────────────────────┘

           runs on top of all of it, unattended:
   ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
   │  MULTI-PROVIDER (09)│   │   CRONS (10)        │   │ ALWAYS-ON AGENTS (11)│
   │  Anthropic, or      │   │  in-session +       │   │  Pulsar: wake on a   │
   │  Kimi/MiniMax/GLM/  │   │  on-the-machine     │   │  heartbeat, do work, │
   │  Qwen via gateway   │   │  + heartbeats       │   │  stay quiet otherwise│
   └─────────────────────┘   └─────────────────────┘   └─────────────────────┘
```

## How to read the layers

**Context (01).** What loads every session: the `AGENTS.md` / `CLAUDE.md` hierarchy and `rules/*.md`. Kept short on purpose. This is the standing instruction set, governed by the attention budget.

**Capability (02).** What the harness can do: skills (named procedures), MCP servers (reach into mail, calendar, search, your own services), and subagents (forked workers for parallel or heavy work). Skills are the centerpiece, and the discipline is keeping the set small.

**Enforcement (03).** What must happen deterministically: hooks. Inject the current time on every prompt, block recursive deletes, ask before a remote-pipe-to-shell, scan for secrets before a push, format on save. Rules persuade; hooks enforce.

**Memory (04) and Learning (05).** When you correct the agent, two things fire. Memory writes a durable note so the next session does not repeat the mistake. The learning loop writes a work order that names the exact skill, rule, or agent file to edit so the mistake cannot recur. One is the sticky note, the other is the fix.

**The vault.** The hub. Every memory, learning, session journal, and project note is written here as plain markdown. It is human-readable, version-controlled, and model-agnostic. Everything downstream reads from it.

**Continuity (06).** How a session survives compaction and how the next one resumes: session journals keyed by thread, a SessionStart handoff that drops the last session's open items into context, and a post-compact reinjection that restores state when the window is summarized.

**Session search (07) and Second brain (08).** Two retrieval systems over the same hub. `mneme` indexes your past sessions into LanceDB so you can ask "when did we solve this before." The second brain embeds the whole vault into Qdrant so the agent can semantically search its own notes, memories, and learnings, even when it does not know the exact filename.

**Multi-provider (09), Crons (10), Always-on agents (11).** The autonomy layer. Run the harness against a non-Anthropic model through a gateway, schedule work both inside Claude Code and on the host machine, and stand up an agent like Pulsar that wakes on a heartbeat, does a slice of work, and goes quiet when there is nothing to say.

## The named systems (glossary)

You will see these names in the docs. They are referred to directly because they are public-facing patterns, not because you should install them as-is.

| Name | What it is | Doc |
|------|------------|-----|
| **mneme** | LanceDB-backed search over your own Claude Code sessions. | [07](07-session-search-mneme.md) |
| **continuum** | A reader and router over the durable memory homes (memory, learnings, rules). | [04](04-memory.md) |
| **Pulsar** | A persistent agent that runs on a heartbeat and acts as a chief of staff. | [11](11-always-on-agents.md) |
| **Slopless** | The voice system that makes the harness write like you, not like an LLM. | [12](12-voice-and-antislop.md) |
| **charter** | A per-lane file naming what an autonomous lane may decide alone and what it escalates. | [20](20-the-autonomy-charter.md) |
| **lane** | One chartered autonomous harness working a single slice of a larger project. | [21](21-lanes-and-the-cockpit.md) |
| **cockpit** | The operator's session: it runs no loop, it surfaces what needs a human and stages the rest. | [21](21-lanes-and-the-cockpit.md) |
| **seam** | The human gate where a fleet's escalations land as one ranked queue. | [22](22-the-seam.md) |

## Beyond the core: operations and the long read

The numbered docs continue past the diagram with the operational layer:

- **[14 Subagents and workflows](14-subagents-and-workflows.md)** — when to fork work to a forked worker, what model the fork runs, and when the harness writes its own orchestration.
- **[15 Loops and autonomy](15-loops-and-autonomy.md)** — the loop as the smallest unit of autonomy, and the overnight experiment that shows why it matters.
- **[16 The fleet](16-the-fleet.md)** — the machines the harness runs on and the role each one plays.
- **[17 Settings](17-settings.md)** — the `settings.json` knobs that actually change how a session behaves.
- **[18 MCP](18-mcp.md)** — how the harness reaches the systems it does not own, and why every MCP response is untrusted data.
- **[19 Running wide open](19-running-wide-open.md)** — the candid case for broad machine access, and the deterministic floor that makes it sane.

For the whole system as a narrative rather than a reference, read [the story](../STORY.md). It ties the philosophy, the architecture, and the why-it-matters into one long read.

## Running more than one: Part Two

Everything above is one harness. The second arc of this cookbook, docs 20 through 24, is what the picture looks like when you run several at once and are not watching any of them.

```
                    ┌────────────────────────────┐
                    │   YOU  ·  the cockpit       │  runs no loop of its own:
                    │   inspect · rule · stage    │  surfaces what needs a human
                    └──────────────┬──────────────┘
                                   │   the seam (22): one ranked human queue
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │  LANE A    │       │  LANE B    │       │  LANE C    │   each lane is a
       │  charter   │       │  charter   │       │  charter   │   FULL harness (the
       │  cursor    │       │  cursor    │       │  cursor    │   diagram above),
       └─────┬──────┘       └─────┬──────┘       └─────┬──────┘   held to a charter (20)
             └────────────────────┼────────────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │  SHARED FILES = the bus     │  handoff inbox · ledger · vault
                    │  lanes coordinate here      │  (files, never messages)
                    └────────────────────────────┘
```

Each lane is a full harness, the diagram at the top of this page, wrapped in a [charter](20-the-autonomy-charter.md) that says what it may decide alone. Lanes coordinate through shared files, not messages, the same vault-is-the-hub logic already at work inside one harness. You sit at the cockpit, which runs no loop of its own; it surfaces what needs a human across every lane and stages the rest. The one place your judgment gets spent is the seam.

- **[20 The autonomy charter](20-the-autonomy-charter.md)** — trust written down: what a lane decides alone, what it escalates, and the ledger that records every time the line moves.
- **[21 Lanes and the cockpit](21-lanes-and-the-cockpit.md)** — one project as parallel chartered lanes, coordinating through files, and the operator session that runs no loop.
- **[22 The seam](22-the-seam.md)** — the human gate as a designed interface, and the two ways it fails.
- **[23 Instruments](23-instruments.md)** — how to trust work you did not read: verify the artifact, not the exit code.
- **[24 The model budget](24-the-model-budget.md)** — judgment on the premium model, labor delegated off it.

One correction Part Two makes to the ladder in [the philosophy](../PHILOSOPHY.md): the top rung, lived in, is not a dark factory. It is supervised autonomy with one light on, and the light is the cockpit.

## The one-sentence version

Standing context is small, capability is curated, enforcement is deterministic, every correction edits the source and lands in a searchable vault, and the whole thing can run unattended on whatever model you point it at.
