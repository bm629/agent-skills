# `test_validate_integrations_prior_art.py` — how this suite is kept honest

## Run it

```
uv run --group dev pytest skills/integrations-prior-art-survey/scripts -q
```

## Every rule fires AND is silent

A rule tested only on its mutation is indistinguishable from a rule that always fires. Every rule
has a negative (it fires on its own mutation) and the clean fixtures assert the whole set is silent.

## `NEED` and `NOT_NEEDED` PARTITION the rule set

`NEED` is every rule with a VALUE-LEVEL boundary the clean fixture's values sit AWAY from; each
carries an explicit NARROW mirror, because a clean fixture far from a boundary cannot exercise it.
`NOT_NEEDED` is the complement, each with a one-line reason.

The two are asserted EQUAL to the rule ids DERIVED from the validator source. There is no fourth
case, so a rule added later cannot inherit a side — someone has to put it in one and say why.

## The sweep is derived, not transcribed

`SHIPPED_RULES` is extracted from the validator's own `_fail(` call sites. A hand-maintained second
list would just be a third copy that drifts.

Rules emitted by the SHARED trigger engine — `angle-always-fires`, `registry-out-of-scope` — are
excluded by name, because asserting them reads identically to a negative for a rule of our own.

## No rule sits below an early return

Walked as an AST rather than grepped: a `_fail` following an unconditional `return` in the same
block is a rule that never fires.
