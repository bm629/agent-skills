# The extraction record — template and headings

An extract record is one file per source item: a YAML frontmatter block carrying the machine
fields, above a markdown body carrying the analysis. The frontmatter contract is
`schemas/extract-output.schema.json`; the body's headings are fixed and the validator checks
they are all present and in order.

Co-locating the machine block with the human analysis is deliberate. A record outlives the code
that wrote it, and splitting the two halves into separate files guarantees they drift.

## The nine headings, in order

```markdown
## What the source says
## Which surfaces it applies to
## Evidence of exploitation
## Severity as published
## The control the source prescribes
## Preconditions and limits
## Relationship to other items
## What this does not establish
## Provenance
```

**What the source says** — the item in your own words, not its abstract pasted. If you cannot
restate it, you have not read it.

**Which surfaces it applies to** — named from the caller's scope, matching the `surfaces`
frontmatter field. "The approval workflow", not "web applications".

**Evidence of exploitation** — what puts this at its tier, or an explicit statement that nothing
does. This is the section that makes a tier defensible rather than asserted.

**Severity as published** — every scoring system the source carries, each with its version.
Never collapse them into one number, and never compare across versions: a 7.5 under one revision
and a 7.5 under the next are not the same claim.

**The control the source prescribes** — quoted or closely paraphrased from the source, with
where it says so. Where the source prescribes nothing, this section says exactly that. It is a
legitimate and common outcome, and inventing a control to fill the space is the single worst
thing you can do in this record.

**Preconditions and limits** — what has to be true for this to apply. Attack patterns state
prerequisites; advisories state affected version ranges; incidents state a context. This is
what stops a register row being applied where it does not belong.

**Relationship to other items** — which identifiers name this same thing (`aliases`) and which
name neighbours (`related`). Get this wrong and synthesis either merges two distinct threats or
reports one threat twice.

**What this does not establish** — the honest boundary. A proof-of-concept establishes
reproducibility somewhere, not exposure here. An incident at another company establishes that
the pattern pays, not that your product is affected. Writing this section is what stops the
register overclaiming.

**Provenance** — where you read it, when, and whether a content-sanitization guardrail was
applied.

## The record's filename

`item_id` is the record's IDENTITY; the filename is a separate, derived thing. Per the
per-source-class identifier policy a non-registry item carries a stable URL as its identity —
and a URL written verbatim as a filename turns its slashes into directories. The record then
sits somewhere no consumer looks: the caller's queue cursor and the synthesis loader both
resolve a record BY NAME, so a misplaced record is invisible while remaining perfectly valid,
and nothing ever reports it missing.

Derive the stem with `record_filename(item_id)` from the package's validator script. The
validator checks the name against the frontmatter, so a mismatch fails the gate.

| `item_id` | filename |
|---|---|
| `CVE-2026-31337` | `CVE-2026-31337.md` — already safe, unchanged |
| `v5.0.0-2.1.1` | `v5.0.0-2.1.1.md` — already safe, unchanged |
| `https://hackerone.com/reports/3417162` | `https-hackerone.com-reports-3417162-f374e84a.md` |

The digest is taken over the WHOLE id, so two ids differing only in characters the sanitizer
collapses (`a/b` and `a:b`) still get different names.

## The relevance bail

Before the deep read, skim the item and ask one question: does this apply to **any** of the
caller's scope — its capabilities, its stack or dependency names, its surfaces? Bail only on a
confident "none". **Uncertainty keeps the item**: the expensive read is cheaper than a missed
threat, and this is the only cut in the entire survey.

A bail record is frontmatter only, with no body. It carries the reason, a real rationale naming
what you checked and why none of it is touched, and the scope elements you actually considered.
"Not relevant" is not a rationale — it is a restatement of the verdict.

Never bail because a control seems already handled, or because the item looks low-severity.
Neither is a relevance judgment: the first requires an architecture that does not exist yet, and
the second is the tiering's job, downstream.

## Worked example — a full extraction

```markdown
---
schema_version: 1
item_id: "CVE-2026-31337"
id_class: registry
outcome: extracted
surfaces: ["receipt upload", "document rendering"]
tier: 2
tier_evidence:
  - {kind: public-poc, reference: "exploit archive entry 51999", as_of: "2026-08-03T12:00:00Z"}
source_authority: authoritative-registry
severity:
  - {system: CVSS, version: "3.1", vector: "AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H", score: 8.8}
  - {system: CVSS, version: "4.0", score: 8.6, as_of: "2026-08-03T12:00:00Z"}
control:
  stated: true
  text: "upgrade to 2.4.1, or disable the PDF raster path for untrusted input"
  source_reference: "advisory, Remediation section"
aliases: ["GHSA-xxxx-yyyy-zzzz"]
related: ["CWE-434"]
extracted_at: "2026-08-03T12:05:00Z"
sanitization: {status: sanitized}
---

## What the source says
...
```

## Worked example — a bail

```markdown
---
schema_version: 1
item_id: "CVE-2026-40001"
id_class: registry
outcome: skipped
skip:
  reason: irrelevant
  bail_rationale: "affects an industrial control protocol stack with no HTTP, storage or identity surface; the product exposes none of those and names no component in that ecosystem"
  checked_scope: ["receipt upload", "approval workflow", "payouts", "named third-party services"]
---
```

No body. A bail is a decision, not an analysis.
