# 19 — Running wide open

Time to be honest about the permission posture, because it is a real choice and most write-ups dodge it.
I run my Claude Code with broad access to my own machines. Shell commands are open. The MCP servers are
open. File edits apply without a prompt. Long jobs run unattended while I am asleep. People see that and
assume it is recklessness. It is the opposite. It is a deliberate trade, and it only works because the
floor underneath it is built first. This doc is the case for the trade, and the guards that make it sane.

---

## Why open the throttle at all

Every permission prompt is friction, and friction is the thing that kills the compounding this whole
cookbook is about. That part is obvious. The part that is less obvious, and more important, is what
happens to *you* when the prompts are constant: you stop reading them. An agent that asks permission
forty times an hour does not make you safer. It trains you to hit approve without looking, which is
strictly worse than no prompt at all, because now there is a confirmation step that confirms nothing.

So the move is not "add more prompts." It is to remove the theater and replace it with a floor that does
not depend on me paying attention. Let the agent edit files and run commands freely, and put the safety
in deterministic code that fires whether or not I am watching. The prompt I keep is the one that means
something. The forty that did not, I delete.

---

## The real threat is not the one you fear

When people picture an agent with open shell access, they picture it typing `rm -rf /` by accident. That
is the wrong fear. At this permission level the realistic attack is not the agent fat-fingering a
destructive command. It is an **injected instruction**: text on a web page, in a repo file, or in an
[MCP response](18-mcp.md) that tells the agent to chain an allowed command into something that exfiltrates
a secret or deletes your work. The agent was not careless. It was following instructions it should never
have treated as instructions.

Design for that, and the guards almost write themselves. The question is not "how do I stop the agent from
making a mistake." It is "how do I stop a hostile instruction, arriving through a channel I trust, from
turning my open access into someone else's leverage."

---

## The floor that makes it work

Wide-open access on top of nothing is recklessness. Wide-open access on top of this is leverage. The
guards, roughly in order of how much they earn:

- **Deterministic hooks, not deny rules, for the things that must never happen.** A recursive delete is
  refused before it runs. A command that pipes the internet into a shell, or pairs a secret source with an
  outbound network call, or redirects the API to an external host, gets stopped for confirmation. A push
  is scanned for secrets first. These are code, in a [hook](03-hooks.md), because a written rule loses to
  an injected instruction and a deny list has enforcement limits. The hook is the floor; the deny list is
  a speed bump. Do not confuse the two.
- **Secrets never live in cleartext.** Every key, token, and credential routes through a password manager.
  This is what makes open file access survivable: even with the run of the disk, the agent (or an
  injection driving it) does not find a `.env` full of plaintext keys, because there is no such file.
- **Layered backups, so a mistake is recoverable, not terminal.** Open access is only sane if the worst
  case is "restore from this morning," not "it is gone." Versioned local snapshots plus an offsite copy
  turn a catastrophic loss into an annoying one.
- **A hard fence on anything that leaves the machine.** This is the line that makes the rest defensible.

---

## Wide open inside, fenced at the edge

The posture is not "trust the agent with everything." It is two different trusts, and keeping them
separate is the whole discipline:

- **Inside the machine, wide open.** Edit my files, run my commands, drive my tools, iterate all night.
  The cost of a mistake here is bounded by the backups, and the speed is worth it.
- **At the edge, fenced.** Anything that leaves the machine or cannot be undone stops for me. Sending an
  email or a message. Posting in public. Publishing or deploying. Anything irreversible or anything that
  moves money. The default for outbound and irreversible is ask, every time, no matter how trivial it
  looks, because that is exactly where an injection wants to push.

So the agent has the run of my laptop and almost none of my voice. It can rewrite a project and cannot
send a single message as me without a deliberate yes. That asymmetry is the design, not an accident.

---

## A word before you copy this

This is a personal-risk choice on personal machines that I back up and can restore. It is not a
recommendation to disable safety on a shared box, a work machine, or anything you cannot afford to lose
and rebuild. Calibrate the throttle to what you can recover from. The principle that generalizes is the
order of operations, not the specific setting: **build the floor, then open the throttle.** Safe is not
the slow way. Done right, with the deterministic guards carrying the load instead of your attention, safe
is the fast way.

---

## Ship / scrub

- The case for removing prompt-theater, the injection-not-fat-finger threat model, the deterministic-floor
  list, the wide-open-inside / fenced-at-the-edge split, and the build-the-floor-first principle are all
  generic. Ship them.
- Ship this doc with its caveat attached. The posture is defensible *with* the guards and the backups and
  the secret hygiene; lifted without them, it is just the reckless version everyone assumes it is.
- Scrub any specific allow/deny entries or hook paths; those are in [settings](17-settings.md) and
  [hooks](03-hooks.md) and are yours to adapt, not to copy blind.
