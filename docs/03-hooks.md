# 03 — Hooks: the deterministic layer

A rule written in a config file competes with the model's habits, and under load it loses. A hook does not. A hook runs every time, deterministically, before or after the tool call, no matter what the model intended. So the principle of this layer is one line: **if something must happen, it is a hook, not a sentence.**

This matters more the more autonomy you give the harness. A setup that runs broad-allow (`Bash(*)`, auto-accepted edits, live web access) has a realistic threat that is not you fat-fingering a command. It is an injected instruction, from a web page, a repo file, or an MCP response, that chains an allowlisted command into something you did not ask for. Hooks are the deterministic floor under that. They are also where you fix the model's blind spots, the first of which is the clock.

---

## <a id="time-injection"></a>The flagship: inject the current time

The model does not know what day it is. Its training has a cutoff, and left alone it will reason as if the date is sometime in its past. That breaks date math, "latest" lookups, anything time-sensitive.

The fix is one hook. On every prompt, inject the wall-clock time as context. In `settings.json`:

```json
"UserPromptSubmit": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "echo '{\"systemMessage\": \"Current time: '$(date '+%A, %B %d, %Y %I:%M %p %Z')'\"}'"
      }
    ]
  }
]
```

The empty matcher means it fires on every prompt. The `$(date ...)` expansion runs at submit time, and the result lands in context before the model reads your message. Now it always knows the time.

There is a logical extension for web search. When a query is temporally ambiguous (no year, no "latest" or "today" in it), a `PreToolUse` hook on the search tool appends the current year so you do not get stale results:

```
PreToolUse  →  WebSearch  →  if no temporal anchor in query, append current year
```

Two layers, both cheap, and the model stops living in the past.

---

## The guards

These run on `PreToolUse` and stop the small set of actions that are either irreversible or are the signature of an injection.

**Block recursive deletes.** A hard deny on any command that actually invokes `rm` with recursive-force flags. The implementation detail that matters: the regex is anchored to a command boundary (`(?:^|[\n;&|(])`), so it fires on `rm -rf`, `sudo rm -rf`, `&& rm -rf`, but not on `grep "rm -rf"` or a heredoc that merely contains the string. Boundary-anchoring is the difference between a guard and a nuisance.

**The injection guard.** This one returns "ask" (a human confirm), never a hard deny, on the shapes injection uses:

- a remote pipe into a shell: `curl ... | sh`
- a remote pipe into a bare interpreter: `curl ... | python3` with no fixed script
- an inline `ANTHROPIC_BASE_URL` pointed at an external host (an API-key exfiltration vector)
- a secret source and an outbound sink in the same command: an SSH key or password-store read combined with `curl`, `nc`, or a request library

It is tuned not to fire on the legitimate versions: a curl to your own gateway, sourcing a local env file, an authenticated `ssh`/`rsync`. The posture is "ask, do not block," because the rare legitimate case should stay possible.

**Block secret files.** A hard deny on edits to `.env` and `.env.<anything>`, with an exemption for `.env.example` / `.env.template`. Secrets belong in a password manager, not a file that might get committed. The exemption keeps the normal workflow (committing a placeholder template) unbroken.

**Scan before push.** On any `git push`, run a secret scanner in git mode, scoped to the commit range being pushed (`{upstream}..HEAD`), not the whole working tree. Scoping to the commit range is what makes it fast and false-positive-free: it ignores gitignored build artifacts and never re-flags secrets already in pushed history. A real finding denies the push. A missing scanner asks, with install instructions, rather than silently passing.

---

## Deny, then inject: making a rule actually fire

A rule sitting in a system prompt or a config file is available to the model. Available is not the same as enforced. Under load, with enough competing instructions, a model can skip a rule it technically read, and nothing in a passive setup tells you it happened.

The fix is a specific `PreToolUse` pattern: deny the first action that would trigger the rule, inject the rule's full text into context as the reason for the denial, then let the model retry the same action now that the rule is in front of it. The retry succeeds, and the rule has actually been read at the moment it mattered, not just loaded somewhere upstream in the prompt.

The detail that makes this non-obvious: injecting context on the *allow* path does nothing useful for that action. By the time an allowed tool call returns, the action already happened. Whatever you inject afterward can shape the next thing the model does, but it cannot undo the one that already ran without the rule applied. A deny is the only hook outcome that buys a pre-action intervention, because it is the only one that stops the call before it executes and hands the model new information before it tries again.

This was proven on a real failure. A large, always-on instruction telling the model to write in a specific voice was loaded into context on every turn, and it was still measurably not firing, the same way, two days running. The instruction was present. It was not enforced. Moving that rule from passive context into a deny-then-inject hook on the first voice-bearing write of the session fixed it immediately, because getting past the denial required actually reading the rule.

Generalize this: any rule a passive system-prompt sentence cannot reliably hold is a candidate for this pattern. If you have caught the model skipping the same instruction twice, it is worth one small `PreToolUse` hook.

---

## The quality gate: format on save

A `PostToolUse` hook on file edits that runs the formatter for the language touched (prettier/eslint for JS and TS, ruff for Python, gofmt for Go, rustfmt for Rust), each with `|| true` so a missing tool never blocks. Zero config, fail-open, and every file the harness writes comes out formatted.

There is a sibling pattern worth knowing: `PostCompact`. When the context window gets summarized, a hook re-injects the things that must survive (the project continuity ledger, the active session's next-steps, standing rules). That one belongs to continuity; see [06](06-continuity.md).

---

## The five principles

Everything above is an application of these.

1. **Anchor at command boundaries.** Put `(?:^|[\n;&|(])\s*` in front of any command-matching regex so the hook fires on the command, not on the string sitting inside an echo, a heredoc, or a replay payload. This is the single most important implementation detail across every bash hook.
2. **Fail open. Never wedge the tool.** Every hook wraps its logic in try/except and exits clean on any internal error. A hook that crashes and blocks all of Bash is worse than the narrow risk it covered.
3. **Ask, do not deny, except for two cases.** Hard-deny only (a) irreversible actions with no legitimate agent use (`rm -rf`, editing a secret file) and (b) a confirmed secret leak. Everything else asks, so the rare legitimate case survives.
4. **Ship a test suite with the hook.** Name the command shapes that should fire and the ones that must not, and run them before deploying a change. A routing hook with twenty named cases catches the false positive before it derails a real session.
5. **Time injection is universal.** Every harness should do it. One line, every prompt.

---

## Wiring (settings.json)

| Event | Matcher | What runs |
|-------|---------|-----------|
| `SessionStart` | startup/resume/clear | mint the session journal, inject the last handoff (see [06](06-continuity.md)) |
| `UserPromptSubmit` | all | inject `Current time: ...` |
| `PreToolUse` | Bash | block-rm-rf, injection-guard, gitleaks-pre-push |
| `PreToolUse` | Edit/Write | block-env-edits |
| `PreToolUse` | WebSearch | append current year when ambiguous |
| `PostToolUse` | Edit/Write | format on save |
| `PostCompact` | auto/manual | re-inject continuity state |

Working, scrubbed versions of these scripts are in [`hooks/`](../hooks/).

---

## Ship / scrub

- The time-injection hook, the format-on-save hook, and the env-block and gitleaks hooks are generic. Ship as-is.
- The injection guard references a private gateway host and tailnet range in its allow-tuning. Replace those with your own before sharing, but keep the four detection shapes and the ask-not-deny posture.
- The deny-then-inject pattern is fully generic and ships as-is; only the rule text you inject (your own voice guide or house style) stays private.
- Never ship a hook that hardcodes a real path, host, or credential. Genericize first, then run your own gitleaks pass over the `hooks/` directory before publishing.
