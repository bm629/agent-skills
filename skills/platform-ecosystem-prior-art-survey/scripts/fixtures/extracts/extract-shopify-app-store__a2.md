---
# CLEAN calibration fixture — one extracted record, wave 2.
# Frontmatter and body in ONE file: the machine block and the human analysis are never split.
schema_version: 1
meta:
  item_id: shopify-app-store__a2
  as_of: '2026-08-21'
  revision: 1
outcome: extracted
finding:
  platform_id: shopify-app-store
  platform_name: Shopify App Store
  platform_type: marketplace
  mechanism: a2
  corpus:
    name: Shopify developer documentation
    version: '2026-01-01'
    url: https://shopify.dev/docs/apps/launch/distribution/revenue-share
    retrieved_at: '2026-08-21'
    robots_checked: true
  authority: first-party-normative
  volatility: contractual
  statement: The platform takes no revenue share below a stated annual threshold and a fixed
    percentage above it, assessed per developer account rather than per app.
  evidence_quote: Apps earning under the threshold in a calendar year pay 0% revenue share.
  enumeration_count: null
  announced_on: null
  enforced_on: null
  applicability:
    applies: true
    basis: business.platform.type = marketplace
  reversibility: costly
  vocabulary_refs: []
notes:
  - The billing migration announced separately is a4's finding, not this record's.
---

# shopify-app-store__a2 — commercial terms

## What the platform prescribes

A two-tier revenue share assessed on the developer account's annual earnings, with a zero-rate
band below a stated threshold.

## Evidence

The revenue-share page states the zero-rate band verbatim, and carries an effective date in its own
front matter. That date is `corpus.version`; `retrieved_at` is when this record read it.

## Why it is costly to reverse

Pricing built against a zero-rate band is priced for that band. Moving off the platform after
launch means re-pricing to a different rail, which is a commercial decision rather than a code
change — costly, not one-way.
