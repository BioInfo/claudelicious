---
name: post-update
description: >
  Dispatch an already-approved status update to a channel (chat, social, a
  webhook) via a CLI. ALWAYS invoke when the user says "post the update",
  "send the update", "broadcast this", after they have approved the text. This
  is a DISPATCH point, not an author — it never writes the content itself.
agent: cli-runner
allowed-tools: Bash
disable-model-invocation: false
---

# post-update

The hands, not the author. This skill takes text that was already drafted in the
main session and approved by the user, and shells out the send command. It is the
canonical shape for any skill that posts, sends, or publishes on your behalf.

<!-- protected:start reason="dispatch-only contract" -->
## DISPATCH-ONLY CONTRACT

This skill MUST NOT compose or edit the message it sends. The content is drafted
in the main session by the strongest model, shown to the user, and explicitly
approved BEFORE this skill is invoked.

If this skill is invoked with an instruction to *write* the update (e.g.
"post an update about the launch"), STOP and refuse. Respond: "Draft the update
in the main session, get approval, then invoke me with the approved text." Do not
generate the content here. The judgment and the voice stay with the main session;
only the mechanics are automated.
<!-- protected:end -->

## Procedure (once approved text is in hand)

1. Confirm you were handed the exact approved text. If you were handed a *topic*
   instead of finished text, invoke the contract above and stop.
2. Dispatch via the channel CLI, e.g.:
   `<your-cli> post --channel "<channel>" --text "<approved text>"`
3. Report the result (the post URL / message id, or the error verbatim). Do not
   silently retry on failure — surface it.

## Notes

- One send per invocation. Do not fan out to multiple channels unless the user
  approved each.
- Never send on a guess. No approved text, no send.
