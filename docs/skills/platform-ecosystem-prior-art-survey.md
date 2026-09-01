# `platform-ecosystem-prior-art-survey`

Survey how existing platform ecosystems are actually architected — their boundary resources, their
declarative contracts, their commercial terms and their review gates — before building a plugin
system, an app marketplace or a connector surface of your own.

**Wave 1 only.** This version registers two kinds: the vocabulary map, and one search angle. The
extract and synthesis waves are not in it, and nothing here claims to produce an answer — it
produces a searched, recorded corpus that a later wave turns into one.

## The organising idea

The evidence for these decisions is unusually public. Platforms document their contribution
points, publish their revenue splits, and announce their breaking changes years ahead. It is also
almost never gathered before the decision is made, so teams rediscover by accident what four
vendors wrote down.

The problem is not access. It is that **a platform that publishes no term and a search that never
ran look identical downstream**, and this corpus makes that failure especially easy. Twenty-two
hosts across the registry, none gated, all open — and the highest channel-death rate of any type
in this family: four named channels moved or died in fourteen months, and one URL changed twice
inside a single eleven-day window. A survey that does not record its own retrieval cannot tell you
whether Shopify publishes no threshold or whether the page simply moved.

So the coverage grid is the product. Every query is recorded as it was run, every source the angle
declares owes a cell, a zero is written down rather than omitted, and a redirect to a live
replacement is `superseded` rather than `unreachable` — because the fetch succeeded, and
conflating the two hides that the corpus is moving under the survey.

## Two procedures

**Procedure 1 — the platform-and-mechanism vocabulary map.** Built before any searching. It mints
the platform slugs once, so that two angles cannot spell one platform two ways and defeat the
dedupe; it records the mechanism vocabulary with expansions, because vendors name one thing five
ways ("contribution point", "extension point", "manifest contribution"); and it gives every one of
the seven angles a verdict with a reason, including the ones that do not hold.

`angle_applicability.holds` is the angle's precondition evaluated over **the scope** — the project
the survey is for. Not "is this angle worth running", and emphatically not "does some platform in
the comparable set satisfy it". A scope whose `platform.type` falls outside an angle's set records
`holds: false` even when every comparable platform falls inside it, because the comparable set is
a survey target and the precondition is a statement about the project.

**Procedure 2 — one search angle.** Seven angles, four always-on:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 boundary-resource retrieval | always | 12 |
| a2 program policy and commercial terms | always | 12 |
| a3 declarative-contract enumeration | always | 14 |
| a4 change-process forensics | always | 12 |
| b1 third-party code execution and isolation | `platform.type in {app-store, dev-platform}` | 8 |
| b2 regulatory obligation and compliance delegation | `platform.type in {marketplace, app-store, payments-network}` OR `regulatory.applies` | 10 |
| b3 complementor-friction evidence | `platform.type in {marketplace, app-store, dev-platform}` | 10 |

A child runs ONE angle. It never runs the whole survey and never reads another angle's output.

## A count is meaningless without its frame

This is the rule the type exists around, and a3 is where it bites. One enumerable set in this
corpus yielded **six defensible counts in a single day**: a manifest schema gives 40 naive, 45
under one conditional branch, a different 45 under the other, and 47 as a union describing no valid
manifest — while the vendor's own page gives 46-under-a-stated-50 by extraction and 29 by counting
sub-page links. None is wrong. They answer different questions.

So every enumeration records four things — which artifact, which extraction method, which
conditional branch, and a reconciliation against a **second independent derivation**. A
`reconciled_by` that restates the same method is one derivation described twice, and proves
nothing: the second must have been able to disagree. Every coverage cell likewise carries a
`count_frame` saying what its `returned` counted and how, because two competent agents counting the
same page under different frames both report honestly and differ.

## Three dates, kept apart

- `retrieved_at` — when you fetched it.
- `as_of` — when the FACT became true. `null` when the content states none, and never defaulted to
  the fetch date, which would be a fabricated fact about the world.
- `source_claimed_modified_at` — the page's claim about itself, with its provenance recorded.

The distinction is not theoretical here. One page in this corpus is footer-dated years before the
format it documents existed. Three registry rows were themselves found filing a page's own revision
date in the `as_of` column — the exact conflation this rule exists to prevent, in the file that
teaches it — and were corrected.

## The absence of a number is a finding

Several platforms in this corpus publish no commission rate anywhere in their guidelines. "The
guidelines state no rate" is evidence about a decision; an empty field is a hole a later reader
takes for an oversight. The judgement is whether a rate WOULD arise: a marketplace that takes a cut
and declines to publish the number has decided something, and a free directory that charges nothing
has not.

## The deterministic gate, and what it does not judge

`scripts/validate_platform_ecosystem_prior_art.py` checks shape, enums, arithmetic and
reconciliation across 36 rules, and exits 0 clean, 1 the artifact has findings, 2 it could not be
used at all. The exit-2 class is load-bearing: a malformed registry, a missing dependency or an
unusable `--keyword-map` are all faults in the invocation or the package, and reporting them as
exit 1 sends an author off to edit an artifact that is fine.

It needs `pyyaml` and `jsonschema`:

```
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_platform_ecosystem_prior_art.py keyword-map <your map>
```

Everything the script cannot decide — whether a query could be re-run, whether a cause carries
observable evidence, whether a second derivation could have disagreed — belongs to the reviewing
twin, and is judged there against numbered conditions rather than restated here.

## Companion

[`reviewing-platform-ecosystem-prior-art-survey`](reviewing-platform-ecosystem-prior-art-survey.md)
— the judgement half of the same gate.
