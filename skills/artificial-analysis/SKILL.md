---
name: artificial-analysis
description: "Compare LLM and media-model performance using Artificial Analysis (artificialanalysis.ai). ALWAYS invoke when the user asks to compare models, asks 'which model is best/fastest/cheapest', asks about model intelligence/coding/math benchmarks, asks about tokens-per-second / TTFT / latency, asks about model pricing, asks about Elo ratings for image/video/TTS models, or names two+ models and wants a head-to-head. Covers all major LLMs (OpenAI, Anthropic, Google, Meta, DeepSeek, etc.) plus text-to-image / image-editing / text-to-speech / text-to-video / image-to-video Elo leaderboards. Cached 1h, no rate limit concerns."
model: opus
---

# artificial-analysis — model comparison

Cross-model comparisons sourced from artificialanalysis.ai instead of training-data recall. Use this skill whenever a model-performance question comes up.

## When to invoke

Triggers (any of these):
- "compare X and Y" where X/Y are models
- "which model is best for coding / math / reasoning / writing"
- "fastest model" / "cheapest model" / "tokens per second"
- "what's the intelligence index for X"
- "Elo for image / video / TTS / image-edit models"
- model release questions where benchmarks are relevant
- pricing questions ("$ per million tokens")

## When NOT to invoke

- Question is about a vendor SDK feature (prompt caching, tool use, etc.) — use a vendor-specific skill
- Question is about *running* a model locally (vLLM/ollama config) — different problem

## Usage

CLI lives at `./aa.py`. Reads API key from `pass api-keys/artificialanalysis` (or `AA_API_KEY` env var). Caches each endpoint at `~/.cache/artificial-analysis/<endpoint>.json` for 1h.

### LLMs

```bash
# Top N by metric (intelligence|coding|math|speed|tps|cheap)
aa.py llms --top intelligence 10
aa.py llms --top coding 5
aa.py llms --top cheap 10

# Filter by creator
aa.py llms --creator anthropic
aa.py llms --creator openai --top intelligence 5

# Specific models by slug or name
aa.py llms --slugs gpt-5-5-high,claude-opus-5-5,gemini-3-1-pro-preview

# Substring search
aa.py llms --search opus

# Force refresh (bypass 1h cache)
aa.py llms --refresh --top intelligence 10

# Raw JSON (when you need fields the table doesn't show)
aa.py llms --slugs gpt-5-5-high --raw
```

Default columns: name, creator, intel, code, math, tps, ttft, $/1M(blended 3:1).

### Media endpoints (Elo leaderboards)

```bash
aa.py text-to-image
aa.py image-editing
aa.py text-to-speech
aa.py text-to-video
aa.py image-to-video
```

Each prints `name<TAB>elo`.

## Reading the data

- **artificial_analysis_intelligence_index** — composite, 0-100, primary headline metric
- **artificial_analysis_coding_index** — coding-specific composite
- **artificial_analysis_math_index** — math-specific composite
- **median_output_tokens_per_second** — generation speed (higher = faster)
- **median_time_to_first_token_seconds** — TTFT latency (lower = snappier)
- **price_1m_blended_3_to_1** — blended $/1M tokens at 3:1 input:output ratio (typical chat)
- **price_1m_input_tokens** / **price_1m_output_tokens** — split pricing

For reasoning models, AA reports the *reasoning effort tier* in the model name (e.g. "GPT-5.5 (high)", "Claude Opus 4.7 (Adaptive Reasoning, Max Effort)"). When comparing, compare like-with-like effort tiers.

## Output

Don't dump the full table unless asked. Pull the 3-5 rows that answer the question and format inline:

> Top 3 by coding (May 2026): GPT-5.5 high (58.5), Gemini 3.1 Pro (55.5), GPT-5.4 xhigh (57.3). Opus 4.7 trails at 52.5 but ~$10.9/1M vs GPT-5.5 at $11.25.

Cite the metric and the relative gap, not just the leaderboard order.

## API reference

- Docs: https://artificialanalysis.ai/api-reference
- Base: `https://artificialanalysis.ai/api/v2`
- Auth: `x-api-key` header
- Rate limit: 1,000 req/day (free tier) — cache covers 99% of repeat queries
- Endpoints: `/data/llms/models`, `/data/media/text-to-image`, `/data/media/image-editing`, `/data/media/text-to-speech`, `/data/media/text-to-video`, `/data/media/image-to-video`
