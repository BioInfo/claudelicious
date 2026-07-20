# 20 — The autonomy charter

*Part Two: Running the Pass.* The first arc of this cookbook built one harness that knows you and runs
while you sleep. The docs from here on are about the threshold after that: the day you are running
several of them at once, and the scarce resource stops being the model's attention and becomes yours.

The charter is where that begins. It is a plain markdown file that answers one question for a working
agent: what may you decide on your own, and what do you bring to me. Write that down and an autonomous
lane is a system. Leave it in your head and it is a series of judgment calls you have to be awake for.

---

## Why the boundary gets written, not felt

A single harness with you in the room needs no charter. You are the boundary. You see the plan, you
approve the risky step, you catch the wrong turn. That does not scale to four lanes running in parallel
while you sleep, because you cannot be the boundary for four things you are not watching.

The instinct is to make the unattended agent cautious: ask before anything risky. That instinct
recreates, one level up, the failure the [attention budget](../PHILOSOPHY.md) already named. An agent
that escalates everything has handed the whole load back to you. Four lanes that each ask ten questions
a day is forty interruptions, and forty interruptions is not a fleet, it is a group chat you are losing.

So the charter is the same move the harness makes on the model, made on the human. The harness keeps
the model's standing context small so attention lands where it is needed. The charter keeps the
operator's decisions small so judgment lands where it is needed. Load the human only when the moment
calls for it, and let the lane handle the rest under a boundary it already knows.

---

## What a charter contains

One file per lane. Four parts, in this order.

**The loop contract.** The handful of steps every lane runs on every tick, stated once at the top:
sense what changed, find the highest-value unblocked work, do anything inside the AUTO boundary with no
gating, coordinate any cross-lane handoff, surface what belongs to the human, and exit. The last step is
the one people leave out and the one that pays. If there is no high-value work this tick, the lane says
so in one line and stops, rather than idling to the next wake. A loop that spins on nothing is a slow
leak with a heartbeat.

**The AUTO list.** The classes of work the lane does without asking. Be concrete. "Additive edits to a
file it owns" is a class. "Fix a broken link, a stale date, a wrong number in a doc it is already in" is
a class. An AUTO item is reversible, low blast radius, and something the lane can verify itself.

**The ESCALATE list.** The classes that always come to you. Anything that sends, posts, publishes, or
deploys. Anything that spends real money. Anything that changes a standing rule or a boundary. Anything
irreversible. A genuine preference fork where the lane has no signal about what you would want. These
are not calls the lane makes carefully. They are a fixed line it does not cross.

**The ledger.** A dated, append-only log of every time the boundary moved, one line each. "Widened lane
X to auto-approve its own doc edits, two weeks clean." "Pulled Y back to escalate after it posted
without a read." The ledger is what turns a charter from a vibe into a contract. The boundary is
supposed to move over time. The ledger is what makes that auditable instead of merely remembered.

---

## The three rules that keep it honest

**Proceed at about ninety percent, ask below it.** When the lane is roughly nine in ten sure what you
would say, it proceeds and states the assumption it made. Below that, it asks. An agent that asks when
it is ninety-five percent sure is friction you pay for nothing. An agent that proceeds when it is sixty
percent sure is a liability you find out about later. The number is a calibration, not a law, but naming
it stops the lane defaulting to either timid or reckless.

**A grant of the channel is not a grant of the call.** This one sentence prevents more autonomy
incidents than any other. "Handle the mail," "run the sweep," "steer the doc through your comments" name
where a decision travels. They do not name who makes it. Widening who *speaks* is not widening who
*decides*. A lane told to carry something to a partner has the channel, not the authority to commit you
to it. Nearly every autonomy mistake traces to blurring that line, and reading the instruction for its
object first is the defense.

**The boundary is earned outward.** Start every lane narrow. A lane that runs clean for a stretch earns
a wider charter, logged. A lane that escalates something the charter should have covered, or proceeds on
something it should have escalated, gets the charter edited, not scolded. The fix is at the source, the
same discipline the [learning loop](05-learning-loop.md) applies to a skill. An agent that keeps
bringing you the same decision is telling you the charter has a hole. Widen it, and stop being asked.

---

## Worked example: a charter skeleton

Generic on purpose. Substitute your own lanes and classes; the shape is the lesson.

```markdown
# AUTONOMY — <lane name>

## Loop contract (every tick)
1. Sense: what changed since last tick.
2. Find: the highest-value unblocked work in this lane.
3. Do: anything on the AUTO list, no gating.
4. Coordinate: post any cross-lane handoff to the shared inbox.
5. Surface: write anything on the ESCALATE list to the human queue.
6. Exit: if there is no high-value work, say so in one line and stop.

## AUTO (do without asking)
- Additive edits to files this lane owns.
- Mechanical fixes: stale dates, dead links, wrong numbers in a doc already open.
- Research, drafting, analysis that stays inside this lane.

## ESCALATE (always bring to the human)
- Anything that sends, posts, publishes, deploys.
- Anything that spends money.
- Any change to a standing rule, a boundary, or another lane's state.
- Anything irreversible. Any preference fork with no signal.

## Boundary ledger (append-only, one line each, dated)
- 2026-07-20  Created narrow. Only additive edits to own files auto.
```

A copyable version lives in [`templates/AUTONOMY.md.template`](../templates/AUTONOMY.md.template).

---

## A cheap sense, an expensive judgment

One texture worth stealing. The sense step at the top of the loop does not need the strong model. Run it
on the fast one and have it return a compact verdict: idle, or escalate with a short list. The reasoning
model only engages when the cheap pass finds something. A clean idle tick then costs almost nothing,
which matters when a lane wakes many times a day and most wakes have nothing to do.

This is the same cheap-triage, expensive-judgment split the
[subagents](14-subagents-and-workflows.md) doc teaches for forked work, applied one level up at the loop
tick. The pattern recurs at every level of the harness. Name it once and you will see it everywhere.

---

## Ship / scrub

- The four parts of a charter, the loop contract with its exit step, the three rules, and the
  cheap-sense split are all generic. Ship them.
- The ninety-percent number is a calibration, not a constant. Ship the framing and let the reader pick
  their own line.
- Never ship a real charter. A live AUTONOMY.md encodes the actual work of an actual operation: a
  partner's name, a company's priorities, which lane touches which system. It is one search-and-replace
  from publishing your org chart. Ship the shape and the generic skeleton above, the same rule the
  [always-on agents](11-always-on-agents.md) doc applies to an agent's identity file.
- This layer is weeks old and still settling. If yours is too, keep the boundary narrow and let the
  ledger show what it has earned. A charter records the trust you have tested, not the trust you hope for.
