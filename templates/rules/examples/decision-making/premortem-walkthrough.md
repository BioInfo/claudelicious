# Premortem walkthrough — "should we migrate to Postgres?"

A worked example of the [`decision-making.md`](../../decision-making.md) rule firing on a hypothetical decision.

## The trigger

> "I'm thinking we should migrate our app database from MongoDB to Postgres. We've outgrown the document model — half our queries are joins now and we're doing aggregation in app code. Should we do it?"

The rule triggers on "I'm thinking", "should we", and on irreversible-ish architecture choices. So Claude offers a premortem before answering.

## The premortem

> *Imagine it's November 2026. The migration shipped six months ago and it failed badly. Here's the post-mortem from that future.*

### What went wrong (5 specific failure modes, named mechanisms)

1. **The migration ran for 8 weeks instead of 2.** The dev team underestimated the schema-translation work — many fields were polymorphic in Mongo (sometimes string, sometimes object, sometimes array). Postgres needs typed columns, so each polymorphic field forked into 2-3 columns plus a discriminator, which broke every read query that touched them. ORM regeneration alone took 3 weeks.

2. **A backfill bug corrupted 40,000 records.** The migration script handled `null` and missing fields differently than the old code did, and 40K records ended up with `created_at = epoch_zero` instead of their original timestamps. Discovered 5 weeks post-cutover when a customer reported their account looked 56 years old. No clean rollback because the writes had continued.

3. **Read latency p99 doubled.** Queries that were O(1) document fetches in Mongo became 4-table joins in Postgres. The team didn't add the right composite indexes until production traffic hit, then spent two weeks tuning. Customers churned during the slow window.

4. **The team lost two engineers.** The senior backend lead burned out on the 8-week slog; another engineer quit because they specifically liked working with Mongo. Hiring took 3 months to backfill.

5. **The thing they wanted from Postgres — joins — turned out to be the wrong primitive.** The actual pain wasn't the query language; it was that the data model was wrong (over-normalized into separate Mongo collections). After migration, the joins were faster but still ran 30+ms because they were joining tables that should have been a single denormalized view. They ended up doing the denormalization in Postgres anyway.

### Top 2 mitigations (back into the present)

1. **Run a 2-week schema audit BEFORE committing to the migration.** Catalog every polymorphic field. Estimate translation cost honestly. If translation cost > the migration's projected payoff, the answer is "redesign the data model in Mongo first, migrate later if still needed."

2. **Plan the cutover as dual-write for 4 weeks, not big-bang.** Write to both DBs, read from old, validate parity in shadow, then flip reads. This catches backfill bugs before they corrupt anything because the old data is still authoritative.

## The actual recommendation

> Based on the premortem, my honest take: don't migrate yet. The "we're doing joins in app code" pain is real, but 4 of the 5 failure modes I just named come from translating a messy Mongo schema, not from Postgres being wrong. Spend the next sprint cleaning up the Mongo schema (consolidating the polymorphic fields, denormalizing the over-split collections). Then re-evaluate. If the joins still hurt after the cleanup, the migration is much safer because you've already paid the schema-design cost.
>
> If you do migrate, the dual-write window and the schema audit are non-negotiable. The 8-week timeline above isn't pessimism — it's what happens when you don't budget those.

## What this example shows

- The premortem doesn't decide for you — it surfaces specifics that gut-feel arguments paper over
- Naming **mechanisms** ("polymorphic fields fork into multiple columns") beats vague risks ("migration might be hard")
- The conclusion can be "don't do it" or "do it but differently" — the rule explicitly says "be willing to conclude no real failure modes, proceed"
- Mitigations come from inverting the failure modes, which is why writing the failures first matters

## When this rule fires

- "Should we adopt X?" / "Should we migrate to Y?"
- New vendor / partner / hire decisions
- Anything described as "obvious" or "clearly the right call" (those are the ones that bite)

## When it doesn't

- Already-decided executions (you said go, I run)
- Reversible edits ("change this function name")
- Time-sensitive responses where the decision is downstream of a hard deadline
