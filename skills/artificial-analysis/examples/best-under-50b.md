# Best and fastest open-source model under 50B

**Asked May 2026.** Pulled live from Artificial Analysis — re-run today and the numbers will move.

## Question

> "I want to know the best and fastest model under 50B that is open source."

## Skill output

The skill triggers on "best", "fastest", and "under 50B". Pulls all LLMs, filters to open-weight families with total or active params ≤ 50B, sorts twice (by intelligence, then by tokens/sec), and reports the tradeoff.

```
=== TOP by INTELLIGENCE (open-weight, ≤~50B) ===
name                              intel    code     tps   ttft    $/1M
Qwen3.6 27B (Reasoning)            45.8    36.5    64.1   1.47   1.350
Qwen3.6 35B A3B (Reasoning)        43.5    35.1   187.5   1.43   0.557
Qwen3.5 27B (Reasoning)            42.1    34.9    89.8   1.38   0.825
Gemma 4 31B (Reasoning)            39.2    38.7    34.8   1.03   free
Qwen3.5 27B (Non-reasoning)        37.2    33.4    92.4   1.49   0.835

=== TOP by SPEED ===
gpt-oss-20B (high)                 24.5    18.5   282.4   0.36   0.088
Qwen3.5 Omni Flash                 25.9    14.0   239.0   0.93   0.275
gpt-oss-20B (low)                  20.8    14.4   237.1   0.40   0.095
Qwen3.5 4B (Reasoning)             27.1    17.5   199.8   0.24   0.060
Qwen3.6 35B A3B (Non-reasoning)    31.5    17.6   189.2   1.46   0.844
```

## Recommendation

**Qwen3.6 35B A3B (Reasoning)** wins the "best AND fastest" framing.

| Model | Intel | TPS | $/1M | Notes |
|---|---|---|---|---|
| **Qwen3.6 35B A3B (Reasoning)** | **43.5** | **187** | $0.56 | MoE: 35B total, 3B active. 95% of Qwen3.6-27B's intelligence at 3x the speed. |
| Qwen3.6 27B (Reasoning) | 45.8 | 64 | $1.35 | Highest pure intelligence under 50B, dense. |
| gpt-oss-20B (high) | 24.5 | 282 | $0.09 | Highest pure speed with usable intel. Apache 2.0. |

## Why 35B A3B

The MoE architecture is the unlock — 35B total weights (memory footprint of a 35B dense model) but only 3B activated per token (compute of a 3B). That's why it scores nearly identical intelligence to dense 27B while running 3x faster.

## When to pick something else

- **Pure intelligence matters more than speed** → Qwen3.6 27B dense (45.8 vs 43.5)
- **Pure speed matters more than intelligence** → gpt-oss-20B high (282 tps, 24.5 intel) — useful for high-volume agentic work where latency dominates
- **Free hosting / Apache 2.0 license matters** → gpt-oss-20B (OpenAI released under Apache 2.0)

## What this example shows

- The skill doesn't dump the full leaderboard — it pulls 5 rows that answer the question
- Speed and intelligence are a tradeoff; the skill names the tradeoff explicitly instead of picking a single "best"
- MoE architectures break the size-vs-speed assumption — total params != compute
