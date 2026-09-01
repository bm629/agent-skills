# Validation — `test_validate_platform_ecosystem_prior_art.py`

**Run.** `pytest -q` from this directory, or the repo-root suite.

**Discipline.** Every rule was written RED-FIRST: its test failed before its implementation
existed. Every comparison ships its MIRROR — a one-directional check on a two-directional property
reads as covered and is not.

**The mirrors that matter most.** A `reached` cell with no count fails, but a `reached` cell
recording ZERO passes: a validator rejecting a recorded zero would push producers toward omitting
the cell, which is the failure the zero-hit rule exists to prevent. And `record_filename` ships a
CROSS-BRANCH collision test, because a within-branch round-trip passes while `f(f(x)) == f(x)` is
still constructible.

**Subcommand reachability.** The command list is DERIVED from the parser, not hand-listed, so a
subcommand added later is covered automatically. The dispatch is asserted in both directions —
`search` routes cleanly AND a search artifact is rejected by the map command — which is what proves
the branches are different code paths rather than one aliased to the other.
