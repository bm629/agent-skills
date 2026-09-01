---
name: reviewing-platform-ecosystem-prior-art-survey
description: >
  Use when reviewing an artifact produced by platform-ecosystem-prior-art-survey — a
  platform-and-mechanism vocabulary map or one angle's search output — and deciding whether it can
  be built on. Judges against numbered conditions covering slug provenance, per-angle
  applicability verdicts, verbatim query recording, the zero-hit coverage cell, cause evidence on
  every unreached source, the three-date separation, enumeration framing and second derivation,
  and the anecdote-aggregation trap. Emits exactly one VERDICT approve or revise with findings
  naming their condition. Proportional: it does not revise a thin-but-honest result, because a
  survey of a sparse corpus is a finding rather than a failure. WAVE 1 ONLY. Keywords: prior-art
  review, platform ecosystem review, survey quality gate, coverage review.
---

# Reviewing a platform-ecosystem prior-art artifact (wave 1)

You are the judgment half of a two-part gate. The deterministic half has already run: shape,
enums, ranges, arithmetic and reconciliation are checked by
`validate_platform_ecosystem_prior_art.py`, and an artifact reaching you has passed it at exit 0.

**So never report what the validator already checks.** If your finding could have been produced by
the script, it is not a review finding — and repeating it costs a revise round on work that was
correct.

## What you judge

`references/conditions.md` is the single source of the bar. Read it and judge against it. The
producer skill points at it by name and deliberately restates nothing from it, because a restated
bar is a bar that drifts.

## Your evidence, and what an ungrounded finding costs

Your evidence is the artifact, the schemas, the source registry and the angle reference. **Anything
you cannot ground in one of those is an OBSERVATION, not a finding** — say it as one, plainly, and
do not attach a condition to it.

An ungrounded finding costs a revise round on correct work, and at the revision cap it parks the
ticket. A parked ticket is a human's time. That is the price of guessing, and it is why the
evidence rule is stated per condition rather than assumed.

## Proportionality

A thin result is not a failed result. A corpus with three comparable platforms yields three, and a
survey that says so honestly is complete. **Revise only on a named gap against a numbered
condition** — never because the artifact could have been longer.

## Output

Findings, each naming its condition, then exactly one terminal line:

```
VERDICT: approve
```

or

```
VERDICT: revise
```

Nothing after it.

## Upstream remedies

If a finding's remedy lies OUTSIDE the file this ticket contracts to write — an upstream map, a
registry row, another angle's output — say so and **park on the first round**. Ordering a revision
the producer cannot perform burns three cycles and ends in a park that names neither the artifact
nor the inconsistency. The test is contractual, not subjective: is the fix inside this file?
