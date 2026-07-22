# Validation proof — test_validate_prior_art.py

- **Method:** executed as the package's test suite (it validates the
  validator; written first per TDD — observed failing with the validator
  absent: 20 failed / 1 passed, then green after implementation). The
  2026-07-19 amendment added 22 tests the same way: each batch written first
  and observed RED (4 extract-cause, 6 search-cell, 4 search cross-field)
  before its implementation landed. The 2026-07-22 synthesis batch added 8
  tests (`TestSynthesis`) the same way — written first and observed RED (8
  failed, `synthesis` subcommand absent) before `validate_synthesis` +
  the `synthesis` subparser landed.
- **Tools invoked:** `uv run --with pytest --with jsonschema --with pyyaml
  python -m pytest -q`, `ruff check` (clean; file-level `noqa: D101, D102` —
  test names are the documentation).
- **Date validated:** 2026-07-22 (synthesis wave — borrow-index validation).
- **Exit codes observed:** original RED run exit 1 (20 failed — validator
  absent); 2026-07-19 amendment RED runs exit 1 (4, then 6, then 4 failing);
  2026-07-22 synthesis RED run exit 1 (8 failed); final GREEN run exit 0
  (`71 passed`).
- **Correction (2026-07-19):** the previous proof quoted `27 passed` against a
  suite that had already grown to 41 — a stale count carried across earlier
  cycles, fixed here while regenerating.
- **Caveats:** imports the validator by path insertion; must live beside
  `validate_prior_art.py` and `fixtures/`.
