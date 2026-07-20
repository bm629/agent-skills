# Validation proof — test_validate_prior_art.py

- **Method:** executed as the package's test suite (it validates the
  validator; written first per TDD — observed failing with the validator
  absent: 20 failed / 1 passed, then green after implementation). The
  2026-07-19 amendment added 22 tests the same way: each batch written first
  and observed RED (4 extract-cause, 6 search-cell, 4 search cross-field)
  before its implementation landed.
- **Tools invoked:** `pytest -q`, `ruff check` (clean; file-level
  `noqa: D101, D102` — test names are the documentation).
- **Date validated:** 2026-07-19 (unreachable-source amendment, spec/plan v3).
- **Exit codes observed:** original RED run exit 1 (20 failed — validator
  absent); amendment RED runs exit 1 (4, then 6, then 4 failing); final GREEN
  run exit 0 (`63 passed`).
- **Correction (2026-07-19):** the previous proof quoted `27 passed` against a
  suite that had already grown to 41 — a stale count carried across earlier
  cycles, fixed here while regenerating.
- **Caveats:** imports the validator by path insertion; must live beside
  `validate_prior_art.py` and `fixtures/`.
