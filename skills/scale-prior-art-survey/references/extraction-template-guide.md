# The extraction template

One record per source. Frontmatter is flat and bounded, with ONE level of array-of-flat-objects
for `episodes` and nothing deeper.

## The filename is DERIVED, never the id written out

The record is `extract-<record_filename(source_id)>.yaml` and its companion `.md`.
`record_filename` is the function of that name in `scripts/validate_scale_prior_art.py`, and it
is the same function the gate reconciles the frozen queue against. **RUN IT rather than
reimplementing it, and do not reason from a description of it** — two attempts to describe this
function in prose were each wrong in more than one clause, and a producer reasoning from either
would have written valid records under names the gate does not compute. Every row below is
re-derived from the function on every test run, and between them they exercise each of its
branches.

| source id | record |
| --- | --- |
| `WEB-techempower-run-3` | `extract-WEB-techempower-run-3.yaml` |
| `ARXIV-2504.01234v2` | `extract-ARXIV-2504.01234v2.yaml` |
| `DOI-10.1145/3477132.3483577` | `extract-DOI-10.1145-3477132.3483577--a799c8611b25.yaml` |
| `WEB-https://cloud.google.com/architecture/framework/reliability/scaling/` | `extract-WEB-https-cloud.google.com-architecture-framework-reliability-scaling--a85566d8fa1a.yaml` |
| `WEB-https://engineering.example.com/2024/09/scaling-the-ingest-tier-to-two-million-events-per-second` | `extract-WEB-https-engineering.example.com-2024-09-scaling-the-ingest-tier-to-two-million--4208c9b04600.yaml` |
| `WEB-run--0123456789ab` | `extract-WEB-run--0123456789ab--a421f8cbac05.yaml` |

**A DOI always contains `/`, so the derived form is the ordinary case and not a corner.** Written
out verbatim, the id puts the record in a directory nothing looks in: it stays perfectly valid,
the frozen queue reports the source as never extracted, and the index that cites it is refused
for a defect it does not have. The digest is taken of the WHOLE id, so two ids differing only in
characters the sanitizer collapses still get different names.

## The envelope

`schema_version: 1`, then `meta{source_id, id_class, as_of, revision}`, then `outcome`.

`outcome: skipped` carries `skipped{cause, detail}` and **nothing else** — no `source`, no
`episodes`. `cause` is one of `concerns-none-of-the-scope`, `source-unreachable` or
`forbidden-by-terms`. **`no-stated-load` is not among them**: refusing a source for stating no
number would delete the operational canon and every negative result, which is a promotion cut
wearing a relevance bail's clothes.

`outcome: extracted` carries `source{…}` and `episodes[]` with at least one member.

## On the SOURCE

`title`, `url`, `published_date`, `system_name`, `access_status`, `license` and `score`. These are
the facts shared by every episode. A licence is a property of the DOCUMENT, not of a claim inside
it — record it here and never per episode.

## On each EPISODE

`id` (`<source-id>#e<N>`), `signal`, `metric_name`, `load_class`, `technology`,
`consistency_model`, `outcome_kind`, `cause_class`, `evidence_class`, `primary_dimension`,
`claim`, `measured_value`, `measured_magnitude`, `measured_unit`, `pattern`, `confidence`,
`configuration_stated` and `transferability`.

**`evidence_class` sits here, not on the source.** A single post routinely carries one measured
episode beside one narrative aside, and recording it once per source would force you to mis-score
one of them.

**The episode's `cause_class` is not the map's.** Two levels, two vocabularies, one name: the map's
names why a registry row was not surveyed; this one names a failure mode. Their members are
disjoint and the validator checks each against its own.

**`measured_value` is verbatim prose** ("p99 47 ms") — never converted, rounded or recomputed.
Where the source states a number, record it in machine form too: `measured_magnitude` and
`measured_unit`. All three travel together or none does.

**`load_class` sub-keys are nullable.** Sources routinely state one or two dimensions and say
nothing about the rest. Record what the source states; the validator re-derives only the
`primary_dimension`'s sub-key, and only where a boundary is published.

**`transferability` is never folded into `confidence`.** It is the founding-risk field: `level` and
a `reason` of at least twenty characters saying where the claim plausibly carries.

## The four fixed body sections

`## System under load` · `## Episodes` · `## Method and configuration` · `## Transferability`.
The gate checks that each is PRESENT and non-trivial. It never judges the prose.
