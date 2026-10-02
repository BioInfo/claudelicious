---
name: dossier
version: "1.0.0"
description: "Decodes an AI company past the marketing site — what they actually do, where the substance vs slideware divide is, and how they compare against 3 contextual alternatives + 1 contrarian build-internal option, ending with a take-the-meeting verdict and 2-3 prep questions sharp enough to expose the gap in 90 seconds. ALWAYS invoke when the user says '/dossier <company>', 'have you seen <company>', 'decode <company>', 'what does <company> actually do', 'should I take a meeting with <company>', 'is <company> any good', or pastes a company website and asks for a read. Always comparative — never produces a single-company writeup without 3 alternatives + 1 contrarian framed against the user's specific use-case lens. V1 SCOPE: AI/data/ML companies only — if the company isn't AI flavored, surface that and ask before proceeding. Refreshes existing dossiers in place (preserves prior verdict in 'Previous decode' section). Skeptical-analyst tone. Output to a per-company directory at ~/vault/Knowledge/AI-Research/Companies/<slug>/dossier.md (leaves room alongside for contacts.md, meeting-notes/, artifacts/)."
argument-hint: '/dossier Fractal Analytics, have you seen Glean, decode Writer Enterprise'
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, WebSearch, WebFetch
user-invocable: true
model: opus
---

# dossier — AI company decoder + comparative shortlist

Decode an AI company past the marketing veneer, produce a vault-ready briefing the user can read in 3 minutes, end with either "take the meeting prepared" or "skip it cleanly." Always comparative against 3 alternatives + 1 contrarian build-internal option.

## What this skill is and isn't

**Is**: Cut-through-marketing decoder + contextual comparative shortlist + take-the-meeting verdict, scoped to AI/data/ML companies, framed against the user's stated use case.

**Is not**:
- Generic company research (different problem, different tools).
- A person-finder (out of scope by design — don't try to identify specific contacts to reach out to).
- A non-AI company evaluator (v1 scope is AI only; surface and skip if mismatch).
- A pure trend research tool. Pair this skill with a trend-research skill as a follow-up offer, not as part of the trigger.

## Vault path

This skill assumes the user keeps research notes in an Obsidian-style vault at `~/vault/` and treats `Knowledge/AI-Research/Companies/` as the home for company dossiers. If the user's vault lives elsewhere, adjust paths at install time (see HOW-TO.md).

## Workflow

### Step 1 — Parse and confirm scope

- Pull the company name from the trigger.
- Check whether the company is AI/data/ML flavored (homepage scan + name pattern). If unclear, ask once: *"Is `<Company>` AI/data/ML flavored, or a different vertical? v1 of /dossier is scoped to AI companies; non-AI gets a different alternative set."*
- Check whether a per-company directory already exists at `~/vault/Knowledge/AI-Research/Companies/<slug>/`. If yes, you're refreshing — read the existing `dossier.md` and preserve the prior verdict in a "Previous decode (YYYY-MM-DD)" section at the bottom of the new one. Never touch sibling files (`contacts.md`, `meeting-notes/`, `artifacts/`, etc.) — those are the user's working notes.

### Step 2 — Ask the two upfront questions (only if not given inline)

If the user's trigger message already names the use case and the relationship signal, skip these questions and proceed. If either is missing, ask both via `AskUserQuestion` in a single round:

**Question 1 — Use case lens**: *"What specific use case are you evaluating them against?"* This determines whether the 3 alternatives are commercial-flavored, R&D-flavored, infra-flavored, or methodology-flavored.

**Question 2 — Warm or cold**: *"Warm (someone introduced them, you got an invite, your boss flagged them) or cold (inbound LinkedIn, conference booth, you stumbled across them)?"* This shapes the verdict and the "why they probably reached out" section.

Don't ask more than two upfront questions. Respect the user's time.

### Step 3 — Parallel research dispatch

Send these in a single tool batch:

1. **Marketing decode**: `WebFetch` the company homepage.
2. **Vertical/use-case decode**: `WebFetch` the company's industry or solution page that maps to the user's use case (e.g., healthcare-and-life-sciences, enterprise-AI, dev-tools).
3. **Substance searches** (3-4 parallel `WebSearch` calls):
   - `"<Company> founder CEO interview <use-case keyword>"` — where the thesis shows up, not the marketing.
   - `"<Company> case studies <vertical> 2025 2026"` — concrete customers, concrete outcomes.
   - `"<Company> vs <known competitor 1> vs <known competitor 2> <vertical>"` — competitive landscape.
   - `"<Company> engineering blog architecture <product name>"` — real technical substance if it exists.
4. **Vault context** (parallel with web research, if a vault is configured):
   - Search the vault for adjacent capabilities the user already has on the topic. Tools depend on setup — `Grep` or `Glob` over `~/vault/` works; if the user has a semantic search MCP server, prefer that.
   - Search the vault for the company name itself — have they been mentioned before? Prior meeting notes? Prior decode?

If `WebFetch` returns thin content (paywall, JS-heavy SPA, marketing fluff), suggest the user install a richer scraping path (e.g., a self-hosted firecrawl MCP) and proceed with what you have.

### Step 4 — Surface the 3 alternatives + 1 contrarian

This is the mandatory structure — never produce a dossier without it.

- **Alternative 1**: The closest vertical-native match. For pharma/life sciences this is often ZS Associates, IQVIA, or Komodo Health. For dev tools this is often the obvious incumbent. Should be the option that beats the subject company on vertical depth.
- **Alternative 2**: The methodology / consulting / framework leader. Often McKinsey QuantumBlack, BCG X, EY's AI arm, or Accenture Applied Intelligence. Should be the option that beats the subject company on process or methodology rigor.
- **Alternative 3**: The data-or-workflow incumbent. Often the company that already owns the data layer or workflow the user's customers live in. Frame partnership with caution if they compete with the user's employer.
- **Contrarian (always present)**: "Don't hire any consultancy or vendor — build internal, hire 2-3 senior people instead." For senior practitioners, this is often viable. Name what would have to be true for the build-internal path, and what scale problem would force the hire-instead-of-build decision.

Each alternative gets: one-line description, **better than subject if X**, **worse if Y**. Cite the specific product, case study, or published asset that backs the claim.

### Step 5 — Verdict + prep questions

Verdict is a single phrase: `take-the-meeting`, `take-the-meeting-with-sharp-prep`, `skip`, `monitor-only`, `delegate-to-a-team-member`, or similar. Put it in frontmatter and in the verdict section.

**Prep questions** are the highest-value output. Aim for one opener question that exposes the biggest gap in 90 seconds (the question they don't want to answer), plus 2-3 follow-ups. Frame each as a quoted question the user could read aloud in the meeting. Avoid generic "what's your pricing" or "tell me about your roadmap" — those waste the user's leverage.

If the company is warm-invited (private event, intro from someone), name the "why they probably reached out" angle explicitly and use it to inform leverage framing.

### Step 6 — Voice and tone

- Skeptical analyst, not over-indexed on skeptical. Real revenue + real customers + real product earn acknowledgement; vague claims earn skepticism.
- Plain professional register. Complete sentences. No em-dashes.
- Avoid filler LLM intensifiers (transformative, leverage, unprecedented, crucial, pivotal, paradigm-shifting). State what's specific and let the specifics carry weight.
- Avoid "honestly" / "to be honest" hedging — implies prior content was dishonest.
- Be willing to land "skip the meeting" or "this is mostly marketing" when the research supports it. Don't manufacture take-the-meeting verdicts to sound balanced.

### Step 7 — Output

Per-company directory layout. Create the directory if it doesn't exist, then write the dossier inside:

```
~/vault/Knowledge/AI-Research/Companies/
└── <slug>/
    ├── dossier.md          ← this skill writes here
    ├── contacts.md         ← user populates over time (don't touch)
    ├── meeting-notes/      ← user populates over time (don't touch)
    └── artifacts/          ← decks, PDFs, screenshots the user drops in (don't touch)
```

Slug is kebab-case company name (e.g., `fractal-ai`, `glean`, `writer-enterprise`). Only ever write `dossier.md` inside the directory. The other files and subdirectories are the user's working notes; treat them as read-only.

Frontmatter schema:

```yaml
---
type: company-decode
slug: <kebab>
company: <Full Legal Name Inc.>
website: https://...
hq: City, Country
founded: YYYY
employees: <approx>
status_signal: <warm-invited-private-event | warm-intro-from-X | cold-inbound | conference-booth | press-discovery>
verdict: <take-the-meeting | take-the-meeting-with-sharp-prep | skip | monitor-only | delegate>
use_case_lens: <one-line description from question 1>
last_decoded: YYYY-MM-DD
alternatives: [slug1, slug2, slug3]
contrarian: build-internal-not-hire-consultancy
tags:
  - ai-research/company-decode
  - <vertical-tag>
  - <use-case-tag>
---
```

Body sections in this order:

1. **One-sentence decode (without their words)** — describe what they actually do in a single sentence that doesn't use any of their marketing vocabulary.
2. **Actual substance vs the marketing** — 3 sub-paragraphs: what the marketing says, what they actually do (with evidence), where the website misleads. Name the founder/leadership signal if relevant.
3. **Why they probably reached out** (only if warm) — best-guess one-paragraph on what they want from the user.
4. **What's already in your vault that's relevant** — wikilinks to specific notes you found via vault search. Pull at least 2-3 if they exist.
5. **Three contextual alternatives** — sections 1, 2, 3 with structure above.
6. **Contrarian: build internal instead** — what would have to be true for build, what scale forces hire.
7. **Verdict** — short verdict statement + prep angle + 2-3 prep questions in quoted form + "who would actually staff your account" if consulting/services flavored.
8. **Gaps in this research** — what you couldn't find publicly that's worth asking in the meeting.
9. **Bottom line in one paragraph** — single-paragraph TL;DR that stands alone.

Target length: 1000-1500 words. Tight, scannable, skim-friendly.

### Step 8 — Hand-back

After writing, surface:
- The vault path.
- A one-sentence summary of the verdict and the sharpest prep question.
- One follow-up offer if topical and not stale: *"Want me to pair this with a recent-signals research pass on <Company> to see if they're showing up in cross-platform discussions right now?"*

## Refreshing an existing dossier

If `<slug>/dossier.md` already exists:
1. Read the existing dossier first. Do not read or touch sibling files in the directory — they are the user's working notes.
2. Preserve the entire prior dossier under a `## Previous decode (<old_last_decoded>)` heading at the bottom of the new file.
3. Write the new decode at the top (frontmatter `last_decoded` updated to today).
4. In the hand-back, name what changed vs the prior decode (new product, new alternative emerged, verdict flipped, etc.).

## What NOT to do

- Don't identify specific individuals to contact (out of scope by design).
- Don't manufacture take-the-meeting verdicts to be polite. If the substance is thin, say so.
- Don't skip the 3+1 alternatives. The shortlist is the value.
- Don't reuse the same 3 alternatives for every company. The set should be specific to the subject's vertical, the user's use case, and the user's stated role.
- Don't reach for "Have you seen <X>" pleasantries — open with substance.
- Don't write "this is a strong company with real revenue and real customers" as a closer. Land specifics or cut.

## When to suggest expanding scope

If asked to decode a non-AI company (consulting firm doing AI work, healthcare company adopting AI, traditional vendor with an AI bolt-on), surface that v1 is AI-native only and ask before proceeding. Note the gap as a candidate for v2.

If a particular use case repeatedly surfaces the same 3 alternatives, that's a signal the alternative set should be cached for the use case. Offer to save a reference doc at `Knowledge/AI-Research/Alternatives/<use-case>.md` the user can point future decodes at.
