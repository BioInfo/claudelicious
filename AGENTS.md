# AGENTS.md — how to work inside this repo

You are probably reading this because a human pointed their Claude Code (or another agent) at Claudelicious to help them understand or build a Claude Code harness. This file orients you.

## What this repo is

A reference cookbook. It documents one operator's full Claude Code setup and the reasoning behind each part: rules, skills, hooks, memory, the learning loop, continuity, session search, the second brain, multi-provider routing, scheduling, and always-on agents. It is documentation and templates, not a runnable application.

## Layout

- `README.md` — front door and findability index.
- `PHILOSOPHY.md` — the three ideas that hold the system together.
- `docs/` — the comprehensive reference, numbered in read order (`00` through `24`), in two arcs: Part One (`00`–`19`) builds one harness, Part Two (`20`–`24`) is running several of them at once. Each doc is self-contained.
- `templates/` — copy-able files: an `AGENTS.md` template, memory and learning templates, a settings example, generic rule examples.
- `hooks/` — scrubbed, working hook scripts you can adapt.
- `skills/` — a few generic example skills.
- `assets/` — the logo and generated infographics.

## Conventions every doc follows

1. **Principle first.** Each doc opens with the idea, then shows the worked example, then gives ship-or-scrub notes. Read in that order.
2. **Placeholders, not real paths.** Every path, host, IP, and credential reference is generic. `<vault>`, `<gateway-host>`, `~/sessions/`, `com.<you>.<job>`. Treat any concrete-looking path as an example to replace, never a real target.
3. **Named systems.** A few systems are referred to by name because they are public: `mneme` (session search), `Pulsar` (heartbeat agent), `continuum` (memory router), `Slopless` (the voice system). These are patterns to learn from, not packages to install blindly.

## How to apply a pattern for a user

1. Identify the right doc from the README's "Find what you need" table.
2. Read the principle and the worked example.
3. Ask the user for their real paths, hosts, and preferences. Do not guess them.
4. Adapt the template, substituting their values for the placeholders.
5. If the pattern touches security (hooks, secrets, scheduled jobs that send or publish), surface the action and confirm before wiring it.

## What not to do

- Do not treat any example path, hostname, IP, or `com.<you>.*` style label as real infrastructure.
- Do not copy a secret, key, or credential pattern into a live file. The whole system routes secrets through a password manager; honor that.
- Do not publish, push, or deploy anything without explicit confirmation from the user.
- Do not paste a whole section of someone else's harness into a user's setup without adapting it to their context. Bloat is the failure mode this cookbook exists to prevent (see [`docs/02-skills.md`](docs/02-skills.md)).

Start at [`docs/00-the-map.md`](docs/00-the-map.md).
