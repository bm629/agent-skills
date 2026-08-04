# Sources

Provenance for the research behind this skill's bar. The bar itself is `conditions.md`.

This half and its producing twin were built from **one** dossier, so the two cannot grade the
same artifact by different rules. What follows is what that research supplied to the conditions.

## Method standards

- **PRISMA-S** (Rethlefsen et al., 2021), 16 reporting items — read at the open PMC mirror,
  2026-08-04. Three items are the direct grounding for C11, C13 and C15: item 8 requires search
  strategies "copied and pasted exactly as run", item 13 the date of each search, item 15 the
  number of records identified from each source. C11's reproducibility test is item 8 applied to
  an artifact rather than to a paper.
- **GRADE Working Group** — certainty of evidence and its rating domains, read 2026-08-04. GRADE
  folds **indirectness into the single certainty rating**. C26 exists because this survey must
  not: a high-certainty finding about a different population is exactly the case a collapsed
  rating hides, and both judgments belong to the wave that has done the full read.

## What the source-access research supplied to the conditions

Verified by direct fetch, 2026-08-04 (full detail in the producer's `references/sources.md` and
encoded in its `source-registry.yaml`):

- **C23** rests on the citation-graph index documenting a **globally shared unauthenticated
  pool**, explicitly throttleable under load. That makes a 429 there a normal operating condition
  and puts three statuses in play where a careless artifact records one.
- **C24** rests on two sources having a website that refuses this survey and an API that does
  not. The condition judges the `source_id`, not the corpus name, because reaching the wrong host
  is a breach the artifact will not otherwise show.
- **C17** rests on three sources declaring crawl delays of 60, 15 and 10 seconds. Where a delay is
  declared the selection IS the method, and the un-fetched remainder is the part that makes the
  coverage honest.
- **C18/C19** rest on the observation that retrievable full text and a stated method are
  independent: practitioner argument is fully retrievable and reports no study, while much
  method-bearing work is abstract-only. Checking one conjunct passes half the artifact.

## Method note

One identifier was guessed rather than looked up during this research and resolved to an
unrelated retracted paper; the claim was re-grounded by search instead. It is recorded because it
is the same failure C21 exists to catch, one level up — an identifier that looks plausible is not
an identifier that was read.
