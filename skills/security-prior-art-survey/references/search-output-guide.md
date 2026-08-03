# The per-angle search output, explained

`schemas/search-output.schema.json` is the contract. This guide explains it and shows worked
examples; where the two appear to differ, the schema wins.

## Three outcomes, and why they are distinct

`outcome` discriminates the whole artifact. Getting this wrong is the central failure mode of a
prior-art survey, so the schema makes the three states structurally different rather than
leaving them to prose.

| outcome | meaning | carries |
|---|---|---|
| `not_run` | the angle's precondition was unmet | the precondition and the cause. **No coverage cells** — an unrun angle owes no coverage, and writing cells for it fabricates a search. |
| `vacated` | the precondition held, but the applicable set computed empty because the map emptied a factor | which factor was empty and the map entry responsible |
| `ran` | the angle executed | coverage, retrieval summary, bound, candidates |

"We did not look" and "we looked and found nothing" are different facts. A team that confuses
them rebuilds what already exists, or ships a threat someone documented years ago. `not_run` and
`vacated` both mean the first; only a `reached` cell with `returned: 0` means the second.

## The applicable set

When the angle runs, a cell exists for every pair in:

    (map groups whose types the registry marks applicable to this angle)
      x (map sources.active  ∩  registry sources for this angle)

Compute it before you start. Recording cells only for the sources you happened to work reads as
a coverage gap, because that is exactly what it is.

If the product computes empty — every applicable group type absent, or every source skipped —
the outcome is `vacated`, not a cell-less `ran`. Otherwise the angle reads as an honest empty
search while concealing that it was hollowed out upstream.

## Cell statuses

| status | meaning | also required |
|---|---|---|
| `reached` | the source answered | `returned` and `kept` |
| `unreachable` | could not be queried at all | `cause`, `fallbacks_tried` |
| `partial` | answered incompletely | `cause` |
| `embargoed-placeholder` | a stub pending disclosure | `cause` |
| `content-withheld` | answered, but the guardrail withheld it | `cause`, the item, the classification, whether it was routed to notes |
| `not-attempted` | you chose not to run this pair | `cause` naming the **specific** bound |

**A non-`reached` outcome is never written as `reached` with `returned: 0`.** That single
substitution converts "we could not look" into "there is nothing there" and survives every other
check in the bar. `reached` with zero is honest and expected — it just has to be true.

Two statuses carry extra burden because both are always available and neither can be disproved.
`unreachable` requires the registry's fallbacks to have been tried, or it becomes the cheap exit
from a merely slow source. `not-attempted` requires a specific bound, not a blanket "judged
unproductive" repeated across cells — and if most of an angle is `not-attempted`, the honest
record was a `not_run` angle or a skipped source in the map.

## Queries

`queries` holds **every** query you ran for the pair, as run. A pair worked with a broad pass and
two narrow ones records three. At least one must be a broad pass over the group's canonical term:
an angle of nothing but hyper-narrow queries returns honest zeros everywhere while having covered
nothing.

Queries come from the map — the group's canonical term and expansions, honouring its negative
terms. Not from your own domain knowledge, and not from the caller's raw request.

## returned, kept, and the bound

`returned` is what the source gave back; `kept` is what you carried forward. They are equal
unless the cap truncated the tail. Any other difference is a relevance cut, and this wave applies
none.

`bound.dropped` records each dropped item with **the cell it came from** and its ordering value,
so a per-cell difference reconciles against the drop record. Without the cell, a capped angle is
unjudgeable and a relevance cut launders as cap truncation.

## Candidates

`id_class` governs the identifier, because three of the four always-on angles surface items that
have no registry id:

| id_class | identifier |
|---|---|
| `registry` | the corpus's own id — `CVE-…`, `GHSA-…`, `CAPEC-…`, `CWE-…` |
| `attack-technique` | the ATT&CK technique id |
| `control-requirement` | the **version-pinned** control id, e.g. `v5.0.0-1.2.5` |
| `incident-record` | the corpus's record id plus the incident date |
| `non-registry` | a stable URL, the published title, and the retrieval date |

Never invent a registry-shaped id for a write-up, a talk or a post-mortem. `found_by` lists
**every** cell that returned the item — an item several groups surface against one source is
recorded once with all its cells, not duplicated per cell, since duplication is padding and the
cell's `kept` counts results rather than distinct candidates.

For an item that ranked inside the cap without an obvious scope link, the honest relevance line
is `retained under the no-cut rule; scope link unclear`. Inventing a connection is the failure
mode that leaves no arithmetic trace.

## Worked example (abridged, outcome `ran`)

```yaml
schema_version: 1
meta: {angle_id: a2, as_of: "2026-08-03T11:00:00Z"}
outcome: ran
coverage:
  - group_id: approval-authz
    source_id: capec
    queries: ["authorization bypass", "CAPEC authorization bypass user-controlled key"]
    timestamp: "2026-08-03T11:02:00Z"
    status: reached
    returned: 6
    kept: 6
    sanitization: {status: sanitized}
  - group_id: file-upload-weaknesses
    source_id: capec
    queries: ["unrestricted file upload"]
    timestamp: "2026-08-03T11:04:00Z"
    status: reached
    returned: 0
    kept: 0
    sanitization: {status: sanitized}
  - group_id: approval-authz
    source_id: attack
    queries: ["valid accounts abuse"]
    timestamp: "2026-08-03T11:06:00Z"
    status: unreachable
    cause: "endpoint returned 503 across three attempts"
    fallbacks_tried: ["mirror export", "cached corpus download"]
    sanitization: {status: unavailable, cause: "no content retrieved"}
retrieval_summary:
  degraded_sources:
    - {source_id: attack, status: unreachable, cause: "endpoint returned 503 across three attempts"}
  status_counts: {reached: 2, unreachable: 1}
bound:
  cap: 50
  ordering_signal: "CAPEC Likelihood Of Attack"
  dropped: []
candidates:
  - id: "CAPEC-639"
    id_class: registry
    title: "Probe System Files"
    authority_band: authoritative-registry
    found_by:
      - {group_id: approval-authz, source_id: capec, query: "authorization bypass"}
    ordering_value: "Medium"
    relevance: "approval workflow exposes a claim id the caller supplies; this pattern targets exactly that"
notes:
  - {kind: vocabulary, text: "CAPEC uses 'privilege abuse' where the map says 'self-approval'"}
```

The second cell is the honest zero this artifact exists to make provable. The third is a failure
recorded as a failure, appearing in both the cell status and the retrieval summary — the two
records a reviewer reconciles against each other.
