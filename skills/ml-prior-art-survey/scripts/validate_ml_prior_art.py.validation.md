# Validating `validate_ml_prior_art.py`

Run from this skill's directory:

```
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_ml_prior_art.py keyword-map scripts/fixtures/ml-task-vocabulary-map.valid.yaml
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_ml_prior_art.py search scripts/fixtures/search-output.valid.yaml \
    --keyword-map scripts/fixtures/ml-task-vocabulary-map.valid.yaml
```

Both must exit 0 and print nothing.

## The exit contract, and why 2 is not 1

- **0** clean.
- **1** the ARTIFACT has findings. The author has something to fix.
- **2** it could not be used at all — a fault in the package, the registry, the invocation or the
  input file. **Never the author's to fix by editing the artifact.**

Reporting a class-2 fault as a 1 sends someone off to edit a file that is correct. That has
happened in this family: an unguarded import made a missing dependency exit 1 with a traceback and
no `FAIL` line, so a cold agent had an exit gate it could not satisfy and no way to tell the fault
was not its own.

Check it:

```
PYTHONPATH=/tmp/no-yaml python scripts/validate_ml_prior_art.py keyword-map anything.yaml
# FAIL dependency-missing: ... ; exit 2, no traceback
```

## What this gate does NOT check

Whether a query could be re-run, whether a cause carries observable evidence, whether an authority
ranking is defensible, whether a `holds: false` on a CONDITIONAL angle is right for the scope.
Those are the reviewing twin's, and each of its conditions names the rule that owns the other half.

The `holds` limitation is worth stating plainly: the map records the scope as prose and
`assumptions`, not as the structured capability fields the registry's predicate is written
against, so the conditional half cannot be machine-checked at all. The deterministic half —
`always-on-angle-holds`, verdict completeness and uniqueness, unknown angles — does ship. A
condition believed to be enforced is worse than one known not to be.
