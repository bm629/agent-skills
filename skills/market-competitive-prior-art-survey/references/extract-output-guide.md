# Extract output guide (frontmatter fields)

`schemas/extract-output.schema.json` is authoritative; this guide explains it. Where the two
disagree, the schema wins and this file is the bug.

## Always present

| Field | Meaning |
|---|---|
| `schema_version` | `1`. |
| `meta.item_id` | The frozen queue row's canonical id this record answers, verbatim. The filename is derived from it, not equal to it. |
| `meta.as_of` | When the sources were read. |
| `meta.revision` | 1 on first write; incremented when a review round rewrites the record. |
| `outcome` | `extracted` or `skipped`. |

`extracted` requires `product` and forbids `skipped`; `skipped` requires `skipped` and forbids
`product`. The schema enforces both directions.

## `skipped` — the bail

| Field | Meaning |
|---|---|
| `skipped.cause` | `serves-no-overlapping-capability` (the relevance bail — requires confidence), `not-a-product`, `site-unreachable` (a retrieval failure, never a finding of non-existence), `forbidden-by-terms` (a decision, not a failure). |
| `skipped.detail` | Why, in your own terms, ≥10 characters. A bare cause code is a verdict without evidence. |

## `product` — the extracted record

| Field | Meaning |
|---|---|
| `id` / `aliases` | Canonical product id, plus every other name it is known by. Aliases are what stop the same product entering the register twice. |
| `name` / `url` | Human name and the official URL. |
| `tier` | `direct`, `adjacent`, `substitute`, `historical`. Evidence, never a computed score. |
| `overlapping_capabilities` | **Required non-empty on a `direct` row.** Head-to-head is a claim about which capabilities are shared; a direct tier naming none is an assertion. |
| `category` | The product category in the market's own vocabulary. |
| `positioning` | How the vendor positions itself, in its terms. Their claim is evidence of the claim, not of its truth. |
| `source_authority` | `first-party` > `authoritative-registry` > `review-aggregator` > `secondary-commentary`. Ranking and dedupe input only, never a cut. On conflict first-party wins for commercial facts. |
| `lifecycle.status` | `live`, `discontinued`, `acquired`, `unknown`. A `discontinued` row must carry `dated` — that is what makes it a provable fact. |
| `lifecycle.dated` / `evidence_url` | When it ended, and where that is stated. |
| `pricing.model` / `tiers` / `as_of` | The pricing shape and the date it was true. Required together: pricing without a date is a claim about now that will be read months from now. |
| `reception.rating` / `denominator` / `source` / `as_of` | A rating is meaningless without its denominator, so the denominator and source are required and the rating is not. |
| `adoption.signal` / `value` / `as_of` | What signal, what it read, when. |
| `corporate.owner` / `funding_status` / `as_of` | Ownership and funding decay fast; the date is required. |
| `capability_tags` | The scope capabilities this product overlaps. These are what downstream document authoring consumes from the register. |

## `notes`

Leads and observations that are not this product. A neighbouring competitor you noticed goes here,
never as a second record — the unit is one product.

**Never a dated fact.** A review count, a certification, a user total or a funding round is a
point-in-time claim and belongs in the structured field that requires its `as_of`. Parked in
`notes` it carries no date the schema can enforce, and the reviewer will send it back under the
point-in-time condition.
