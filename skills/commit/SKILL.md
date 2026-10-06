---
name: commit
description: >
  Create a well-formatted git commit using conventional-commit format. ALWAYS
  invoke when the user says "commit", "commit this", "make a commit", or asks to
  save work to git. NOT for pushing (that has its own gitleaks gate) and NOT for
  staging review.
model: sonnet
allowed-tools: Bash, Read, Grep
disable-model-invocation: false
---

# commit

A process-encoding skill: the steps for a good commit are always the same, so
this makes them one word. It does NOT push — pushing is a separate, gated action.

## Procedure

1. **See what changed.** `git status` and `git diff` (staged and unstaged). If
   nothing is staged, look at the unstaged changes to decide what belongs in this
   commit.
2. **Group, don't dump.** If the changes are several unrelated things, say so and
   propose splitting into more than one commit rather than one mixed commit.
3. **Stage** the files for this commit (`git add <paths>`), not a blanket
   `git add -A` unless everything genuinely belongs together.
4. **Write the message** in conventional-commit form:
   `type(scope): summary` — e.g. `fix(auth): retry on expired token`.
   Types: feat, fix, docs, refactor, test, chore, perf. Keep the summary under
   ~70 chars, imperative mood. Add a body only when the *why* is not obvious from
   the diff.
5. **Commit.** Show the resulting `git log -1 --stat` so the user sees what landed.

## Notes

- Do not push. If the user wants to push, that is a separate step and runs the
  secret-scan hook first.
- Do not invent a scope. If the change has no clear scope, omit it:
  `docs: fix broken link`.
- Match the repo's existing commit style if it clearly differs from the above
  (look at `git log --oneline -10` first).
