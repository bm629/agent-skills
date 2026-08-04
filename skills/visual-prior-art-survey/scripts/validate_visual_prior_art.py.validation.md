# Validation — `validate_visual_prior_art.py`

## What it is

The deterministic gate for the two wave-1 artifacts.

```
validate_visual_prior_art.py keyword-map <file>
validate_visual_prior_art.py search <file> --keyword-map <file>
```

One `FAIL <rule>: <detail>` line per violation. Exit **0** clean, **1** a rule failed, **2** an
input could not be read (missing path, unparseable YAML). An input fault is not an artifact
fault, and the two must not share an exit code — a caller reading only the code would otherwise
go and edit a file that may be perfectly fine.

## Scope — shape only

Schema conformance, enums, ranges, required fields, and arithmetic reconciling two records
against each other. It never judges whether a convention really binds, whether a corpus was well
chosen, or whether a relevance line persuades — those are the reviewing skill's numbered
conditions. A fuzzy heuristic in a deterministic gate produces false failures on honest artifacts
and duplicates the reviewer.

**The corollary, learned here:** a rule that duplicates the schema can never fire. Four such
rules were written and removed — the schema marks `corpus_version`, `prescriptivity`,
`admission.corpus_url` and `admission.corpus_release` required, so it short-circuits first. The
schema owns presence; the validator owns what the schema cannot express (per-class id shapes,
cross-record arithmetic, registry agreement); the reviewer owns judgment.

## Rules emitted (44)

Inherited shape rules, plus the type-specific ones: `id-class-shape` (per-corpus identifier
form), `token-format-pinned` (a claimed token format must be DTCG and versioned),
`negative-terms-required` (scoped to `design-system` groups only), and the trigger-anchor family
`anchor-required` / `anchor-must-be-required` / `anchor-only-on-conditional`.

## Inputs

Reads `../schemas/*.json` and `../references/source-registry.yaml` relative to its own location,
so the package is relocatable. **The registry is a validator INPUT, not reference prose** —
angle verdicts, per-angle caps, applicable group types, trigger anchors and the excluded-source
list all come from it.

## How it was validated

- `python -m pytest scripts -q` → **96 passed**.
- Both subcommands against the shipped fixtures → exit 0.
- Rule sweep both directions: every emitted rule has a test.
- Each rule class proven by a **planted defect on a scratch copy** — introduce the defect,
  observe the suite fail on exactly the owning test, discard the copy.
  **This is what caught the real gap:** after the angle references landed, the suite was green at
  76 and three planted defects survived it, because stripping the sibling's market-specific test
  classes had left every visual rule uncovered. A green suite is not evidence; a sweep is.
- `ruff check --ignore D` and `ruff format --check` clean.

## Dependencies

`PyYAML` and `jsonschema` (Draft 2020-12) importable. No network, no project-specific imports.
