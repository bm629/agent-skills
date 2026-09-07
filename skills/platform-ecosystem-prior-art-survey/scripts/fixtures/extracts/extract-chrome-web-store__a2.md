---
# CLEAN calibration fixture — the record a DISSENT names.
# A dissent must name the platform that dissents, so the record it rests on has to exist.
schema_version: 1
meta:
  item_id: chrome-web-store__a2
  as_of: '2026-08-21'
  revision: 1
outcome: extracted
finding:
  platform_id: chrome-web-store
  platform_name: Chrome Web Store
  platform_type: app-store
  mechanism: a2
  corpus:
    name: Chrome Web Store developer documentation
    version: retrieved-only
    url: https://developer.chrome.com/docs/webstore/
    retrieved_at: '2026-08-21'
    robots_checked: true
  authority: first-party-normative
  volatility: contractual
  statement: The store operates no first-party payments rail, so a developer bills through a
    third party and the store takes no share of it.
  evidence_quote: Chrome Web Store payments are no longer supported.
  enumeration_count: null
  announced_on: null
  enforced_on: null
  applicability:
    applies: true
    basis: business.platform.type = app-store
  reversibility: one-way
  vocabulary_refs: []
notes: []
---

# chrome-web-store__a2 — commercial terms

## What the platform prescribes

No first-party payments rail at all. Billing is the developer's own arrangement with a third party.

## Evidence

The store's documentation states the removal directly. The page carries no reliable date of its
own, so `corpus.version` is `retrieved-only` rather than a date this record would be inventing.

## Why it is one-way

A product that bills through its own rail has built a billing relationship with its users. There
is no path back to a store rail that does not exist.
