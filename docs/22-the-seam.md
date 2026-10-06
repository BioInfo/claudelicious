# 22 — The seam

A cookbook with a chef's hat on the logo earns this metaphor. In a real kitchen the chef de cuisine does
not cook every dish. They run the pass: the station where every plate stops for three seconds of expert
inspection before it goes out or gets sent back. Part One taught you to cook. The seam is you running the
pass.

It is the single interface where a fleet's judgment calls reach a human, and it deserves to be designed
like an interface, not left as whatever each lane happens to print. Get it right and one person can
oversee work they never read. Get it wrong and you are either a bottleneck or a rubber stamp, the two
[cockpit failures](21-lanes-and-the-cockpit.md).

---

## An escalation is a block a script can read, not a line of prose

When an autonomous lane hits a fork it cannot resolve, it has no one to ask, so it writes the fork down.
Where it writes it matters. A concern buried in the middle of a session's prose is a dropped item; nobody
scrolls four lanes of narrative looking for the one sentence that needed them. The fix is a fixed-format
block, the same shape in every lane, that a separate script reads and merges into one operator view.

The rule underneath: the thing an unattended agent cannot resolve has to land somewhere a *script* can
aggregate, not somewhere a human might happen to notice. If your escalations live only in prose, you will
miss one, and it will be the one that mattered. This happened once for real before the block existed,
which is why the block exists.

Each entry is one line: what the decision is, what the lane would do if forced to guess, and a marker if
it is time-sensitive. Not the whole story. The story is in the lane's cursor if you want it. The queue
carries the ask.

---

## Rank the queue, do not dump it

Four lanes surfacing everything they touched is a firehose, and a firehose gets skimmed, which is the
same as unread. The queue is ranked by one question: who can unblock this. The items only a human can
move go to the top. The items a human starts and the lane finishes come next. The things a lane already
handles and is only reporting do not belong in the queue at all; that is noise wearing a badge.

This is the [judgment budget](../PHILOSOPHY.md) turned into a mechanism. Your attention is the scarce
resource, so the queue spends it in order: the highest-value human move first, and the things that were
never yours to decide filtered out before they reach you.

---

## Silence by default, scaled up

The [always-on agents](11-always-on-agents.md) doc already argued that a good agent stays quiet when it
has nothing to say. The seam is that rule for a fleet. Four lanes do not produce four status reports. They
produce one short surface, and on a clean day that surface says almost nothing, because almost nothing
needed you. A cockpit that lights up every tick has taught you to ignore it, and an ignored seam is worse
than none, because you still believe it is watching.

The measure of a healthy fleet is a short queue. Not an empty one, a short one: the few things that
needed a human, and no more.

---

## Reversals surface now, wins can wait

Not everything in the queue moves at the same speed. A reversal, a failure, a lane that just did
something it should not have, surfaces immediately, unfinished, before you have the full picture. A win
can batch into the next roll-up. The asymmetry is deliberate. The cost of learning about a good outcome
an hour late is nothing. The cost of learning about a bad one an hour late can be the hour it took to
make it worse. Bad news travels first, and it travels raw.

---

## Ship / scrub

- The machine-readable escalation block, the ranked queue, silence-by-default at fleet scale,
  and reversals-first-wins-batch are all generic. Ship them.
- Scrub the escalation examples. That a lane escalates a genuine fork is the pattern; which forks your
  lanes escalate is your operation.
- The seam is only as honest as your reading of it. A ranked queue you skim is a firehose with extra
  steps. If you are not reading it, the problem is not the queue.
