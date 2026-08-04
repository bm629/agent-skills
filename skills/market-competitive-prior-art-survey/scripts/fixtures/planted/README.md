# Planted defects

Each fixture here **passes the deterministic gate** and is nonetheless wrong. That is the point:
a gate demonstrating only approve-on-good proves nothing about the judgment half. These exist to
prove the reviewing skill's conditions actually bite.

Every one was verified to exit 0 through the validator before being committed. If a change to
the validator ever makes one of these FAIL the gate, that is a signal to re-read — either the
defect became mechanically detectable (move the check into the gate and retire the fixture) or
the gate grew a false-positive.

| Fixture | Passes gate | Must be caught by | The defect |
| --- | --- | --- | --- |
| `search-output.failure-as-zero.yaml` | yes | **C12** | A rate-limited cell rewritten as `reached, returned: 0`. The arithmetic reconciles perfectly. The tail was never read, and the artifact claims the search ran and found nothing. |
| `search-output.hollow-admission.yaml` | yes | **C16** | `first-party-resolved` with `capability_stated` present but containing pure positioning ("Built for modern teams who move fast") — no capability, so the candidate rides on evidence that does not exist. |
| `market-vocabulary-map.category-echo.yaml` | yes | **C2** | The `job-to-be-done` group paraphrases the category. Correct type, enough expansions, varied relations — but the axis that exists to find substitutes returns only direct competitors. |

## Why these three

They cover the three ways this artifact fails while looking healthy:

1. **A failure laundered into a zero** — the defect the whole survey exists to prevent, and the
   only one that actively misleads rather than merely omitting.
2. **Evidence that is present but empty** — the shape check can see a field, never whether it
   says anything.
3. **A structurally complete map that cannot find what it was built to find** — the failure that
   produces a tidy, plausible, incomplete competitor set.

## Running the gate against them

```
validate_market_competitive_prior_art.py search planted/search-output.failure-as-zero.yaml \
  --keyword-map ../market-vocabulary-map.valid.yaml     # exit 0
validate_market_competitive_prior_art.py keyword-map planted/market-vocabulary-map.category-echo.yaml
                                                        # exit 0
```
