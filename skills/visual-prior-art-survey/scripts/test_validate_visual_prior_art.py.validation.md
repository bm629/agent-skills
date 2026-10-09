# Validation — `test_validate_visual_prior_art.py`

**163 tests** in this file, plus 24 in `test_capture_live_site.py` for the b6 capture script
(187 as of 1.4.0). Run: `python -m pytest scripts -q`.

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
| `TestBound` | A bound cap says what it dropped |
| `TestReviewFindings` | Cases a code review found untested, each of which would have shipped green |
| `TestExtractsBoundary` | `--extracts` supplied but unusable does not read as "the rows are wrong" |
| `TestQueueCoverage` | The third direction: frozen queue to record |
| `TestExtractHeadings` | A required heading must be a whole line, not a substring |
| `TestLiveSiteFixtures`, `TestLiveSiteSchema` | b6's fixtures pass clean; the defects the schema owns are asserted at the schema |
| `TestObservedKeptApart`, `TestCapturesNeverBind` | `live-site`, `observed-site` and `observed` travel together; a capture binds nothing (`applies: false`) |
| `TestExcludedSite`, `TestCaptureFile`, `TestCaptureVerbatim`, `TestCaptureOrder`, `TestOneUserAgent`, `TestCaptureIdentity` | b6's capture rules, one class each |
| `TestBranchesThatMustBite` | Each test fails when the one branch it names is removed |
| `TestWaiTutorial` | A WAI tutorial page is its own id class, and is `descriptive` |

## Why the cross-branch injectivity test matters

`record_filename` must never map two ids to one stem. The identity branch returns a
filename-safe id unchanged — and a hashed stem is filename-safe, so without a guard it
round-trips to itself and collides with the id it was derived from. Testing collisions only
*within* the hashing branch gives false assurance; the constructible collision is across them.

## Dependencies

`pytest`, `PyYAML`, `jsonschema`. No network; fixtures are local.
