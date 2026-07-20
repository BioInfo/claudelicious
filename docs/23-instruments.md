# 23 — Instruments

At width you stop reading the work. One person cannot read four lanes of output a day, and the whole
point of Part Two is that you do not have to. You read instruments instead: the checks, the health
signals, the green ticks that stand in for the work you are not looking at. Which means the instruments
have to be trustworthy, and the ways they lie are specific and worth knowing cold.

Part One's [hooks](03-hooks.md) and [wide-open](19-running-wide-open.md) docs built a deterministic floor
to guard against damage. This doc promotes that floor to a second job: guarding against false belief.
Damage you notice. A false green you do not, and at width a false green is the more dangerous of the two,
because it is the one you are trusting in place of your own eyes.

---

## An instrument that cannot fail certifies whatever you point it at

This is the sentence to keep. Before you believe any green result, ask what a broken check would have
shown, and if the answer is "the same green," the check told you nothing.

The story that teaches it: a search index's embedder was loaded, pinned to the GPU, showing full
utilization, and reporting healthy for three days. It was also returning a null result on every single
call. Every surface check passed, because every surface check asked "is it up," and it was up. None of
them asked "does the thing it produces make sense," which is the only question that would have caught it.
A health check that verifies presence and calls it health is an instrument that cannot fail. It will
certify a corpse as long as the corpse is warm.

The fix is not a better version of the same check. It is a different question. Validate what the thing
*produces*, not that it is running.

---

## Verify the artifact, not the exit code

There is a tiering of evidence, and it decides ties.

**Files and a live operational test** are ground truth. Read the row. Make the real request. Run the
actual query and look at what comes back. The artifact and its behavior do not lie.

**Logs** are second. They lag, and they only show what someone thought to log.

**Documents** are last, and they are the trap. A heartbeat file, a commit message, a changelog, a status
dashboard, and your own summary from an hour ago are all documents. They are claims about the work, not
the work. An exit code is a document too, and it lies in both directions: a command can fail and exit
zero, or do the job and exit nonzero on a warning. Gate on the file the command claims to have written,
never on the fact that it returned.

The shorthand: files beat logs beat docs. A memory that says "fixed" is a document, and it is the weakest
thing you own.

---

## Probe with an input that has actually failed

A check that only ever runs on easy input is a check tuned to pass. The canary that is always green is
decoration. When you build a verifier, feed it the case that broke last time, not a benign sample it will
sail through. A test suite full of inputs the system already handles measures your confidence, not the
system. The failing case is the one worth keeping in the harness.

---

## Put the watchdog where it cannot be fooled

A monitor's false-alarm rate is load-bearing, not cosmetic. A watchdog that cries wolf gets muted, and a
muted watchdog is worse than none, because everyone still believes something is watching. The most common
way to build a lying watchdog is to run it somewhere it can lose sight of its target for reasons that have
nothing to do with the target. A monitor on your laptop that alerts "the server is down" every time the
laptop sleeps is measuring your laptop, not the server, and after the third false alarm you will silence
the one signal you needed. Put the watchdog on the host it watches, so its only failure mode is the real
one.

---

## Silence that looks like success

The quiet version of a false green. A data collector wrapped in a bare catch-all returns an empty list
when the source is blocked, and "zero results" reads exactly like "nothing to report." A backup that
skipped its one real step still writes its success timestamp. Nothing errors, so nothing alerts, and the
gap is invisible until you need the thing that was never there.

The rule is to make the silent path loud. A source that drops to zero says so. A backup verifies the
artifact it produced, not that the command ran. Pair every job that can fail quietly with a check that
alerts on the quiet failure, and confirm the checker itself is alive. An alert you never tested is one
more instrument that cannot fail.

---

## Ship / scrub

- All of it is generic, and this is the doc to ship whole. The instrument-that-cannot-fail framing, the
  files-over-logs-over-docs tiering, probing with a real failing input, the watchdog placement rule, and
  making silent failure loud apply to any operator running any system they cannot watch by hand.
- The stories are illustrations, not configs. Scrub the specific index, the specific box, the specific
  job. The lesson is the shape of the lie, not the hardware that told it.
- This is the doc that makes the rest of Part Two safe. Autonomy you cannot verify is not autonomy, it is
  a guess you stopped checking.
