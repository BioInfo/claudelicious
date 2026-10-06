---
name: feedback-heartbeat-whole-pipeline
description: Gate the success heartbeat on the whole pipeline, not just the last step, or a green light hides an uncaptured dump.
metadata:
  type: feedback
---

When a job has a pre-step (a DB dump, a fetch) before its main work, gate the
success heartbeat on the WHOLE pipeline, not just the last step. Set an ok flag,
flip it to 0 on any step failure (check both the exit code and that the expected
artifact exists and is non-empty), and write the heartbeat only when the flag is
still 1. A green heartbeat must mean every step succeeded.

**Why:** A nightly job dumped a DB, then archived files. The dump failure was
swallowed (`... || log 2>/dev/null`), so the archive step still succeeded on the
files that were there, the heartbeat wrote, and the freshness monitor showed
green — while the DB was never captured. The gap was invisible for the job's
whole lifetime because the one signal anyone watched (the heartbeat) only proved
the last step ran.

**How to apply:**
1. `OK=1` at the top; after each step, `[ $? -eq 0 ] && [ -s "$artifact" ] || OK=0`.
2. Write the heartbeat only inside `if [ "$OK" = 1 ]`; else log "HEARTBEAT WITHHELD".
3. Pair every job with a freshness check that *alerts*, not just logs. A backup
   nobody is told failed is a backup that failed.

See [[reference-ingest-db]].
