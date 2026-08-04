# The per-angle search output, explained

One angle's result, with the receipts that make it re-runnable. Everything here exists so a
later reader can tell a market with no competitor from a search that never ran.

Schema: `schemas/search-output.schema.json`. Gate:
`validate_market_competitive_prior_art.py search <file> --keyword-map <map>`.

## Three outcomes, and why they are distinct

| `outcome` | Means | Owes |
| --- | --- | --- |
| `not_run` | The angle's precondition did not hold | A `not_run` block with a reason. **No cells.** |
| `vacated` | The precondition held, but the applicable set came out empty — no group of the right type, or no source of this angle's in the map's active list | A `vacated` block with a reason. **No cells.** |
| `ran` | The angle executed | Coverage, retrieval summary, bound |

An unrun angle writing empty cells would manufacture zeros that read as searches. That is the
single most damaging thing this artifact can do, so the gate rejects it outright.

`vacated` exists because "the precondition held but there was nothing to query" is a different
fact from "we chose not to run" — and a reader who cannot tell them apart will assume the
market was searched.

## The applicable set

The pairs the angle owed a cell for:

```
applicable = { (group, source) : group.type ∈ angle.applicable_group_types
                               ∧ source ∈ angle.sources ∩ map.sources.active }
```

Both halves matter. A source the angle lists but the map skipped was never available to it, so
no cell is owed. A group whose type this angle does not query is not this angle's work.

The gate checks this **in both directions**: a missing cell is an unexplained gap, and a
surplus cell means the angle worked outside its assignment — which duplicates a sibling angle
and inflates this angle's arithmetic.

## Cell statuses

| Status | Meaning |
| --- | --- |
| `reached` | The source answered. Requires `returned` and `kept`. |
| `unreachable` | A fetch was attempted and failed. Requires `cause`. |
| `partial` | **The catch-all for a fetch that succeeded but did not yield a clean result set** — some of the set was obtained, or the source answered without honouring the query (a site with no search endpoint that serves its homepage regardless). Requires `cause`. |
| `rate-limited` | Throttled before the query completed. Requires `cause`. |
| `forbidden-by-terms` | **A deliberate non-fetch** — the source's terms forbid automated access. Requires `cause`. |
| `content-withheld` | An intermediary withheld the content. Requires `cause`. |
| `not-attempted` | Owed but not tried. Requires `cause`. |

`forbidden-by-terms` versus `unreachable` is the distinction that carries the most weight. The
first is a decision you made; the second is a failure that happened to you. Collapsing them
hides a policy choice inside an outage report, and a later reader cannot tell whether trying
again would help.

## Queries

Record every query **as run**, verbatim. A paraphrase cannot be re-run, and a coverage record
that cannot be re-run proves nothing. This is the single most-violated reporting rule in
systematic search practice — searches that intended to be reproducible routinely are not, and
the failure is invisible in the write-up.

At least one query per cell is a broad pass over the group's canonical term. Apply the group's
negative terms; without them a category or product term returns a category's worth of homonyms.

## returned, kept, and the bound

- `returned` — what the source gave back.
- `kept` — how many distinct candidate **rows** this cell carried forward into `candidates`
  plus `unadmitted`. Never a result count.

  **`kept` is frequently far below `returned`, and that is normal.** A directory page returning
  14 entries may yield 2 rows worth carrying. Three things reduce it, and all three are
  legitimate: the relevance filter (most results are not competitors), dedup against rows this
  angle already carried, and the cap truncating the tail. Only the last needs `bound.hit`.
  The rule is arithmetic, not judgement: **`kept` must equal the number of `candidates` +
  `unadmitted` entries whose `found_by` names this cell.**
- `bound.cap` — **the registry's number for this angle**, sized against the corpus it walks.
  Not the run's to choose: the gate rejects a `cap` that disagrees with the registry in either
  direction, since a run may neither raise its own ceiling nor quietly lower it.
- `bound.hit` — whether the cap actually bound. If true, `dropped_note` says what was dropped,
  in kind. A cap that bound and is not described reads downstream as exhaustive coverage.
  If false, the candidate count must not sit at the cap by coincidence without explanation —
  and a declared hit with candidates *under* the cap is rejected, because a limit that did not
  bind must not be recorded as though it had.

There is **no total queue cap** anywhere in this survey. The per-angle limit is the only limit,
which is why it is recorded so carefully: it is the sole place coverage is deliberately bounded.

## retrieval_summary — the duplication IS the check

It restates the cell statuses and names every degraded source with its cause. That looks
redundant and is not: reconciling the two is how a failure laundered into a zero is caught. If
the summary says everything was reached and a cell says otherwise, one of them is wrong, and
the gate says so.

## Candidates, and the admission rule

A candidate is carried forward only if:

- **`corroborated`** — two *independent* angles found it (name them), or
- **`first-party-resolved`** — its official site resolves and states a capability that overlaps
  the scope (quote the capability, in the site's own words).

**Which basis is available to you depends on what you were handed.** Procedure 2 runs ONE angle
and cannot see a sibling's output, so `corroborated` is only usable when the caller explicitly
hands you another angle's findings. Running a single angle in isolation, **every admission is
`first-party-resolved`** — which means one live fetch per candidate, so the cap is also a fetch
budget. Plan for that rather than discovering it at candidate 20.

Everything else goes to `unadmitted` with its name, where it was found, and why it was not
carried. **Never drop it silently** — a silent drop makes "we did not look" indistinguishable
from "we looked and found nothing", one layer down from the zero-hit cell.

The rule exists because listicles and roundups pad. A "top 15 tools" article routinely carries
a handful of real products and a tail of affiliate entries and defunct names, and each filler
entry that survives costs a full deep read later.

**Identity.** `id_class` governs the shape of `id`: `wikidata` → `WD-Q<number>`, `package` → a
package URL, `app-store` → `APPLE-`/`STEAM-<id>`, `web` → a **minted** `WEB-<official-domain>`
plus the `url` it came from. A web-class item must never be given an invented registry-shaped
id — inventing an identifier for something that has none is how two records for one product,
or one record for two, gets created.

**Authority.** `authority_band` orders and breaks dedupe ties. It is **never a cut**. On a
conflict first-party wins: aggregators lag pricing by months, and a pricing page is
definitionally current.

## Notes

Vocabulary discovered mid-run, dead ends, and cross-angle leads. A lead belonging to another
angle goes here for the caller to route — chasing it duplicates another worker and corrupts
this angle's coverage arithmetic.

## Worked example (abridged, `outcome: ran`)

```yaml
schema_version: 1
meta: {angle_id: a1, as_of: "2026-08-04T10:00:00Z", revision: 1, map_revision: 1}
outcome: ran
coverage:
  - group_id: team-collaboration
    source_id: openalternative
    queries: ["category:team collaboration software", "category:workplace collaboration -\"team building\""]
    timestamp: "2026-08-04T10:02:00Z"
    status: reached
    returned: 14
    kept: 9
  - group_id: notion
    source_id: openalternative
    queries: ["alternatives-to:Notion"]
    timestamp: "2026-08-04T10:08:00Z"
    status: rate-limited
    cause: >
      429 on the third page after the documented rate window; the first two pages were kept and
      the tail was not read. Retried once after backoff with the same result.
retrieval_summary:
  degraded_sources:
    - {source_id: openalternative, status: rate-limited, cause: "429 on deep pagination"}
  status_counts: {reached: 1, rate-limited: 1}
bound: {cap: 25, ordering: "directory rank, then most-recently-updated", hit: false}
candidates:
  - id: WEB-linear.app
    id_class: web
    name: Linear
    url: https://linear.app
    authority_band: first-party
    found_by: team-collaboration/openalternative
    relevance: Its own site states a shared documents surface, overlapping part of the capability set.
    admission:
      basis: first-party-resolved
      capability_stated: "Docs — write, plan and collaborate on product specs alongside your issues."
unadmitted:
  - name: TeamSyncPro
    found_by: team-collaboration/openalternative
    reason: One directory listing, no resolving official site, no corroboration from another angle.
```

The full fixture is `scripts/fixtures/search-output.valid.yaml`.
