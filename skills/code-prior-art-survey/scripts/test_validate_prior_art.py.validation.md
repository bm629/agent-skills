# Validation proof — test_validate_prior_art.py

- **Method:** executed as the package's test suite (it validates the
  validator; written first per TDD — observed failing with the validator
  absent: 20 failed / 1 passed, then green after implementation).
- **Tools invoked:** `pytest -q`, `ruff check` (clean; file-level
  `noqa: D101, D102` — test names are the documentation).
- **Date validated:** 2026-07-17.
- **Exit codes observed:** RED run exit 1 (20 failed — validator absent);
  GREEN run exit 0 (`27 passed` (verbatim pytest tail; suite grown across self-review cycles, re-validated 2026-07-17)).
- **Caveats:** imports the validator by path insertion; must live beside
  `validate_prior_art.py` and `fixtures/`.
