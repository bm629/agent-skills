# The evidence tier — how an item gets ranked, and what ranking is not

A register is read top-down, so the ordering is the most consequential thing the survey
produces. This rubric fixes what that ordering is made of.

## The three tiers

| tier | meaning | what puts an item here |
|---|---|---|
| **1** | exploited in the wild against products like ours | listed in a known-exploited catalog, or a matching real-world incident from the incident or disclosure corpora |
| **2** | proven exploitable, not observed here | a public proof-of-concept, an exploit-archive entry, a detection template, or a high exploitation-probability score |
| **3** | documented pattern, no observed exploitation | a catalog entry, a control requirement, or a weakness class with nothing behind it |

Tier 3 is not a failing grade. Most of what a control-standard angle produces is tier 3 by
construction, and that is the point: those are the requirements that hold whether or not anyone
has attacked you yet.

## Why evidence and not a score

The ordering is deliberately **not** a computed risk number. Three model estimates multiplied
together produce a figure that looks precise, has no traceable basis, and cannot be checked by
anyone — a nine and a twelve are indistinguishable claims. Tiers are checkable: either the
identifier is in the catalog or it is not; either a disclosed incident exists or it does not.

This is also why every tier-1 or tier-2 record must carry its evidence with a reference and a
read date. A tier claim with nothing behind it is exactly the failure the tiering was adopted
to prevent, and the validator rejects it.

## The published ordering this follows

The relationship between the three common signals is not this skill's invention, and it matters
that they are used in the right roles:

- **A severity score establishes a floor**, not a rank. It says how bad the outcome is if
  exploited, and says nothing about whether anyone is exploiting it.
- **An exploitation-probability score ranks within a severity band.** It is a short forward-
  looking window — typically thirty days — which is why it is meaningless without the date it
  was read, and why it must never be recorded as a durable property.
- **Evidence of actual exploitation supersedes the probability**, because the probability is
  computed before threat intelligence arrives. Once something is known-exploited, its predicted
  likelihood is no longer the interesting number.

So: catalog membership or a matching incident outranks a high probability score, which outranks
a documented pattern. Severity never moves an item between tiers — it orders items *within*
one.

## What a proof-of-concept does and does not prove

A public exploit, a framework module or a detection template means someone made the weakness
work in at least one environment. It is real evidence and it earns tier 2.

It does not establish that this product is affected, that the vulnerable path is reachable, or
that the deployment exposes it. Those are architecture questions about a system that does not
exist yet. The record's "what this does not establish" section exists to say so explicitly,
because a tier-2 row read carelessly becomes a claim about the product rather than about the
weakness.

## Ordering within a tier

By impact on the product's assets, stated as reasoned judgment naming the asset — "the payout
destination field, which controls where money goes" — not as a number. The judgment is visible
and arguable, which is the property a number would destroy.

## What never changes a tier

- How severe the score is.
- How recent the item is.
- How prominent the source is.
- How much the finding would matter if true.

Each of those is a reason to order items *within* a tier, or to write a sharper relevance line.
None is evidence of exploitation, and letting any of them promote an item is how a register
stops meaning what it says.
