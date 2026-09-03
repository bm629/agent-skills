# `validate_integrations_prior_art.py` — what it checks, and what it deliberately does not

## Run it

```
uv run --no-project --with pyyaml --with jsonschema python validate_integrations_prior_art.py \
  keyword-map <your map>
uv run --no-project --with pyyaml --with jsonschema python validate_integrations_prior_art.py \
  search <your file> --keyword-map <the map>
```

## Exit codes, and the distinction is load-bearing

| code | meaning |
| --- | --- |
| `0` | clean |
| `1` | the ARTIFACT has findings — the author has something to fix. `schema` is here |
| `2` | it could not be used at all — the package, the registry, the invocation or the input file |

Reporting a `2` as a `1` sends someone off to edit a file that is fine. The registry-integrity rules are
`2` on the class definition: they read the REGISTRY, which the artifact's author cannot edit. That
set is DERIVED from the emitting function's AST and asserted equal to the constant, so it cannot be
stated wrongly here -- an earlier version of this sentence said "eight" when the set had nine.

## What it does NOT check, and who does

The gate checks SHAPE. It never fetches, so it cannot know:

- whether a `locator` host really is the vendor's own — `locator-resolvable` checks the syntax only;
- whether an `evidence_quote` supports its `claim`;
- whether a `source_authority` band is defensible for the page the locator points at;
- whether every capability in the capability map is covered — nothing here can see that file.

Each is a condition in the reviewing twin, and each names the rule that owns the other half.

## The schemas run FIRST and return EARLY

A sibling loaded its schemas nowhere: deleting a required field produced ZERO findings while
silently disabling eight rules that read it. Running them first and returning early is what stops
every rule below comparing against a shape that is not there.
