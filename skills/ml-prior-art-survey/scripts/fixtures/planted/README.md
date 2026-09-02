# Planted fixtures

Artifacts that **pass the deterministic gate at exit 0** and are nonetheless wrong. They test the
judgment half of the two-part gate, which a validator run cannot exercise: a gate demonstrated only
on good input proves nothing about it.

Filenames are deliberately uninformative, and no file here names, hints at or comments on what is
wrong with it. The defect-to-condition mapping is the answer key, and it lives in the package's
test module — which the reviewer under test never reads. Recording it here would turn every future
blind run into an open-book one.

Each fixture carries ONE defect. A fixture with two does not test which one a reviewer can find; it
tests which one it happens to look at first.

Each is a complete, schema-valid artifact. A failing validator run against anything in this
directory is a bug in the fixture or a change in the validator, and either way the fixture is the
thing to look at first — do not "fix" one by making it valid, because passing at exit 0 is the
point.

To reproduce the blind run, hand a subagent the reviewing skill, one fixture, AND the clean
vocabulary map — the map is a separate INPUT to a search-output review, not context to be
withheld. Two conditions judge a candidate against the group the map minted, and a reviewer
without it cannot exercise either. Then require a numbered condition in the finding.
