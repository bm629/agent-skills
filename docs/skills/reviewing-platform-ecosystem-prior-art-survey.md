# `reviewing-platform-ecosystem-prior-art-survey`

The judgement half of a two-part gate. The deterministic half has already run: an artifact that
reaches this reviewer has passed `validate_platform_ecosystem_prior_art.py` at exit 0.

## What it is for, and what it must never do

Shape, enums, ranges, arithmetic and reconciliation are the script's. **A finding this reviewer
could have produced by running the script is not a review finding** — it is a duplicate, and a
duplicate costs a revise round on work that was correct.

That boundary is enforced in the conditions themselves. Where a property has both halves, the
validator owns the SHAPE and the condition owns the JUDGEMENT, and the condition says so: C2 keeps
"a slug naming the wrong platform" and disclaims "a slug the map does not carry" to
`slug-not-in-map`; C17 keeps "an ordering that restates the outcome" and disclaims a missing one to
`bound-needs-ordering`. A condition whose stated gap the gate already catches can never be cited,
because no artifact carrying it ever arrives — it would occupy a number, read as covered, and cover
nothing.

## The twenty conditions

C1–C7 judge the vocabulary map, C8–C17 an angle's search output, C18–C20 both. Each carries its
EVIDENCE — what grounds it — and an *IS a gap* / *NOT a gap* pair, because the calibration belongs
beside the condition a reviewer cites under time pressure, not in a preamble read once.

The ones that decide most outcomes:

- **C4** — a verdict is justified against the scope in BOTH directions. `false` where the scope
  satisfies the predicate silently shrinks a survey; `true` where it does not silently inflates one
  with an angle whose mechanism has nothing to retrieve. A disjunctive precondition needs a third
  reading: a reason establishing one leg and reporting the verdict of another.
- **C9** — a zero is recorded, not omitted, and a zero that had something to drop says why. A note
  restating the zero ("nothing was carried") is the observation, not the reason.
- **C12/C13** — the three dates kept apart, and a page's self-claimed date treated as a claim.
- **C14** — an enumeration's second derivation must have been able to disagree with the first.
- **C18** — nothing asserted that the source does not say. A claim about what a platform DOES,
  resting on a quote about what a document SAYS, is the recurring shape.

## Evidence, and what an ungrounded finding costs

The artifact, the wave-0 map, the schemas, the source registry, and the angle reference. Three of
those five live in the producer package — and it is not always installed alongside this one, so the
skill says which conditions become unexecutable without it rather than letting a reviewer
improvise. Deriving an angle's source list from the artifact is circular: an artifact that omits a
source omits it from any list read off it.

Anything that cannot be grounded in those five is an OBSERVATION, not a finding. Observations are
licensed deliberately, and they earn their place: across the cycles that built this pair, three
runs returned a grounded observation and two of the three turned out to be gaps in the CONDITIONS
rather than in the artifact — a reviewer that can ground a finding but cannot land it is reporting
that the bar has the hole.

## Proportionality

A thin result is not a failed result. A corpus with three comparable platforms yields three, and a
survey that says so honestly is complete. Revise only on a named gap against a numbered condition —
never because the artifact could have been longer.

## Upstream remedies

If a finding's remedy lies outside the file the author was asked to write, they cannot perform it.
Label it `UPSTREAM:` and name the exact file and field that must change; one that names no target
is a finding you could not localise, and belongs in Observations. **A file whose every finding is
UPSTREAM gets `approve`** — you judge that artifact against its own contract, and if the defect is
elsewhere it is not the defective thing.

## Output

Findings, each naming its condition, then exactly one terminal line: `VERDICT: approve` or
`VERDICT: revise`. Nothing after it. There is no third verdict.

## Companion

[`platform-ecosystem-prior-art-survey`](platform-ecosystem-prior-art-survey.md) — the producing
half.
