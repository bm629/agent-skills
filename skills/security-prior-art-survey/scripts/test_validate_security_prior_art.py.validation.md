# Validation proof — `test_validate_security_prior_art.py`

## Syntax and lint

```
python3 -m py_compile test_validate_security_prior_art.py  -> clean
ruff check scripts/                                          -> All checks passed!
```

The file carries a module-level `# ruff: noqa: D103`. Test names are the documentation — each
names the single rule it proves — which is the same convention the sibling code-survey package
uses for its own test file.

## Execution

```
pytest -q  ->  64 passed
```

Dependencies: `pytest`, `pyyaml`, `jsonschema`. The suite imports the validator as a module and
also shells out to it, so both the library surface and the CLI contract are covered.

## Method

Each mutation test deep-copies a shipped valid fixture, breaks exactly one thing, and asserts
the matching rule appears in the returned failures. One violation per test keeps a failure
diagnostic: when a test goes red, the rule it names is the rule that changed.

Two tests run the opposite way, asserting a `not_run` and a `vacated` artifact validate clean
with no coverage whatsoever. A validator that faults those is worse than no validator, because
it pressures a producer to invent coverage for an angle that never ran — which is the exact
dishonesty this whole package exists to prevent.

One test is a deliberate non-case: an unknown angle id returns a single failure and stops,
because nothing downstream is computable without the angle. The multi-violation test explicitly
avoids that combination and says why in a comment, so a future reader does not "fix" the early
return.
