---
name: reviewing-user-research-prior-art-survey
description: >
  Use when judging a finished user-research prior-art artifact before it is accepted — a
  research vocabulary map, a per-angle search output, an extract container, or the evidence
  register and report. An acceptance gate, not authoring. Judges a single-sourced bar: a
  recorded zero is distinguishable from an unreachable source; a claim stays within what its
  method could measure; recorded facts match the source; transferability carries a weighable
  reason and is never folded into certainty; numbers are the source's own; findings in one
  container are genuinely distinct; population and platform describe the study rather than the
  project; convergence is across INDEPENDENT sources; certainty is never averaged; absence is
  phrased as a search result. Approves a thin-but-honest result and revises only on a named,
  unrecorded gap. Emits exactly VERDICT: approve|revise plus actionable findings.
extensions:
  claude: {}
  codex: {}
  copilot: {}
  cursor: {}
  gemini: {}
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-08-04
  reviewed: 2026-08-04
---

# `reviewing-user-research-prior-art-survey` — SKILL.md

## Overview

Judge one produced artifact against the twenty-seven-condition bar in
`references/conditions.md`. **That file is the authoritative bar** — this body describes how to
apply it and never restates a condition normatively.

The arrangement exists because a bar duplicated across a producer and its reviewer drifts: one
document says `kept` counts results, the other says it counts rows, both look right in isolation,
and the disagreement only surfaces when an artifact is graded by the half that did not write it.

## When to activate

- Judging a research vocabulary map, or one angle's search output, before it is accepted.

**Do NOT activate for:** authoring either artifact (the producing twin); judging an extract
record or a findings register (wave 2, not yet shipped); assessing whether the underlying
research is any good as science — the bar is whether the ARTIFACT is honest about what was
searched and what was found.

## What you are handed

The artifact, and — for a search output — the vocabulary map it was produced from. **Stop the
review and say so if a search output arrives without its map:** the applicable set, and therefore
coverage completeness, cannot be derived without it, and a review that proceeds anyway silently
drops the condition that matters most.

## Workflow

1. **Run the deterministic gate** if it has not run:
   `validate_user_research_prior_art.py keyword-map <file>` or
   `... search <file> --keyword-map <map>`. Its failures are the producer's to fix before review.
   Conditions marked *(gated)* are discharged by that run and are **not** restated as findings —
   duplicating the validator buries the judgment half in noise.
2. **Walk the judgment conditions in order.** Read the artifact against each; do not skim for
   problems.
3. **Ground every finding.** Quote the artifact text that fails, and name the condition number.
   Anything you cannot ground in the artifact, its schemas, the registry or the map is an
   **OBSERVATION**, not a finding.
4. **Emit one verdict line**, then the findings.

## Where reviews of this artifact go wrong

- **Grading the research instead of the record.** Whether a study is well designed is not this
  bar. Whether the artifact honestly says what was searched, what was found, and what was not
  retrievable, is.
- **Using your own knowledge of the literature as evidence.** If a landmark paper seems missing,
  the finding is that the coverage does not account for it — not that you know its title. The
  producer queried from a map; the map is what a finding must point at.
- **Reading thinness as failure.** Most product scopes have very little research addressing them
  directly. C27 is a numbered condition precisely because the reflex is strong.
- **Re-probing a source and treating your success as proof.** One source here runs a globally
  shared pool whose throttling varies minute to minute. That you reached it now says nothing
  about whether the producer could.
- **Reporting findings one at a time.** Each round costs a revise cycle, and the loop caps out on
  work that was nearly right. One pass, every finding.

## The two conditions this type turns on

Stated here because they are what makes this survey different from its siblings, not because they
are restated normatively — the wording that binds is in `conditions.md`.

**Admission has two conjuncts** (C18, C19). Retrievable full text alone admits practitioner
argument that reports no study. A stated method alone admits a record built from an abstract,
which reads exactly like one grounded in the method section. A reviewer who checks one and not
the other passes half the artifact.

**Certainty and transferability are not wave-1 judgments** (C26). Both turn on the full read, and
admission is decided before it. A wave-1 artifact that grades its evidence has invented a
precise-looking value nothing can check.

## Output

Exactly one verdict line — `VERDICT: approve` or `VERDICT: revise` — followed by findings, each
naming its condition number and quoting the artifact text that fails it. Nothing after the
verdict line, unless the caller's brief names an equivalent form, in which case that replaces it.
Emitting both forms is the violation; the cardinality is what is fixed, not the wording.

## Related

- `user-research-prior-art-survey` — the producing half. Its validator discharges the *(gated)*
  conditions; its `references/source-registry.yaml` is part of your evidence.
- `references/conditions.md` — **the authoritative bar.**
