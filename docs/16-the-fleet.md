# 16 — The fleet

The cookbook keeps saying the harness is wired around a homelab, and so far that has been an assertion.
This doc makes it concrete. You do not need five machines to run any of this; the single-laptop version
of every pattern works. But the architecture changes shape once work can land on the right machine
instead of the only machine, and understanding the roles is what lets you grow into it without a rewrite.

The principle: **assign each machine a role, make one of them canonical, and let work flow to whichever
one fits it.** The mistake is a pile of equal machines with no source of truth, which gives you sync
conflicts and no answer to "which copy is real."

---

## The roles

A mature fleet sorts into a handful of jobs. Yours might collapse several onto one box; that is fine.
The roles matter more than the count.

| Role | What it is | What runs there |
|------|-----------|-----------------|
| **Canonical workstation** | Where you actually work. The source of truth. | The vault, the skills, the full config, the password store. Interactive browser-driving (it has a display). Edits originate here. |
| **Always-on node** | A quiet box that never sleeps. | Scheduled jobs, the heartbeat agents, anything that has to run whether or not you are at the keyboard. Lightweight self-hosted services. |
| **GPU box** | The heavy-compute machine. | Local models, the embedding and reranking for the [second brain](08-second-brain.md), the search index, the model gateway, training and batch jobs. |
| **Edge node** | A small, cheap, low-power machine. | Lightweight services, a test environment, things that want to be on but not on the workstation. |
| **Production host** | A box that faces outward. | The public web services, the things real users hit, kept separate from everything personal. |

The split that does the most work is the first two. The workstation is where you think; the always-on
node is where the harness keeps running after you close the laptop. Push the scheduled jobs and the
agents off the workstation onto the always-on node, and your automation stops depending on whether your
laptop is awake.

---

## One machine is canonical

With more than one machine, the most important decision is which one is the source of truth, and the
answer should be boring and fixed, not "whichever was edited last." The canonical workstation holds the
real vault, the real skills, the real config. Everything else receives.

This matters because of a failure mode that looks like success. Two machines drift, each accumulates
edits, and a well-meaning sync flattens one into the other, silently dropping work. The fix is
directional sync: edits originate on the canonical box and flow outward; the downstream machines are
receive-only by default. When you do want a particular area to flow back from a particular machine,
that is a deliberate, named exception you open on purpose, not the default everywhere.

Source of truth is decided by designation and version history, never by file modification time. A
machine's clock is not an argument about which copy is real.

One hazard the directional rule does not fully cover: two live sessions editing the same shared file at
the same moment. A second session can silently overwrite a change you just made, and the service comes
back up green, so nothing tells you. Treat a shared file as something you never restore your own copy
over. Re-apply your change on top of whatever is there now, add only the files you touched, and confirm
by reading the result back rather than trusting that the write succeeded.

---

## What flows between them

Three kinds of traffic hold a fleet together:

- **Config and skills**, pushed from the canonical workstation outward, so every machine runs the same
  harness. Edit once, sync everywhere.
- **The vault**, replicated so the second brain and the agents on every machine read from the same notes.
  One-way by default, per the rule above.
- **Heartbeats**, the small success-timestamp files from [scheduled jobs](10-crons-and-scheduling.md),
  collected so one health check can see the whole fleet and alert when any job goes stale.

Address services on the fleet by a stable network name, not by `localhost`. A loop-back call assumes the
service is on the same box as the caller, and on a fleet it often is not. The session running on your
laptop and the service running on the always-on node are different machines; the call has to say so.

---

## Why bother

The payoff is not raw horsepower. It is that the harness stops being tied to one machine being awake.
The agents run on the always-on node. The models run on the GPU box. The public services run on the
production host. Your laptop becomes the place you think, not the place everything depends on, and you
can close it without anything stopping. That separation, more than any single machine's specs, is what
turns a personal setup into a system.

---

## Ship / scrub

- The role taxonomy, the canonical-source-of-truth rule, the directional-sync default, and the
  address-by-network-name rule are all generic. Ship them.
- Scrub every hostname, IP, and tailnet address. The roles are the lesson; your topology is yours.
- Do not ship your actual fleet map. Like the [skill list](02-skills.md) and the
  [job list](10-crons-and-scheduling.md), a full topology diagrams your whole operation. Ship the roles
  and a generic example.
