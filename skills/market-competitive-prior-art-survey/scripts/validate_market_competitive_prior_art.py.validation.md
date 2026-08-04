# Validation — `validate_market_competitive_prior_art.py`

## What it is

The deterministic gate for the two wave-1 artifacts. Two subcommands:

```
validate_market_competitive_prior_art.py keyword-map <file>
validate_market_competitive_prior_art.py search <file> --keyword-map <file>
```

Prints one `FAIL <rule>: <detail>` line per violation. Exit **0** clean, **1** a rule failed,
**2** an input could not be read (missing path, unparseable YAML) — an input fault is not an
artifact fault and the two must not share an exit code.

## Scope — shape only

It checks schema conformance, enums, ranges, required fields, and arithmetic that reconciles
two records against each other. It never judges whether a competitor is real, whether a bail
was honest, or whether a relevance line persuades — those are the reviewing skill's numbered
conditions. A fuzzy heuristic inside a deterministic gate produces false failures on honest
artifacts and duplicates the reviewer, so it is deliberately kept unclever.

## Rules emitted (42)

**keyword-map:** `schema`, `group-id-unique`, `expansion-cap`, `expansion-floor`,
`negative-terms-required`, `group-type-accounted`, `relation-variety`, `probe-record`,
`sanitization-cause`, `forbidden-source-not-active`, `angle-verdict-complete`, `angle-unknown`,
`always-on-angle-holds`.

**search:** `schema`, `outcome-block-required`, `unrun-angle-has-cells`, `ran-requires-coverage`,
`coverage-complete`, `cell-in-applicable-set`, `reached-needs-counts`, `kept-exceeds-returned`,
`status-needs-cause`, `summary-reconciles`, `degraded-source-recorded`, `cell-group-known`,
`cell-source-known`, `cell-source-excluded`, `cap-matches-registry`, `cap-respected`,
`bound-hit-needs-note`, `bound-hit-consistent`, `id-class-shape`, `candidate-id-unique`,
`candidate-provenance`, `admission-corroboration`, `admission-first-party`, `web-id-needs-url`,
`cell-pair-unique`, `vacated-not-empty`, `fallback-declared`, `keyword-map-invalid`, `input`.

**keyword-map** additionally: `angle-verdict-unique`.

## Inputs

Reads `../schemas/*.json` and `../references/source-registry.yaml` relative to its own location,
so the package is relocatable. The registry is a validator INPUT, not reference prose: angle
verdicts, per-angle caps, applicable group types and the excluded-source list all come from it.

## How it was validated

- `python -m pytest scripts -q` → **93 passed**.
- Both subcommands run against the shipped fixtures → exit 0.
- Rule sweep, both directions: every emitted rule has a test; every rule the design enumerates
  is emitted.
- Each rule class proven by a **planted defect** on a scratch copy — the defect is introduced,
  the suite is observed failing on exactly the owning test, and the copy is discarded. A gate
  demonstrating only approve-on-good proves nothing about the checks.
- `ruff check` clean on the module (docstring rules included); `ruff format --check` clean.

## Dependencies

`PyYAML` and `jsonschema` (Draft 2020-12) must be importable. No network, no project-specific
imports — the package ships standalone.

## Note on `record_filename`

Its injectivity guarantee is load-bearing: two ids must never map to one stem, or two records
silently merge into one file. The hashing branch appends a `--<12-hex>` marker and the identity
branch refuses any input already carrying one, so the two branches cannot share an output
namespace — an earlier version without that guard had a constructible collision (feeding a
hashed stem back in returned it unchanged).
