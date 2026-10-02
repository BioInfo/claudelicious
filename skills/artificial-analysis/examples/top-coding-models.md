# Top coding models right now

**Asked May 2026.** Re-run the skill to get current numbers — leaderboard moves weekly.

## Question

> "Which model has the best coding score right now?"

## Skill output

```
$ aa.py llms --top coding 5

name                       creator   intel   code    tps    ttft   $/1M
GPT-5.5 (xhigh)            OpenAI    60.2    59.1    75.1   37.3   11.25
GPT-5.5 (high)             OpenAI    58.9    58.5    69.7   13.9   11.25
GPT-5.4 (xhigh)            OpenAI    56.8    57.3    77.8  160.0    5.63
GPT-5.5 (medium)           OpenAI    56.7    56.2    72.0    6.1   11.25
Gemini 3.1 Pro Preview     Google    57.2    55.5   121.3   24.0    4.50
```

## Reading this

GPT-5.5 sweeps the top 4 (across effort tiers), then Gemini 3.1 Pro Preview slots in at #5.

But the picture changes once you factor cost and latency:

| Pick if you optimize for... | Choose | Why |
|---|---|---|
| Pure coding score | GPT-5.5 (xhigh) | 59.1, top of the table |
| Coding score per dollar | Gemini 3.1 Pro Preview | 55.5 at $4.50/1M vs GPT-5.5 at $11.25 (60% cheaper, ~94% the score) |
| Coding score under 30s TTFT | GPT-5.5 (high) | 58.5 with 13.9s TTFT vs xhigh's 37.3s |
| Cheap coding with reasoning | GPT-5.4 (xhigh) | 57.3 at $5.63/1M — half the cost of GPT-5.5 |

## Anthropic / Claude?

Not in the top 5 by coding score this month. Run `aa.py llms --creator anthropic --top coding 5` to see where Opus 4.7 lands and how the gap looks.

## What this example shows

- "Best at X" is rarely a one-row answer when cost and latency are in play
- Effort tiers matter a lot (xhigh vs high vs medium can swing scores by 5+ points and TTFT by 30+ seconds)
- The skill returns ranked rows; the editorial work is naming the cost/latency tradeoff explicitly
