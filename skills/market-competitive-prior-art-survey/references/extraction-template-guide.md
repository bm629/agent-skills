# Extraction template guide (Procedure 3 output)

One extraction is a Markdown file per **competing product** — a **YAML frontmatter** machine block
above a **3-section markdown body**. The frontmatter is defined and validated by
`schemas/extract-output.schema.json` (see `extract-output-guide.md`); this guide covers the body.

The unit is ONE PRODUCT. Pricing, features, reception, adoption, corporate status and lifecycle are
FIELDS on that record — not records of their own. One record per *claim* would force every parallel
child to invent the comparison taxonomy while reading; one record per *source page* would make the
same product on three aggregators into three records synthesis must re-merge.

**The vendor's own site is read HERE.** First-party reading is extract work, not a search angle: a
pricing page is definitionally current where an aggregator lags by months, and the reading is per
product rather than per corpus.

The file is written as `record_filename(item_id) + .md`. Deriving the name any other way puts the
record where nothing looks for it — valid, unreported, and treated as never written. The QA phase
checks this; the validator deliberately does not.

## The 3 body sections are FIXED

The validator's `EXTRACT_HEADINGS` constant checks each `## <heading>` is present, so this guide
and the validator share one list and cannot drift.

1. **## Positioning** — how the vendor positions the product, in the vendor's own terms. Their
   claim is evidence of the claim, never evidence that it is true.
2. **## Evidence** — the passage the positioning and the commercial fields rest on, named to its
   source and date. A summary of a landing page is not evidence.
3. **## Overlap** — which of the scope's capabilities this product serves, and how. On a `direct`
   row this is the argument for the tier, and the schema requires the capabilities be named.

## Tiers are evidence, not arithmetic

`direct`, `adjacent`, `substitute`, `historical`. Never a computed competitiveness score:
multiplying model guesses yields a precise-looking number with no traceable basis, uncheckable by
validator or reviewer alike. A `direct` claim must name the capabilities it shares.

## Dates are not decoration

Every commercial field carries `as_of`. Pricing, funding and ownership decay fastest, and a
landscape document is read months after it is written. A rating carries its **denominator** — 4.8
from six reviews and 4.8 from six thousand are different facts, and only one of them is a signal.

## Dead products are in scope

A discontinued competitor is first-class evidence and the highest-value input to a risk section;
no competitor-comparison source carries it. Record `lifecycle.status: discontinued` with the date
and the evidence URL. A dated discontinuation is a provable fact, where "nobody has built this" is
usually an unprovable absence.

## Skipped records still ship

The relevance bail is the only cut and is taken at the FRONT, before the deep read. Write the
record with `outcome: skipped`, a typed `cause`, and a `detail` that says why in your own terms.
`site-unreachable` is a retrieval failure and never a finding that the product does not exist;
`forbidden-by-terms` is a decision, not a failure.
