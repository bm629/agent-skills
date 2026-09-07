# HF-facebook/bart-large-mnli

## What it is

A BART-large checkpoint fine-tuned on MultiNLI, used for zero-shot classification by posing each
candidate label as an entailment hypothesis.

## Fit to our capabilities

Covers `text-classification` without task-specific training data, which is the only rung available
before we have labelled examples of our own.

## Evidence

The Hub card states the MNLI fine-tune and the zero-shot recipe. The 89.9 matched-accuracy figure
is a third-party `lm-eval` 0.4.3 run recorded 2026-06-01, not a vendor self-report.

## Licence and use restrictions

MIT. No field-of-use restriction, no non-commercial clause, no downstream-share obligation.

## Cost and serving

No hosted endpoint is offered by the publisher; self-serving needs ~1.6 GB and runs on CPU. No
price applies, so the `cost` block is null rather than zero.

## Risks and limitations

English only, and the card reports no fairness assessment and no energy figure. Entailment-based
zero-shot degrades where labels are not natural-language phrases.

## Verdict rationale

Scored 7: licence clear, third-party measured, actively maintained; loses points for absent
fairness and energy reporting and for having no vendor-documented serving figures.
