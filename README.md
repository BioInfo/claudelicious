<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-banner-dark.png">
    <img src="assets/logo-banner-transparent.png" alt="Claudelicious" width="640">
  </picture>
</p>

<h1 align="center">Claudelicious</h1>

<p align="center"><em>A working cookbook for running Claude Code as a system, not a chat box.</em></p>

<p align="center"><strong>The model is the commodity. The harness is the moat.</strong></p>

---

This repo is the wiring diagram behind one operator's full Claude Code setup: the rules, skills, hooks, memory, learning loop, session search, second brain, multi-provider routing, scheduled jobs, and always-on agents, plus the reasoning for why each piece exists and how they connect.

It is **not a catalog**. The community already maintains one of those at [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code), and you should use it: that is where you go to find a skill, a hook, a slash command, an MCP server. Claudelicious is the other half. It shows how those pieces fit together into a harness that remembers across sessions, improves itself when you correct it, and runs while you sleep, all wired around a homelab.

Most "here is my setup" repos are a flat list. This one leads with the systems underneath the skills, because those are the part you cannot reverse-engineer from a screenshot.

Part One builds one harness. Part Two, the second arc, is what it looks like to run several of them at once: chartered lanes working in parallel while you stand at a single seam and rule on what surfaces.

---

## Reading this as an agent

If a human pointed their Claude Code at this repo to help build or understand a harness: start at [`AGENTS.md`](AGENTS.md). It tells you how the repo is laid out, the conventions every doc follows, and how to adapt a pattern without copying anyone's private paths. Then read [`docs/00-the-map.md`](docs/00-the-map.md).

Every doc is written to be applied, not just read: principle first, then a worked example, then explicit ship-or-scrub notes.

---

## Find what you need

| You want to... | Go to |
|----------------|-------|
| Get the spine in place in your first week | [QUICKSTART.md](QUICKSTART.md) |
| Read the whole thing as one long story | [STORY.md](STORY.md) |
| Understand the whole thing in 10 minutes | [00 The map](docs/00-the-map.md) + [Philosophy](PHILOSOPHY.md) |
| Stop repeating instructions every session | [01 Rules and context](docs/01-rules-and-context.md) |
| Build a skill library that stays small and sharp | [02 Skills](docs/02-skills.md) |
| Decide what to lift from someone else's repo, paper, or tool | [02 Skills](docs/02-skills.md#a-skill-that-decides-what-to-steal) |
| Make the agent stop doing dangerous things | [03 Hooks](docs/03-hooks.md) |
| Fix that Claude does not know the date | [03 Hooks](docs/03-hooks.md#time-injection) |
| Make Claude remember things across sessions | [04 Memory](docs/04-memory.md) |
| Make a correction stick instead of recurring | [05 The learning loop](docs/05-learning-loop.md) |
| Resume work cleanly after a compaction | [06 Continuity](docs/06-continuity.md) |
| Search your own past sessions | [07 Session search (mneme)](docs/07-session-search-mneme.md) |
| Let Claude semantically search your notes | [08 The second brain](docs/08-second-brain.md) |
| Run Claude Code on Kimi / MiniMax / GLM / Qwen | [09 Multi-provider](docs/09-multi-provider.md) |
| Push bulk, mechanical coding to a cheaper flat-rate model | [09 Multi-provider](docs/09-multi-provider.md#delegation-spending-the-cheap-lanes-on-purpose) |
| Schedule jobs inside Claude Code and on the machine | [10 Crons and scheduling](docs/10-crons-and-scheduling.md) |
| Build an agent that runs on a heartbeat | [11 Always-on agents](docs/11-always-on-agents.md) |
| Make the harness write in your voice | [12 Voice and anti-slop](docs/12-voice-and-antislop.md) |
| Generate logos, infographics, diagrams | [13 Visual generation](docs/13-visual-generation.md) |
| Fork work to subagents, or let the harness orchestrate itself | [14 Subagents and workflows](docs/14-subagents-and-workflows.md) |
| Run a loop until the work is done, not just on a timer | [15 Loops and autonomy](docs/15-loops-and-autonomy.md) |
| Spread the harness across more than one machine | [16 The fleet](docs/16-the-fleet.md) |
| Tune `settings.json` so a session behaves the way you want | [17 Settings](docs/17-settings.md) |
| Connect the harness to mail, calendar, search, a browser | [18 MCP](docs/18-mcp.md) |
| Understand running with broad machine access, and the guards | [19 Running wide open](docs/19-running-wide-open.md) |
| **Part Two — running several harnesses at once** | |
| Let an autonomous agent decide some things without asking | [20 The autonomy charter](docs/20-the-autonomy-charter.md) |
| Run one project as parallel autonomous lanes | [21 Lanes and the cockpit](docs/21-lanes-and-the-cockpit.md) |
| Design the human gate so a fleet does not drown you | [22 The seam](docs/22-the-seam.md) |
| Trust work you did not read | [23 Instruments](docs/23-instruments.md) |
| Spend the premium model only where it earns | [24 The model budget](docs/24-the-model-budget.md) |

Templates and copy-able files live in [`templates/`](templates/), [`hooks/`](hooks/), [`skills/`](skills/), [`settings/`](settings/), and [`mods/`](mods/).

---

## Mods

Mods are Claude Code plugins built on function hooks. A hook module subscribes to session events (a prompt, a tool call, a finished turn) and can draw a pane beside the session, show a toast, or add a line to the model's context. This repo is also a plugin marketplace that ships them:

```
/plugin marketplace add BioInfo/claudelicious
/plugin install command-center@claudelicious
```

The first one is [command-center](mods/command-center/): one pane with the session's intent, running jobs, files changed, the last reply's open questions, and the 5h/7d limit pace. Watch the [two-minute walkthrough](https://youtu.be/rY4fyCVfD5c). The index is [`mods/`](mods/).

---

## The five words

Everything here is built from five primitives. Lock these first.

| Word | What it is |
|------|------------|
| **Model** | The LLM. The smallest decision you make. |
| **Harness** | Everything around the model. The part that compounds. |
| **Agent** | A model in a harness, given a goal and the room to pursue it. |
| **Skill** | A repeatable procedure the harness invokes by name. A business process, encoded. |
| **MCP** | Model Context Protocol. How the harness reaches external systems. |

A great model with no harness is a demo. A harness with a great model is a second nervous system.

---

## The shape of it

To make the scale concrete: a skill library deliberately pruned from a peak of over 130 down to a curated few dozen, because the cut is the craft and not a footnote to it. Around 15 MCP servers, each a doorway into a real system. A four-tier memory taxonomy over roughly seventy thousand plain-markdown vault documents. A mesh of five machines from a laptop to a GPU box. Eight named agents, each with its own role and memory, for less than a couple of lunches a month. That figure holds for the heartbeat agents. The chartered lanes of Part Two do not run on lunch money; several full harnesses in parallel is a real bill, which is why Part Two closes on a [model budget](docs/24-the-model-budget.md).

None of those numbers is the point. That they are *governed* is the point. A system this size that nobody pruned would collapse under its own context.

---

## What this is not

Not a clone-and-run starter kit. It is docs-first, with templates and worked examples so you adapt the pieces to your own paths, hosts, and vault. The reasoning is the product. A scaffold you paste in without understanding becomes the next thing you cannot maintain.

It is also scrubbed. No real hostnames, IP addresses, credentials, or private paths. Where the original used a specific path or host, the docs use a placeholder and tell you what to substitute.

---

## The companion

This cookbook is the implementation. The reasoning for why you would build a harness at all, what it does to your working life, and how to lead a team across the same gap, lives in the book: **Builder-Leader: The AI Exoskeleton That Crosses the Gap** ([builder-leader.com](https://builder-leader.com)).

The book is the why. This is the how.

The ideas keep developing in public on two blogs: **[AIXplore](https://ai.rundatarun.io)**, the technical, practitioner-facing one closest to this repo, and **[Run Data Run](https://rundatarun.io)**, the leadership and strategy angle. A lot of these patterns were first worked out in the open there.

---

## License

Dual-licensed by content type. The **code** you would copy into your own setup —
everything in `templates/`, `hooks/`, `skills/`, and `mods/` — is **MIT** ([`LICENSE`](LICENSE)),
so use it however you like. The **prose** — `docs/`, this README, and `PHILOSOPHY.md` —
is **CC BY-NC 4.0** ([`LICENSE-docs`](LICENSE-docs)): share and adapt it with
attribution, but not for commercial repackaging.

---

Start small. Be a builder.
