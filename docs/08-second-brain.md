# 08 — The second brain

[mneme](07-session-search-mneme.md) searches your sessions. This searches everything else: the vault. Your notes, your memories, your learnings, your project docs, all of it. By the time a vault reaches tens of thousands of files, `grep` is not enough. Related ideas use different words, a concept is spread across five notes, and exact-string search misses everything that does not match the term you happened to type. The second brain makes the whole vault semantically searchable from inside a session.

This is the payoff of the whole "files are ground truth" commitment. Because every memory and learning and journal is written to the vault as markdown, embedding the vault makes all of it retrievable by meaning. The agent can search its own knowledge.

---

## The data flow

```
vault (markdown files)
   │  nightly indexer on the GPU box
   ▼
chunk  →  dense embedding  +  sparse BM25 tokens
   │
   ▼
Qdrant (vector DB on the GPU box)
   collections, versioned behind an alias
   dense vectors + sparse vectors + a cross-encoder reranker
   │  REST API on the GPU box
   ▼
MCP proxy (thin client, runs where Claude Code runs)
   translates tool calls → HTTP, resolves local file paths, does MOC rollup
   │
   ▼
Claude Code session
   tools: search_vault, search_all, list_collections, get_document
```

---

## The stack, layer by layer

**The vault is canonical.** Everything writes here first, as plain markdown. The embedding pipeline is downstream of the files. That means the store is human-readable, version-controlled, and not locked to any embedding model. You can swap the whole retrieval stack and lose nothing, because the source of truth is the files, not the index.

**The indexer runs on the GPU box.** A nightly job chunks each changed file, computes a dense embedding and a sparse BM25 representation, and upserts to Qdrant. Incremental, so it only touches what changed.

**Qdrant holds three signals.** A dense vector (semantic similarity), a sparse vector (exact-term match), and a payload with the file path and text. A cross-encoder reranker sits on top. Collections are versioned (`v1`, `v2`, ...) and a named alias points at the current one, so promoting a new index is transparent to every consumer.

**Search has modes.** `dense` (pure similarity), `hybrid` (dense plus BM25, merged), and `agentic` (the query is decomposed and expanded, then hybrid retrieval, then the cross-encoder reorders). Agentic is the default for a session: it handles a vague natural-language question better than raw similarity.

**The proxy is thin.** On the workstation, the MCP server is a small HTTP client. No local model, no local vector DB. It translates tool calls to REST, resolves the GPU box's file paths to local ones for document retrieval, and does one clever thing on top: MOC rollup.

---

## MOC rollup

When a hub note (an index, a map-of-content, a README) surfaces in the results, the proxy reads it, parses its `[[wikilinks]]`, resolves them to vault paths, and appends those linked notes to the result. It does not displace the original ranking; the children get appended at the tail, with caps (only the top few hubs expand, a bounded number of children listed and fetched).

This exploits the graph structure of the vault. A hub note is a hand-curated cluster. When you hit one, following its links gives you the cluster around the answer, not just the single note that matched. You get contextually complete retrieval without knowing in advance which leaf notes to ask for.

---

## The closed loop

This is where the [memory](04-memory.md), [learning](05-learning-loop.md), and [continuity](06-continuity.md) systems pay off together:

```
a correction → a feedback memory in the vault
a promotion  → a learning entry in the vault
a session    → a journal in the vault
   │
   ▼  nightly indexer embeds the new files
   ▼
next session: "what did we decide about the backup pipeline?"
   → surfaces the feedback and reference notes by meaning,
     even though they use their own words and you forgot the filename
```

Keyword search needs you to remember the term. Vector search finds it by meaning. That difference is what turns a folder of notes into a brain.

---

## Two design choices worth copying

**Thin client, remote inference.** The model and the DB live on a machine with a GPU. The workstation runs only the proxy. Upgrading the embedding model means reindexing on the GPU box; no consumer code changes. The trade is that you need that box reachable (a private network handles this); the win is a single place to upgrade and a tiny footprint on the laptop.

**Fleet sync is part of the deployment.** When you promote a new collection or swap the alias, every consumer (each machine's proxy, each CLI) has to update its default collection in the same pass. The failure mode is quiet: the old collection still answers, just with worse recall, because the alias now points somewhere the consumers are not looking. Treat consumer sync as the last step of the upgrade, not an optional follow-up.

---

## Ship / scrub

- The architecture (canonical vault, thin proxy, hybrid plus rerank, MOC rollup, fleet-sync contract) is generic and worth publishing in full.
- Scrub the GPU host, the IP, the collection names, and the proxy paths to placeholders.
- The vault itself is your knowledge and your private data. Never ship it or the index. Ship the architecture and the proxy pattern.
