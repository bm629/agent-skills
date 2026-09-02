# Validating `test_validate_regulatory_prior_art.py`

```
uv run --no-project --with pyyaml --with jsonschema --with pytest \
  python -m pytest scripts/test_validate_regulatory_prior_art.py -q
```

## Every rule gets a negative AND a mirror

A negative test proves a rule CAN fire. It does not prove the rule is not firing on everything —
and a membership check that fires on everything passes its negative test and fails nothing else.
The mirror is mutated **toward the boundary**: expansions exactly AT the cap, candidates exactly AT
the ceiling, a reached cell that returned zero, a conditional angle that legitimately does not hold.

Asserting the unmutated fixture is not a mirror. It passes with the rule deleted.

`TestTheSuiteGuardsItself` sweeps this file and asserts the property rather than trusting it. Two
forms of mirror are credited: an explicit `not in _rules`, and a `== []` assertion on a clean
artifact — which is a real mirror for every rule at once, because a rule firing on correct input
would break it.

**What that does not prove**, stated so it is not rediscovered: for a rule whose triggering INPUT a
clean artifact cannot exhibit — `not-a-mapping` needs a non-mapping — the broad credit is true and
vacuous. The nineteen rules where "fires on everything" is a live risk carry the narrow form, and a
separate test asserts exactly that list.

## Guards that read this file strip its docstrings first

A sweep that scans its own prose finds its own examples. This one matched the sentence describing
its pattern and reported a phantom rule; the test proving the stripper worked then spelled its
probe as a literal and asserted something that could never hold. Both are derived now, and
`_TESTS` removes docstrings via AST — a guard reads CODE, and prose about a guard is not an
instance of what it guards.

## `_resync` exists so a mutation tests one thing

Moving one field changes `kept`, `status_counts` and `degraded_sources` downstream. Without
recomputing them, a test that moves one thing trips three unrelated rules and its assertion passes
for the wrong reason. Where the omission IS the thing under test, the test re-empties the field
after resyncing, on purpose and with a comment.

## The AST guard

`test_no_unreachable_code_in_the_validator` walks the validator for statements after an
unconditional exit. This shipped in a sibling: an entire half of a validator sat below an early
return and the suite was green, because every test that would have caught it asserted a clean
artifact stays clean.
