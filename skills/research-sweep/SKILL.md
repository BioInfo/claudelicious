---
name: research-sweep
description: >
  Run a multi-source research sweep on a topic and synthesize a cited summary.
  ALWAYS invoke when the user says "research X", "sweep X", "what's being said
  about X", or asks for a grounded summary across sources before drafting
  something. NOT for a single-source lookup (just fetch that source).
model: opus
allowed-tools: Read, WebSearch, WebFetch, Write
disable-model-invocation: false
---

# research-sweep

The spine of the procedure lives here; the per-source query patterns and the
synthesis spec live in `references/`, loaded only when the task reaches that
branch. That is progressive disclosure inside a skill — this body stays short.

## Procedure

1. **Scope.** If the topic is underspecified (no audience, timeframe, or angle),
   ask one or two clarifying questions before sweeping. A vague sweep wastes the
   whole run.
2. **Gather.** Run the per-source queries. The patterns for each source (search,
   forums, primary docs) are in [`references/sources.md`](references/sources.md).
   Read that file now.
3. **Verify.** Cross-check any claim that appears in only one source before it
   goes in the summary. A single-source claim is flagged, not asserted.
4. **Synthesize.** Follow the two-pass spec in
   [`references/synthesis.md`](references/synthesis.md) — a mechanical rollup pass,
   then a judgment pass. Read that file when you reach this step.
5. **Write** the summary with inline citations to the URLs actually used, and a
   short "what's still uncertain" section. Save it where the user asked, or
   surface it inline if they did not specify.

## Notes

- Cross-platform signals (a claim that shows up in several independent sources)
  are weighted highest. A single loud source is the weakest evidence.
- Never fabricate engagement numbers or citation counts. If a number isn't in the
  fetched content, don't put it in the summary.
