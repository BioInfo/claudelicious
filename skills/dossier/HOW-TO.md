# dossier — how to use it

A skill that decodes AI companies past the marketing site, runs them through a forced comparison against 3 alternatives plus 1 contrarian "build internal" option, and lands a take-the-meeting verdict with 2-3 prep questions sharp enough to expose the gap in 90 seconds. The output is a markdown briefing you can read in 3 minutes.

Built because every senior practitioner gets the same question: *"Have you seen `<AI company>`?"* Their marketing site is useless. A general LLM gives you a Wikipedia entry. What you actually want is the substance, framed against your specific role and the alternatives that actually compete for your attention.

## Install

```bash
git clone https://github.com/BioInfo/claudelicious.git
cp -r claudelicious/skills/dossier ~/.claude/skills/
```

Next Claude Code session, the skill auto-loads. Fires on `/dossier <company>` and on the natural-language triggers in the frontmatter (`"have you seen X"`, `"decode X"`, `"should I take a meeting with X"`, `"what does X do"`, etc.).

## How a run goes

You say one of:
- `/dossier Glean`
- `Have you seen Writer Enterprise?`
- `Decode Acme Decision AI — they want to talk to me about analytics tooling.`

If your trigger already names the use case and the relationship (warm or cold), the skill goes straight to research. If not, it asks two questions before starting:

1. **What specific use case are you evaluating them against?**
   This determines whether the 3 alternatives are commercial-flavored, R&D-flavored, infra-flavored, or methodology-flavored. Without this, the alternatives are generic.
2. **Warm or cold?**
   Warm (private event invite, intro from your boss, conference booth where they sought you out) vs cold (inbound LinkedIn, generic press, you stumbled across them). Warm changes the verdict math and surfaces the "why they probably reached out" angle.

Then it dispatches parallel research:
- `WebFetch` on the homepage and the vertical/use-case page.
- 3-4 `WebSearch` calls for substance: founder interviews, vertical case studies, competitive landscape, engineering blog.
- Vault search for adjacent capabilities you already have (and for prior mentions of the company in your notes).

Then it synthesizes:
- One-sentence decode (without their marketing vocabulary).
- Actual substance vs marketing, with evidence.
- 3 contextual alternatives + 1 contrarian.
- Verdict + 2-3 prep questions in quoted form.
- Gaps in the research (what to ask in the meeting).

Output lands at `~/vault/research/companies/<slug>/dossier.md`.

## The per-company directory

The skill creates a directory, not a single file:

```
~/vault/research/companies/
└── acme-decision-ai/
    ├── dossier.md          ← the skill writes here
    ├── contacts.md         ← you populate over time
    ├── meeting-notes/      ← you populate over time
    └── artifacts/          ← decks, PDFs, screenshots
```

The skill only ever writes `dossier.md`. Everything else in the directory is yours. The skill will refresh `dossier.md` in place on subsequent runs (preserving the prior verdict in a "Previous decode" section at the bottom).

## Customizing the vault path

If your vault isn't at `~/vault/`, edit the SKILL.md after install and replace `~/vault/research/companies/` with your actual path. The skill body references the path in 4-5 places.

## Optional enhancements

The skill works with stock Claude Code tools (`WebFetch`, `WebSearch`, `Read`, `Write`, `Bash`, `AskUserQuestion`). Three optional upgrades make it sharper:

1. **Self-hosted firecrawl MCP** — better at JS-heavy SPA marketing sites where `WebFetch` returns thin content. Edit Step 3 to add `mcp__firecrawl__firecrawl_scrape` calls in parallel with `WebFetch`.
2. **Semantic vault search** — if your Obsidian vault is indexed in a vector database with an MCP server, swap the `Grep`/`Glob` vault lookups for the semantic search MCP. Finds adjacent capabilities you'd miss with keyword grep.
3. **Cached alternatives** — if you repeatedly evaluate companies in the same use case (e.g., developer-tools vendors), save the 3+1 alternative set once at `research/Alternatives/<use-case>.md` and reference it from future dossiers. The skill suggests this when it notices a repeated pattern.

## What this skill won't do

- **Identify specific people to contact.** Out of scope by design. You'd rather know what to ask than who to email.
- **Decode non-AI companies.** v1 is AI/data/ML only. Non-AI gets a different alternative set; v2 territory.
- **Run trend research.** Pair the dossier with a separate trend-research skill as a follow-up offer. Different problem.
- **Replace your judgment.** The skill is opinionated by design — it'll land "skip the meeting" when the research supports it. But the verdict is a recommendation, not a decision.

## Why the 3+1 alternatives are non-negotiable

A single-company writeup tells you what they do. A 3+1 shortlist tells you whether to care.

The contrarian "build internal" option is there because for senior practitioners, the consulting markup often doesn't buy anything they couldn't do faster by hiring 2-3 senior people directly. Naming that option in every dossier forces the comparison to happen.

## Voice

The skill writes in plain professional register. No em-dashes. No filler LLM intensifiers (transformative, leverage, unprecedented). No "honestly" / "to be honest" hedging. Skeptical analyst tone — real revenue and real customers earn acknowledgement, vague claims earn skepticism. If you want a different register, edit Step 6 of the SKILL.md.

## Why I built this

I kept getting names of AI companies thrown at me by colleagues, executives, and inbound sales. The pattern was always the same:

1. Hear the name.
2. Visit their website. Marketing fluff.
3. Ask a general LLM. Wikipedia-grade summary, no opinion.
4. Spend 20 minutes digging until I find something substantive.
5. Realize I still don't know whether they're better or worse than the obvious alternatives for my actual use case.

The dossier skill compresses steps 2-5 into one parallel research pass with a structured output, ending with a verdict. It works because the 3+1 alternatives force a comparison and the prep questions force the meeting to expose the gap.

The conversation that produced this skill is written up in the companion blog post (link in the repo README). The pattern of brainstorming-then-codifying is the meta-point.
