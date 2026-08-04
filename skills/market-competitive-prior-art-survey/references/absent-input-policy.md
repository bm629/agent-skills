# Absent-input policy

What to do when the context you were handed is missing something you need. The rule in one
line: **proceed on what you have, and record what you assumed — never fabricate, and never
stop.**

## Why inference rather than a default or a halt

Three options exist when an input is missing, and two are worse.

**Halting** turns a survey into a support ticket. Most missing inputs are recoverable from
signals already present, and a survey that stops on the first gap never runs at all in the
messy real cases it exists for.

**A silent default** is the dangerous one. If an absent audience quietly becomes `b2b`, the
downstream reader cannot tell an inferred value from a stated one, and every conclusion that
rests on it inherits a confidence nobody granted. That is how an assumption becomes a fact.

**A recorded inference** keeps the run moving and keeps the seam visible. The value is used,
and it is used *as an assumption*, listed with the signal it came from, where a reviewer can
challenge it and a later reader can discount it.

## The record

Every forced value lands in the map's `assumptions` block:

```yaml
assumptions:
  - input: business.model
    assumed: saas
    inferred_from: >
      The scope describes a hosted multi-tenant product with tiered pricing; no explicit model
      field was supplied.
```

Three fields, all required. `inferred_from` must name a **signal**, not a rationale — "it
seemed likely" is not a signal; "the scope names tiered hosted pricing" is.

An assumption is never folded into the scope as though the caller had stated it, and it is
never used to justify a *further* inference. One hop only: an inferred audience does not then
license an inferred segment.

## Per-input fallbacks

| Missing | Do this | Never |
| --- | --- | --- |
| Category / market name | Derive from the capability nouns and the job phrasing; record it | Invent an industry label |
| Audience segment | Infer from the scope's own description of who it is for | Default to `b2b` silently |
| Seed products | Leave `seed-product` absent and **declare it** in `scope_guard.absent_types` | Guess an incumbent |
| Business model | Infer from pricing/distribution signals in the scope | Assume commercial |
| An angle's precondition input | Treat the disjunct as false — absent input means not-in-set | Assume it holds |

The `seed-product` row matters most. It is the highest-leverage group in the map, because the
alternatives graph is densest around a named incumbent — but a *guessed* incumbent sends the
whole angle into the wrong market. Declaring the absence costs one line and is honest; guessing
costs the run.

## Absent inputs versus empty results

These look alike downstream and are not:

- **Absent input** — you were never given something. Goes in `assumptions`.
- **Declared-absent group type** — the type genuinely has no members here. Goes in
  `scope_guard.absent_types` with a reason. A type that is neither present nor declared is a
  silent omission, and it silently empties every angle that depends on it — which the gate
  rejects.
- **Empty result** — you searched and found nothing. That is a zero-hit coverage cell, and it is
  a *finding*, recorded with the query that produced it.
- **Unreachable source** — you could not search. A typed cell failure with a cause.

Collapsing any of these into any other is the failure this whole survey is built to prevent.

## When there is genuinely not enough

If the scope is too thin to produce a map at all — no capability nouns, no domain, nothing to
derive a category from — say so plainly in the map's `meta` and produce what you can rather
than padding. A thin-but-honest map is correct output for a thin scope, and a reviewer must not
revise it for thinness alone. Padding a map to look substantial manufactures queries that
return noise, and every false candidate costs a full deep read later.
