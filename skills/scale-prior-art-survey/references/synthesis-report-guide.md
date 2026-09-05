# Writing the synthesis report

The index is the machine-readable artifact; the report is what a human reads beside it. One
section per area, in the index's own order.

Each section states, in this order: the `default_pattern` and what converged on it; the
`confidence` and **which episode made it that weak**, named by id; the `hard_limits[]` with
`blocks_requirement: true` first, because those are the ones that stop a design; the
`failure_modes[]` with the episodes that evidence each; the `migration_trigger` and the
`dimension` it sits on; the `open_gap`, written as the question rather than as an apology; and
the `currency` caveat LAST — its `note`, with its `dates` beside it — because it qualifies
everything above it rather than adding to it.

`currency` is lens 8 and it is the one output a reader weighs rather than acts on. An area whose
newest evidence is four hardware generations old is not less CONFIDENT — the measurements are
what they are — it is less CURRENT, and this type's founding risk is that what ages is the
machines underneath the argument, not the argument. Do not fold it into `confidence`; do not omit
it because the dates look recent. Where every backing source is undated it is null, and the
section says so.

Two rules about numbers. Every figure carries the episode id it came from. No figure is converted,
rounded or recomputed from `measured_value` — if you want the machine form, quote
`measured_magnitude` and `measured_unit` as the record carries them.

The report never re-scores anything. `confidence`, `score` and `transferability` are the record's,
and restating one differently in prose is how a reader ends up with two answers.
