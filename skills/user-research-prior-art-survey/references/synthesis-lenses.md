# Synthesis lenses — the five corpus cuts

Load when running Procedure 4. The extract set is the corpus, and here it is a set of CONTAINERS:
one file per source, N finding-records inside each. Every lens cuts across findings, not across
files — clustering by claim is the reason the record is a finding rather than a paper.

## The five lenses

1. **Claim convergence.** Which findings from independent sources support the same claim.
   Independence is the load-bearing word: two findings from the same paper are one study
   agreeing with itself, and grouping by the source prefix is how you tell.
2. **Contradiction.** Where findings disagree, and what differs between them — population,
   platform, or date. A contradiction that dissolves once you notice one study was desktop-2009
   and the other mobile-2024 is the most useful thing this survey produces.
3. **Certainty weighting.** What the corpus supports at `high` certainty versus what rests on
   `low`. Never average the levels: a claim is supported at the certainty of the evidence behind
   it, and a mean of ordinal labels is a number with no meaning.
4. **Transferability.** Which findings were measured on a population and platform close enough to
   this project's to carry, and which are excellent evidence about somebody else. This is why
   transferability is a separate field — a high-certainty, low-transferability finding is exactly
   the one a careless reader misapplies.
5. **Currency and absence.** What the corpus says only about an older platform generation, and
   what it does not cover at all. An angle that vacated produced no evidence about the world; an
   angle that ran and found nothing did.

## Never recompute

Effect sizes and sample sizes are carried verbatim from the records. Do not convert between
measures, pool across studies, or derive a summary statistic — that is meta-analysis, it needs
methods this survey does not run, and a pooled number would look authoritative while resting on
nothing.

## Phrasing an absence claim

"No study surfaced across the angles that ran addresses X for this population" — never "there is
no research on X". The first is a survey result; the second is a claim about the literature that
this survey cannot support.

## Grounding

Every report sentence carries the finding id it rests on, and every claim about strength carries
its certainty and transferability. A claim reported without them has silently promoted itself.
