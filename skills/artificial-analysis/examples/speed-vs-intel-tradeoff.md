# Speed vs intelligence — finding the Pareto frontier

**Asked May 2026.** Skill output sorted twice (intel desc, then tps desc) to find models that aren't dominated by anything else on both axes.

## Question

> "Show me the speed-vs-intelligence Pareto frontier — I want models that aren't dominated by anything else on both axes."

## How the skill answered

A Pareto-frontier query isn't a built-in mode, so this is the skill's data + a few lines of post-processing. The skill returns the JSON; the answer composes from it.

```python
# After: aa.py llms --raw > all.json
import json
models = json.load(open("all.json"))
points = []
for m in models:
    ev = m.get("evaluations") or {}
    intel = ev.get("artificial_analysis_intelligence_index")
    tps = m.get("median_output_tokens_per_second")
    if intel is None or tps is None:
        continue
    points.append((m["name"], intel, tps))

# Pareto frontier: no other model has BOTH higher intel AND higher tps
frontier = []
for name, intel, tps in points:
    dominated = any(i > intel and t > tps for _, i, t in points)
    if not dominated:
        frontier.append((name, intel, tps))

for name, intel, tps in sorted(frontier, key=lambda x: -x[1]):
    print(f"{name:40} intel={intel:5.1f}  tps={tps:6.1f}")
```

## Frontier (May 2026)

```
GPT-5.5 (xhigh)                          intel= 60.2  tps= 75.1
Gemini 3.1 Pro Preview                   intel= 57.2  tps=121.3
Claude Opus 4.7 (Adaptive Reasoning)     intel= 55.9  tps= 89.7
Gemini 3 Flash (Reasoning)               intel= 50.4  tps=178.6
Qwen3.6 35B A3B (Reasoning)              intel= 43.5  tps=187.5
gpt-oss-20B (high)                       intel= 24.5  tps=282.4
Qwen3.5 0.8B (Non-reasoning)             intel=  9.9  tps=364.5
```

(Numbers shift weekly. Re-run the skill to see today's frontier.)

## Reading the frontier

Each row is **non-dominated** — for any model on the frontier, no other model has BOTH higher intelligence AND higher speed. Picking a different point on the frontier means making a deliberate tradeoff.

Notable transitions:

- **60→57 intel costs nothing in tps** — Gemini 3.1 Pro is faster than GPT-5.5 xhigh while only 3 points behind on intel. Strong default for general work.
- **57→50 intel buys 60% more speed** — Gemini 3 Flash Reasoning at 178 tps vs Opus 4.7 at 90 tps.
- **50→43 buys speed and dramatic cost cut** — Qwen3.6 35B A3B is open-weight, $0.56/1M vs $4.50+ for the proprietary frontier.
- **43→24 is the steep part of the curve** — losing 19 intelligence points to gain 100 tps. Probably not worth it unless latency is the entire game.

## Use this when

- You're picking a default model for a new app and need to defend the choice
- A vendor pitched you a "fastest model" claim and you want to see whether they're on the frontier or just on a slow path
- You're building a router that picks model by query complexity — the frontier tells you which models are worth routing to at all

## What this example shows

- The skill returns structured data; the value is in what you compose with it
- Pareto framing turns "best model" debates into "pick your tradeoff" conversations
- A handful of models dominate the entire space; everything off the frontier is a worse pick on some axis with no upside
