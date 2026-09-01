# Validation — `validate_platform_ecosystem_prior_art.py`

**Scope.** Wave 1: the `keyword-map` and `search` subcommands.

**Exit contract.** `0` clean · `1` the artifact under test has findings · `2` it could not be used
at all — unreadable, unparseable, or a PACKAGE fault such as a malformed registry. The `2` class
exists so a package defect never sends a caller off to edit an artifact that is fine.

**What it checks.** Shape and completeness only: schema conformance, enums, ranges, required
fields, timestamp format, applicability completeness in both directions, the zero-hit coverage
cell, `kept` against `returned`, summary reconciliation, bound-with-ordering, slug provenance,
source resolution, and the a3 enumeration locator.

**What it does NOT check.** Whether a platform is comparable, whether a mechanism claim is
persuasive, whether an exclusion was fair. Those are the reviewing skill's numbered conditions. A
fuzzy heuristic inside a deterministic gate produces false failures and duplicates the reviewer.

**Registry self-check.** `anchor_failures` runs inside `main()` BEFORE either subcommand reads its
input, on every path — not on one branch only.

**Run it.**

```
python validate_platform_ecosystem_prior_art.py keyword-map <file>
python validate_platform_ecosystem_prior_art.py search <file> --keyword-map <file>
```
