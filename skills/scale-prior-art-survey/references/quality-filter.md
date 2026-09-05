# The quality filter

**It RANKS. It never cuts.** `score` is an integer 0-10 on the SOURCE record, and nothing in the
gate uses it to admit or refuse anything. A filter that cut would delete the operational canon and
every negative result — the same reasoning that keeps `no-stated-load` out of the bail causes.

The validator checks two things and no more: that `score` is PRESENT, and that it is an integer in
range. It never checks the number's justification, because a deterministic gate cannot judge one.

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
