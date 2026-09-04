# Calibration fixtures

The CLEAN artifacts, copied byte-for-byte from the producer's `scripts/fixtures/`. They are what
both halves of this pair calibrate against: the producer's gate exits 0 on them, and this reviewer
returns `approve`.

They are copies, not a second source. A guard asserts they are byte-identical to the producer's and
that they still return `[]` from the producer's own validator -- the fixture's reading is the one
that propagates, and a drifted copy calibrates the reviewer against an artifact the gate would
refuse.

Planted fixtures live in the producer package only. A reviewer that has seen the answer key is not
a blind reviewer.

## WITHHOLD THIS DIRECTORY FROM A BLIND RUN

A cold reviewer dispatched against one of these artifacts must NOT be given this directory. The
first blind run over the clean search output said so in its own words: the artifact it was judging
was byte-identical to a file in its own reference material, and that file's README stated the
expected verdict. **A reviewer told the expected verdict by its own references is not blind.**

Stage a blind packet with `SKILL.md`, `references/conditions.md`, `references/sources.md`, and
**all five** producer-package paths `SKILL.md`'s evidence table names:
`integrations-prior-art-survey/schemas/`,
`integrations-prior-art-survey/references/source-registry.yaml`,
`integrations-prior-art-survey/references/angles/`,
`integrations-prior-art-survey/references/absent-input-policy.md` and
`integrations-prior-art-survey/references/category-vocabulary.md` and
`integrations-prior-art-survey/references/integration-vocabulary-map-guide.md` -- **plus the SCOPE the
producer was handed** — for the calibration run that is
`integrations-prior-art-survey/scripts/fixtures/scope-acme-scheduling.md`, the file the map's
own `meta.scope_ref` names — which C19 judges `meta.classification` against -- and the artifact under
review, alone.

**All five, and the last two are the ones this list used to omit.** C9 cannot be discharged without
the absent-input policy and C13 cannot be discharged without the category vocabulary — `sources.md`
says so of both — so a packet missing them stages a reviewer that is not blind but *blindfolded*,
and then calibrates the pair against what it could not see. Withholding is for WORKED ANSWERS (the
fixtures, the test module), never for the contract a condition is judged against. The vocabulary map a search output was produced against is evidence and IS supplied,
as a separate file, not as a calibration fixture.
