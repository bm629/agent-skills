# `reviewing-integrations-prior-art-survey`

The second half of a two-part gate. The deterministic validator has already run; this skill judges
what a gate that never fetches cannot.

## What it owns

**19 conditions**, each naming the rule that owns the other half where one exists — so a finding
raised against a rule the gate already enforces is noise that costs the author a cycle.

The ones with no rule behind them at all are the reason this half exists:

- **the claim-versus-quote boundary** — `evidence_quote` is verbatim from the `locator` and `claim`
  is what the survey asserts from it. A rule joining the two would refuse exactly the honest case.
- **the two-conjunct admission test** — a candidate is admitted only where it has a first-party home
  AND a corpus row was retrieved. Neither conjunct is decidable without a fetch. And the carve-out
  that matters: admission does NOT test whether a public API exists, because a domain-expected
  service with no public API is a RISK a later wave reports, not an absence.
- **the truth of `enumerated`** — the gate checks the shape; only a reviewer can see that a catalog
  recorded as completely walked was actually paged through and abandoned.
- **the four-band authority record** — `source_authority` is the band of the source the LOCATOR
  points at, not of the cell that found the row, so a candidate discovered in a connector catalog
  and quoted from the vendor's own page correctly carries `first-party`.
- **`present_on[]`'s completeness** — a catalog the producer walked, that carried the service, and
  that is missing from the list, is the one wave-1 observation wave 2 cannot recover.

## The proportionality condition

C18 exists because the failure it prevents is invisible in a single review. Three candidates from a
narrow scope is a result. An enumerated zero is evidence. A `vacated` angle with observable causes
is an honest record of a bad run.

A reviewer who treats a small number as a defect teaches the next producer to pad — and padding is
the failure this survey exists to prevent.

## Its evidence

EIGHT sources, five of them producer-package paths this package does not ship: the schemas, the
source registry, the angle references, the absent-input policy and the category vocabulary.

**Two are easy to skip, and two conditions cannot be discharged without them**: the absent-input
policy, which C9 needs for the catalog auth modes, and the category vocabulary, which C13 judges a
`category` against. The artifact looks judgeable without either, which is exactly why they get
skipped.

The SCOPE and CLASSIFICATION the producer was handed is the third that matters and the one with no
substitute: `meta.classification` is a transcription, every angle verdict is judged against it, and
judged only against itself a fabricated value reads exactly like a real one. C19 asks that question
and nothing else does.

## Install

```
npx skills add bm629/agent-skills@reviewing-integrations-prior-art-survey
```
