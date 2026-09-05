# Calibration fixtures

The four CLEAN artifacts, byte-identical to the producer package's copies, plus the SOURCE one of
them was extracted from, the `extracts/` directory the index resolves its evidence against, and
the frozen `extract-queue.valid.yaml` it is reconciled against.

**All four gate at exit 0**, and that includes the synthesis one: it needs BOTH its companions.
Without the extracts directory the gate prints `SKIP extracts-crosscheck`, without the queue it
prints `SKIP queue-crosscheck`, and either one exits 1 — so shipping the index without them would
make the sentence above false for one of the four. It was false once, for the extract copy,
because its companion `.md` was not mirrored.

**They are not a template to match.** A correct artifact for a different scope looks different in
every value and the same in every shape.
