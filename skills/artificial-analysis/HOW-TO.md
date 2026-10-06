# How to use the `artificial-analysis` skill

A Claude Code skill that grounds model-comparison questions in live data from [artificialanalysis.ai](https://artificialanalysis.ai) instead of training-data recall.

## What it does

Triggers automatically when you ask things like:

- "compare Opus 4.7 and GPT-5.5 on coding"
- "fastest open-source model under 50B"
- "cheapest model with reasoning"
- "what's the Elo for image-edit models right now"

Returns a 3-5 row answer with the relevant metrics (intelligence, coding, math, tokens/sec, TTFT, $/1M tokens), not the full leaderboard.

## Setup (5 minutes)

### 1. Get an API key

Sign up at [artificialanalysis.ai](https://artificialanalysis.ai) → org settings → API access. Free tier gives you 1,000 requests/day, which is way more than you need (the skill caches each endpoint for 1 hour).

### 2. Store the key

Pick whichever fits your setup:

**Option A — environment variable (simplest):**
```bash
export AA_API_KEY="aa_yourkeyhere"
# Add to ~/.zshrc or ~/.bashrc to persist
```

**Option B — `pass` (recommended if you already use it):**
```bash
pass insert artificialanalysis/api-key
# Paste your key when prompted
```

The skill checks `AA_API_KEY` first, falls back to `pass`.

### 3. Drop the skill into Claude Code

```bash
# From the claudelicious repo root:
cp -r skills/artificial-analysis ~/.claude/skills/

# Or symlink so updates flow through:
ln -s "$(pwd)/skills/artificial-analysis" .
```

Skills are auto-discovered on the next Claude Code session start. No restart needed if you launch a new conversation.

### 4. Test it

In Claude Code:
```
which model has the best coding score right now
```

Claude should invoke the skill, fetch the data, and reply with a short ranked answer. First call hits the API; subsequent calls within an hour use the local cache at `~/.cache/artificial-analysis/`.

## CLI usage (without Claude)

You can also run the script directly:

```bash
# Top 10 by intelligence
./aa.py llms --top intelligence 10

# Specific models head-to-head
./aa.py llms --slugs gpt-5-5-high,claude-opus-5-5

# Filter by creator
./aa.py llms --creator anthropic

# Force refresh (bypass cache)
./aa.py llms --refresh --top coding 5

# Media leaderboards
./aa.py text-to-image
./aa.py text-to-speech
```

Pass `--raw` to get JSON instead of the formatted table — useful when you want fields the default columns don't show.

## Metrics primer

| Field | Meaning |
|---|---|
| `intelligence_index` | Composite quality score, 0-100 — primary headline metric |
| `coding_index` | Coding-specific composite |
| `math_index` | Math-specific composite |
| `median_output_tokens_per_second` | Generation speed (higher = faster) |
| `median_time_to_first_token_seconds` | Latency to first token (lower = snappier) |
| `price_1m_blended_3_to_1` | $/1M tokens at 3:1 input:output (typical chat ratio) |

For reasoning models, AA tags the effort tier in the model name ("GPT-5.5 (high)", "Opus 4.7 (Adaptive Reasoning, Max Effort)"). Compare like-with-like effort tiers when ranking.

## When this skill is the right answer

- Pre-purchase decision: which API to wire into a new app
- Spec-checking a vendor claim ("our model is 30% faster than X")
- Filtering candidates for self-hosting (size + speed + license)
- Sanity-checking a press-release benchmark before quoting it

## When it's not

- You need to *run* the model locally (use `vllm`/`ollama` skills instead)
- You're benchmarking your own deployment (this is vendor-published data, not your stack)
- The model is too new to be on AA yet (check the [supported models list](https://artificialanalysis.ai/models))

## Examples

See [`examples/`](examples/) in this repo for worked examples.

## Troubleshooting

**`error: no API key`** — set `AA_API_KEY` or run `pass insert artificialanalysis/api-key`.

**Stale data?** Cache is 1h. Force refresh with `--refresh` or delete `~/.cache/artificial-analysis/`.

**Model not in results?** AA adds new models on a delay. Check [their model list](https://artificialanalysis.ai/models). If it's not there yet, you'll need to wait or use a different source.
