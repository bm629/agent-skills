# The synthesis lenses

A lens is a **cut ACROSS** the extract corpus, not a walk through it. A report that reads as a list
of records has been concatenated, not synthesised. Every lens output must be copied from a record
that says it — which is why every claim in the index carries the record ids it rests on.

| id | formula |
| --- | --- |
| **L1 — convergence** | Group by `(mechanism, normalised decision)`. Convergent when **two or more distinct `platform_id`s with `authority: first-party-normative`** state the same value independently. The output NAMES the platforms, never just a count. |
| **L2 — divergence with cause** | For each disagreed decision, partition the disagreeing set by `platform_type` and by `reversibility`. A disagreement that partitions cleanly on `platform_type` is a **type-determined** choice: recommend what platforms sharing ours do. One that does not partition is a genuinely open choice: present the tradeoff and **refuse to pick**. **Never resolve a divergence by dropping the weaker source** — record the dissent and its basis. |
| **L3 — surface size** | Take `enumeration_count` from each platform's enumerating records; report min / median / max, each paired with ecosystem age. **The recommendation is the MINIMUM surface any comparable platform shipped, not the median.** |
| **L4 — trust-boundary cost** | Join each platform's sandbox record to its review record and report the PAIR. The pattern to test: a stronger sandbox correlates with lighter review. **Recommending a sandbox without stating its review cost is forbidden.** |
| **L5 — commercial terms with volatility** | One row per platform over the `volatility: contractual` records, each cell carrying its `as_of` and `evidence_quote`. A cell more than **90 days** older than the report date renders with a staleness marker, and the gate refuses a decision resting on one that does not. **No cross-platform average is computed** — averaging contractual terms across platform types is meaningless, and is precisely how a fabricated "industry standard" enters a document. |
| **L6 — complementor friction** | Pair each reported friction against the first-party record for the same `platform_id`. A friction WITH a matching record is a known cost; one with NO matching record is an **undocumented cost** — and the undocumented set is the report's highest-value output, because it is exactly what our own documentation would also fail to mention. |
| **L7 — migration debt** | Over the migration records, compute `enforced_on − announced_on` per platform, record what the platform built to survive the interval, and report the DISTRIBUTION and its correlation with `reversibility`. |
| **L8 — build-order by reversibility** | Sort `one-way` → `costly` → `cheap`, then within a tier by L3's minimum-surface evidence. `build_first` iff `one-way` **or** in the minimum surface of every comparable platform. Defer iff `cheap` **and** absent from the minimum surface of at least one comparable platform — and the deferral **must name the trigger that un-defers it**, taken from L7's intervals. A bare "later" is what this replaces, and the gate refuses one. |
| **L9-bis — an angle the TRIGGER excluded** | Neither vacated for want of a source nor ran-and-found-nothing: never dispatched. Those sections render `not-applicable: <the predicate that excluded it>` — never an empty heading, and never silence, which reads as "we looked and found nothing". |
| **L9 — absence** | An angle that VACATED for want of a source produced no evidence about the world; one that RAN and found nothing did. Phrase it as *"no documented X found across N angles and M reference platforms, at their `<date>` revisions"* — never *"no platform does X"*. |

## The expected result on this corpus, stated so nobody treats it as thin work

**Most marketplaces do not publish their ranking function.** An honest zero for the discovery
section is worth more than an inferred ranking model, and a reviewer must not read it as a gap.

## `convergent_answer: null` is a result

No convergence found is a finding about the ecosystem, not a hole in the survey. Filling it with
the most common answer, or with the answer from the platform most like ours, converts a real
disagreement into a false consensus.

## `capability_tags` are checked against the project first

The synthesis run's FIRST deterministic check validates every tag against the project's
`capability-map.yaml`, before any tally. The portable gate never sees that file, and exact set
membership is the wrong task to hand a judgement — so it belongs to the run that owns the scope.
