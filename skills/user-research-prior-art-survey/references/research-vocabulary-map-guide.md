# Research vocabulary map — field by field

The search protocol, built **before** any searching. Schema:
`schemas/research-vocabulary-map.schema.json`. Reference:
`scripts/fixtures/research-vocabulary-map.valid.yaml`.

---

## `meta`

`as_of` is RFC3339 with a time, not a date. `revision` increments when the map is rebuilt for the
same scope; `scope_ref` names what was handed in, so a later reader can tell which scope produced
which map.

## `groups` — the four axes

Each group is one concept with its retrieval vocabulary. `id` is yours to choose and is referenced
by every coverage cell, so make it readable.

### `user-population`

Who was studied. This is what separates a finding about older adults from one about a
convenience sample of students, and it is the axis a synthesis later weighs transferability
against. Name the population the product will actually have.

### `task`

What they were doing. Task terms are what most people reach for first and they under-retrieve on
their own — the literature indexes by design as much as by topic.

### `method`

**The axis peculiar to this survey, and the one that makes it work.** Bibliographic corpora are
indexed by study design, so "diary study", "think aloud", "task completion rate", "controlled
experiment" and "field study" reach work no topic term will.

A method group whose terms are really topic terms in disguise — "mobile usability",
"kiosk research" — retrieves nothing the task axis did not already reach, and the map has lost
the axis it most needs.

**`negative_terms` are mandatory here.** "Interview" collides with journalism and with hiring;
"card sort" with games; "usability" with every discipline that has borrowed the word. Write
exclusions that name the actual collision, not decorative ones.

### `component`

Widget terms. Present because assistive-technology research is indexed **by widget** — "screen
reader" plus "combobox", never "screen reader" plus "browsing". Without this axis the
accessibility angle queries on tasks and returns advocacy rather than interaction evidence.

### `expansions`

Each carries a `relation` (SKOS: `broader`, `narrower`, `related`, `alt-label`) and a
`provenance`:

| Provenance | Means | Honest when |
| --- | --- | --- |
| `extracted` | A real corpus used this term | You fetched something while building the map |
| `model-knowledge` | You supplied it from recall | The default, because the map precedes the search |
| `probe-discovered` | A live vocabulary probe surfaced it | `probe.performed` is true |

**`extracted` is a claim about an action.** Unless you queried an index while building the map,
the honest value is `model-knowledge` — which a reviewer weighs differently, not rejects.

Floor of three expansions. Below that, record `short_reason` and **do not pad**: manufactured
near-synonyms return noise, and every false candidate costs a full deep read later.

`expansion_cap` is yours, per group, and the gate checks you stayed AT OR UNDER your own
declaration — the check is `n > cap`, so a group sitting exactly on its cap passes.

## `probe`

Optional, but if any expansion claims `probe-discovered` then `probe.performed` must be true —
otherwise the provenance is unfalsifiable. A probe declared not-performed needs a reason.

## `scope_guard`

`excluded` records what you deliberately kept out of scope and why. `absent_types` records any
axis carrying no group — an axis neither present nor declared silently empties every angle
depending on it, and the gate treats that as a failure rather than a choice.

## `angle_applicability`

**One verdict per registry angle, no more and no fewer.**

- `precondition` is the registry's, **verbatim**. Restating it in your own words is where a
  verdict quietly stops matching the predicate it claims to evaluate.
- `reason` cites the scope's actual values. "The scope declares `regulatory.applies = false`" is a
  reason; "this does not seem regulated" is not.
- An always-on angle can never be `holds: false`.

Both directions matter. A wrong `holds: false` drops an angle silently; a wrong `holds: true`
spends a whole cap on literature the scope ruled out.

## `sources`

The wave-0 posture, and it is load-bearing twice.

`active` means **the source answered you at least once at wave 0, with content you could have
queried**. Not a HEAD, not a 200 on a landing page, not a liveness probe.

**"At least once" is the boundary, and it is what makes `throttled` coherent.** A source that
served you and then rate-limited is `active` + `throttled`; its later refusals are `rate-limited`
CELLS, which is the case that status exists for. A source that refused *every* wave-0 attempt was
never established as reachable: it is `skipped`, and calling it active would be the false receipt
this field exists to prevent. Its angles then owe no cells for it — correct, because you cannot
report on a channel you never opened.

That definition is load-bearing: `active` decides which sources every later angle may query, each
angle's applicable set is the intersection with this list, and coverage completeness is computed
from the difference. Left vague, two producers derive different owed sets from the same scope and
both validate.

Each `active` entry carries a `release` (the version or wave read, or the literal `rolling`), an
`as_of`, an `access_status`, and a `sanitization` result. `skipped` carries an `id`, a `cause` and
an `access_status`.

### `access_status` — six members, and not the sibling surveys' field

| Member | Means |
| --- | --- |
| `open-access` | Full text retrievable without payment or registration |
| `free-registration` | Retrievable, but behind a free account |
| `crawl-delayed` | Retrievable, at a rate the source **declares** up front |
| `throttled` | Answers, but rate-limits **under load** — reachable, so `active` |
| `paywalled-abstract-only` | The fetch succeeds and still cannot support a record |
| `blocked` | The source refuses this survey |

`paywalled-abstract-only` is the load-bearing member. It is a **success** that still cannot ground
a finding, because a record extracted from an abstract is indistinguishable from one grounded in
the method section.

`throttled` is the second, and it is a GENERAL posture rather than one source's label. Any
source that answers and then rate-limits takes it. `semantic-scholar` is only its clearest
instance — it documents a globally shared unauthenticated pool throttled under load, so a 429
there is a normal operating condition — but a keyless index that throttles concurrent requests
is the same posture and is recorded the same way. Without
this member such a source has no honest posture: it is not `open-access`, and grading it `blocked`
pushes it into `skipped`, where no angle may query it — which makes the cell-level `rate-limited`
status **unreachable by construction**, for the very source the type is built around. A throttled
source is `active`.

**A source whose halves have different postures gets one entry per half.** The registry already
splits two sources across hosts for exactly this reason. Do not grade the whole thing by its most
permissive half and push the rest into `scope_guard`; there is deliberately no `partial` member.

### Two rules that catch silent failures

1. **A `blocked` source may not be listed active.** A source that refused the survey was never
   read, so listing it active is a false receipt.
2. **Every source belonging to an angle whose verdict holds must appear in one list or the
   other.** Every later angle's applicable set is the intersection of its registry sources with
   this `active` list — so a source in neither list is removed from the survey with no trace that
   it was ever considered.

Before finalising, check that every `holds: true` angle still has at least one active source. An
always-on angle left with none is forced to `vacated`, which is the survey silently doing nothing.

## `assumptions`

`inferred_from` names the **signal**, not the motive. See `absent-input-policy.md`.

## `lineage`

Present when this map inherits from an earlier request's. `inherits` names what carried over;
`net_new` what this revision added.
