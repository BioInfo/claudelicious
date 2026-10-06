# 15 — Loops and autonomy

[Scheduling](10-crons-and-scheduling.md) answers "do this at a fixed time." Loops answer something
different and more interesting: "keep going until the work is done." A loop is the smallest unit of
autonomy, the place where the harness stops waiting for your next prompt and starts driving itself
toward a goal. This doc is about the three shapes a loop takes and the one experiment that shows why
they matter.

---

## The three shapes

**The fixed-interval loop.** Run a prompt or a slash command every N minutes: poll a build, watch a
log, re-check a status until something flips. It lives and dies with the session, and it is the right
tool when you want to watch something *now* rather than stand up a persistent job. Simple, bounded,
disposable.

**The self-paced loop.** Hand the harness a task and let it decide its own cadence. Instead of a fixed
interval, it works, judges whether it is done, and either continues or schedules its own next wake-up.
This is the shape for open-ended work where you cannot know in advance how many passes it will take:
keep finding bugs until two rounds come back clean, keep refining until a quality bar is met.

**The wake-up.** The harness can schedule precisely when to resume, which turns a loop from a busy
spin into a patient watch. The detail that makes this efficient is unglamorous and real: the prompt
cache has a short lifetime, so waking inside that window is cheap and waking after it pays a full
re-read. A loop that polls a remote job every thirty seconds and one that checks back in twenty
minutes are different animals, and choosing the interval to match what you are actually waiting for
is most of the craft. Do not poll every minute for something that changes every hour.

The thing to internalize: a loop is not a timer. A timer fires on the clock. A loop fires until a
condition is met, and the condition, not the clock, is what you are designing.

---

## The night a loop earned its keep

The case that makes this concrete. A research-loop pattern, taken almost verbatim from a public
experiment, two lines of configuration changed, pointed at a GPU box and left running overnight. By
morning it had run a hundred and fifty-one experiments and beaten its baseline by better than twenty
percent.

The result was good. The insight underneath it was better, and it was sitting in the logs. The machine
had a hundred and twenty-eight gigabytes of GPU memory available, and the loop had discovered that the
best configuration used about six. That is a hardware-tuning result no one in the room would have
guessed, and no one was going to hand-run a hundred and fifty-one trials to find it. The loop did,
unattended, for the cost of electricity.

The pattern generalizes past GPUs, and the generalization is the actual takeaway:

> **Change. Measure. Decide. Repeat.**

Any problem where you can define what *better* means and measure it cheaply is a candidate for a loop.
A kernel parameter, a piece of copy, an experiment design, a prioritized list. The autonomy is not the
point. The measurable, self-correcting iteration is. Give a loop a clear target and a cheap measurement
and it will out-patience any human.

---

## From loop to agent

A loop that survives the session becomes an agent. The progression is natural: a self-paced loop that
keeps its own state, wakes on a heartbeat, does a slice of work, and writes the result back to the
[vault](08-second-brain.md) is most of the way to a persistent worker. The difference between "a loop
I started" and "an agent that runs" is mostly durability: where the state lives, whether it survives a
restart, and whether it knows when to stay quiet. That last part matters more than it sounds. An agent
that reports every heartbeat is noise. One that acts when there is something to do and says nothing
when there is not is a colleague. The [always-on agents](11-always-on-agents.md) doc picks up there.

---

## Guardrails

Autonomy without brakes is how you wake up to a surprise. Three that pay for themselves:

- **A stop condition that cannot be skipped.** A loop with a fuzzy "until it seems done" runs forever.
  Give it a hard ceiling: a max number of rounds, a budget, a count to reach. The clock is the backstop
  even when the condition is the goal.
- **No silent truncation.** If a loop caps its own work (top-N, no-retry, sampling), it should say so
  in its output. A loop that quietly stopped looks identical to one that finished, and that ambiguity
  is where trust dies.
- **Cost awareness on every wake.** A loop that wakes too often, or holds an expensive resource between
  wakes, is a slow leak. Match the cadence to the thing you are waiting for, and release what you are
  not using.

---

## Ship / scrub

- The three shapes, the until-a-condition framing, the Change-Measure-Decide-Repeat generalization,
  and the three guardrails are all generic. Ship them.
- The overnight experiment is a true story; tell it as an illustration, not as a config to copy. The
  specific GPU, the experiment harness, and the numbers are one person's run.
- Scrub any concrete wake-up intervals tuned to your own infrastructure. The interval-matches-the-wait
  principle ships; your exact thirty-second-versus-twenty-minute choices do not.
