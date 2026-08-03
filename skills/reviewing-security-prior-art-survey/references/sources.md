# Research provenance

This skill is the reviewing half of a pair. Its bar is derived from the same method research as
its producer — see `security-prior-art-survey/references/sources.md` for the full provenance of
the corpus, channel, signalling and record-format findings. No second research pass was run, by
design: a reviewer grading against a bar it derived independently would be grading a different
artifact than the one the producer was told to make.

## What shaped the conditions specifically

**Provable absence.** Systematic-review practice (PRISMA-S) treats a recorded zero as evidence
that a search ran, and a missing cell as no evidence at all. This is the origin of conditions 9,
10 and 11 — and the reason condition 14 exists separately, since an angle that could not run is a
third state that neither a hit nor a zero represents, and condition 11 covers the same split one
level down at the individual cell.

**Reproducible search records.** PRISMA-S requires the queries as executed, the source, the date,
and the result count, on the grounds that a paraphrased query cannot be re-run. This produced
condition 12, and condition 13's spot-check posture — verifying a sample rather than re-deriving
the whole search, which would cost more than the work under review. The probe-asymmetry clause
sits in condition 11, beside the failure statuses it protects.

**Point-in-time signals.** EPSS is an explicitly short-window forward probability and CISA KEV
membership changes as the catalog is updated. Both are meaningless without a read date, which
produced condition 16.

**Corpus versioning.** CWE ships several releases a year while CAPEC can sit unchanged for
years, and OSV, GitHub Advisory and KEV are rolling with no release concept at all — so an
artifact that does not stamp what it read cannot be compared with a later run. This produced
condition 6.

**Adversarial corpus.** Unlike other prior-art domains, this one's sources include material
authored to be acted upon by automated readers. Condition 19 exists because a survey that
follows a retrieved instruction turns the project's own research step into its first
compromise — and because that failure leaves visible traces in the artifact, which makes it
reviewable.

**Condition numbering is load-bearing.** Every finding must cite a number, so a renumbering that
does not sweep this file produces findings the producer cannot act on. Any change to the
condition set updates the conditions file first, then sweeps every cross-reference here.

**Review posture.** The producer/reviewer split, the deterministic-check-first ordering, the
independence requirement, the collect-all-findings-in-one-pass rule, and the no-false-revise
calibration are inherited from the established shape of this collection's other reviewing skills,
which pair each producing skill with an acceptance gate that judges craft rather than domain.
