---
name: project-widget-pipeline
description: Rebuild of the nightly widget ingest — phase 2, adapter live, scheduler still TODO.
metadata:
  type: project
---

**Goal:** Replace the old monolithic widget importer with a per-source adapter
pipeline that writes one normalized store, so a single bad source can't stall
the whole run.

**Status:** Phase 2. The adapter framework and the first three source adapters
are live and have seeded the store by a manual run. The recurring scheduler and
the per-source freshness monitor are not wired yet.

## Done

- Adapter interface + base class; sources A, B, C ported.
- Normalized `items` table in the ingest store (see [[reference-ingest-db]]).
- One manual full run; store seeded and verified.

## Open

- Wire the scheduler so the producer runs nightly. The seed run is a one-off —
  until this is scheduled, the store goes stale silently the moment the manual
  run is forgotten. (This is the trap [[feedback-heartbeat-whole-pipeline]] warns
  about: committing the producer is necessary, not sufficient.)
- Add the per-source heartbeat + an alerting freshness check.
- Port the remaining sources.

## Decisions / gotchas

- One store, one `items` table — consumers never touch per-source intermediate
  files. Decided to keep the old `.bak` file out of the read path entirely.
