# When something is absent

Three different absences, and collapsing them is the failure this survey exists to prevent.

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
