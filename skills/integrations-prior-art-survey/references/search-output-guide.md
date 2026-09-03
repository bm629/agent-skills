# Producing one angle's search output (wave 1)

One file per angle. `outcome` decides what else is owed.

## The owed grid is DERIVED from three terms

`{(group, source) for group in the map's groups OF THIS ANGLE'S APPLICABLE TYPES
                 for source in THIS ANGLE'S OWN sources INTERSECT the map's ACTIVE sources}`

All three, and dropping any one is wrong in a measurable way. For the calibration fixture's a1:
five groups x five sources = **25 cells**. Drop the second term and every angle would owe every
active row — 5 x 19 = 95, nearly four times the real obligation. Drop the third and a1 would owe a
cell against `make-integrations-sitemap`, the channel this run recorded as dead.

## What `outcome` owes

| `outcome` | owed |
| --- | --- |
| `ran` | cells, a `bound`, a `retrieval_summary`, and candidates if anything was admitted |
| `not_run` | NOTHING but `not_run{map_verdict}` |
| `vacated` | cells with causes, `vacated{cause}`, a `retrieval_summary`; NO candidates or unadmitted |

`bound` is owed on `ran` ALONE — an angle that did not run bounded nothing.

## `enumerated`, and why it is this type's own field

`true` when the source was walked as a COMPLETE listing — every entry examined, whatever term filter
was then applied to the RESULTS. `false` when the TRAVERSAL itself was bounded by a cap, a cursor or
a page limit. **ABSENT** where the source row's `complete_listing` is `n/a`.

The distinction is the TRAVERSAL, not the query. a1 filters every catalog it walks, so defining
`false` on the filter would make every a1 cell `false` and collapse the distinction entirely.

It is what makes a zero readable.

## `fallback_used` is a PREFIXED route

`angle:<row_id>` or `row:<row_id>`. Both prefixes name the LEVEL whose declaration was walked, and
the token is ALWAYS a registry source row — an angle's declared `fallback` is itself a row id, and
no angle may fall back to another angle. A bare id cannot say which channel was taken.

## `bound`

`cap` is the registry's value transcribed VERBATIM. `null` transcribes a registry row that declares
NO cap, and no angle here declares one — so a null is a `cap-matches-registry` finding rather than
an option. `ordering` is the registry's
`ordering_signal` verbatim, or the ordering the run DID apply with the reason in
`ordering_deviation`. `hit: true` owes a `dropped_note` saying what fell off the end.

**A run that stopped BELOW the cap.** `bound.hit` means the CAP truncated the result. A run that
stopped earlier for its own reasons — an evidence budget, a time box — records `hit: false` and puts
the stop in `notes[]` with the ordering position it reached and the rows immediately after the cut.
The schema has no field for it, and saying so is better than overloading `hit`, which would make a
budget stop indistinguishable from a cap hit for every later reader.

## `present_on[]` — a1 ONLY

The `source_id`s whose catalog listed the service. **It INCLUDES the `found_by` cell's own
source** — the list is the COMPLETE membership, not the membership minus the catalog that won.

Every member must be a source this run REACHED. A member that is a legal registry row but sits in
the map's `skipped[]` has no reached cell, and a presence numerator that can name a source nobody
walked is unfalsifiable.

## `found_by` when several catalogs carry the service

The winner is **the first catalog in the angle's own `sources` order that carried it**. The order is
the registry's, so the choice is derivable rather than a producer's free pick, and two runs over the
same corpus attribute the same row to the same cell. Every other catalog that carried it is recorded
in `present_on[]`, so nothing is lost by the choice.

## EVERY term a group declares must be asked on that group's cells

Not just the seeded services — every `canonical` and every `expansions[]` entry of every group that
has a cell, minus any term a `shared_terms` entry assigns to a different group. `group-term-unqueried`
enforces it, and it matches the term ANYWHERE in the query string, so any re-runnable filter form
works.

**The seeded services are the sharpest instance.** `integrations.third_party_list` is a1's and a3's
`seed_input`; a name in it that is never asked for on the `service` axis can be silently lost in a
scope where the other axes miss it, and nothing in the artifact would show it had not been asked.
That is the failure this survey exists to prevent, one level down from the founding error.

## `found_by` when several GROUPS match the same row

The source rule above settles which catalog wins. When two groups' terms both match a row in that
catalog — a seeded service that is also a category member — **prefer the `service` axis for a
service the map seeded, and otherwise take the first group in the map's declaration order.**

`found_by` is a single `group/source` key and `kept` is checked EXACTLY against the rows citing each
cell, so an unstated group rule produces two different, equally gate-clean artifacts from one run.

## `kept`

The number of candidate rows PLUS unadmitted rows this cell carried forward. **Never a result
count.** A cross-catalog re-find of an already-recorded service goes in `present_on[]` ALONE and is
never an `unadmitted{duplicate-of}` row — `duplicate-of` is for two distinct NAMES resolving to one
canonical host.

## Worked example

`scripts/fixtures/search-output.valid.yaml` is the calibration fixture and validates clean:

```
uv run --no-project --with pyyaml --with jsonschema python scripts/validate_integrations_prior_art.py \
  search scripts/fixtures/search-output.valid.yaml \
  --keyword-map scripts/fixtures/integration-vocabulary-map.valid.yaml
```
