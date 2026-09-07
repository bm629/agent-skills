# Writing the synthesis report

`integration-register.yaml` is the machine half and the build-handoff index; `report.md` is what a
human reads beside it. The survey ships both, and no third file — a feature matrix or a merged
inventory regenerated from the same corpus drifts from the register the moment either is edited.

## The eight sections are FIXED, in this order

The coordinator's synthesis brief demands exactly these, so guide and brief cannot drift.

1. **Survey scope.** What was surveyed and how: the domain, the angles that ran, the sources
   reached, and the date. Name `a3_directories_reached` here — it is a denominator two lenses
   divide by, and a reader who does not see it cannot weigh anything below.
2. **Coverage and absence** *(second on purpose — it is what a reader checks before trusting the
   rest)*. Lens 8: per angle, ran / vacated / not run, each non-`ran` outcome with its cause; then
   every zero-hit cell, phrased as what did not surface across what was searched, with its named
   limits.
3. **Table stakes.** Lens 1: the services above both thresholds, each with BOTH ratios written out
   and the `presence_split` beside the count. "4 of 6 catalogs — 2 of 2 commercial, 2 of 4
   developer-facing — and 4 of 5 comparable products' directories" is the shape; a bare "present in
   most" is the claim this section exists to replace.
4. **Differentiators.** Lens 2, with the same two ratios, phrased as a search result rather than as
   a claim about the world.
5. **Conventions.** Lenses 3, 4 and 5 in that order: API style with its first-party denominator;
   the auth pair distribution **beside its base rate**, never alone; the event taxonomy clustered
   by noun. Where a convention is absent, say so — an absent convention is a finding.
6. **Cost to integrate.** Lens 6: the complexity ranking, every score written with its four
   components, and the services scoring 4 or more called out as needing their own milestone.
7. **Unavailable or gated.** Lens 7, each entry with its specific gate and the date that gate was
   true. This is the section a comparison site never writes, and the one a product team acts on
   soonest.
8. **Amendments changelog** *(delta runs only)*. One dated entry per delta run: what changed, what
   was added, and what a prior run claimed that this one corrects.

## What does not go in the report

No recommendation about which integrations THIS product should build, or in what order. The survey
reports the ecosystem; choosing what to build within it is the downstream document's job, working
from the register. A report that picks the roadmap has quietly replaced the decision it was meant to
inform.

No re-scoring either. `complexity.score`, `priority` and `availability` are the register's, each
re-derivable from its own components, and restating one differently in prose is how a reader ends
up with two answers and no way to tell which is current.

## Grounding

Every figure carries the extract record id it came from, and anything commercial carries the date it
was true. A pricing shape, a rate limit or a compliance gate without its date is a fact about a
moment nobody can locate. An unattributed sentence in an ecosystem report is an opinion wearing a
citation's clothes.
