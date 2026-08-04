# Validation — `test_validate_market_competitive_prior_art.py`

## What it is

The test suite for the wave-1 gate. **93 tests.** Run:

```
python -m pytest scripts -q
```

## Conventions

- Every test mutates a **deep copy** of a valid fixture in-process. Never revert a planted
  defect with `git checkout` — that discards uncommitted work.
- Tests assert on **rule names** (`"coverage-complete" in _rules(...)`), not on message text, so
  wording can improve without breaking the suite.
- Positive and negative cases are both present for rules that have a direction. Where a check
  has a mirror — more than the cap and fewer than the cap, a missing cell and a surplus cell —
  both are tested, because a one-directional check on a two-directional property reads as
  covered and is not.

## What is covered

| Group | Asserts |
| --- | --- |
| `TestFixtureIsValid` | The valid fixtures pass clean, and exercise every group type |
| `TestSchemaShape` | Required keys, enums, timestamp format, short-circuit on schema failure |
| `TestGroupRules` | Id uniqueness, expansion cap/floor, type accounting, relation variety |
| `TestNegativeTerms` | Required on the two collision-prone types, and **not** on the others |
| `TestProbeRecord` | `probe-discovered` provenance must have a performed probe |
| `TestSourceAccounting` | Sanitization cause; a terms-excluded source may not be active |
| `TestAngleVerdicts` | Completeness, unknown angles, and no always-on angle switched off |
| `TestRegistryContract` | Angle/source/fallback resolution; angle references exist both ways |
| `TestSearchShape`, `TestOutcomeBranches` | The three outcomes and their owed blocks |
| `TestCoverageReconciliation` | Counts, causes, summary reconciliation, known group/source |
| `TestCoverageCompleteness` | Missing and surplus cells against the applicable set |
| `TestBound`, `TestAngleCapContract` | Cap vs registry (both directions), hit consistency |
| `TestAdmissionRule` | Admission bases, id-class shape, uniqueness, provenance |
| `TestTriggerAnchors` | Every conditional trigger rests on a REQUIRED capability field |
| `TestRecordFilename` | Identity, sanitization, and **injectivity** — including a hashed stem fed back in, the collision that was actually constructible |
| `TestMalformedInputs` | A malformed keyword-map reports rather than raises; CLI exit codes 0/1/2 |
| `TestUniquenessAndSubstitution` | Duplicate cells and verdicts; `fallback_used` validity; `vacated` corroboration |

## Why the injectivity test matters

`record_filename` must never map two different ids to one name. A non-injective mapping merges
two records into one file; downstream stages that locate a record by deriving its filename then
treat the orphan as never written, and it is regenerated forever while looking perfectly valid.
The test asserts two ids differing only in characters the sanitizer collapses still get
different names.

## Dependencies

`pytest`, `pyyaml`, `jsonschema`. No network, no fixtures outside `scripts/fixtures/`.
