# Calibration fixtures

The CLEAN artifacts, copied byte-for-byte from the producer's `scripts/fixtures/`. They are what
both halves of this pair calibrate against: the producer's gate exits 0 on them, and this reviewer
returns `approve`.

They are copies, not a second source. A guard asserts they are byte-identical to the producer's and
that they still return `[]` from the producer's own validator — the fixture's reading is the one
that propagates, and a drifted copy calibrates the reviewer against an artifact the gate would
refuse.

Planted fixtures live in the producer package only. A reviewer that has seen the answer key is not
a blind reviewer.
