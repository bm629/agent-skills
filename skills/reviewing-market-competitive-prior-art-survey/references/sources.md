# Sources

Research provenance for this skill's method and quality bar. Distinct from
`source-registry.yaml`, which is the runtime list of sources a *survey* queries and is a
validator input.

## Method and quality bar

| Source | Used for |
| --- | --- |
| PRISMA-S extension (Rethlefsen et al., *Systematic Reviews*, 2021) — 16 reporting items | Search reproducibility: queries copied as run, per-source result counts, date of each search, declared limits |
| PRISMA 2020 + PRISMA-S flow-diagram guidance | Per-source counts rather than aggregates |
| "Systematic review search strategies are poorly described and not reproducible" (medRxiv, 2023) | Why reproducibility is enforced mechanically rather than requested |
| Porter — five forces (substitutes, new entrants) | Why substitutes belong in a competitor set |
| Levitt — "Marketing Myopia" | The category-definition blind spot |
| Competitive-intelligence practitioner literature on competitor typology | Direct / adjacent / substitute / replacement tiers, and that indirect competitors are the most commonly overlooked |
| Reporting on B2B software review fraud (Forbes, 2020) and platform research on incentivized reviews and cherry-picking | Review-corpus reliability; why a rating needs its denominator |
| Startup post-mortem corpora and survivorship-bias literature | Why dead competitors carry analytical value that comparison sites systematically drop |
| SaaS pricing-change tracking (2025–2026) | Decay rate of pricing claims — ~1 in 3 competitors change pricing in a given week |
| CI practitioner reporting on intelligence half-life | A competitive study decays within roughly 90–120 days |

## Contested

The claim that incentivized reviews *reduce* participation bias in B2B comes from a review
platform writing about review platforms, and runs against the consumer-review literature. It is
recorded as contested; nothing in this skill's bar depends on which way it resolves.

## Access verification

Every access status in `source-registry.yaml` was verified by direct fetch of the primary
source on the date recorded there — not from a summary. Two sources in an earlier draft were
described from a second-hand digest and both were wrong: one was reported as robots-blocked when
its robots file permits crawlers and its *terms* are what forbid extraction, and another was
reported as blanket-blocked when the operative rule is a path-level disallow. Re-verify at the
primary source before changing any access claim.
