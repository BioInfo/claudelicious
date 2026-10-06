# 09 — Multi-provider: Claude Code on other models

Claude Code is a harness, and a harness is not married to one model. You can point it at Kimi, MiniMax, GLM, or a local Qwen and keep every skill, hook, and memory you built. This is one of the bigger unlocks in the whole setup: a weekly subscription to another lab becomes a drop-in engine for the same harness you already trust, and you switch with one command.

It takes some tuning. The harness assumes Anthropic's API in a few places, and a different model behind the same endpoint needs those assumptions made explicit. Here is the whole recipe.

---

## The architecture

Do not put a provider's raw API key in the client. Route everything through a gateway (a self-hosted LiteLLM instance works well). The gateway holds the real provider keys; the client carries only a gateway-scoped virtual key. That gives you per-host spend attribution, rate caps, and one place to rotate credentials.

```
Claude Code client
   ANTHROPIC_BASE_URL  = <gateway-host>:4000
   ANTHROPIC_AUTH_TOKEN = <virtual key>
        │
        ▼
   LiteLLM gateway  ──►  maps model name → provider API
                    ──►  holds the real keys (kimi, minimax, glm, qwen)
                    ──►  logs spend per key
```

Claude Code speaks the Anthropic API shape. The gateway translates that to whatever the provider speaks, so the client never knows the difference.

---

## The launcher pattern

Wrap each provider in a shell function that sets the environment, then launches `claude`. The shared setup clears Anthropic-specific variables and points the client at the gateway:

```bash
# shared, runs for every non-Anthropic mode
unset ANTHROPIC_MODEL ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN
export ANTHROPIC_BASE_URL="$GATEWAY_URL"
export ANTHROPIC_AUTH_TOKEN="$(pass show <your-vk-path> | head -1)"
export API_TIMEOUT_MS=3000000
```

Then a per-provider alias pins the model and the output ceiling. The trick most people miss: the client thinks in three tiers (Opus, Sonnet, Haiku). A single-model provider needs all three pointed at its one model, or tier routing fails:

```bash
# example: a single-model provider
export ANTHROPIC_DEFAULT_OPUS_MODEL="<provider-model>"
export ANTHROPIC_DEFAULT_SONNET_MODEL="<provider-model>"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="<provider-model>"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000   # provider-specific
claude --dangerously-skip-permissions \
       --disallowedTools WebSearch WebFetch \
       --append-system-prompt "$PROVIDER_PROMPT"
```

`cki`, `cmin`, `cglm`, `cqwen`: one short alias per engine, and `cmax` to reset back to Anthropic. Switching providers is now a four-keystroke decision.

---

## What you must tune or turn off

| Setting | Why | What to do |
|---------|-----|------------|
| `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` | route to the gateway, authenticate with a virtual key | set both |
| The three tier model vars | a single-model provider has no Opus/Sonnet/Haiku split | point all three at the one model |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | providers cap output lower than Anthropic | set per provider (32K to 64K) |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | adaptive thinking is an Anthropic-API feature | set to `1` for providers that do not support it |
| `WebSearch` / `WebFetch` | the built-in web tools hit Anthropic infrastructure, not your gateway | disable with `--disallowedTools`, route web through an MCP instead |
| agentic child endpoint | a `claude -p` child needs reasoning_content preserved | use the gateway's coding/anthropic endpoint, not a generic `/v1` (a generic endpoint drops reasoning and the child loops) |

For the disabled web tools, give the model the replacement in the appended system prompt: tell it the gateway has no WebSearch or WebFetch, and to use your self-hosted scraping MCP instead. State it plainly so the model does not waste turns rediscovering it.

---

## Per-provider quirks

These come from running the providers, not from their docs.

- **Kimi.** Strong, large context, but parallel tool calls fail at a meaningful rate on a busy week. Prefer sequential calls; push heavy fan-out elsewhere. Thinking is keyword-driven (a `[[think]]` / `[[fast]]` prompt convention) rather than a tier toggle.
- **MiniMax.** Aggressive rate limiting on concurrent tool calls. Keep tool use sequential.
- **GLM.** Handles concurrency well, high output ceiling. A good default for fan-out work.
- **Qwen (local).** No rate limit because it runs on your own hardware. Parallel calls are fine. Disable adaptive thinking; it is not supported.

The general rule when a provider throws a 429 or times out: switch models, do not retry the same one into the wall.

---

## Wiring a new provider, step by step

1. Add the model to your gateway with the provider's key, and give it a route name.
2. Mint a virtual key for the client and store it in your password manager.
3. Write a launcher alias: set the base URL and auth token, pin the three tier vars to the model, set the output ceiling, disable adaptive thinking if needed.
4. Disable WebSearch/WebFetch and append the system prompt that points web work at your MCP.
5. Test a real completion through it before trusting it: a tool call, a multi-step task, not just a "hello." Confirm spend is logging on the gateway.

---

## Delegation: spending the cheap lanes on purpose

Doc 09 got you the engines. This is the discipline for using them.

Once you can point the harness at a flat-rate model, the flagship model's metered quota stops being the only place work runs. So stop spending it on grunt work. A wide, mechanical refactor, a batch of near-identical edits, a boilerplate generation pass: none of that needs your best model. Push it to a flat-rate lane and keep the expensive quota for the work only the flagship does well.

Wrap this in a `delegate` skill that launches the cheap engine as a `claude -p` child through your gateway. The one rule that keeps it safe: **it is opt-in.** It fires only when you name it. A bare "handle this" still runs on the flagship. You decide, per task, that the work is mechanical enough to send down.

**What never delegates.** Judgment, voice, and architecture stay on the flagship, in your main context. The moment a task needs taste, a design call, or writing in your own voice, it is not a delegation candidate. The cheap lane is a factory floor, not a design studio.

**Match the lane to the shape of the work.** Not every engine wants every job. A fan-out-safe lane takes parallel batch edits across many files. A sequential lane takes a multi-tool agentic loop where one step feeds the next. A long-context lane takes one big read-and-summarize. Sending a fan-out job to a sequential engine buys you a wall of rate-limit errors, so pick the lane by the work's shape, not by which alias you typed last.

**The non-negotiable part: verify everything yourself.** The flagship writes the full spec before the child ever launches: the task, the scope, the acceptance criteria, and the gate that proves the work is done. Then the flagship checks the result itself. Read the git diff. Run the gate. You never trust the child's "done," because a cheaper model saying it finished is a claim, not evidence. The child does the typing; the flagship owns the outcome.

Done right, you spend pennies on the volume and keep the flagship for the calls that matter.

---

## Ship / scrub

- The architecture, the launcher pattern, the tuning table, and the per-provider quirks are generic. Ship as-is.
- Replace the gateway host, the virtual-key path, and any model route names with placeholders before sharing.
- Never put a raw provider key in a launcher. The whole point of the gateway is that the client never holds one.
- The delegation discipline (opt-in, judgment stays on the flagship, verify every result yourself) ships as-is; strip your specific lane aliases and provider names.
