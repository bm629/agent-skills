# The scale vocabulary map (wave 0)

The scope every angle that follows searches against. Built before any searching.

## `meta`

`scope_ref` (the path to the scope document), `classification`, `retrieved_at`, `revision`.

**`scope_ref` is load-bearing**: the reviewing twin judges the transcribed band against it, and a
map without it leaves that condition able to record only "unjudgeable".

**`meta.classification.scale` is the project's declared band, carried VERBATIM** — all five
required leaves, `concurrency`, `real_time`, `availability_target`, `geo_distribution` and
`data_volume`, each checked against the capability map's OWN enum for that leaf. Lens 1 reads the
corpus from it and lens 4 intersects the envelope with it, so a map that drops it makes both
lenses un-runnable. **A map is REFUSED without it.**

## `groups[]`

Four axes, and the group `type` says which: `system-class`, `load-dimension`, `named-technology`,
`failure-class`. Each group carries `id`, `type`, `canonical`, `expansions[]` and `expansion_cap`.

`expansion_cap` bounds the EXPANSIONS, not the cell count — the `canonical` is always one term on
top of it.

Give `system-class` and `failure-class` groups `negative_terms[]`: the words are ordinary English
and the false-positive corpus is large ("saturation" also means market saturation).

The `type` and the `id` are both load-bearing. The owed grid selects the applicable groups on
their TYPE, and every coverage cell's `group_id` resolves against the `id`.

## The four corpus arrays

`system_classes[]`, `load_dimensions[]`, `named_technologies[]` and `failure_classes[]`, each with
its `terms`, its `corpus_version` and its `as_of`.

**`named_technologies` is the input b1, b2 and b4 are otherwise tempted to take from a sibling
angle's output**, which L-9 forbids. Seed it from the scope, never from a1's candidates.

## `scope_guard`

`excluded[]` (an item and its reason), `absent_types[]` (an axis with no group), `shared_terms[]`
(a term two groups share, naming its `owner` so it is queried once).

An axis with no group is declared in `absent_types` WITH its reason in `excluded[]`. Silence is not
a declaration.

## `probe`

Three checks — two terminal fetches and one name resolution, three separate requests — recorded in
`probe{ran, note}`. A zero here is a finding about the corpus, not a failure, and a probe with no
note says neither.

## `angle_applicability[]`

**A verdict for all TEN registry angles, in both directions.** An always-on angle (`a1`, `a2`,
`a3`) can NEVER be `holds: false` — the registry declares it `trigger: always`, so a map saying
otherwise contradicts the contract rather than describing the project. A `holds: false` names the
DECIDING value from the classification, by path.

Each verdict also carries `applicable_group_types` — the first of the owed grid's three terms.

## `sources`

Every registry row in exactly ONE of `active[]` or `skipped[]`.

An ACTIVE row carries `as_of`, `access_status` and `sanitization{status, cause}`. A SKIPPED row
carries `cause_class` and a `cause`, and **never a posture** — you did not read it.

`blocked` is a REGISTRY value only: a source refusing THIS run is `skipped`, not `active`.

## `notes` and `assumptions`

`notes[]` for anything a reader would otherwise re-derive; `assumptions[]` for what you had to
assume. Both are arrays and both are required, empty or not.
