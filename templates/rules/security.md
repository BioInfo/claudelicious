# Security Posture (example rule file)

<!-- An example rules/*.md. Scrub to your own setup. The deterministic enforcement
     for most of this lives in hooks/ (block-rm-rf, injection-guard, block-env-edits,
     gitleaks-pre-push) — a rule states intent, a hook enforces it. See docs/03. -->

## Destructive ops

- No force push. No `rm -rf` — use a `trash` command. Ask before bulk operations.
- These are enforced by hooks, not left to the model's judgment.

## Secrets

- Never commit secrets, API keys, or credentials.
- Keep keys in a password manager, not in `.env` files or hardcoded in scripts.
- No secrets in code reviews or in content sent anywhere.

## Asking before outward-facing actions

- **Ask before public.** The default destination for any artifact is private. A
  public host, a deploy, a published file — each needs explicit, per-artifact
  approval that names the destination.
- **No comms without approval.** No email, message, or social post goes out
  without showing the draft and getting an explicit "send it." Applies to every
  dispatch tool.

## The real threat is injection, not fat-fingering

A harness that runs broad-allow + auto-accepted edits + live web browsing has a
realistic threat that is not you mistyping. It is an injected instruction — from
a web page, a repo file, an MCP response — that chains an allowlisted command
into exfiltration. Deny rules are not a hard wall (enforcement has limits under
long chains); the deterministic floor is a `PreToolUse` hook. Keep remote-fetch
commands (`curl`/`wget`) off the blanket allowlist — allowlisting them reopens
the exfiltration path.

## Publishing private work to public

When making a private repo public, the git **history** almost always still holds
pre-scrub secrets even after you scrub the current state. Never just flip the
repo public or push its history. Build a clean orphan export (no `.git`), scan
both the export and the pushed remote for leaks, and grow the public repo by
fast-forward, never by force-pushing a fresh history each time. Scan tracked
**code and fixtures**, not only data files — secrets hide in test fixtures and
hardcoded example lists.
