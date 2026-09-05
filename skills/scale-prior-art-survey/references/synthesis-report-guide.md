# Writing the synthesis report

The index is the machine-readable artifact; the report is what a human reads beside it. One
section per area, in the index's own order.

Each section states, in this order: the `default_pattern` and what converged on it; the
`confidence` and **which episode made it that weak**, named by id; the `hard_limits[]` with
`blocks_requirement: true` first, because those are the ones that stop a design; the
`failure_modes[]` with the episodes that evidence each; the `migration_trigger` and the
`dimension` it sits on; and the `open_gap`, written as the question rather than as an apology.

Two rules about numbers. Every figure carries the episode id it came from. No figure is converted,
rounded or recomputed from `measured_value` — if you want the machine form, quote
`measured_magnitude` and `measured_unit` as the record carries them.

The report never re-scores anything. `confidence`, `score` and `transferability` are the record's,
and restating one differently in prose is how a reader ends up with two answers.
