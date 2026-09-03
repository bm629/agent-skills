# `integrations-prior-art-survey`

Establish which third-party services a described project will actually have to integrate with, and
on what terms — before the architecture commits to a connector platform, an abstraction layer, or a
protocol the services in question do not speak.

**Wave 1 only.** Two kinds: the integration vocabulary map, and one search angle's output. Extract
and synthesis are not in it, and nothing here produces a recommendation — it produces a searched,
recorded corpus of vendor-scoped candidates a later wave turns into one.

## The organising idea

This type was nearly built on a number that does not exist. The 2026-06 draft sized the whole
survey on Zapier's "number of active Zaps" — a figure six page-fetches across three services and
two platforms could not find, because nobody publishes it.

So every registry row carries a **`yields`** field stating what it actually returns, and a row that
cannot state its yield is a row nobody probed. That field is the direct answer to the founding
error, and it is unique to this type.

The second shaping idea is **`enumerated`**, also unique to this type. A zero from a source is only
evidence if you know whether the source was walked completely. `enumerated: true` means every entry
was examined — whatever term filter was then applied to the results — so an absence is real.
`false` means the TRAVERSAL itself was bounded by a cap, a cursor or a page limit, and the zero says
nothing. The distinction is the traversal, not the query, and it is what separates "this service is
absent from Nango" from "we did not find it".

## Two procedures

**Procedure A — the integration vocabulary map.** Built before any searching, over **six axes**:
`category`, `capability`, `service`, `pattern`, `domain-noun` and `seed-product`. Each names where
its terms come from — an axis whose input is undeclared has no bootstrap.

It carries a verdict for every angle in both directions, the capability-coverage record, and every
one of the 23 registry rows in exactly one of `active[]` or `skipped[]`.

**Procedure B — one angle's search output.** The 2-D coverage grid, the candidates at vendor scope,
the `bound`, and the retrieval summary. The owed grid is derived from **three** terms, and the
package proves what dropping each one costs: for the calibration fixture's `a1`, five groups × five
sources = 25 cells. Drop the filter on the angle's applicable group types and it would owe 35 — ten
cells against a `pattern` and a `seed-product` group `a1` does not search, each recorded reached
with an honest-looking zero. Drop the angle's own source list and it would owe 95. Drop the map's
active set and it would owe a cell against a channel this run recorded as dead.

## Eight angles, three always-on

`a1` connector-catalog enumeration · `a2` API-descriptor retrieval · `a3` first-party
integration-directory reading — these three always run. Then five conditional: `b1` package-registry
SDK adoption, `b2` event/webhook delivery conventions, `b3` regulated-integration constraints, `b4`
unified-API abstraction reading, `b5` MCP / agent-channel retrieval.

**No angle reads another angle's output.** The naive reading of the taxonomy would have `a2` resolve
`a1`'s candidates — three such violations, and a survey undispatchable without `a1`. The resolution
is that each angle DISCOVERS from wave 0 and ENRICHES from its own channel, and the cross-angle join
happens at two places that are not angles.

## Every cap was MEASURED, and two of the measurements changed the design

- **`a2` = 100, and it does NOT clear its corpus.** The largest single apis-guru category by
  provider is 94 — which sat under 100 by luck. The union across a multi-category map reaches 180 at
  two categories and 236 at three. So the cap truncates, `bound.hit: true` is a2's normal path, and
  its ordering is load-bearing rather than decorative.
- **`a3` = 60, and the binding constraint is REACHABILITY, not size.** Directory sizes over a
  ten-product sample span 18 to 7,805 — three orders of magnitude — and **six of the ten yielded no
  count at all**. No number is a ceiling against that spread. Four of the ten are recorded by name;
  the six that yielded nothing were not, so the spread is re-derivable and the sample is not.
- **`b1` = 40, and it binds.** 59.2% of sampled connector rows carry a vendor-confirmed, published
  npm SDK; one mid-sized category clears 40 on its own. The rate is the measurement — the sample's
  size and membership were not recorded, so like `a3`'s it is not re-derivable.
- **`b3` = 25.** Over the regulated slice, 53.5% of vendors carry a trust surface but only 20.9%
  carry a machine-readable one.

## What the deterministic gate checks

**85 rules**, split across a map validator and a search validator, with the exit contract tested per
rule rather than in aggregate: the **9** registry-integrity rules return 2 because only a
package author can cause them, the input-class faults return 2, `schema-unavailable` returns 2
because an unloadable schema FILE is a package fault, and everything else — including `schema` —
returns 1, because an artifact that fails a schema which LOADED is exactly what its author can
repair.

That exit-2 registry set is DERIVED from the validator's own AST rather than hand-listed. An earlier
version compared it to a hand-copied literal of itself, so a rule could be added on one side and not
the other; deriving it immediately found `registry-unreadable` missing.

The rule set is PARTITIONED: every rule is in `NEED` (carries an explicit narrow mirror) or
`NOT_NEEDED` (carries a one-line reason), asserted by equality against the ids derived from the
source. There is no fourth case, so a rule added later cannot inherit a side.

**23 registry rows**, in six fallback families with six terminals, walked rather than described: 0
cycles, 0 dangling. A terminal declares `fallback: null` WITH a rationale, because requiring every
row to name a fallback in a finite graph guarantees a cycle by pigeonhole.

## What it deliberately does NOT check

It never fetches. Whether a `locator` host really is the vendor's own, whether an `evidence_quote`
supports its `claim`, whether an authority band is defensible for the page it points at, whether the
capability coverage is honest — none of those is decidable without a request, and each is a
numbered condition in the reviewing twin.

## Install

```
npx skills add bm629/agent-skills@integrations-prior-art-survey
npx skills add bm629/agent-skills@reviewing-integrations-prior-art-survey
```
