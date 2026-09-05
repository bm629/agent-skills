# The quality filter

**It RANKS. It never cuts.** `score` is an integer 0-10 on the SOURCE record, and nothing in the
gate uses it to admit or refuse anything. A filter that cut would delete the operational canon and
every negative result — the same reasoning that keeps `no-stated-load` out of the bail causes.

The validator checks two things and no more: that `score` is PRESENT, and that it is an integer in
range. It never checks the number's justification, because a deterministic gate cannot judge one.

## The ten signals

Transcribed from the type's design record, in its order. `score` is the count of these the source satisfies — a
COUNT, not a judgement, which is what makes "whether a 9 is a 9" answerable by reading the source
rather than arguing with a band.

They are **this artifact class's ten**, not a sibling's: a repository's CI status says nothing
about whether a scale claim is trustworthy.

| # | signal | satisfied when |
| --- | --- | --- |
| 1 | **A number present WITH its configuration and its date** | The SPEC/TPC bar, and the strongest single signal. All three together — a figure with no configuration or no date does not count. |
| 2 | **The load class STATED rather than inferable** | The source says what load it ran at. "Millions of users" is not a band. |
| 3 | **The measurement method stated** | A workload, a testbed, or identified production traffic — something a reader could picture running. |
| 4 | **Independent verification** | An adversarial analysis, a reproducibility badge, or a third-party benchmark under published run rules. |
| 5 | **A negative result, regression or limit** | Not only a success. The corpus is systematically biased toward wins and this is the counterweight. |
| 6 | **The system named and the claim attributable** | To someone who actually ran it, not to an unnamed "we". |
| 7 | **A before/after pair for a fix episode** | "We made it faster" with no before is a press release. |
| 8 | **Recency relative to the HARDWARE and managed-service generation** | Not calendar recency. This type's founding risk: what ages is the machines underneath the argument. |
| 9 | **Percentiles rather than means** | Wherever latency is claimed. A mean hides the tail that matters. |
| 10 | **Cost stated alongside throughput** | A number without what it took to reach it is not comparable. |

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
