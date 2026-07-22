# Validation proof — validate_prior_art.py

- **Method:** TDD (tests written first and observed failing), lint, full test
  suite, CLI smoke on a clean fixture and a deliberate mutation.
- **Tools invoked:** `ruff check` (0 findings — "All checks passed!"), `pytest`
  (test_validate_prior_art.py), the CLI directly.
- **Date validated:** 2026-07-22 (synthesis wave — borrow-index validation).
- **Exit codes observed:** pytest exit 0 (`71 passed`); CLI
  `synthesis <borrow-index.valid fixture>` exit 0 ("OK"); CLI on a mutated copy
  (`score: 99`) exit 1 with a `FAIL schema:` line; CLI
  `extract <skip-unavailable fixture>` exit 0 ("OK").
- **Captured output excerpts:**
  - `71 passed` (verbatim pytest tail — 63 from the prior waves, plus 8 added
    by the synthesis wave)
  - `All checks passed!` (ruff)
  - `FAIL cause: a 'unavailable' skip must carry a substantive cause (the HTTP
    status or error text as observed)` (deliberate mutation)
- **Correction (2026-07-19):** the previous proof quoted `27 passed` against a
  suite that had already grown to 41 — a stale count carried across earlier
  cycles. Fixed here as a side effect of regenerating. The discrepancy was
  pre-existing and is recorded rather than silently overwritten.
- **Caveats:** requires `jsonschema` + `pyyaml` on the invoking interpreter;
  resolves `schemas/` and `references/source-registry.yaml` relative to its
  own package location (do not vendor the script out of the package).
