# Worked example: `/dossier Fractal Analytics`

A real run of the `dossier` skill against Fractal Analytics. Frames the company through the lens of an AI product leader at a hypothetical clinical data vendor who is being courted for a meeting because they sit at a high-leverage seam: building AI products on the vendor's data layer that downstream biopharma customers consume.

Names, vault paths, and identifying details have been sanitized. The structure, alternatives, and prep questions are unchanged.

---

## The trigger

> *"Decode Fractal Analytics — they invited me to a private event. I'd be evaluating them for the seam between our clinical data layer and our biopharma customers' commercial and R&D workflows."*

The trigger names both the use case (data-vendor + downstream-biopharma agentic seam) and the relationship signal (warm, private event invite). The skill skips the upfront questions and goes straight to research.

## Research dispatch (parallel)

1. `WebFetch` https://fractal.ai
2. `WebFetch` https://fractal.ai/industry/healthcare-and-life-sciences
3. `WebSearch` "Fractal Analytics pharma life sciences agentic AI case studies 2025 2026"
4. `WebSearch` "Srikanth Velamakanni Fractal CEO interview decision intelligence agents"
5. `WebSearch` "Fractal Analytics vs QuantumBlack vs ZS Associates AI consulting pharma"
6. Vault search for adjacent capabilities the user already has

Took ~15 seconds wall-clock.

## What came back

**Marketing decode**: Homepage is generic ("Power enterprise decisions with AI that works"). Sub-pages are vertical-specific. The healthcare/life-sciences page is **pharma commercial heavy**: sales co-pilot, next best action, content tagging, patient analytics, claims anomaly detection. No R&D or clinical-scientific agent. Their *Decision Agentic AI Engine* (showcased at a Databricks Healthcare webinar) is a Next Best Action solution for pharma commercial teams.

**Substance signal**: Founder Srikanth Velamakanni is the real thesis carrier. India's first AI-services IPO, FY26, 21% revenue growth, $360M TPG investment 2022 minted them unicorn. The decision-intelligence and behavioral-economics framing is real, not slideware — one case study on using behavioral science to reduce prescription attrition is the cleanest evidence.

**Competitive landscape signal**: ZS Associates has Max.AI (low-code/no-code agent platform), Trials.ai (clinical trial design agent), and a partnership with Phylo for biomedical AI in R&D. McKinsey QuantumBlack is publishing on agentic evaluations and has deeper methodology rigor. Both are more pharma-vertical-native than Fractal.

**Vault signal**: The user already has substantial work on business-process decomposition with agents, and their incoming role is the agentic platform layer that lets pharma companies consume the clinical data through AI agents — one-to-one with what Fractal sells, just at a different layer of the stack.

## The output (excerpt)

The full dossier landed at `~/vault/Knowledge/AI-Research/Companies/fractal-ai/dossier.md`. Key sections:

### One-sentence decode (without their words)

> A 26-year-old India-headquartered analytics consultancy that pivoted hard into agentic AI, with a real decision-intelligence and behavioral-science layer wrapped around vendor models, currently strongest in pharma **commercial** (sales co-pilot, next best action, patient analytics) rather than R&D or clinical-scientific decisions.

### Why they probably reached out

> The user is exactly the buyer-persona seam Fractal needs: an incoming AI platform leader at a clinical data vendor whose product is consumed by dozens of biopharma + healthcare partners. Fractal's Omnichannel Decision Agentic AI Engine wants to sit on top of pharma commercial CRM + RWD; the clinical data vendor is a top-tier RWD source. The user is the seam between Fractal's product and the data layer they want to be closest to. Best case for Fractal: the user becomes a customer AND a channel partner that recommends them to dozens of downstream pharma customers. That's a 10x outcome, which is why this is a private-event invite rather than a sales call.

### Three contextual alternatives

**1. ZS Associates — the closest match, probably ahead of Fractal**
- 40+ years pharma-native; AI arm is vertical, not a pivot from CPG.
- *Max.AI*: low-code/no-code agent platform with LLM + RAG + fine-tuning + orchestration. Productized.
- *Trials.ai*: AI-native clinical trial design agent. The R&D-scientific agent Fractal doesn't have.
- *Phylo x ZS*: research strategy + data integration + governance for biomedical AI. Closest analogue to the user's actual seam.
- **Better than Fractal if**: vertical depth and a real agentic platform you can recommend downstream.
- **Worse if**: you want decision-intelligence/behavioral-science framing as differentiator (Fractal's edge).

**2. McKinsey QuantumBlack — methodology leader, weaker on owned IP**
- Acquired by McKinsey 2015; deep process-mapping methodology.
- Publishing on agentic evaluations (e.g., "Evaluations for the agentic world") — ahead on eval rigor.
- **Better than Fractal if**: you want defensible process-decomposition frameworks to deploy across 30 different customers.
- **Worse if**: you want reusable agentic IP — QB walks away with a playbook, Fractal leaves you with a platform.

**3. IQVIA's AI arm — data-and-workflow incumbent, partner with caution**
- Most pharma commercial data + workflow expertise of any consulting-flavored option.
- Pointed agentic-AI-in-commercial-life-sciences content through 2025-2026.
- **Better than Fractal if**: your customer needs the data + workflow combo and is already in IQVIA's orbit.
- **Worse**: IQVIA competes with most clinical data vendors on RWD. Recommending them downstream erodes the user's employer's moat. Competitive watch, not partner.

### Contrarian: don't hire a consultancy at all

The user's profile is what Fractal would brag about hiring. They've shipped agent infrastructure, done business-process decomposition with agents, and understand the pharma data layer at depth. For the first 6-12 months in role, the consulting markup may not buy anything they can't do faster with 2-3 senior ex-pharma-commercial-ops hires plus 1-2 agentic platform engineers. The case for hiring any of the three above is **only** if customer-facing process-mapping work needs to scale to dozens of biopharma orgs simultaneously and the user doesn't want to staff it internally.

### Verdict — take the meeting with sharp prep

Warm invite, exact buyer-persona match, leverage is high.

**The opener that exposes the gap in 90 seconds**:

> *"Your Omnichannel Decision Agentic AI Engine is mature on top of CRM data for pharma commercial teams. My buyers include biopharma R&D and medical affairs, not just commercial. The data layer is patient-event-level and the decisions are scientific, not commercial. Show me one case study where you've built process-mapping for that buyer, where the agent's job was a scientific or R&D decision."*

That single question tells you in 90 seconds whether they're really pharma-commercial-only (interesting but not your core need) or whether they've gone deeper into R&D and medical-affairs (meaningful partnership).

**Two more prep questions**:

> *"Of your 113 enterprise transformations, name the three most similar in shape to 'data vendor + AI product layer + dozens of downstream pharma customers.' I'm building platform-of-platforms, not direct enterprise."*

> *"Walk me through your LLM Studio architecture. Is it a wrapper around vendor models with thin orchestration, or do you have proprietary agent orchestration IP that's defensible?"*

**Who would actually staff your account?** Their healthcare-and-life-sciences leadership listed publicly is engagement-manager / principal-consultant tier. Ask explicitly to meet the partner-level lead who would own your account.

### Bottom line

Fractal is a real company with real revenue, a real decision-intelligence thesis, and a productized agent engine for pharma commercial. They are also currently weaker than ZS on pharma-vertical agentic product depth and weaker than QuantumBlack on methodology rigor. The warm private-event invite is high-signal because the user is their dream channel partner. Take the meeting. Open with the R&D-vs-commercial question. Decide partnership based on what they show for R&D and medical-affairs use cases, not what they sell on commercial. The fallback (build internal) is genuinely viable given the user's profile.

---

## What this example demonstrates

- **Use-case lens shapes alternatives**: ZS, QuantumBlack, IQVIA showed up because the user's seam is pharma-vertical agentic platforms. A different use case (dev tools, financial services, retail) would surface a different shortlist.
- **The 3+1 contrarian forces honest evaluation**: Naming "don't hire any consultancy" alongside the three alternatives means the user has to actively choose to hire, not drift into it.
- **The opener question is the highest-value output**: One question, calibrated to the gap between marketing pitch and actual buyer need, exposes the gap in 90 seconds. The rest of the dossier supports that question.
- **Warm signal raises stakes both ways**: A warm invite means the meeting is worth taking, AND your leverage is higher than they'll assume. Both halves of that matter.

Total wall-clock from trigger to vault-ready dossier: ~3 minutes.
