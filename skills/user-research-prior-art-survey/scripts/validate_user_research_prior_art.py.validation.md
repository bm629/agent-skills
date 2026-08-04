# `validate_user_research_prior_art.py` — validation

## What it is

The deterministic gate for both wave-1 artifacts. Two subcommands, 46 rules, 97 tests.

```
validate_user_research_prior_art.py keyword-map <file>
validate_user_research_prior_art.py search <file> --keyword-map <file>
```

Exit **0** clean · **1** a rule failed · **2** an input could not be read at all. The third code
matters: a missing file, a YAML syntax error and a non-UTF-8 blob are all CALLER faults, and
reporting them as rule failures would send someone off to edit an artifact that may be fine.

## What it checks, and what it deliberately does not

**Shape and arithmetic only.** Schema conformance, enums, ranges, required fields, and the
reconciliations that hold two records against each other: coverage completeness in both
directions, `kept` against the rows naming each cell, `status_counts` against the cells, the cap
against the registry.

**It judges nothing semantic.** Whether a stated method really appears in the paper, whether a
relevance line is persuasive, whether a zero is a laundered failure — all of those are the
reviewing twin's numbered conditions. A fuzzy heuristic inside a deterministic gate produces
false failures and duplicates the reviewer, which is why the module docstring says so and why
this document repeats it.

## The type-specific rules

Four rules exist only here, and each checks something no schema can:

- **`crawl-delay-honoured`** — where the registry declares a delay for a cell's source and the
  cell actually retrieved something, the cell must record its `selection`. Registry-dependent, so
  the schema cannot express it. Deliberately does **not** fire on a cell that never got a
  response: demanding a selection from a rate-limited cell would be a false failure, and worse, it
  would push a run to invent a selection it did not make.
- **`access-status-required`** — every source belonging to an angle whose verdict HOLDS must
  appear in the map's `sources.active` or `sources.skipped`. A source in neither has no posture
  anywhere, and the applicable-set intersection then drops it silently. Sources of a non-holding
  angle are correctly exempt.
- **`web-id-needs-url`** — a `web` candidate must carry its url. A DOI and an arXiv id each have a
  resolver behind them; a web id has nothing.
- **`admission-vs-access-status`** — a candidate admitted on retrieved full text whose cell's
  source the map records as `paywalled-abstract-only`. One of the two records is wrong, and the
  contradiction is exactly this survey's worst failure made mechanically visible.

## Reachability

Every rule has a test that makes it fire. That is not a coverage nicety: the shipped precedent in
this family twice contained a function defined and never called, and a green suite hid it both
times because the tests called the function directly rather than through the subcommand.
`TestTriggerAnchors::test_anchor_failures_are_wired_into_the_map_subcommand` exists specifically
to assert the wiring rather than the function.

No rule duplicates a schema `required`. A rule the schema short-circuits can never fire, and
shipping one is dead code that reads as a check.

## `record_filename`

Ships but is **not called by this module** — wave 1 mints ids and writes no records. It is here
because the ids are minted here and a later stage derives filenames from them; shipping the
minting without its mapping invites the id being used verbatim downstream, which for a DOI turns
its slash into a directory and lands the record where nothing looks for it, perfectly valid and
treated as never written.

Its injectivity is tested across **both** branches, including that a hashed stem fed back in does
not return itself — the identity branch must refuse a hashed-looking input, or the two branches
share an output namespace and a stem collides with the id it came from. That defect shipped live
in a sibling package.

## How to run it

```
unset VIRTUAL_ENV RUFF_NO_CACHE
python scripts/validate_user_research_prior_art.py keyword-map scripts/fixtures/research-vocabulary-map.valid.yaml
python scripts/validate_user_research_prior_art.py search scripts/fixtures/search-output.valid.yaml \
    --keyword-map scripts/fixtures/research-vocabulary-map.valid.yaml
```

Both shipped fixtures exit 0 and are the reference; the tests mutate copies in memory so the
files on disk stay clean.

## Dependencies

`pyyaml`, `jsonschema` (Draft 2020-12). Both schemas are read from `../schemas/` and the registry
from `../references/source-registry.yaml`, so the package is self-contained and relocatable.
