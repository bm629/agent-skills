# Script validation

Loaded during Step 4.2. Validates candidate scripts before they are written; only validated scripts ship.

## Per-language

| Ext | Syntax | Lint (if present) | Smoke (if applicable) |
|---|---|---|---|
| `.sh` | `bash -n <f>` | `shellcheck <f>` | `bash <f> --help` |
| `.py` | `python -m py_compile <f>` | `ruff check <f>` | `python <f> --help` |
| other | (none) | (none) | mark manual-required; skip from the skill |

## Pass criteria

Syntax MUST pass (exit 0) or the script is excluded — no exceptions. Lint and smoke are optional, but a failure on an available tool counts as a failure. A missing tool is not a failure.

## On pass

Write `scripts/<name>.{sh,py}` and a sibling `scripts/<name>.validation.md`:

```
# Validation: <name>
- Method: <checks run>
- Tools: <tool versions>
- Date: YYYY-MM-DD
- Exit codes: <per tool>
## Captured output
<relevant excerpts>
## Caveats
<if any — e.g. smoke only covers --help>
```

## On fail

Exclude the script; append a block to `references/skipped-scripts.md` (name, attempted method, failure reason, why we think it failed, recommended action). Strip every reference to it from the `SKILL.md` body during Step 4.3. If all scripts fail, the skill ships with no scripts — a non-fatal warning, not an abort.
