# Extraction template guide (Procedure 3 output)

One extraction is a Markdown file per **source** — a **YAML frontmatter** machine block above a
**3-section markdown body**. The frontmatter is defined and validated by
`schemas/extract-output.schema.json` (see `extract-output-guide.md`).

**This type has TWO units, and they differ on purpose.** The queue row and the ticket are one
SOURCE — a paper or an article. The record is one published FINDING. One child reads one source
and writes ONE file containing the N findings it found.

The split is forced, not stylistic. How many findings a paper contains is only knowable after the
deep read, so finding-level queue rows would make the search child do the extract's work; and
paper-level rows mapped to N files would leave "the row lacking a file" undefined, breaking the
cursor that decides doneness. One row, one file, N records inside resolves both.

This is the outlier among the sibling surveys, where one record is one thing. Do not carry their
shape over.

The file is written as `record_filename(source_id) + .md`, and this type is the most exposed of
the three: a DOI *always* contains a `/`. Written verbatim, the record lands in a directory nobody
looks in, stays valid, and is treated as never written.

## The 3 body sections are FIXED

The validator's `EXTRACT_HEADINGS` constant checks each `## <heading>` is present.

1. **## Method** — what was actually done: design, participants, what was measured. The scope
   admits published research only, and the method is what makes a finding weighable.
2. **## Findings** — prose accompanying the records in the frontmatter, one per finding.
3. **## Transferability** — who the claims were measured on and where they plausibly carry.

## Certainty is assigned by RULE, not appraisal

Four levels, borrowed from GRADE's vocabulary — `high`, `moderate`, `low`, `very-low` — and the
table is TOTAL: every admitted source lands on exactly one row. You do not perform a five-domain
GRADE assessment; you record four facts (design, sample size, effect size, whether the read finds
a method at all) and the level follows.

The validator re-derives the level from those facts and rejects a mismatch. A disagreement is an
error, not an opinion — which is the whole point of assigning by rule.

## Transferability is SEPARATE and never folded in

GRADE folds indirectness into one number; here it must not be. A methodologically excellent
finding from another domain is **high-certainty and low-transferability**, and collapsing those
hides exactly what the reader needs. State the population it was measured on and give the
judgment a reason a reader can weigh.

## Numbers travel verbatim

Effect sizes and sample sizes are carried as the source words them. Never recomputed, never
converted, never rounded into a cleaner-looking figure.

## Currency is first-class

Study date, population and platform context are required on every record. A 2009 finding about a
UI convention may not hold in 2026, and synthesis cannot weigh recency against an optional field.

## Access is recorded

`access_status` says how the source was reached — open, free-registration, crawl-delayed,
paywalled to the abstract, or blocked. Channels die; recording how you got in makes the next death
visible instead of silent.
