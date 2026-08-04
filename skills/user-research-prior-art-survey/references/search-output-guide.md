# Per-angle search output — field by field

One angle's work. Schema: `schemas/search-output.schema.json`. Reference:
`scripts/fixtures/search-output.valid.yaml`.

---

## `outcome` — the discriminated union

| Value | Means | Carries cells? |
| --- | --- | --- |
| `not_run` | The angle's precondition failed | **No** |
| `vacated` | The precondition held; nothing was applicable | **No** |
| `ran` | The angle worked its cells | Yes |

An angle that did not run owes no cells, and writing them manufactures zeros that read as
searches. An angle may not `vacate` itself while applicable pairs existed — that is a claim the
gate checks against the map.

## The applicable set

**Your group types × (your registry sources ∩ the map's ACTIVE sources).** Exactly the cells you
owe: no more, no fewer.

A source your angle lists but the map skipped is **not** in your applicable set — it was never
available to you. A cell outside the set means you worked another angle's channels, which
duplicates a sibling and inflates your own arithmetic.

## `coverage` — one cell per (group, source) pair

### `queries` — verbatim as run

Every query issued for this pair, exactly as issued, including field qualifiers and date bounds.
A paraphrase cannot be re-run, and a coverage record that cannot be re-run proves nothing.

**For a corpus walk the query IS the traversal**: which index or sitemap, which sections, and the
criterion that selected from them. Write it as a string that describes an action someone else
could repeat.

### `status` — three different facts, never collapsed

| Status | Asserts |
| --- | --- |
| `reached` | The search ran. `returned: 0` means the corpus held nothing. |
| `unreachable` | The fetch failed. |
| `rate-limited` | The source throttled you. |
| `partial` | Some of the pair was covered. |
| `forbidden-by-terms` | A **decision** not to fetch. |
| `content-withheld` | Retrieved, then withheld by sanitization. |
| `not-attempted` | Owed and not worked, with a cause. |

Everything but `reached` owes a `cause`, and the cause must name an observation. "Not worth it"
is not a cause; "the subject listing returned 503 on three consecutive fetches at the declared
spacing" is.

**One source in this registry runs a globally shared unauthenticated pool** and documents that it
throttles under load. A 429 there is `rate-limited` with that cause. `unreachable` overstates it,
and `reached, returned: 0` is the worst thing this artifact can do — the arithmetic of a laundered
failure reconciles perfectly, so nothing mechanical will catch it.

### `returned` and `kept`

Required on a `reached` cell.

**`returned` is the number of records the source HANDED BACK to this run** — never the total it
claims to match. A paged index will report millions of matches and return twenty; those are
different numbers by six orders of magnitude, and only the handed-back reading makes the
arithmetic mean anything. Put the match total in `selection`, where it describes the **bound** on
what you saw rather than the yield.

Recording the match total instead makes a search of twenty titles read as exhaustive coverage of
the corpus, which is the survey's central failure wearing a very respectable number.

**A traversal shared across cells apportions.** Enumerate the index once, then each cell records
the records it actually drew from that enumeration. Writing the whole walk's size into every cell
it served means six cells report a hundred each for one hundred retrieved titles — a grid
claiming six hundred returns. Say in `selection` that the enumeration was shared.

**`kept` is how many ROWS** — candidates plus unadmitted — name this cell. Never a result count.
The gate reconciles it against the rows themselves.

### `selection` — required where the registry declares a crawl delay

Three sources here declare delays of 60, 15 and 10 seconds. For those cells, **the selection is
the method**: enumerate an index first (one fetch), shortlist from the titles, fetch only the
shortlist.

Record **both halves**: what you shortlisted and on what criterion, **and what you identified and
deliberately did not fetch**. The un-fetched remainder is what makes the coverage honest — without
it a reader cannot tell a narrow corpus from a truncated one.

The rule does not apply to a cell that never got a response. A rate-limited cell made no
selection, and inventing one would be worse than recording none.

## `retrieval_summary`

`status_counts` duplicates the cells on purpose: a discrepancy between the two is the signal that
a source failure was laundered. Every source with a non-reached cell must appear in
`degraded_sources`. A `fallback_used` must be the registry's declared fallback for the angle —
the substitution belongs to the registry, not to the run.

## `bound`

`cap` is the **registry's**, copied. Both directions are checked: a raised cap makes the limit
meaningless, a lowered one truncates coverage while looking compliant.

`hit: true` requires a `dropped_note` saying what was dropped **in kind**, and is inconsistent
with carrying fewer candidates than the cap — a limit that did not bind must not be recorded as
though it had.

## `candidates` — SOURCES, not findings

**A candidate here is one paper, report or article.** How many findings it contains is knowable
only after the full read, so finding-level identity is minted in the extract wave and appears in
no artifact you produce. This differs from the sibling surveys and is deliberate.

### `id` and `id_class`

| `id_class` | Shape | Needs `url`? |
| --- | --- | --- |
| `doi` | `DOI-10.xxxx/...` | No — the DOI resolves |
| `arxiv` | `ARXIV-2401.01234` or `...v2` | No |
| `web` | `WEB-<domain>-<slug>` | **Yes** — nothing resolves it otherwise |

Read the identifier; never construct a plausible-looking one.

### `admission` — this survey's own rule, with two conjuncts

```yaml
admission:
  basis: full-text-retrievable-with-method
  full_text_url: <where the full text was actually reached>
  method_stated: <the study design, as the source itself names it>
```

**Both conjuncts are load-bearing.**

- Full text without a stated method admits practitioner argument that reports no study — a record
  with nothing to weigh.
- A stated method behind a paywall admits a record built from an abstract, which reads exactly
  like one grounded in the method section.

`method_stated` is what the source calls it, not your inference from its title. A title stating a
result is not a method.

**`full_text_url` will usually not be a registry source, and that is correct.** Where an angle's
index returns metadata only, following the resolver to the open-access full text IS the admission
check. The host you land on takes no coverage cell — the cell records the search — and it is
recorded here instead. Where the resolver leads to a paywall, the row is `unadmitted` with
`abstract-only`.

The gate catches one form of this mechanically: a candidate admitted on retrieved full text whose
source the map records as `paywalled-abstract-only`. One of the two records is wrong.

### `relevance`

Why this source looks worth a deep read. It may **not** grade the evidence — certainty and
transferability turn on the full read, which has not happened.

## `unadmitted` — recorded, never dropped

**Every source that reached the admission check and failed it** — not every record the search
screened. A run that screens a hundred index rows on their titles and deep-checks five records
**five**, and the cell's `kept` counts those five.

That boundary is load-bearing because `kept` is derived from it. Recording all hundred would make
`kept` a screening tally rather than a count of what was carried forward, and two conscientious
producers would derive different numbers from the same search while both passing the gate.
Title-level screening belongs in the cell's `selection` — the same distinction the crawl-delay
rule already draws between what was shortlisted and what was identified and not fetched.

Each row carries the real reason. `abstract-only` will be the commonest. **The reason is free
text, not a controlled vocabulary**, because the outcomes do not enumerate: a resolver that
returns 403 on a gold-open-access article is neither a paywall nor abstract-only — you never saw
the abstract either — and it is not an excluded source. Name what actually happened.

A silent drop makes "we did not look" and "we looked and it was not usable" indistinguishable one
layer down. Unadmitted rows feed the `kept` arithmetic exactly as candidates do, so an unrecorded
one also breaks the cell's reconciliation.

## `notes`

Cross-angle leads for the caller to route. Working another angle's channels inflates your
arithmetic and leaves the other's cells unexplained.
