# Planted fixtures

Four artifacts, one per kind. Each is SHAPE-LEGAL, each **passes the deterministic gate at exit
0**, and each carries exactly one thing that is wrong.

That combination is the whole point. A defect the validator catches proves the validator works,
which was never in question — the REVIEWER is what these calibrate, and a reviewer only ever sees
artifacts that already passed the gate. A fixture the gate refuses never reaches it.

The answer key is NOT here. Which condition each plant is keyed to, and what the defect is, lives
in the test module, which the reviewer under test never reads. The four file headers are
byte-identical for the same reason: a header that varies per file can carry a hint.

Each differs from its clean base in exactly one edit, asserted over the PARSED documents. A
fixture wrong in two ways proves nothing about either — the second defect can mask the first, and
a reviewer that finds one cannot say which.

Parsed, not byte-compared, and that is a real limit rather than an oversight: these files are
re-emitted from their base with one value changed, so YAML comments in the base do not survive
into them. A comment-level difference is expected and is not a second defect; a DATA difference
is, and is what the check counts.
