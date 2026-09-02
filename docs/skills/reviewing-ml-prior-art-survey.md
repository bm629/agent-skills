# `reviewing-ml-prior-art-survey`

The judgement half of a two-part gate. The deterministic half has already run: an artifact reaching
this reviewer has passed `validate_ml_prior_art.py` at exit 0.

## What it is for, and what it must never do

Shape, enums, ranges, arithmetic and reconciliation are the script's. **A finding this reviewer
could have produced by running the script is not a review finding** — it is a duplicate, and a
duplicate costs a revise round on work that was correct.

That boundary is enforced inside the conditions. Where a property has both halves, the validator
owns the SHAPE and the condition owns the JUDGEMENT, and the condition names the rule that owns the
other: C1 disclaims `borrowed-vocabulary-unmarked`, C5 disclaims four verdict rules, C10 disclaims
`coverage-complete` and `kept-matches-rows`. A condition whose stated gap the gate already catches
can never be cited, because no artifact carrying it ever arrives.

## The twenty-two conditions

Each lives under the artifact it JUDGES, and the numbers are stable identities rather than
positions — a finding cites a number, so renumbering would invalidate every report already written.
C2 therefore sits in the search-output section despite its number: it judges a candidate, and takes
the map as its second input.

The ones that decide most outcomes:

- **C5** — a verdict justified against the scope in BOTH directions. `false` where the scope
  satisfies the predicate silently shrinks a survey; `true` where it does not silently inflates one
  with an angle whose mechanism has nothing to retrieve. A disjunctive precondition needs a third
  reading: a reason establishing one leg and reporting the verdict of another.
- **C9 / C9a** — a query recorded so it can be re-issued, and a count carrying a frame a reader
  could re-derive it under. A frame naming a filter the query does not contain, or describing more
  searches than the cell records, is proof a query was lost.
- **C12** — the status the evidence supports. `gated` is not `unreachable` (the fetch completed and
  was refused); a 301 to a live replacement is `superseded`; a shared-pool 429 is `rate-limited` and
  never a searched zero; and `not-attempted` owes a cause naming a CHOICE, because a failure dressed
  as a choice is the direction that hides work.
- **C17** — authority recorded honestly, ranking rather than cutting. Both directions: a vendor's
  card labelled `independent-benchmark`, and a relevant option dropped for "low authority".
- **C19** — nothing asserted that the source does not say. A claim about what a model DOES resting
  on a quote about what a document SAYS is the recurring failure in this type.

## Evidence, and where it lives

The artifact, the wave-0 map, the schemas, the source registry, and the angle reference. **Three of
those five live in the producer package**, which is often not installed beside this one — so the
skill locates each by path and says which conditions become unexecutable without them. Deriving an
angle's source list from the artifact is circular: an artifact that omits a source omits it from any
list read off it.

Anything not groundable in those five is an OBSERVATION, not a finding. Observations are licensed
deliberately and they earn it: across the cycles that built this pair, reviewer observations found a
source-accounting hole that let an angle owe zero cells, an `unadmitted` row aggregating across
three cells while naming one, and two verdicts pre-stating what their angle was dispatched to
establish.

## Read `outcome` first

It decides which conditions apply at all. `not_run` owes nothing and the gate REQUIRES that
emptiness — reading a coverage condition against it would revise work the other half certified.
`vacated` owes cells and causes but no candidates. `ran` owes the full owed set.

## Proportionality

A thin result is not a failed result. A task with three published models yields three, and a survey
saying so honestly is complete. Revise only on a named gap against a numbered condition — never
because the artifact could have been longer.

## Upstream remedies

If a finding's remedy lies outside the file the author was asked to write, label it `UPSTREAM:` and
name the exact file and field. One that names no target is a finding you could not localise, and
belongs in Observations. **A file whose every finding is UPSTREAM gets `approve`** — you judge that
artifact against its own contract, and if the defect is elsewhere it is not the defective thing.

## Output

Findings, each naming its condition, then exactly one terminal line: `VERDICT: approve` or
`VERDICT: revise`. Nothing after it. There is no third verdict.

## Companion

[`ml-prior-art-survey`](ml-prior-art-survey.md) — the producing half.
