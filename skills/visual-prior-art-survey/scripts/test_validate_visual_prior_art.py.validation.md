# Validation — `test_validate_visual_prior_art.py`

**96 tests.** Run: `python -m pytest scripts -q`.

## Conventions

- Every test mutates a **deep copy** of a valid fixture in-process. Never revert a planted defect
  with a VCS checkout — that discards uncommitted work alongside it.
- Tests assert on **rule names**, not message text, so wording can improve freely.
- Where a check has a direction, both are tested — more than the cap and fewer, a missing cell
  and a surplus one. A one-directional check on a two-directional property reads as covered and
  is not.
- A test asserts the **layer that owns the check**. Removing a schema-required field asserts
  `schema`, not a semantic rule — asserting the semantic rule would be asserting a rule that can
  never fire.

## Coverage

| Group | Asserts |
| --- | --- |
| `TestFixtureIsValid` | Fixtures pass clean and exercise every group type |
| `TestSchemaShape` | Required keys, enums, timestamps, short-circuit on schema failure |
| `TestGroupRules` | Id uniqueness, expansion cap/floor, type accounting, relation variety |
| `TestProbeRecord` | `probe-discovered` provenance needs a performed probe |
| `TestSourceAccounting` | Sanitization cause; a terms-excluded source may not be active |
| `TestAngleVerdicts` | Completeness, unknown angles, no always-on angle switched off |
| `TestRegistryContract` | Angle/source/fallback resolution; angle references both directions |
| `TestSearchShape`, `TestOutcomeBranches` | The three outcomes and their owed blocks |
| `TestCoverageReconciliation` | Counts, causes, summary reconciliation, known group/source |
| `TestCoverageCompleteness` | Missing and surplus cells against the applicable set |
| `TestMalformedInputs` | A bad map reports rather than raises; CLI exit codes 0/1/2 |
| `TestUniquenessAndSubstitution` | Duplicate cells/verdicts; `fallback_used` validity; `vacated` |
| `TestVisualCandidateRules` | Id shape per corpus, token-format claim, kept arithmetic, cap vs registry, negative terms scoped to design-system groups |
| `TestTriggerAnchors` | Every conditional angle anchors on a REQUIRED field; optional legs are legitimate wideners |
| `TestRecordFilename` | Identity, sanitization, and **cross-branch injectivity** |

## Why the cross-branch injectivity test matters

`record_filename` must never map two ids to one stem. The identity branch returns a
filename-safe id unchanged — and a hashed stem is filename-safe, so without a guard it
round-trips to itself and collides with the id it was derived from. Testing collisions only
*within* the hashing branch gives false assurance; the constructible collision is across them.

## Dependencies

`pytest`, `PyYAML`, `jsonschema`. No network; fixtures are local.
