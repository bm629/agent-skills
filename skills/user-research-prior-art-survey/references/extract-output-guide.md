# Extract output guide (frontmatter fields)

`schemas/extract-output.schema.json` is authoritative; this guide explains it.

## Always present

| Field | Meaning |
|---|---|
| `schema_version` | `1`. |
| `meta.source_id` | `DOI-<doi>`, `ARXIV-<id>` or `WEB-<domain>-<slug>`. Names the queue row, the spawn key and the file. |
| `meta.as_of` | When the source was read. |
| `meta.revision` | 1 on first write; incremented when a review round rewrites it. |
| `outcome` | `extracted` or `skipped`. |

## `skipped` — the bail

| Field | Meaning |
|---|---|
| `skipped.cause` | `concerns-none-of-the-scope` (the relevance bail — requires confidence), `no-stated-method` (out of scope by L-1), `source-unreachable` (a retrieval failure, never a finding of absence), `forbidden-by-terms`. |
| `skipped.detail` | Why, in your own terms, ≥10 characters. |

## `source` — facts shared by every finding in the file

| Field | Meaning |
|---|---|
| `title` / `url` / `venue` | The source itself. |
| `study_date` | When the study was run. Required: synthesis weighs recency and cannot do so against an optional field. |
| `study_design` | `systematic-review`, `meta-analysis`, `controlled-study`, `field-study`, `survey`, `case-study`, `qualitative`, `other`. One of the four facts the certainty rule branches on. |
| `sample_size` | Verbatim, or `null` when none is reported. `null` is a FACT the rule uses, not a gap to fill. |
| `effect_size` | The standardized effect as stated, or `null`. Routinely absent in papers that report means and p-values without one — which is why its absence does not by itself lower certainty below `moderate`. |
| `access_status` | `open-access`, `free-registration`, `crawl-delayed`, `paywalled-abstract-only`, `blocked`. |

## `findings` — one entry per published finding

| Field | Meaning |
|---|---|
| `id` | `<source-id>#f<N>`, minted here after the read enumerated them. The prefix is how synthesis groups by source, and the validator rejects an id that does not extend its source's. |
| `claim` | What the source found, in terms a reader can check against the method. |
| `certainty` | `high`, `moderate`, `low`, `very-low` — assigned by the rule, re-derived by the validator. |
| `transferability.level` / `reason` | Separate from certainty, always. The reason must be substantial enough to weigh; the reviewer grades whether it holds. |
| `population` | Who it was measured on. |
| `platform_context` | The platform or medium — a 2009 desktop result is not a 2026 mobile one. |
| `effect_verbatim` | The measured effect as worded by the source. |

## `notes`

Leads that are not findings of this source. A neighbouring paper you noticed goes here, never as a
second container.
