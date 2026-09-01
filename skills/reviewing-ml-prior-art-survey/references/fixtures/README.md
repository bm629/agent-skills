# Fixtures

Two artifacts that pass both halves of the gate: `map.clean.yaml` and `search.clean.yaml`.

**They are calibration, not a bar.** Read them to see what a complete, honest artifact looks like
when nothing is wrong — a recorded zero, a cause with observable evidence, three dates held apart,
an absence recorded as a finding. Do not treat any structure in them as required: `../conditions.md`
is the bar, and these illustrate it rather than defining it.

They are byte-identical to the producer's own valid fixtures, deliberately and under test, so what
the reviewer calibrates on is exactly what the producer is checked against.

**The planted defects are NOT here.** They live in the producer's `scripts/fixtures/planted/`,
because a fixture named for the condition it violates cannot GRADE a reviewer that reads its own
directory. Calibration and grading are different jobs and live in different places.
