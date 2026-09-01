# Planted fixtures

Artifacts that **pass the deterministic gate at exit 0** and are nonetheless wrong. They exist to
test the judgment half of the two-part gate, which is the half a validator run cannot exercise: a
gate demonstrated only on good input proves nothing about it.

Filenames are deliberately uninformative, and no file here names, hints at or comments on what is
wrong with it. The defect-to-condition mapping is the answer key, and it lives in the package's
test module — which the reviewer under test never reads. Recording it here would turn every future
blind run into an open-book one, and a reviewer that has read the key cannot demonstrate anything.

Each fixture is a complete, schema-valid artifact of its kind. Do not "fix" one: a failing
validator run against anything in this directory is a bug in the fixture or a change in the
validator, and either way the fixture is the thing to look at first.

To reproduce the blind run, hand a subagent the reviewing skill and one fixture, with no other
context, and require it to name a numbered condition.
