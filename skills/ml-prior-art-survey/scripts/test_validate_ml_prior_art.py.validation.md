# Validating the test suite

```
uv run --group dev pytest scripts/ -q
```

## What the suite is built to prevent

**Every comparison ships its mirror (#34).** A one-directional check on a two-directional property
reads as covered and is not. Each `*_fails` test here has a `*_passes` sibling asserting the rule
does NOT fire on the legitimate case — because a rule that fires on everything is as useless as
one that fires on nothing, and only the second direction catches it.

**No unreachable code.** `TestNoUnreachableCode` walks the AST and fails on any statement
following a `return` or `raise` in the same block. This is not hypothetical: the entire
candidate/kept/bound half of `validate_search` was once appended after a `return out` and never
ran. The clean fixture passed either way.

**Every rule has a negative test.** The same class asserts that every `FAIL <rule>` the module can
emit appears in a test as `"<rule>" in _rules(...)`. On its first run it found three rules with no
test at all. The exemption list — rules tested through a subprocess instead — is itself asserted,
so it cannot become a hiding place.

**The idiom is uniform on purpose.** A test that binds the finding list to a local variable first
is invisible to the coverage regex, so the guard would pass while the rule went untested. Write
`assert "<rule>" in _rules(V.validate_*(...))`.

**Mutations resync what they move.** `_resync()` recomputes `kept` and `status_counts`, because a
test that mutates a row and leaves them stale fires the reconciliation rule instead of the one it
names — and then passes for the wrong reason.
