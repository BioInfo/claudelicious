# 10 — Crons and scheduling

A harness earns its keep when it does things you did not have to start. That happens at two layers: inside Claude Code, and on the machine the harness runs on. They solve different problems, and you want both.

---

## Inside Claude Code

Two built-in mechanisms, for two different needs.

**Scheduled cloud routines.** Distill a session into a single repeatable task and hand it to a cloud agent that runs it on a cron. The discipline is that the task must be self-contained: a future run has no memory of this session, so the prompt has to carry every path, every success criterion, every constraint. Use it for recurring reports, audits, "every Monday do X," and for one-shot future reminders ("at 3pm, check the deploy"). To change a routine, update it by its id; do not recreate it.

**In-session loops.** Run a prompt or a slash command on an interval within the current session, to poll for something or repeat an action ("check the build every five minutes"). This lives and dies with the session. It is the right tool when you want to watch something now, not stand up a persistent job.

The split: a cloud routine persists after the session ends; an in-session loop does not. Reach for the routine when the work should outlive the window.

---

## On the machine

For anything that has to run whether or not Claude Code is open, the host scheduler owns it. On macOS that is LaunchAgents; on Linux, cron or systemd timers. This is where the real automation lives: nightly indexers, backups, health checks, sync jobs, the always-on agents.

A healthy setup has a lot of these, grouped by job:

| Category | Examples |
|----------|----------|
| Harness infra | index sessions ([mneme](07-session-search-mneme.md)) nightly, sync skills across machines |
| Memory and search | reindex the vault into the [second brain](08-second-brain.md) |
| Backups | scheduled snapshots, remote pulls |
| Always-on agents | the [heartbeat agents](11-always-on-agents.md), kept alive |
| Health | freshness checks, watchdogs, mount persistence |

Two distinctions matter. A job that should run on a schedule and exit uses a calendar interval and no keep-alive. A process that should always be running (an agent, a local model server) uses keep-alive, so the scheduler restarts it if it dies.

---

## The heartbeat pattern

The pattern that ties scheduled jobs together is the success heartbeat. A job writes a timestamp file on successful completion:

```bash
# at the end of a job, only on real success
date +%s > ~/.local/state/<job>-last-success
```

A separate health-check job reads those timestamps and alerts if any is stale beyond a threshold. This is how you catch a backup that has been silently failing for a month, or an indexer that stopped running. The job that fails does not tell you; the freshness check does.

One rule makes this trustworthy: **gate the heartbeat on the whole pipeline, not just the last command.** If a job dumps a database and then runs a backup, a swallowed failure in the dump still lets the backup succeed on the (stale) files, the heartbeat writes, and the monitor shows green while the data was never captured. Set a success flag, flip it to zero on any step's failure, and write the heartbeat only if the flag survived. A green heartbeat has to mean every step worked.

---

## Two operational gotchas worth knowing

These cost real time to learn the hard way.

**Restarting a lock-guarded keep-alive agent.** Do not hard-kill it. A force-restart can terminate the process while it still holds its lock; the keep-alive respawn then sees a fresh lock and exits clean, leaving the agent silently dead and looking like a clean exit. Use a plain restart, and if it will not come up, confirm no live worker, clear the stale lock, then start it.

**The scheduler's minimal environment.** A scheduled job runs with a bare PATH. A script that calls a tool by bare name (a formatter, a secrets manager, anything in a non-standard location) dies with "command not found," even though it works fine in your shell. Set the PATH explicitly in the job definition, and absolute-path the critical calls. An exit code of zero is not proof of success when the failing step was wrapped in a try/except.

---

## Ship / scrub

- The two-layer model, the schedule-vs-loop distinction, the keep-alive-vs-interval rule, the heartbeat-gating pattern, and both gotchas are all generic. Ship them.
- Scrub the job labels (`com.<you>.<job>`), the script paths, and any personal agent names.
- Do not ship your actual job list; it maps your whole operation. Ship the patterns and a couple of generic examples.
