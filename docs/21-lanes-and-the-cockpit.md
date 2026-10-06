# 21 — Lanes and the cockpit

The [charter](20-the-autonomy-charter.md) says what one lane may decide. This doc is about the shape
around it: how a single project splits into several lanes that run at once, how they stay out of each
other's way, and where you sit while they do. It is an org chart for a company of one.

You do not need many lanes to use any of this. Two is enough to learn on, and two is where the lessons
show up. The reference setup runs four; the pattern is the same at two and the failure modes are easier
to see. Grow into it, do not start there.

---

## What a lane owns

A lane is one autonomous harness pointed at one slice of a larger project. Comms is a lane. Modeling is
a lane. Each owns three things and nothing else.

**A charter**, its boundary, per [doc 20](20-the-autonomy-charter.md).

**A cursor**, its own [continuity file](06-continuity.md), so the lane resumes cleanly across sessions
without reading anyone else's state. The cursor is private to the lane. A resuming session reads its
own cursor and knows where it left off.

**An inbox**, a place other lanes drop work for it. Nothing else writes to a lane's files. If comms
needs something from modeling, it does not reach into modeling's cursor, it leaves a note in modeling's
inbox and modeling picks it up on its next tick.

The discipline is ownership. One writer per file. Two lanes editing the same state is the fastest way
to lose work you thought was saved, and it looks like success right up until you diff.

---

## Lanes coordinate through files, not messages

There is no message bus between lanes. A handoff is a markdown note the receiving lane reads on its next
session. This is the same vault-is-the-hub rule the [second brain](08-second-brain.md) already runs on,
now doing organizational duty: the shared files are how independent workers agree on state without a
live connection between them.

Files beat messages here for a plain reason. A message assumes both ends are awake at the same moment,
and lanes are not. One recycles while another sleeps while a third is mid-task. A note in an inbox waits
patiently and survives a restart. A dropped message does not. Coordinate through the thing that persists.

---

## The cockpit runs no loop

Your session is the cockpit, and it is defined by what it does not do: it runs no loop of its own. It
reads the escalations every lane surfaced, shows you the health of the fleet, rules on what needs a
human, and stages the next launch. Then it stops. It does not do lane work.

That last rule is the whole discipline, and it fails in two directions.

The **bottleneck operator** does lane work from the cockpit. A lane blocks on a decision, and instead of
fixing the charter so the lane can decide it next time, you just decide it, by hand, again and again. You
have un-delegated the thing you built to run without you, and now you are four workers with extra steps.
The fix is a charter edit, not a faster you.

The **rubber-stamp operator** approves without reading. The queue gets long, the items look routine, and
you start clicking yes. That is the [prompt-theater](19-running-wide-open.md) the wide-open doc warned
about, reborn one level up: a permission surface you are no longer actually inspecting. A seam you rubber
stamp is not a seam.

Both failures are about the same line. The cockpit inspects and rules; it does not execute. When you
catch yourself doing a lane's work, that is the signal to fix the lane.

---

## The thing that drives the lanes is not a lane

Something has to wake each lane, run its tick, and recycle it when its session gets long. That driver
must not itself be a Claude session. It is dumb: a plain script that walks a list of lanes on a cadence
and, for each, starts it, resumes it, or recycles it. A supervisor written as "just another agent" would
eventually confuse itself for a lane, or worse, kill the thing it was supposed to be managing. Keep the
conductor outside the orchestra.

Two rules keep the driver safe.

**One dispatcher, ever.** Exactly one process drives a given piece of shared state. A second scheduler
added "for redundancy" is not a backstop, it is two writers on one surface, and it will collide with a
live session and corrupt state while every status check stays green. Redundancy on a write path is the
bug, not the safety net.

**Recycle on a measured inflection, not the clock.** A lane is a chain of sessions, not one long one. You
end a session and hand the next a clean cursor when a real signal says to, usually a context-fill ceiling,
not after N minutes. A session recycled by the clock throws away useful context or holds a bloated one;
a session recycled by fill does neither.

---

## Two modes, one boundary

A lane runs in one of two modes, and knowing which changes its behavior but never its permissions.

**Interactive**: you are in the seat, the lane works with you, and an ambiguous fork is a question it asks
you directly.

**Autonomous**: the lane runs unattended under the driver, and there is no one to ask. An ambiguous fork
does not stall the lane waiting for an answer that is not coming. The lane writes the fork into its
escalation block, moves to other unblocked work, and lets the cockpit surface the question later.

The line the lane may not cross is the same in both modes. What changes is only how it behaves at the
line: interactive, it asks; autonomous, it defers and keeps working. A harness that widens its own
permissions when nobody is watching is the exact failure this forecloses. Unsupervised is a reason to be
more careful at the boundary, never a license to move it.

---

## Ship / scrub

- The lane-owns-three-things model, files-not-messages, the cockpit-runs-no-loop rule with its two
  failure modes, the driver-is-not-a-lane rule, single-dispatcher, and the two-modes-one-boundary rule
  are all generic. Ship them.
- Teach at two lanes. Note that a bigger fleet works the same way, and resist showing a reader your real
  lane map, the same reason the [fleet](16-the-fleet.md) doc will not print its machine topology.
- Scrub the lane names. What each lane does is your operation; that it is a chartered lane with a cursor
  and an inbox is the pattern.
