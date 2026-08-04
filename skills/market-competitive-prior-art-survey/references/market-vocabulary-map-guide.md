# The market vocabulary map, explained

The map is a SEARCH PROTOCOL, not a glossary. Everything in it exists so a later reader can
re-run what you ran and tell the difference between "no competitor exists" and "we searched
badly". It is produced once, in wave 0, and every search angle queries from it rather than from
its own recall.

Schema: `schemas/market-vocabulary-map.schema.json`. The deterministic gate checks shape only —
`validate_market_competitive_prior_art.py keyword-map <file>`.

## The five group types

| Type | What it holds | Which angles query it |
| --- | --- | --- |
| `category` | The market as directories and analysts name it | a1, a2, b1, b2, b3, b5, b6 |
| `capability` | The capability-map nouns — what the product DOES | a1, a2 |
| `job-to-be-done` | How a user phrases the need, in outcome terms | a2, b6 |
| `audience-segment` | Who it is for | a2 |
| `seed-product` | Known products the graph walk starts from | a1, b1, b2, b3, b4, b5, b6 |

Every type that carries no group must be listed in `scope_guard.absent_types` with a reason. A
type that is neither present nor declared absent is a silent omission, and it silently empties
every angle that depends on it — the gate rejects that.

`seed-product` deserves particular care: it is the single highest-leverage group in the map,
because a1's graph walk is densest around a named incumbent. A map with no seed product forces
a1 to work from category terms alone and materially weakens the strongest angle. If the scope
genuinely names no incumbent, say so in `absent_types` rather than leaving it empty.

## Expansions

Each group carries a canonical term plus expansions, each with a `relation` (SKOS-style:
`broader`, `narrower`, `related`, `alt-label`) and a `provenance` (`extracted` from a real
source, `model-knowledge` from your own recall, `probe-discovered` from a live probe).

Provenance is not decoration. `extracted` means a real corpus used this term; `model-knowledge`
means you supplied it and it may be a term nobody uses. A reviewer weighs them differently, and
a map that is entirely `model-knowledge` has not been grounded in anything.

The floor is three expansions per group. Below that, record `short_reason` — never pad. A
padded group manufactures queries that return noise, and the noise costs a full deep read
per false candidate. Product-name groups legitimately sit at the floor: a product name has no
sister terms, only spelling and vendor variants.

If no group shows more than one relation kind, the gate fails the map. A map of nothing but
`alt-label` expansions is a spelling list, not an expansion.

## Negative terms — load-bearing for THIS type

`category` and `seed-product` groups MUST declare `negative_terms`. The gate enforces it.

This rule does not exist in the security survey, and the reason is worth understanding rather
than copying. A weakness identifier is unambiguous; a product name is not. Products are called
Notion, Linear, Arc, Sketch, Slack, Ghost, Craft, Bear. Each matches an enormous amount of
unrelated text, and a search built from such a group cannot be made precise afterwards — the
noise is already in the result set.

Negative terms are what make the difference between an angle that returns competitors and one
that returns a category's worth of homonyms. Write them from the collisions you can actually
foresee: "notion of", "the notion that", "linear algebra", "arc welding".

## Angle applicability

One verdict per angle in the registry, each with its precondition, a boolean `holds`, and a
reason. An angle judged inapplicable must leave a trace — otherwise it is indistinguishable
from an angle nobody thought about.

The gate checks BOTH directions, which is the mirror the security survey originally lacked:

- Every registry angle needs a verdict (a missing one is an unexamined angle).
- A verdict naming an angle that is not in the registry is rejected.
- **An always-on angle (a1, a2) cannot be recorded as `holds: false`.** No map may switch one
  off. That is how a survey silently does nothing, and this type fires on every project.

Write the precondition VERBATIM from the registry, and the reason against the capability map's
actual values — "audience is b2b and model is saas, so both limbs hold", not "seems relevant".

## Sources and stamps

Every source is either `active` (you read it) or `skipped` (you did not), and both carry a
cause. Each active source records `release` (or the literal `rolling`), `as_of`, an `access`
status, and a `sanitization` result.

`access` is the field that makes the next channel death visible instead of silent. The values
distinguish cases that look identical downstream and are not: `open`, `crawl-delayed`,
`allowlist-gated`, `login-required`, `forbidden-by-terms`, `blocked`.

`forbidden-by-terms` is a DELIBERATE non-fetch — the source's terms prohibit automated access,
so you chose not to read it. `blocked` is a fetch that failed. A source marked
`forbidden-by-terms` may never appear in `active`; the gate rejects that, because recording a
source you deliberately did not read as one you read is a false receipt.

## Assumptions

Every value the absent-input policy forced is recorded here with the signal it was inferred
from — never folded into the scope as though the caller had stated it. See
`absent-input-policy.md`.

## Worked example (abridged)

```yaml
schema_version: 1
meta:
  as_of: "2026-08-04T09:00:00Z"
  revision: 1
groups:
  - id: team-collaboration
    type: category
    canonical: team collaboration software
    expansion_cap: 6
    negative_terms: ["team building", "collaborative filtering"]
    expansions:
      - {term: workplace collaboration platform, provenance: extracted, relation: alt-label}
      - {term: digital workspace, provenance: model-knowledge, relation: broader}
      - {term: async standup tool, provenance: model-knowledge, relation: narrower}
angle_applicability:
  - angle_id: a1
    precondition: always applicable
    holds: true
    reason: Alternatives directories index this category densely.
  - angle_id: b2
    precondition: >
      archetype.primary in {mobile-app, game, browser-extension} OR archetype.secondary contains one
    holds: false
    reason: archetype.primary is web-app and no secondary names a store-distributed form.
sources:
  active:
    - id: openalternative
      release: rolling
      as_of: "2026-08-04T09:00:00Z"
      access: open
      sanitization: {status: sanitized}
  skipped:
    - id: g2
      cause: Excluded by its Terms of Use, which forbid automated extraction of any content.
      access: forbidden-by-terms
```

The full fixture is `scripts/fixtures/market-vocabulary-map.valid.yaml`.
