# Extraction template guide (Procedure 3 output)

One extraction is a Markdown file per **convention source** — a **YAML frontmatter** machine
block above a **3-section markdown body**. The frontmatter is defined and validated by
`schemas/extract-output.schema.json` (see `extract-output-guide.md`); this guide covers the body.

The unit is ONE CONVENTION SOURCE: one design system, one ARIA pattern, one platform HIG
section, one deceptive-pattern type. Not one component, and not one product — a design system's
component catalog belongs in the body of that system's single record, not spread across records.

The file is written as `record_filename(item_id) + .md`. An `item_id` may legitimately carry
characters a filename cannot, so deriving the name any other way puts the record where nothing
looks for it — it stays perfectly valid, nothing reports it missing, and the queue row is treated
as never extracted. The QA phase checks this; the validator deliberately does not.

## The 3 body sections are FIXED

The validator's `EXTRACT_HEADINGS` constant checks each `## <heading>` is present, so this guide
and the validator share one list and cannot drift.

1. **## Statement** — what the convention actually requires or describes, in the corpus's own
   terms. Not why it matters, not whether you agree: the corpus's claim, faithfully. The
   frontmatter carries a one-line `statement`; this section is where it is set out properly.
2. **## Evidence** — the quoted or closely-paraphrased passage the statement rests on, named to
   its corpus section and version. A statement with no locatable passage behind it is the
   failure this section exists to prevent.
3. **## Applicability** — whether the convention binds THIS project, and on what basis. A
   verdict of "does not apply" is a real result and stays in the register; it is not a reason to
   skip the record.

## The DTCG token block

A **design-system** record whose corpus publishes design tokens carries them as a fenced
` ```dtcg ` block in the body, and sets `tokens_in_body: true` in the frontmatter. Synthesis
copies that block verbatim into the register row.

Two rules the validator enforces, because each silently empties the register otherwise:

- `tokens_in_body: true` with no ` ```dtcg ` block in the body fails — the register row would be
  copied from nothing.
- A ` ```dtcg ` block on a design-system record with `tokens_in_body: false` fails — synthesis
  reads the flag, so the tokens would never reach the register.

Tokens are carried **per system, verbatim**. Never merge several systems' token sets into one
blended set: merging is a synthesis judgment that drifts silently from its sources, and the
downstream skill's job is to author THIS project's system from the evidence, not to inherit a
blend.

## Skipped records still ship

The relevance bail is the survey's only cut and is taken at the FRONT of the child, before the
deep read. A skipped record is written with `outcome: skipped`, a typed `cause`, and a `detail`
that says why in its own terms — a bare cause code is a verdict without evidence, and the
validator rejects it. An unread source recorded with its reason is evidence; a missing file is a
gap nobody can distinguish from an oversight.

Bail only on a confident "touches none of the scope". Uncertainty keeps the source.
