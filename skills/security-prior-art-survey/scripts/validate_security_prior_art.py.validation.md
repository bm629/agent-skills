# Validation proof — `validate_security_prior_art.py`

Every script shipped in this package carries a sibling proof. This records what was run and
what it returned; it is regenerated whenever the script changes.

## Syntax and lint

```
python3 -m py_compile validate_security_prior_art.py     -> clean
ruff check scripts/                                       -> All checks passed!
```

## Behaviour

```
validate_security_prior_art.py --help
  -> usage: validate_security_prior_art.py [-h] {keyword-map,search} ...
     both subcommands listed

validate_security_prior_art.py keyword-map fixtures/threat-vocabulary-map.valid.yaml
  -> exit 0, no output

validate_security_prior_art.py search fixtures/search-output.valid.yaml \
    --keyword-map fixtures/threat-vocabulary-map.valid.yaml
  -> exit 0, no output
```

The `search` subcommand's `--keyword-map` argument is required: coverage completeness is the
cross product of the map's applicable groups and its active sources, so the check is not
computable without it and silently skipping it would be worse than refusing.

## Test suite

```
pytest -q  ->  45 passed
```

45 tests. Two assert the shipped fixtures validate clean; one asserts the CLI exits non-zero and
prints `FAIL` lines on a broken artifact; the remaining 42 are mutation tests, each breaking the
valid fixture in exactly one way and asserting the matching rule fires.

Rules proven to fire — keyword map: schema violation, duplicate group id, expansions over the
declared cap, expansions under the floor without a reason (and the same case *with* a reason
passing), a group type neither present nor declared absent, every relation kind identical, a
probe-discovered provenance with no probe record, a non-performed probe with no reason, a
missing release stamp, a missing sanitization record, a non-clean sanitization status with no
cause, a skipped source with no reason, an assumption with no basis, a malformed timestamp, and
an incomplete set of angle verdicts.

Rules proven to fire — search output: a missing cell for an applicable pair, a cell outside the
applicable set, a reached cell without counts, a non-reached cell without a cause, an
unreachable cell with no fallbacks tried, kept exceeding returned, kept below returned with no
drop record accounting for it, a cell with no broad pass, a query using none of its group's
vocabulary, a retrieval summary disagreeing with the cells, wrong status counts, a candidate
naming a cell that does not exist, a candidate naming a query its cell never ran, more
candidates than the cell kept, a non-registry candidate missing its url, a registry-class
candidate whose id is not a database identifier, an unpinned control requirement id, a signal
without an `as_of`, a dropped item not naming its cell, and a not-run artifact carrying
coverage.

Two tests assert the honest paths stay clean: a `not_run` artifact and a `vacated` artifact each
validate with no coverage at all. That direction matters as much as the failures — a validator
that faults a legitimately unrun angle for missing cells is precisely what pressures a producer
into fabricating them.

## Scope

Shape and completeness only. The validator never judges whether a finding matters, whether a
bail was honest, or whether a relevance line is persuasive — those are the reviewing skill's
numbered conditions. Two consequences: it needs no scope context, so it stays portable and
cannot false-fail an honest artifact; and the judgment half of the gate is proven separately, by
planting defects that pass this script and confirming the reviewer catches them.
