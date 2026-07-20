# 07 — Session search (mneme)

[Continuity](06-continuity.md) hands you the last session on this thread. It does not answer the other question you ask constantly: "when did I solve this before?" Your past sessions are a corpus. Months of decisions, fixes, and dead ends, sitting in transcript files, unsearchable. **mneme** makes them searchable.

It is a second brain for your own work. Point a natural-language query at it and it finds the session where you debugged the same thing in March, even though you do not remember the words you used at the time.

mneme is open source (MIT). The pipeline below is the whole thing.

---

## What it indexes

Claude Code writes one JSONL transcript per session under `~/.claude/projects/<encoded-path>/<uuid>.jsonl`. mneme reads those. Each line is a record, and the parser keeps only the parts worth searching:

| Record type | Kept | Dropped |
|-------------|------|---------|
| `summary` | the summary text | |
| `user` | plain-text messages | tool-result blobs |
| `assistant` | the text it wrote | thinking blocks, tool-use calls |

Content is filtered to a sane length (roughly 20 to 2000 characters), so short noise and giant tool dumps do not pollute the index. What is left is the actual conversation: what you asked, what it concluded.

---

## The pipeline

```
session JSONL transcripts
        │  parse: keep summary/user/assistant text, drop tool noise + thinking
        ▼
        chunks
        │  embed: a local sentence-embedding model, asymmetric
        │         (documents and queries get different prefixes)
        ▼
   LanceDB table   ── id, session_id, project_path, timestamp,
        │              chunk_type, content, vector[768]
        │  incremental: an mtime state file means only new/changed
        │               transcripts get re-embedded
        ▼
   + a full-text (BM25) index on the content column
```

Indexing is incremental. A state file records the modification time of every transcript already processed, so a nightly run only embeds what changed. It saves state after each batch, so a crash mid-run loses nothing.

This runs on a timer (a nightly scheduled job, see [10](10-crons-and-scheduling.md)). You wake up and last night's sessions are queryable.

---

## Search

Four modes, increasing in quality and cost:

| Mode | How it ranks |
|------|--------------|
| `vector` | cosine similarity on the embedding |
| `fts` | BM25 keyword match |
| `hybrid` | both, merged with reciprocal-rank fusion |
| `rerank` | hybrid recall, then a cross-encoder reorders the top candidates |

The default is `rerank`. It pulls a wide candidate set with hybrid retrieval, then a cross-encoder scores each candidate against the query with full context, which is more accurate than similarity alone. Results come back grouped by session, so you get "here are the four sessions that touched this," not a scatter of disconnected chunks.

A small skill wraps the query so you can call it inline mid-session: ask "have we hit this before," get the past sessions, keep working.

---

## One index, not one per machine

If Claude Code runs on more than one machine, session search wants to be one index, not one per host. It is tempting to install the pipeline locally on each machine and let each one embed its own transcripts. Do not. Left alone, per-host indexes drift apart: one machine gets indexed reliably because it runs the nightly job, a second has the search skill installed but no engine actually running behind it, and a third's sessions accumulate for months and are never embedded at all. Nobody notices until a query that should surface an obvious past session comes back empty, and the honest answer is that machine's sessions were never in the index to begin with.

The fix is structural, not procedural: run the indexing pipeline and the vector store on one machine, and have every other machine query it as a thin client over the network. There is exactly one place that embeds, one place that stores, and every host reaches the same answer to "have we hit this before," regardless of which machine you happened to be on when you solved it.

---

## Why this is separate from the second brain

mneme and the [second brain](08-second-brain.md) are the same idea pointed at two different corpora. mneme indexes your **sessions** (what you and the agent did). The second brain indexes your **vault** (your notes, memories, learnings, docs). Same retrieval stack in spirit, two stores, because "when did we work on this" and "what do I know about this" are different questions. Keeping them separate keeps each index clean and each query sharp.

---

## The principle

Your transcripts are not exhaust. They are a searchable record of every problem you have already solved. The cost of making them queryable is one parser that knows which records to keep, one embedding model, one vector store, and a nightly job. The payoff is that the harness stops re-solving things, because it can find the time it solved them before.

---

## Ship / scrub

- mneme itself is MIT and built to be generic. The config uses a `~`-relative db path and a swappable embedder. Point it at your own transcript directory and run it.
- The only thing to genericize when sharing your setup is the scheduled-job label and any absolute paths in the config example.
- The one-shared-index / thin-client pattern is generic. Pick whichever one machine in your setup is always on, and point the rest at it.
- Your transcripts contain everything you have ever typed at the agent. The index is local. Do not ship the `.lance` store or the transcripts.
