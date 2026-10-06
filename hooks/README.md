# hooks/

Scrubbed, working PreToolUse / PostToolUse hooks. These are the deterministic
floor under an autonomous harness: a rule in a config file competes with the
model's habits and loses under load; a hook runs every time. See
[`docs/03-hooks.md`](../docs/03-hooks.md) for the reasoning.

| File | Event / matcher | What it does |
|------|-----------------|--------------|
| `block-rm-rf.py` | PreToolUse / Bash | hard-deny `rm -rf` at a command boundary; tells you to use `trash` |
| `injection-guard.py` | PreToolUse / Bash | ask-confirm on the four injection/exfil shapes (remote-pipe-to-shell, remote-pipe-to-interpreter, inline `ANTHROPIC_BASE_URL`, secret-source + outbound-sink) |
| `block-env-edits.py` | PreToolUse / Edit\|Write | hard-deny edits to `.env` files, exempting `.env.example`/`.template`/`.sample` |
| `gitleaks-pre-push.py` | PreToolUse / Bash | run gitleaks on the commits being pushed; deny on a finding, ask if gitleaks is missing or on a force push |

Time-injection and format-on-save are pure shell, so they live inline in
[`settings.example.json`](../templates/settings.example.json) rather than as
files here.

## Wiring

Copy the scripts somewhere stable (e.g. `~/.claude/hooks/`) and point
`settings.json` at them. The matchers and the full hook block are in
[`templates/settings.example.json`](../templates/settings.example.json). The
shape of one entry:

```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      { "type": "command", "command": "python3 ~/.claude/hooks/block-rm-rf.py", "timeout": 5 },
      { "type": "command", "command": "python3 ~/.claude/hooks/injection-guard.py", "timeout": 5 },
      { "type": "command", "command": "python3 ~/.claude/hooks/gitleaks-pre-push.py", "timeout": 60 }
    ]
  }
]
```

## The five principles (from docs/03)

1. **Anchor at command boundaries.** `(?:^|[\n;&|(])\s*` in front of any
   command-matching regex, so the hook fires on the command, not on the string
   inside an echo or heredoc.
2. **Fail open. Never wedge the tool.** Every hook exits clean on any internal
   error. A crashing guard that blocks all of Bash is worse than the risk.
3. **Ask, do not deny, except two cases.** Hard-deny only irreversible actions
   with no legitimate agent use (`rm -rf`, editing a secret file) and a
   confirmed secret leak. Everything else asks.
4. **Ship a test suite with the hook.** Name the shapes that should fire and the
   ones that must not, and run them before deploying a change.
5. **Time injection is universal.** Every harness should do it. One line, every
   prompt.

## Before you share your own

`injection-guard.py` carries host-specific allow-heuristics (the `local` test in
section 2 — gateway naming, tailnet hints). Replace those with your own, keep
the four detection shapes, then run your own `gitleaks` pass over this directory
before publishing.
