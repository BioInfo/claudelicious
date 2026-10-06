# 24 — The model budget

The [multi-provider](09-multi-provider.md) doc taught the swap: run the whole harness on a different
model when you want to. This doc teaches the portfolio. Once several lanes are working at once, the model
bill is the thing that bites, and the answer is not a cheaper model everywhere. It is spending the
expensive one only where it earns its keep, and routing everything else off it.

The split is simple to state. Judgment, voice, spec-writing, and verification stay on the strongest
model. Bulk mechanical labor, the file edits, the refactors, the batch work that is more typing than
thinking, routes to a cheaper or flat-rate model. The premium model becomes the thing you spend on
decisions, not on keystrokes.

---

## The spec-and-verify contract

Delegating labor to a cheaper model is only safe with a contract, and the contract is the whole doc.

**The strong model writes the complete spec.** Task, scope, acceptance test, and the exact gate that
says done. Not "refactor this," but "change these call sites, keep this behavior, the acceptance test is
that this command still passes." A cheap model given a vague brief wanders. A cheap model given a precise
one executes. The quality of the delegation is set before the cheap model does anything.

**The cheap model executes**, in its own context, off the premium quota. Tell it to edit in place and
report a summary plus a verification command, never to echo the files back, because a worker told to
paste a large result into its reply will hit its output ceiling and die with nothing applied.

**The strong model verifies, and never trusts the word "done."** Read the diff. Run the gate. A child
reporting success is a document, the weakest tier of [evidence](23-instruments.md), and this is exactly
the setting that doc warned about: you are believing a green you did not produce. Check the artifact. The
verification is not optional overhead, it is the half that makes the delegation trustworthy.

Spec on the strong model, execute on the cheap one, verify on the strong one. Skip the first or the last
and you have not saved money, you have bought a mess at a discount.

---

## Route by reliability, not only by price

Cheap models are not interchangeable, and the differences show up under load. Some routes hold many
requests in flight and are safe to fan out. Others rate-limit hard on any parallelism and have to be run
one at a time, or they fail half the batch. A long tool-following loop wants the model that stays on
task, not the one that wandered off after step three, even if the wanderer is cheaper per token. Match
the route to the shape of the work, and keep a small ledger of what each one is actually good at, so the
routing is learned from results and not from the price sheet.

---

## The economics of width

At one harness the model bill is a rounding error and none of this is worth the trouble. At four lanes
running real work all day, it is the difference between a hobby and an expense. Four lanes on premium
quota, doing their own grunt work, is a bill you will notice. Four lanes that spend the premium model on
specs and verification and push the labor to flat-rate models is close to the same output for a fraction
of the cost. The portfolio is what makes width affordable, and affordability is what lets width run long
enough to compound.

---

## Ship / scrub

- The judgment-versus-labor split, the spec-and-verify contract, route-by-reliability, and the economics
  of width are all generic. Ship them.
- Scrub the specific models and any routing table that encodes your own subscriptions or gateway. The
  shape of the decision is the lesson; which cheap model you happen to use is yours.
- The one line that does not scrub: never trust the child's "done." That holds no matter whose models
  you route to.
