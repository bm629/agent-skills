# When something is absent

Several different absences, and collapsing them is the failure this survey exists to prevent. Each section below is one of them.

## The source states no value

Record `null` and say so where there is a field for it. A dataset card that publishes no licence
gets `licence: "unstated"`, not a guess and not an SPDX id we chose — a normalised guess is a legal
claim we are not entitled to make.

Where the absence is itself worth a decision-maker's attention, it goes in `finding`: "the card
publishes no evaluation on any held-out split" is evidence. An empty field is a hole someone will
later read as an oversight.

## The source could not be reached

That is a coverage `status` with a cause carrying observable evidence, never a zero. `gated`,
`rate-limited`, `superseded`, `unreachable` are different facts with different remedies, and a
survey that flattens them tells a reader nothing about whether to retry.

## A classification value you were never handed

Four conditional angles are decided by named classification fields and nothing else.

**Evaluate the legs you have before concluding anything.** Three of the four predicates are
disjunctions: one satisfied leg makes the verdict `true` regardless of what else is missing. Two of
them widen on an OPTIONAL field, which is absent in the ordinary case rather than the exceptional
one — so treating "a tested field is missing" as "the angle does not hold" drops those angles on
most scopes that need them.

Only when **no leg can be decided** do you record `holds: false` and say the FIELD was absent —
not that the scope fails the predicate. A verdict that asserts "the scope declares X = false" when X was never
handed to you is a fabricated fact about the project, and it reads downstream exactly like a
considered decision. Note it in `assumptions` too, so the gap is visible where a re-run would look.

## The scope has none of this

That is `scope_guard.absent_types` on the map. A scope with no regulatory exposure has no
`harm-category` groups, and declaring that is what stops a reader assuming the axis was forgotten.

## Dates

`as_of` is when the FACT became true. NULL when the content states none — **never defaulted to the
fetch date**, which would be a fabricated fact about the world.

A page's own "last updated" is a claim ABOUT ITSELF. It goes in `source_claimed_modified_at` with
its provenance, and is never promoted into `as_of`. This corpus contains pages whose self-claimed
dates are provably wrong.

`retrieved_at` is when you fetched it, and is the only one of the three you can always state.
