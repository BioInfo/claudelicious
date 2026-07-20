# 11 — Always-on agents (Pulsar)

Everything so far runs when you are at the keyboard. The last layer runs when you are not. An always-on agent wakes on a timer, does a slice of work, and goes back to sleep. The reference here is **Pulsar**, a persistent agent that acts as a chief of staff: it watches the calendar, the inbox, the homelab, and your own messages, and surfaces only what needs you.

The thing that makes Pulsar useful is not that it is always running. It is that it is almost always silent. An agent that posts "all clear" every thirty minutes is noise. An agent that speaks only when something changed is a colleague.

---

## The anatomy

Pulsar is not a custom runtime. It is a headless Claude Code session (`claude -p`) launched on a schedule, with the full skill and tool set available. Six files and one timer:

```
a LaunchAgent (StartInterval)  ──►  pulse.sh
                                      │
                                      ├─ classify the pulse type
                                      ├─ guard: lock file, quiet hours, failure count
                                      ├─ build the prompt for this pulse type
                                      └─ claude -p  --append-system-prompt-file SYSTEM.md
                                                    --allowedTools <set>  --max-turns N
SOUL.md       identity, values, defaults
HEARTBEAT.md  per-pulse routing (what to check, in what order)
CONTEXT.md    cross-pulse state (travel, deadlines, last pulse summary)
TODO.md       the work queue
```

The timer fires `pulse.sh`. The script decides what kind of pulse this is, guards against the failure modes, composes a prompt, and hands off to a real Claude Code session that can read the vault, invoke any skill, and spawn subagents.

---

## The pulse, step by step

1. **Classify.** Not every wake-up is equal. A pulse triggered by you posting a message gets more turns than a routine 3am check. The script reads the situation (did you message recently, is it the first pulse of the day, is it a weekday) and sets a pulse type and a turn budget. This is progressive disclosure applied to an agent: load only the routine the moment calls for.

2. **Guard.** Three guards, all in the shell before any model call:
   - a **lock file** so two pulses never overlap (and a stuck pulse gets killed after a timeout)
   - **quiet hours** so it does not burn tokens or post at 3am unless you triggered it
   - a **failure counter** so three failed pulses in a row send you one alert, instead of failing silently forever

3. **Work.** The model reorients (what time is it, what is in CONTEXT.md, did you message), runs the routine for this pulse type (calendar, overdue items, homelab health), and does at most one slice of proactive work if nothing urgent is pending. Most routine pulses do nothing visible.

4. **Wrap.** It appends a one-line summary to CONTEXT.md so the next pulse has continuity, and writes to durable memory only for genuinely new facts. Then it stops.

5. **Speak only if there is something to say.** The default output is silence. No status posts, no narrating its own existence. It writes when something changed or needs you.

---

## The pieces that make it work

**SOUL.md** is identity: who this agent is, what it values, what it does by default. Stable, rarely edited.

**HEARTBEAT.md** is behavior: the routing for each pulse type, kept lean and branching, so a routine pulse reads a few lines and a heavy pulse loads more. Same attention-budget logic as everything else.

**CONTEXT.md** is state. It is how the agent has cross-pulse memory without a custom store: each pulse appends a line, the next pulse reads it. Travel, deadlines, the thread it was on. Plain markdown, same as the rest of the harness.

**A bridge process** (optional) keeps a chat channel live between scheduled pulses, so when you message the agent, it wakes immediately instead of waiting for the next timer.

---

## The pattern generalizes

Pulsar is a chief of staff, but the shape is reusable for any always-on agent:

```
a timer  +  a classifier shell  +  a heartbeat routing file
         +  a soul (identity)    +  a context file (state)
         +  silence as the default output
```

A research agent, a monitoring agent, an ingestion agent: same skeleton. The scheduled-job mechanics (LaunchAgent, lock files, the kickstart gotchas) are in [crons](10-crons-and-scheduling.md). The difference between a cron job and an always-on agent is that the agent reasons about what to do each beat, instead of running a fixed script. That is the whole point of putting a model on the heartbeat.

---

## From one agent to a squad

Once one agent runs this way, more is a copy-paste and a different SOUL. The reference setup runs a
small squad of named agents, each on its own heartbeat with its own role: one watches research, one
handles a specific project, one keeps the others honest. They are not a custom multi-agent framework.
Each is the same `claude -p`-on-a-timer skeleton above, and they coordinate the only way the rest of
the harness does, through shared files in the vault. One agent writes a note, another reads it on its
next beat.

The detail that surprises people is the cost. A squad of around eight agents, each waking on its own
schedule and doing real work, runs for less than the price of a couple of lunches a month. The barrier
to standing up a small staff of agents is not money and it is not a special runtime. It is the
discipline to give each one a narrow role and the silence-by-default rule, so eight agents produce
signal instead of eight times the noise.

That squad is still, mostly, watching. Each agent wakes, checks its corner, and stays quiet. The next
threshold is when a member stops being a checker and starts being a worker with a written boundary:
something that decides and acts on its own, inside a charter, while you are not looking. That is where
the second arc of this cookbook begins. See [the autonomy charter](20-the-autonomy-charter.md) and
[lanes and the cockpit](21-lanes-and-the-cockpit.md).

---

## Ship / scrub

- The anatomy (timer plus classifier shell plus heartbeat plus soul plus context, silence-default) is generic and is the valuable thing to copy.
- A real agent's SOUL.md and CONTEXT.md are personal: they hold your state, your channels, your priorities. Describe the pattern; do not ship the files.
- Scrub channel IDs, host names, and the agent's personal context before sharing any of its config.
