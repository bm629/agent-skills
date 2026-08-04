# Sources

Research provenance for this skill's method and quality bar. Distinct from
`source-registry.yaml`, which is the runtime list of corpora a *survey* queries and is a
validator input.

## Corpora, verified at the primary source

| Source | Verified | Used for |
| --- | --- | --- |
| W3C ARIA Authoring Practices Guide | 2026-08-04, direct fetch | The normative interaction contracts. 31 named patterns; free, no login; maintained in a version-controlled repository |
| W3C WCAG 2.2 | 2026-08-04 | 87 success criteria across levels A/AA/AAA — the numeric, testable thresholds a downstream reviewing skill grades against |
| deceptive.design | 2026-08-04, direct fetch | The negative catalogue. 18 named types, plus browsable hall-of-shame, laws and enforcement collections; no advertised API |
| Published design systems (Material, Carbon, Polaris, Primer, Fluent, GOV.UK) | 2026-08-04 | What governed systems prescribe, with rationale. Carbon and GOV.UK are openly licensed and published in git, which is why they are the fallbacks |
| Platform human-interface guidelines (Apple, Android, Windows) | 2026-08-04 | Platform-mandated convention a cross-platform system abstracts away |

## The downstream contract

The consuming design-system authoring skill requires design tokens in **W3C DTCG format at any
size**, consumed as **DTCG-shaped tables in textual markdown** — three tiers
(primitive → semantic → component), named by intent — explicitly *not* a rendered design file
and *not* a compiled token package. It also requires accessibility stated numerically to
**WCAG 2.2 AA unconditionally**, which is why an absent conformance level defaults to AA here
rather than skipping the accessibility angle.

Verified by reading that skill directly rather than assuming; the DTCG format's first stable
release (2025.10) is corroborated in its own reference material.

## Excluded, and why

The screenshot galleries — Mobbin, Pttrns, Dribbble, Pageflows, Lapa Ninja — are excluded on two
independently sufficient grounds. Their terms forbid automated extraction, and a screenshot is
not extractable into the textual artifact this survey produces. Recording the modality reason
matters: an access change would not make them usable.

## Method

The vocabulary map follows PRISMA-S's reporting discipline — per-source exact query, timestamp,
result count, justified limits — transposed from literature search to corpus traversal, and SKOS
for typed expansions. The provable-absence discipline (a recorded zero is a receipt; an
unreachable source is a typed failure; a forbidden source is a decision) is shared across this
family of surveys and is what the coverage grid exists to preserve.
