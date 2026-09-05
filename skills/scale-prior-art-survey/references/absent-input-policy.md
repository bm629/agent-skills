# Absent inputs, dead sources and out-of-enum values

What to record when the thing you needed is not there. Every case below has an honest form; none
of them has a silent one.

## A dead source

A registry row that refuses THIS run is `skipped` in the map, with `cause_class` and an
**observable** `cause` — a status code, a robots directive, a dated refusal. Not "unavailable", not
"could not reach". `blocked` is a REGISTRY value describing the row's standing posture; a refusal
of your run is `refused`.

Then follow the row's `fallback`. When you reach a terminal — `fallback: null` — the branch is
exhausted, and the honest record is a skipped cell with its cause. Substituting a source from
another branch is not a fallback; it is a different search.

## A thin corpus

A source that answered and returned little is REACHED with `returned: 0` and a `count_frame` if
anything was counted. **This is not the same as an absence.** Whether the zero is evidence depends
on the row: `complete_listing: true` means you walked everything and it was not there;
`complete_listing: false` means only that your query did not match. The cell records what happened;
`references/sources.md` says which reading applies.

## An out-of-enum value

The vocabularies are closed and the gate enforces them. A source using a term outside one —
a consistency model Jepsen does not name, a `cause_class` outside the nine — is recorded with the
nearest legal member ONLY if that is honest, and otherwise the episode records `null` and the
source's own word goes in `claim` or `pattern`, which are free text for exactly this reason.

**Never force the nearest-looking member.** A wrong enum value is worse than a null, because it
reads as a measurement.

## No number

`measured_magnitude: null` and `measured_unit: null`, with `measured_value` carrying the source's
prose if it has any. The load-band re-derivation does not run, and the `primary_dimension`'s
`load_class` sub-key must ALSO be null. A band asserted with no number behind it is refused.

## A ruled-out angle

The map recorded `holds: false`. The search output is `outcome: not_run` with
`not_run{map_verdict}` quoting the map's reason, and nothing else — no cells, no candidates, no
bound. An angle that runs anyway produces a grid nobody owed.

## The `sanitization` enum, a criterion per member

| member | the criterion that decides it |
| --- | --- |
| `clean` | You READ the content and it carried nothing that reads as an instruction. Asserts a read. |
| `modified` | You read it, something in it read as an instruction, and you neutralised it. The `cause` says what, in posture terms — never a count. |
| `unavailable` | You reached the host and got no readable body: a 403, a paywall, a JS-only page. The host answered; the content did not. |
| `not-fetched` | You did not open it on this run. **Not the same as `unavailable`**, and `clean` would assert a read that did not happen. |

A reached coverage cell's OWN status is never `not-fetched` — the subject is the CELL, not the map
row it cites.
