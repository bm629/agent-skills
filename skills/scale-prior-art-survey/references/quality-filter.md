# The quality filter

**It RANKS. It never cuts.** `score` is an integer 0-10 on the SOURCE record, and nothing in the
gate uses it to admit or refuse anything. A filter that cut would delete the operational canon and
every negative result — the same reasoning that keeps `no-stated-load` out of the bail causes.

The validator checks two things and no more: that `score` is PRESENT, and that it is an integer in
range. It never checks the number's justification, because a deterministic gate cannot judge one.

## The ten signals

`score` is the count of these that the source satisfies. It is a COUNT, not a judgement, which is
what makes "whether a 9 is a 9" answerable by a reviewer reading the source rather than arguing
with a band.

| # | signal | satisfied when |
| --- | --- | --- |
| 1 | **The number is measured, not modelled** | The source ran something and reports what it observed, rather than projecting from a formula. |
| 2 | **The configuration is disclosed** | Hardware, dataset and workload are stated beside the result — the SPEC conditions-of-observation leg. |
| 3 | **Percentiles rather than a mean** | A latency or duration figure reports a distribution (p95, p99, max), not an average that hides the tail. |
| 4 | **The duration is stated** | The reader can tell a ten-minute sustained rate from a peak. |
| 5 | **Before/after, or a comparison** | The result is placed against something — a prior version, a competing engine, an unloaded baseline. |
| 6 | **The cost is stated** | The number comes with what it took to reach it: instance shape, node count, spend, or the tuning applied. |
| 7 | **Reproducibility** | A harness, a script, a rule-governed benchmark, or an artifact badge — anything a reader could re-run. |
| 8 | **Independence** | The measurer is not the vendor of the thing measured, or the method is auditable enough that it does not matter. |
| 9 | **The failure case is reported** | The source says where it stopped working, not only where it worked. |
| 10 | **Dated within the hardware generation** | The result is recent enough that the machines underneath it still exist — this type's own founding risk. |

A source satisfying none of the ten still gets a `score: 0`, is still extracted, and still carries
its `transferability`. **The filter ranks. It never cuts.**

## What the number means

| band | what it says |
| --- | --- |
| 8-10 | Measured in production or under a rule-governed benchmark, with the configuration disclosed. |
| 5-7 | Measured or peer-reviewed, with part of the configuration stated. |
| 2-4 | A vendor-documented limit, or an independent verification with no configuration. |
| 0-1 | Narrative only: the source describes an outcome and measures nothing. |

The bands are a ranking aid for whoever reads the extract queue. They are not an admission test,
they do not feed `confidence`, and an episode scored 0 is still extracted, still recorded, and
still carries its `transferability`.
