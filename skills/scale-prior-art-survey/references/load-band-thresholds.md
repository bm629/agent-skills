# Load-band thresholds

Per ORDERED dimension: the numeric boundary between each adjacent enum pair, **with the source it
was drawn from** — or, where no published boundary exists, that finding recorded here with the
search that failed to find one.

Nothing upstream defines numeric bands. The classification schema gives the enum NAMES only and no
boundary between them, so this pair cannot cite a table and **must not invent one silently**.

## The machine-readable skip list

The validator reads this block, not the prose. A dimension listed here is one the `load_class`
re-derivation SKIPS: no published boundary exists, so a band cannot be checked against a number,
and a rule that guessed one would refuse correct episodes.

`geo_distribution` is **not** in the list. It is skipped for a different reason and by a different
mechanism — it is NON-ORDINAL, so there is no "adjacent pair" for a boundary to sit between, and
the validator excludes it by construction rather than by discovery. Keeping the two apart is the
point of the list: a dimension discovered to be unsourced must be machine-readable, or the
validator cannot tell a correct episode from a wrong one.

```yaml
unsourced_dimensions:
  - dimension: concurrency
    searched: 2026-09-05
    query: 'published numeric threshold "high concurrency" definition requests per second boundary industry standard'
    finding: >-
      No universally published numeric threshold. The sources located define high concurrency by
      SIMULTANEITY rather than by a number, and the figures they do give are platform-specific
      capacity statements (one instance shape's sustained RPS, one platform's per-service
      concurrency limit), not boundaries between bands. Two sources give incompatible example
      figures for the same word.
  - dimension: real_time
    searched: 2026-09-05
    finding: >-
      The band names are defined terms and their definitions are SEMANTIC, not numeric: hard,
      near and soft real-time are distinguished by the CONSEQUENCE of missing a deadline, not by
      the length of the deadline. A 10 ms deadline can be soft and a 500 ms deadline hard. There
      is therefore no adjacent-pair boundary to record, and any number written here would be an
      invention wearing a citation.
  - dimension: data_volume
    searched: 2026-09-05
    query: 'standard numeric boundary "large dataset" terabytes definition threshold published specification data volume classification'
    finding: >-
      No universal threshold exists, and the sources located say so explicitly: the same dataset
      size qualifies or does not depending on update rate, structure and the tools available. One
      source states that 100 GB may qualify while a static 10 TB dataset may not.
```

## The dimension that IS sourced

| dimension | boundary between adjacent pairs | source |
| --- | --- | --- |
| `availability_target` | The enum members ARE the boundaries: `99` · `99.9` · `99.95` · `99.99` · `99.999`, as percentages of a calendar period. An episode stating a measured availability falls in the band whose member it meets and does not exceed. | The capability map's own `ScaleClassification.availability_target` enum (`project-document-discovery/schemas/capability-map.schema.json`). The members are numeric literals, so no external boundary is needed — the enum is the table. |

The conversion a reader will want, stated once so nobody re-derives it wrongly: over a 365-day
year, `99` allows 3 d 15 h 36 m of unavailability, `99.9` allows 8 h 45 m 57 s, `99.95` allows
4 h 22 m 58 s, `99.99` allows 52 m 35 s, and `99.999` allows 5 m 15 s. This is arithmetic on the
percentage, not a second source, and the validator does not use it — it compares the stated
percentage against the enum directly.

## What the validator does with this file

1. It derives the `primary_dimension`'s `load_class` sub-key from `measured_magnitude` +
   `measured_unit` + this file, and REFUSES a mismatch. **Only** that sub-key: one
   `measured_value` cannot derive five bands, and the other four are recorded from what the source
   states — they are context, not measurement.
2. It parses NOTHING out of prose. `measured_value` is verbatim ("p99 47 ms"); the machine form
   lives in `measured_magnitude` and `measured_unit`, which the producer records. Parsing
   unconstrained text inside a deterministic gate is the fuzzy heuristic the exit contract forbids.
3. `measured_magnitude: null` → the derivation does not run, and the `primary_dimension`'s
   `load_class` sub-key must ALSO be null. **A band asserted with no number behind it is refused.**

**This is not the `confidence` derivation.** That one keys on `measured_value` (prose); this one
keys on `measured_magnitude` (number). A source saying "sub-second" gives prose present and
magnitude null: confidence's absent-branch does not fire while this derivation does not run. That
is correct, and the coherence between them is one separate rule — all three of `measured_value`,
`measured_magnitude` and `measured_unit` travel together or none does.
