# `test_validate_user_research_prior_art.py` — validation

## What it is

The gate's test suite: 97 tests, and **every one of the validator's 46 rules has at least one test
that makes it fire.** That is the suite's organising constraint, not a coverage target.

```
unset VIRTUAL_ENV RUFF_NO_CACHE
python -m pytest scripts -q
```

## Why "a test that makes it fire" rather than "a test that touches it"

Twice in this family a function was defined and never called, and a green suite hid it both times
— because the tests called the function directly instead of going through the subcommand that was
supposed to invoke it. Coverage was satisfied; the rule could not fire in production.

So the suite is structured around driving each rule from the entry point a caller actually uses,
and `TestTriggerAnchors::test_anchor_failures_are_wired_into_the_map_subcommand` asserts the
wiring explicitly rather than the function's behaviour.

The audit that keeps this honest is mechanical: every `_fail("<rule>")` code in the validator must
appear as a literal in this file. Only `input` is exempt, and it is covered through its printed
`FAIL input` output rather than by name.

## The fixtures are the reference, and mutations happen in memory

Both shipped fixtures exit 0 and stay clean on disk. Every negative test deep-copies one and
mutates the copy, so a suite run never rewrites the reference — and a fixture that drifts is
caught by `TestFixturesAreValid` rather than by someone noticing later.

The map fixture describes a **public library self-service borrowing terminal**, chosen to be
unlike anything a caller of this skill is likely to be handed. A fixture that resembles the
scope an agent is working on invites transcription instead of a real search, and that defect was
found in a sibling package's cold run.

## Both directions, wherever the property has two

- Coverage completeness: deleting an applicable cell fails `coverage-complete`; adding one
  outside the applicable set fails `cell-in-applicable-set`.
- The cap: raising it and lowering it both fail `cap-matches-registry`, because a quietly lowered
  cap truncates coverage while looking compliant.
- `crawl-delay-honoured`: it fires for a reached delayed cell with no selection, and is asserted
  **not** to fire for an undelayed source or for a delayed cell that never got a response.
- `access-status-required`: it fires for an unrecorded source of a holding angle, and is asserted
  not to fire for a source of a non-holding angle, or for one recorded as skipped.
- `admission-vs-access-status`: it fires on an admitted candidate from an abstract-only source,
  and is asserted not to fire when that same source carries only unadmitted rows — the rule bites
  on admission, not on honestly recording that a source was reached and unusable.

## `record_filename` gets a property test, not an example test

Six tests, including the two that matter: that a hashed stem fed back in does not return itself
(the cross-branch collision), and that a mixed sample of DOIs, arXiv ids and web ids maps to
distinct stems. This type is the family's most exposed, because a DOI always contains a slash.

## Package-consistency tests

Four tests assert the package holds together rather than testing the validator: that every angle
source exists and is not excluded, that every registry source carries a `verified` date, that an
angle reference file exists for every registry angle, and that no wave-2 field is reachable in a
wave-1 candidate. The last one is how the wave split stays a fact rather than an intention.

## Known lint note

`ruff check` reports `D` docstring findings on this file under a repo-wide configuration whose
per-file ignores key on a `tests/` path segment. These live in `scripts/`, and CI lints only
application source, never a skills tree. The validator module itself is clean.
