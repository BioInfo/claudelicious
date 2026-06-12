---
name: council
description: "Convenes a council of orthogonal thinker-lenses (Munger, Taleb, Thiel, plus idea-lenses base-rates and second-order-effects, plus a functional skeptic seat) to pressure-test a decision from multiple perspectives, force disagreement, then synthesize. Stateless three-phase engine: blind parallel reads, a dissent round against the consensus, then a synthesis (where they agree, sharpest live dissent, the lens you ignored, decision-shaped close). Invoke when the user says 'convene the council', 'council this', 'pressure-test this decision', or wants multiple mental-model perspectives on a decision before committing. Seats fan out in parallel; the main session synthesizes."
disable-model-invocation: true
model: opus
---

# Council

Pressure-test a decision against a panel of orthogonal mental-model lenses. The value is the **disagreement**, not the consensus. Output is a decision, not a transcript. This is also the cleanest example in the repo of the [subagent fan-out pattern](../../docs/14-subagents-and-workflows.md): parallel seats that cannot see each other, distilled, then synthesized in the main thread.

## What this is NOT

- Not the same prompt across several providers for model diversity (that is a different pattern).
- Not a single hostile reviewer going claim-by-claim through a fact-making draft.
- Not a vibe generator. Every seat commits to a score on its own axis, or it is not pulling its weight.

## The engine (stateless, three phases)

### Phase 0, frame the decision

Restate the user's decision in one crisp sentence. Pick a seat slate from `slates.md`. Honor overrides:

- `--seats munger,base-rates,...` an explicit seat list (overrides the slate)
- `--decision <type>` force a slate (`fund-or-kill`, `vendor-or-partner`, `public-claim`, `strategy-bet`, `default`)

**Orthogonality rule:** never seat two lenses that collapse to the same objection. A person-lens already contains its idea (Munger contains inversion), so do not also seat the standalone idea. Default slate size is 4 to 6. More than 6 is noise.

### Phase 1, blind parallel reads

For each seat, spawn ONE subagent. They must not see each other.

```
Agent(
  subagent_type: "general-purpose",
  model: "sonnet",        # explicit on the Agent call, matched to the task
  description: "council seat: <name>",
  prompt: <contents of lenses/.../<name>.md> + "\n\n## THE DECISION\n" + <framed decision + any context the user gave>
)
```

Issue all seat calls **in one message** so they run concurrently. Each returns under ~150 words: a read, one sharpest objection, and a score on its `scoring_axis` (0 to 10, higher = this lens is more alarmed). Use medium effort for this round. The lens prompt does the work; do not pay for high here.

### Phase 2, dissent round

Distill Phase 1 into a compact **consensus summary** (5 to 8 lines: the dominant read, the median scores, what most seats agreed on). Do NOT pass the raw transcript. Re-spawn each seat with its lens file plus:

```
## EMERGING CONSENSUS
<the 5-8 line distillation>

The council is converging on the above. From YOUR lens specifically, find where this
consensus is wrong, lazy, or blind. If you genuinely agree, say so in one line and stop,
do not manufacture dissent. Under 120 words.
```

Run concurrently again (one message, all seats). Passing the distilled consensus rather than the full transcript keeps each dissent context small and cheap.

### Phase 3, synthesis (main context, do NOT fork)

You (the main session) reconcile. Read every seat's score and its declared `blind_to`. Produce, in the user's voice, a decision-block shape:

1. **Where they agree** the load-bearing consensus you can actually trust.
2. **Sharpest live dissent** the objection that survived the dissent round. Name the seat. This is the real risk.
3. **The lens you were ignoring** the seat whose score was highest *and* whose `blind_to` is NOT covered by any other seat. Collective blind-spot check: if every seat shares a `blind_to` (nobody scored upside, say), name it; that is the failure a council is most likely to commit.
4. **The call** one paragraph stating the decision and why, then bullets with an owner and date per item. Be willing to conclude "proceed, no real failure mode." The value is the check.

## Token discipline

Seats are the cheaper model, capped ~150 words. Six seats over two rounds stays cheap. Phase 2 reads the distilled consensus, never the full transcript. The synthesis runs once, in the main context, never forked per seat.

## Output

Render the synthesis in chat by default. If the user says "save it", write to `<vault>/decisions/<slug>/council.md` with the framed decision, the seat scores table, and the synthesis. Ask before writing; never auto-save.

## Libraries

The shipped lenses are a representative set, not the whole space. Each is a small file with a worldview, a `scoring_axis`, and a `blind_to`. The engine does not care which library a seat comes from, so the set is meant to be extended.

- `lenses/thinkers/people/` worldview-and-temperament seats (Munger, Taleb, Thiel here).
- `lenses/thinkers/ideas/` one mental model, cleanly applied (base-rates, second-order-effects here).
- `lenses/roles/` functional seats (a skeptic here). Add your own: a CFO, a customer, a regulator, a competitor. Same schema.

## Why this is a good example

It shows the fan-out pattern end to end: blind parallel seats so they cannot anchor on each other, a distillation step so the dissent round stays cheap, and a single synthesis in the main thread instead of one-more-agent. The lens files show how to give a subagent a sharp, narrow persona in about twenty lines.
