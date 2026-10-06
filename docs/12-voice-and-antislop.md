# 12 — Voice and anti-slop

A harness that drafts in default-LLM voice is a liability. The output is recognizable on sight: hedged, padded, em-dashed, built on the same handful of scaffolding phrases, every paragraph the same length. People can smell it, and once they can, everything the harness produces under your name reads as machine-written. The fix is to encode your actual voice as a rule the harness cannot skip.

This is its own published system, **Slopless**. This doc covers how it plugs into the harness and why it is a rule, not a suggestion.

---

## Voice is a rule file, not a vibe

Your voice lives in the [rules layer](01-rules-and-context.md) as a single canonical file, auto-loaded every session, referenced by every skill that drafts anything you will send or publish. One source of truth. A drafting skill does not get to improvise a register; it reads the voice file and writes to it.

That file is not a paragraph of "write like me." It is mechanical enough to enforce:

- **A register ladder.** Different channels demand different formality. A Slack message, an internal email, a slide, an exec brief, and a published essay are five different voices. The ladder names each tier and its rules, so the harness picks the right one for the channel instead of writing everything at one flat formality.
- **Banned lists.** The specific words and phrases that mark machine output: the inflated verbs (delve, leverage, harness-as-verb), the empty intensifiers (crucial, robust, seamless), the scaffolding ("here's the thing", "it's worth noting"), the faux-depth closers. These are greppable. You can scan for them.
- **Structural rules.** No em-dashes. Vary sentence length, one short and one long per paragraph. No rule-of-three rhythm. No manufactured parallelism. No paragraph-ending profundity. These are the textures that betray generated text even when no banned word appears.

---

## The two-pass scan

Before any draft ships, it gets two scans, because the failure modes split into two kinds.

**A literal scan.** Grep the draft against the banned lists and the em-dash rule. Mechanical, fast, zero hits required. A machine catches these.

**A structural scan.** Read it by eye for the things grep cannot catch: three same-length sentences in a row, three clauses starting with the same word, a closer that announces importance instead of demonstrating it, an invented specific that sounds helpful but is not true. These are textures, not words, so you have to read for them.

The order matters. The literal scan is cheap, so it runs first. The structural scan needs judgment, so it runs second, on a draft already clean of the obvious tells.

---

## The score gate

For anything that matters, the draft gets rated before it ships, on a few axes: is it direct (statements, not announcements), does the rhythm vary, does it respect the reader's intelligence, does it sound like you, does every line earn its place. Score it, and anything under the bar gets revised and re-scored. The gate is what stops "good enough" from going out under your name.

---

## The discipline around it

Two rules make the voice system hold:

- **Voice-sensitive drafting uses your best model, always.** A fast model can orchestrate, dispatch, and run the send command. It does not draft anything you will publish. The draft comes from the strongest model you have, every time.
- **Nothing sends on its own.** No message, post, or email goes out without you seeing the draft and approving it. The harness drafts and shows; you decide. This is a hard rule, not a default, and it is enforced in the [dispatch-only contract](02-skills.md) of every posting skill.

---

## Why this belongs in a cookbook about systems

It is tempting to treat voice as a soft concern next to hooks and vector search. It is not. The harness produces text on your behalf at volume, and the single fastest way to destroy trust in everything it does is to let that text read as slop. A voice rule, scanned and gated, is the quality control on the harness's most visible output. It is the same discipline as the rest of the system: write the standard down, then enforce it mechanically instead of hoping.

---

## Ship / scrub

- The architecture (voice as a canonical rule file, the register ladder, the two-pass scan, the score gate, the best-model and no-send-without-approval rules) is generic. Ship the framework.
- Your actual banned lists and register examples are partly personal taste and partly universal. The universal half (the LLM tells) is safe to share; Slopless is the published version of exactly that.
- Your identity and the personal proper nouns in your voice file are not for sharing. Ship the structure, point to Slopless for the worked version.
