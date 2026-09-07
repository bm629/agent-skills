# API-openai-gpt-4o-mini

## What it is

A hosted general-purpose model offered only as an API, with no downloadable weights.

## Fit to our capabilities

Covers `text-classification` with no training data of our own, which is what makes it the first
rung worth testing.

## Evidence

Vendor documentation only. No third-party measurement on anything resembling our task surfaced
across the angles that ran.

## Licence and use restrictions

The hosted terms permit training on submitted content unless a separate agreement is signed. That
is a data-handling restriction rather than a licence clause, and it is what disqualifies this rung.

## Cost and serving

0.15 USD per 1M input tokens and 0.60 per 1M output, as of 2026-08-22. Serving is the vendor's.

## Risks and limitations

No weights, so no offline path and no way to pin a version we control. Fairness and energy
reporting are both absent from the documentation.

## Verdict rationale

Scored 6: available today and cheap at our volume, but vendor-measured only, with a data-handling
term our processing agreement forbids.
