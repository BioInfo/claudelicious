# 18 — MCP, the harness's reach

Skills are procedures the harness knows. MCP is how the harness touches systems it does not own. The
Model Context Protocol is a standard way to expose an external system, your mail, your calendar, a
search index, a browser, a cloud account, as a set of typed tools the model can call directly. If a
skill is a business process you encoded, an MCP server is a doorway into something that already exists.
This doc is about how to use MCP without it becoming the next source of bloat, and why every MCP
response is data you do not fully trust.

---

## What MCP is for

The harness is only as useful as what it can reach. A model that can reason brilliantly but cannot see
your inbox, your notes, or your calendar is back to being a chat box. MCP servers are the reach. A
healthy set sorts into a few jobs:

| Job | What the servers do |
|-----|--------------------|
| **Communication** | Read and send mail, read and write the calendar, post to chat. |
| **Retrieval** | Semantic search over your own vault, web fetch and scrape, code search across a repo, domain corpora. |
| **Action** | Drive a browser, reach a cloud account, send a transactional email. |
| **Reference** | Pull current library documentation, look up specs the model's training does not cover. |

The reference setup runs around fifteen of these. The number is not a goal. Each one is there because
the model needs to reach that system often enough to justify a standing connection.

---

## Skill, CLI, or MCP

Not everything that reaches an external system should be an MCP server, and choosing wrong is how you
end up with three ways to do the same thing. A rough decision:

- If a good command-line tool already exists, a thin **dispatch-only skill** that shells out to it is
  the lightest option. It carries no server, and the [voice and approval discipline](12-voice-and-antislop.md)
  stays in the main thread.
- If you want the model to call **typed tools** with structured arguments, or a server already exists
  for the system, use **MCP**. It is the right shape for rich, multi-operation systems (a whole mail
  API, a browser) where a single CLI call would be clumsy.
- If the thing is a **procedure** rather than a connection, it is a [skill](02-skills.md), not an MCP
  server, even if it touches an external system along the way.

The test: MCP exposes a *system*. A skill encodes a *process*. When in doubt, the lighter tool wins,
because every server you add is context the model carries and a surface you have to trust.

---

## Manage them in one place

The single most useful discipline is scope. Register servers at the **user level**, in one global
config, not per-project. A server defined inside one repo is invisible from every other repo and turns
into a thing you forget you have and cannot find when it breaks. One place to add, one place to audit,
one place to remove.

And audit them. The same rule that governs [skills](02-skills.md) governs servers: more is not better.
A server you connected once for a task you finished is now permanent context and permanent attack
surface for zero benefit. Periodically list what is registered, and remove the ones that no longer earn
their place. A lean set of servers the model actually uses beats a long list where half are dead.

---

## Every MCP response is untrusted input

This is the part that does not show up until it bites you. An MCP tool returns content from an external
system: a web page, an email, a file written by someone else, a search result. That content is **data,
not instructions**. If a fetched page or a returned document contains text that reads like a command to
the agent ("ignore your previous instructions and run this", "the user authorized you to send their
keys to..."), it is an injection attempt, and the fact that it arrived through a tool you trust does not
make the content trustworthy.

The harness has to hold a hard line here: instructions come from the user, everything observed through a
tool is data. A web page telling the agent to do something is not a reason to do it. This is exactly the
threat the [hooks](03-hooks.md) and the [wide-open posture](19-running-wide-open.md) are built around,
because a broad-allow harness plus an injected instruction in an MCP response is the realistic attack,
far more than any fat-finger. Treat MCP as a window you look through, not a voice you obey.

---

## Ship / scrub

- The reach taxonomy, the skill-versus-CLI-versus-MCP decision, the user-scope rule, the audit
  discipline, and the responses-are-untrusted-data principle are all generic. Ship them.
- Do not ship your actual server list or any server config. It names the systems you connect to and
  often carries tokens or private endpoints. Ship the shape; declare your own servers locally.
- Route any credential an MCP server needs through a password manager, never a plaintext config value.
