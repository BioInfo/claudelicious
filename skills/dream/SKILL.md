---
name: dream
description: "Consolidates memory across all layers (the durable memory files, the learnings log, project continuity) by pruning stale entries, merging duplicates, and resolving contradictions. Invoke when the user says 'dream', 'consolidate memory', 'clean up memory', 'merge duplicates', or after a heavy session that produced many similar entries. Different from per-correction capture (memory and the learning loop write new entries; dream cleans the corpus). Run periodically when memory feels noisy or after a multi-day push."
disable-model-invocation: true
context: fork
model: opus
---

# Dream: memory consolidation

A periodic maintenance pass across all memory layers. Defrag for context. The harness writes memory constantly during normal work (see [memory](../../docs/04-memory.md) and [the learning loop](../../docs/05-learning-loop.md)); dream is the janitor that keeps that corpus from rotting into noise. This is the "it cleans its own memory while you sleep" piece.

## The memory layers it sweeps

Adapt these to your own homes. The pattern is the point, not the paths.

| Layer | Holds | Format |
|-------|-------|--------|
| **Durable memory** | per-topic facts, corrections, project state, references | one file per fact + an index |
| **The index** | a one-line pointer per memory, loaded every session | a single capped file |
| **Learnings** | experience-based lessons with promotion targets | a rollup log |
| **Continuity** | per-session "what was I doing / next" journals | live + archive dirs |

The index is the one with a hard ceiling: it loads every session, so it has to stay short. Dream's main job is keeping that index lean while nothing of value is lost.

## When to run

- Explicitly, via `/dream`.
- When the memory file count or the learnings log crosses a size you have picked.
- On a periodic cadence (weekly or monthly).
- When memories feel cluttered or stale.

## Phase 1: orient

List the memory directory and count files. Read the index. Skim each file's frontmatter (name, description, type). Check the learnings log size. Note counts and any obvious bloat. Do not read full bodies yet.

## Phase 2: audit each memory

For every file, evaluate against five checks:

| Check | Action |
|-------|--------|
| **Stale?** | References something resolved, completed, or no longer true? Verify against current files/git if unsure. |
| **Contradicted?** | Does another memory or the current codebase contradict it? Fix or delete the wrong one. |
| **Duplicate?** | Another memory covering the same topic? Merge into one, delete the other. |
| **Ephemeral?** | A one-time event (a flight, a meeting, a deadline) now past? Archive or delete. |
| **Still useful?** | Would a future session benefit from knowing this? If not, delete. |

Decision framework: helps future sessions orient faster → KEEP. A behavioral rule the user confirmed → KEEP (these are durable). Describes a completed event → DELETE. Two memories overlap → MERGE into the better one. Uncertain → KEEP and flag for review.

## Phase 3: consolidate

For keepers: convert relative dates to absolute, update facts that changed (verify against source first), merge overlaps into a single file, fix frontmatter to match the body. For removals: delete the file and its index line. For merges: update the survivor with combined content, delete the absorbed file, update the index.

## Phase 4: index hygiene

Remove pointers to deleted files, add pointers for new ones, keep each line short, group by type, and stay under the ceiling. The index is a triage surface, not a content store.

## Phase 5: durable-store sweep

After the per-file pass, sweep the append-heavy stores (a decisions log, the learnings log). Remove entries older than a threshold that are fully resolved and no longer inform future work. Merge related entries. Keep anything that set an ongoing precedent. Archive rather than delete when uncertain; these stores are cheap to keep and expensive to lose.

## Phase 6: cross-layer dedup

Content that exists in two layers is the subtle bloat. A memory that duplicates a standing rule: delete the memory, the rule is canonical. A learnings entry that duplicates a memory with a richer "why": keep the memory. Resolve toward the single most useful copy.

## Phase 7: report

```
Dream complete.
  Files: X total (was Y). Deleted: N. Merged: N. Updated: N.
  Index: Z lines (was W).
  Durable stores: pruned N entries.
  Flagged for review: N (with reason).
```

## Rules

- NEVER delete a confirmed behavioral rule unless the user explicitly reverses it.
- NEVER delete anything the user asked to save.
- Verify against source files before marking something "contradicted".
- When merging, keep the more detailed version as the survivor.
- Do not create new memories during a dream pass; this is cleanup, not capture.
- Do not read session transcripts (too expensive, low signal). Skim frontmatter first; only open a body if something looks off.

## Why this is a good example

It shows that memory is not write-only. A harness that only ever appends turns its own context into noise. The discipline that keeps memory compounding instead of accumulating is a scheduled pass that prunes, merges, and resolves, with a hard rule against deleting confirmed knowledge. Same "more is not better" thesis as the [skills](../../docs/02-skills.md), applied to memory.
