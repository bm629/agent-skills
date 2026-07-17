# Validation proof — validate_prior_art.py

- **Method:** TDD (tests written first and observed failing), syntax/lint,
  full test suite, CLI smoke.
- **Tools invoked:** `python -m py_compile` (implicit via pytest import),
  `ruff check` (0 findings — "All checks passed!"), `pytest`
  (test_validate_prior_art.py).
- **Date validated:** 2026-07-17.
- **Exit codes observed:** pytest exit 0 (`27 passed` (verbatim pytest tail; suite grown across self-review cycles, re-validated 2026-07-17)); CLI
  `keyword-map <valid fixture>` exit 0 ("OK"); CLI on a mutated fixture
  exit 1 with `FAIL schema: ...` lines; `search` without `--keyword-map`
  exit 2 (usage).
- **Captured output excerpts:**
  - `27 passed` (verbatim pytest tail; suite grown across self-review cycles, re-validated 2026-07-17)
  - `All checks passed!` (ruff)
  - `FAIL coverage_missing: group kw-anchor-ccxt x source deps-dev has no
    coverage cell (zero-hit cells are required too)` (deliberate mutation)
- **Caveats:** requires `jsonschema` + `pyyaml` on the invoking interpreter;
  resolves `schemas/` and `references/source-registry.yaml` relative to its
  own package location (do not vendor the script out of the package).
