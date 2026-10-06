# 17 — Settings, the real tweaks

`settings.json` is the harness's control panel, and most people touch three keys and leave the rest at
default. The defaults are fine, but a handful of changes are worth understanding because they shift how
the whole session behaves: how hard the model reasons, what it can do without asking, and what fires
automatically on every turn. This doc walks the knobs that actually matter and the reasoning behind each.

A full, working example lives in [`settings.example.json`](../settings/settings.example.json) and in
[`templates/`](../templates/settings.example.json). Read this doc for the why; copy the file for the how.
JSON has no comments, so the file annotates itself with a single `_comment` key and points back here for
the reasoning.

---

## How hard it reasons

The effort level governs how much the model thinks per turn. There is a ladder from low to maximum, and
it is a real tradeoff, not a "more is better" dial. Higher effort produces better work on hard problems
and can overthink simple ones, and it spends more of whatever budget you care about. Set a sensible
floor as the standing default and raise it per task when the work is genuinely hard. The reason to keep
the standing default modest rather than maxed is that it applies to *every* turn, including the trivial
ones, and the trivial ones are most of them.

For one-off depth without changing the setting, most harnesses take a per-session override or an
in-prompt keyword. Reach for those on the occasional hard problem instead of raising the global floor.

---

## What it can do without asking

The permission mode sets the default friction of a session. The useful modes:

- **Ask on everything**, the cautious default, where the agent stops before each action that touches the world.
- **Accept edits**, where file edits inside the project apply without a prompt but external actions still
  pause. This is the practical working mode once you trust the setup: the agent iterates on files freely,
  and you stay in the loop on anything that leaves the machine.
- **A fuller auto mode**, which approves the safe actions and pauses on the risky ones, for long
  unattended runs where you have given full context up front.

The matching `permissions` block is an allowlist and a denylist: name the read-only commands that should
never prompt (status, diff, list, search) so they stop interrupting you, and deny the few genuinely sharp
edges. Here is the load-bearing caveat, and it is the reason the [hooks](03-hooks.md) doc exists: the
denylist is not a hard wall. Its enforcement has limits, and a sufficiently long or chained command can
slip a naive deny rule. The deterministic floor is a hook, not a deny entry. Treat the allowlist as
ergonomics, the denylist as a speed bump, and the hooks as the actual fence.

---

## What fires on every turn

The `hooks` block is where the harness stops being passive. Wired into the example settings:

- **On session start**, a script that mints the session journal and injects the last session's open items,
  so you resume mid-thought. See [continuity](06-continuity.md).
- **On every prompt**, the current date and time injected into context, because the model does not know
  what day it is and will confidently guess wrong. The single highest-value hook for the least effort.
- **Before a web search**, a small rewrite that appends the current year to a query that lacks a date,
  so "latest framework version" does not return last year's answer.
- **Before a tool runs**, the safety layer: block a recursive delete, ask before piping the internet into
  a shell, scan for secrets before a push, refuse edits to environment files.
- **After a file edit**, format-on-save for the language that was touched.
- **After a compaction**, a reinjection that restores the working state the summary dropped.

The principle is the one from the hooks doc, repeated here because it is what makes settings worth
tuning at all: the things that must happen every time belong in a hook, not in a rule you hope the model
remembers. [Doc 03](03-hooks.md) covers the scripts; this is where you register them.

---

## The small quality-of-life keys

Less dramatic, still worth setting:

- Point the built-in memory at your store so durable notes land where the rest of the harness reads them
  (see [memory](04-memory.md)).
- A cleanup period that prunes old session transcripts on a schedule, so the projects directory does not
  grow forever.
- Turn-duration and git-instruction flags that surface how long work took and keep commit hygiene
  consistent.
- A status line, if you want the session to show its own context at a glance.
- MCP servers, declared once, so the harness's reach into your external systems is part of the config and
  not a per-session setup step.

None of these changes how the model thinks. They are the difference between a setup that fights you and
one that gets out of the way.

---

## Where settings live

There is a hierarchy: a user-level file that applies everywhere, and a project-level file that overrides
it for one repo. Keep the broad, personal preferences at the user level and the project-specific
permissions and hooks at the project level. The same progressive-disclosure instinct from
[rules](01-rules-and-context.md) applies: the global file holds what is true everywhere, and the specific
lives close to where it is specific.

---

## Ship / scrub

- The effort ladder, the permission-mode progression, the deny-list-is-not-a-wall caveat, the hook
  registry, and the user-versus-project split are all generic. Ship them.
- The example file uses placeholder paths (`<path-to>/...`, `~/.claude/hooks/...`). Scrub them to your own
  before use; a copied hook path that points nowhere fails silently.
- Do not ship your real MCP server block. It names the external systems you connect to, and some entries
  carry tokens or private endpoints. Ship the shape, declare your own servers locally.
