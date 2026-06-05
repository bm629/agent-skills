---
name: reviewing-document-set
description: >
  Use when reviewing or judging a SET of finished project documents as one corpus,
  to decide whether they are mutually coherent and ready to plan from — the
  corpus-level analog of a single-document design review. It assumes each document
  already passed its own gate and judges only how the documents relate. Checks six
  dimensions: cross-document consistency (incl. one name per entity), completeness
  and traceability from the upstream-most document (every requirement carried
  downstream; no dropped/orphaned items or TBDs), contradictions, dependency
  integrity (each doc consistent with its declared upstreams), divergent
  duplication, and ready-to-plan sufficiency. Emits exactly one terminal
  `VERDICT: approve|revise` for the whole set, each finding prefixed with the
  affected document id(s) so a caller can act per document. Approves a coherent
  corpus (no false-revise); revises only on a real, named cross-document gap. Not
  for judging one document's internal quality, nor for authoring or fixing them.
extensions:
  claude:
    when_to_use: "judging a finished SET of documents for cross-document coherence and emitting one approve/revise verdict"
    argument-hint: "<the set of finished documents to review as a corpus>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-05
---

# `reviewing-document-set` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished SET of documents as one corpus — checking they are mutually coherent and ready to plan from, then emitting `VERDICT: approve|revise` with per-document findings.

## Overview

This skill is the **corpus-level acceptance gate** over a set of finished, related documents. Loaded by a reviewer holding the whole set, it answers one question: **do these documents form one coherent body that carries the project's intent forward and is sufficient to plan and build from?** It applies a fixed **six-dimension cross-document checklist**, then emits a single machine-parseable verdict plus per-document-attributed findings the producers can act on.

It is the complement to single-document review — each document's own quality gate ran earlier. This skill **never re-litigates one document's internal quality**; it judges only how the documents **relate** as a set. It is review-only: it does not author, fix, or rewrite anything.

## When to activate

- A finished set of related project documents needs an accept/revise decision on **mutual coherence** before downstream planning.
- You are the independent gate over a corpus *after* each document has passed its own per-type review.
- Re-judging a corpus after fixes from a prior `revise`.

**Do NOT activate when:**

- You are judging a **single** document's internal quality — use the matching per-document review (e.g. a design review for one design doc).
- You are **authoring or fixing** a document — this is review-only.
- There is only one document — there are no cross-document relationships to judge.

## Workflow

The method is six dimensions, then a verdict. Read every document first.

### Step 1 — Orient

Identify the **upstream-most document** (the originating brief / requirements document) — it is the **traceability root** that anchors the "carried downstream" checks. Note each document's declared **upstream dependencies**. Assume each document already passed its own gate, so you are looking only for cross-document defects. Judge the set you are **handed** — you do not need a separate list of "intended" documents.

### Step 2 — Judge the six dimensions

For each dimension, collect findings (a defect is always *between* documents):

1. **Cross-document consistency (incl. key terms).** The same fact, number, decision, scope boundary, or named entity is described the same way in every document that touches it. Two finding classes: **substantive** (a value/decision/scope stated differently) and **key-term** (the same core entity given different names across documents — "members" here, "accounts" there, with no statement they are the same). Flag both. Do **not** flag prose style, tone, or harmless synonyms.
2. **Completeness & traceability (anchored on the root).** Every goal/requirement in the root document is **carried forward** into the documents that should elaborate or realize it; nothing is silently dropped. Flag a **dropped requirement** (in the root, absent downstream), an **orphan** (a document nothing references and that references nothing upstream), and unresolved **TBD/placeholder** intent.
3. **Contradiction detection.** No two documents assert facts/decisions that **cannot both be true**. This is consistency's hard edge — logically incompatible, not merely worded differently.
4. **Dependency integrity.** Each document faithfully elaborates the documents it declares as upstreams — same entities, decisions, and scope, adding detail without contradicting or quietly re-scoping them.
5. **No unnecessary duplication.** A fact/decision/definition that belongs to one document should live there once and be referenced, not copied where the copies can drift. Flag **divergent** duplication (the same thing stated in two places that disagree, or substantial unowned redundancy that will).
6. **Ready-to-plan.** Taken together, is the corpus sufficient and coherent enough that a planner could derive defensible milestones **without going back to ask?** Surface any gap that would **block planning** — an unresolved decision a later phase depends on, a requirement with no testable acceptance anywhere, a named dependency never specified. This is the difference between `approve` and `revise`.

### Step 3 — Decide and emit

Weigh the findings. **Approve** a corpus that is consistent, complete, traceable, and ready-to-plan — do not false-revise a coherent set over nits. **Revise** on any real, named cross-document gap. Emit the output contract below.

## Rules

**Hard rules (never violate):**

- **One terminal verdict for the whole corpus.** End with **exactly one** line — `VERDICT: approve` or `VERDICT: revise` — for the **entire set**. Never emit a verdict per document (a caller typically reads only the last `VERDICT:` line, so multiple verdicts corrupt the result).
- **Bracketed per-document attribution.** Every finding line **begins with the affected document id(s) in square brackets**, then states what is wrong across them and how to reconcile it: `- [d-prd, d-arch] auth model differs (PRD: OAuth, arch doc: SAML) — pick one and align both.` A single inconsistency may name more than one id; decide which document(s) should change. This lets a caller route one fix per affected document.
- **Cross-document only.** Never re-litigate a single document's internal quality — that was an earlier, separate gate.
- **Judge the handed-in set.** Do not require a separate list of intended documents; the set you are given is the set under review.
- **No false-revise.** Approve a coherent corpus; revise only on a real, named gap, with findings **actionable in one pass** (what + which documents + how to reconcile).
- **Review-only.** Never author, fix, or rewrite a document; report findings, the producers revise.

## Gotchas

- **Naming mismatch read as a contradiction.** Different names for the same entity (Dimension 1) is not the same as two statements that cannot both be true (Dimension 3). Classify correctly — the fix differs.
- **Drifting into single-document review.** Judging whether the PRD is *good* is the per-document gate's job; here, judge only whether the PRD *agrees with and is carried into* the rest.
- **"Each document is fine, so the set is fine."** A set of individually-correct documents can still disagree with each other — coherence is a property of the *relationships*, not the parts.
- **Pairwise-only checking hides dropped requirements.** A requirement dropped *everywhere* downstream has no pair to conflict with; only the root-anchored traceability pass catches it.
- **Per-document verdicts.** Tempting with per-document findings, but they break a caller that reads the last verdict line. One verdict; attribution lives in the findings.

## Anti-patterns

- **A verdict per document** instead of one for the corpus.
- **Free-prose attribution** ("the PRD and the architecture doc disagree") with no bracketed ids — a caller cannot act per document.
- **Flagging style** — synonyms, tone, formatting — as inconsistency.
- **Rubber-stamping** because the document count looks complete, without tracing requirements or comparing decisions.
- **Rewriting the documents** instead of returning findings.

## Output

A findings report: zero or more per-document-attributed finding lines (each starting `- [id, …]`), followed by **exactly one** terminal `VERDICT: approve|revise`. On `revise`, the findings are the actionable list a caller turns into one fix per affected document. The abstract consumers are the orchestrator that routes the fixes and the producers who revise.

## Related

- A single-document **design review** skill — the per-document analog; this skill is its corpus-level complement, run *after* each document passes its own gate.
- **Per-type document review** skills — judge one document's internal quality; this judges how documents relate as a set.
- The practice this operationalizes — requirements traceability (RTM), single-source-of-truth / terminology consistency, IEEE 830 consistency & completeness, and the agile Definition of Ready — see `references/sources.md`.

## Progressive disclosure

- `references/sources.md` — research provenance for the six-dimension bar.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap; the combined `description` + `when_to_use` is truncated at 1,536 chars in the listing).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; heavy content lives in `references/`.
