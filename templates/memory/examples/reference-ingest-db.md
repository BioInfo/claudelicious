---
name: reference-ingest-db
description: The widget ingest store — its location, the one live table, and the producer that writes it.
metadata:
  type: reference
---

The nightly widget ingest writes to a SQLite store at `<data-dir>/ingest.db`. The
only table consumers should read is `items` (id, source, fetched_at, payload).
The producer is `run-adapters.<ext>`, scheduled nightly; it dumps each source,
then upserts into `items`. A sibling file `ingest.db.bak` is a stale build
artifact from an earlier version — do not read it; it has no live writer.

Per-source freshness is a heartbeat file at `<state-dir>/ingest-<source>-last-success`
(epoch). A stale heartbeat means the producer did not run for that source.

See [[project-widget-pipeline]], [[feedback-heartbeat-whole-pipeline]].
