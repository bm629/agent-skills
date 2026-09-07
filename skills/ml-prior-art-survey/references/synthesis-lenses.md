# The synthesis lenses

Seven lenses over the extract records, producing `ml-option-register.yaml`. L1 is the spine; the
rest qualify it.

## L1 — the adoption ladder, per capability

For each `capability_tag`, take the **FIRST admissible rung**, in this order:

| # | rung | admissible when |
| --- | --- | --- |
| 1 | `use-hosted-api` | a hosted model exists whose measured latency and throughput meet the SLA — or the SLA is not constraining, where that angle did not fire — at a recorded unit price, with compatible data-handling terms |
| 2 | `adopt-open-weights` | an open-weight model exists whose `license_use_restrictions` permit our use AND which has a **third-party** measured result on a benchmark L2 judges appropriate |
| 3 | `fine-tune-pretrained` | rung 2's model exists but misses the bar, a licence-compatible fine-tuning dataset exists, and the run is costed |
| 4 | `train-from-scratch` | rungs 1-3 each fail for a NAMED reason, the run is costed, and the data exists or its acquisition is costed |

**Descending a rung must be justified in one sentence naming the record that failed and why.** The
gate checks the arithmetic of this — a verdict at position N owes N descents, each for a rung
strictly above it, each naming a record that resolves. Whether the reason is TRUE is a reviewer's
condition, and an undefended descent is the exact failure this survey exists to prevent.

Note what rung 2 requires: `reported_by: third-party`. A vendor's own number is documentation, not
measurement, and a rung taken on one is a rung taken on the vendor's word.

## L2 — yardstick validity

Does the benchmark ranking these candidates measure OUR capability? The register names the
`BENCH-` record, what it measures, the delta to our capability, and its `contamination_noted`
state. **This is why `benchmark` is a record class at all**: without a record there is nothing to
judge, and a benchmark name in prose resolves to no evidence.

`contamination_noted: unstated` is a finding about the benchmark, reported as such — not a blank
and not an accusation.

## L3 — licence and use-restriction feasibility

Group by `license_use_restrictions` **across models AND datasets**. A permissively-licensed model
fine-tuned on a non-commercial dataset is not permissively licensed downstream, and that
composition is invisible unless the lens crosses both kinds — which is why `composed_from` on a
tuning rung must name more than one artifact, and the gate says so.

**A restriction disqualifies regardless of `score`.** An excellent artifact we may not use is not
an option.

## L4 — cost and serving envelope

Roll the per-record `cost` and `serving` blocks into a **collective** envelope for a NAMED
capability set: CPU versus GPU, batch versus real-time, unit cost at the volume the scope implies,
and whether the real-time target is reachable at all.

**Never sum across capabilities without saying which ones** — which is what `capabilities_covered`
records, and why it is required rather than optional.

## L5 — realistic accuracy expectation

Translate the headline metric into a user-visible consequence, always carrying the metric, the
benchmark and the measured population: *"F1 0.85 on `<benchmark>` means roughly 15% of fraud
undetected — measured on `<population>`, not on ours"*.

**NEVER RECOMPUTE.** No pooling across benchmarks, no metric conversion, no derived statistic. The
figure is the record's, carried as the record states it; the consequence is prose beside it, not
arithmetic on it. A number that has been through an unstated transformation is no longer evidence
of anything, and nobody downstream can tell it happened.

`measured_population` is required for exactly this reason: it is the field that says the figure was
measured on somebody else's data.

## L6 — the governance-documentation gap

**Fires only when the governance angle ran.** For the chosen rung, which of the documentation an
AI-governance regime would require can be evidenced from the record's `governance` and
`considerations` blocks, and which cannot.

**Where that angle did not fire, the register carries a null gap, the report states that, and
stops.** It never speculates about a regime that was not searched, and it never substitutes for a
dedicated regulatory survey. The gate enforces both directions: a gap reported when the lens did
not run is refused, and so is a null gap when it did.

## L7 — currency and absence

Every record carries `as_of`; the report dates every claim, and flags anything resting on a frozen
or archived corpus as historical rather than current.

Absence is phrased as a search result — *"no adoptable model surfaced across the N angles that ran
and the M terms searched, at their state on `<date>`"* — **never "none exists" and never "this is
novel"**. This corpus moves faster than most: the lead source this survey was designed around is
gone, and a second channel that was open at design time now refuses. An absence sentence that
claims more than a search can support is wrong the day it is written and embarrassing six months
later.

## `capability_tags` are checked against the project first

The synthesis run's FIRST deterministic check validates every `capability_tags` value against the
project's `capability-map.yaml`, before any tally. The portable gate structurally cannot see the
project's scope files, so this one belongs to the run that owns them. A tag outside the map means
either the tag is invented or the map is incomplete — different findings, different owners. Say
which.
