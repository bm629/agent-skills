# Validating `validate_regulatory_prior_art.py`

Run from this skill's directory:

```
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_regulatory_prior_art.py keyword-map \
    scripts/fixtures/regulatory-scope-map.valid.yaml
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_regulatory_prior_art.py search \
    scripts/fixtures/search-output.valid.yaml \
    --keyword-map scripts/fixtures/regulatory-scope-map.valid.yaml
```

Both must exit 0 and print nothing.

## The exit contract, and why 2 is not 1

- **0** clean.
- **1** the ARTIFACT has findings. The author has something to fix.
- **2** it could not be used at all — a fault in the package, the registry, the invocation or the
  input file. **Never the author's to fix by editing the artifact.**

Reporting a class-2 fault as a 1 sends someone off to edit a file that is correct.

`probe_method` is a REGISTRY field, so a wrong-shaped one is exit 2 rather than sitting with the
artifact rules at exit 1. Grouping it with them would have left its exit code undecided, which is
the ambiguity the registry-integrity pass exists to remove.

## The dependency guard must be NON-RAISING

The shared root guard at `agent-skills/tests/test_registry_trigger_integrity.py` `exec_module`s
this file to read `REQUIRED_CAPABILITY_FIELDS`. A raising import turns that test into an ERROR
rather than a run — and an ERROR reads like a broken test rather than a missing dependency. The
guard binds a sentinel and leaves the names bound to `None`; `main()` reports `dependency-missing`
with the working invocation and no traceback.

## What this gate does NOT check

Whether an instrument actually binds this scope. Whether a quote supports the claim resting on it.
Whether an authority ranking is defensible. Whether a sector verdict of `undetermined` should have
been settled.

Those are the reviewing twin's, and each of its conditions names the rule that owns the shape half.
**A condition believed to be enforced is worse than one known not to be**, which is why the split is
written down rather than implied.

One limitation belongs here rather than in a docstring nobody reads: whether a `holds: false` on a
CONDITIONAL angle is right for a given scope cannot be machine-checked. The map records the scope as
prose plus `assumptions`, not as the structured fields the registry's predicates are written
against. The deterministic half ships — an always-on angle can never be false, verdicts are
complete and unique, an unknown angle is refused — and the judgement half is a reviewer condition.

## Re-verifying the registry

The rows carry dates and a probe method because they go stale. Twelve days cost this type one
channel death, one silent-redirect trap and three stale notes. Re-probe by **GET**, with the user
agent and headers each row records, before trusting a note.


## Re-verifying the fixture quotes

`agent-skills/tests/verify_fixture_quotes.py`, author-time and not in CI, because it fetches.

For every fixture candidate carrying a prose quote it fetches the instrument the record's OWN
`provenance` cites — never its `locator`, because a record whose locator and citation disagree is
precisely what it looks for — and asserts the quote appears verbatim.

It exists because a blind reviewer found a fabricated citation in the CLEAN calibration fixture
that four mechanical guards missed and the author had reported as verified. The author had fetched
the neighbouring part, found the sentence, and attached it to a record citing a different part.
**Verifying that a sentence exists somewhere is not verifying a citation.**

Run it whenever a fixture quote changes. A zero-check run FAILS rather than passing: a checker that
reaches no source otherwise reports a clean sweep, which is the same failure one level up.
