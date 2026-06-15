---
name: reviewing-document-set
description: >
  Use when judging a SET of finished project documents as one corpus, to decide
  whether they are mutually coherent and ready to plan from — the corpus-level
  analog of a single-document design review. Assumes each document passed its own
  gate; judges only how they relate, against an eight-dimension bar: cross-document
  consistency (incl. one name per entity); completeness/traceability from the
  upstream-most doc (no dropped/orphaned items or TBDs); contradictions; dependency
  integrity; divergent duplication; ready-to-plan sufficiency (Definition-of-Ready
  + a referenced-but-absent doc); amend/delta-scoped re-review when a doc changed
  (ripple to its dependents); and version-skew (a doc citing a stale version of
  another). Emits exactly one terminal `VERDICT: approve|revise` for the whole set,
  each finding prefixed with the affected document id(s). Approves a coherent
  corpus (no false-revise); revises only on a real, named cross-document gap. Not
  for one document's internal quality, nor authoring or fixing them.
extensions:
  claude:
    when_to_use: "judging a finished SET of documents for cross-document coherence (incl. amend re-review + version-skew) and emitting one approve/revise verdict"
    argument-hint: "<the set of finished documents to review as a corpus (+ any stated change, for an amend re-review)>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-05
  reviewed: 2026-06-15
---

# `reviewing-document-set` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished SET of documents as one corpus — checking they are mutually coherent and ready to plan from, then emitting `VERDICT: approve|revise` with per-document findings.

## Overview

This skill is the **corpus-level acceptance gate** over a set of finished, related documents. Loaded by a reviewer holding the whole set, it answers one question: **do these documents form one coherent body that carries the project's intent forward and is sufficient to plan and build from?** It applies a fixed **eight-dimension cross-document checklist**, then emits a single machine-parseable verdict plus per-document-attributed findings the producers can act on.

It is the complement to single-document review — each document's own quality gate ran earlier. This skill **never re-litigates one document's internal quality**; it judges only how the documents **relate** as a set. It is review-only: it does not author, fix, or rewrite anything.

## When to activate

- A finished set of related project documents needs an accept/revise decision on **mutual coherence** before downstream planning.
- You are the independent gate over a corpus *after* each document has passed its own per-type review.
- Re-reviewing a corpus after a change — either the producers fixed a prior `revise`, or one (a few) document(s) changed independently. Both run **Dimension 7 (amend / delta-scoped re-review)**: re-validate only the edges the change touched, not the whole corpus.

**Do NOT activate when:**

- You are judging a **single** document's internal quality — use the matching per-document review (e.g. a design review for one design doc).
- You are **authoring or fixing** a document — this is review-only.
- There is only one document — there are no cross-document relationships to judge.

## Workflow

The method is eight dimensions, then a verdict. Read every document first.

**Scale the audit to the corpus (proportionality).** The depth of the cross-document audit — and which dimensions even apply — scales with corpus size. A small, coherent set (2–3 documents, few cross-document edges) is **approved**; do not manufacture RTM-style ceremony to justify a revise on it. Several dimensions are explicitly **n/a** in common cases: Dimension 7 (amend) is n/a on a greenfield first-pass set with no prior version or stated change; Dimension 8 (version-skew) is n/a on a single-version set. Applying a heavyweight audit to a thin or first-pass corpus is a false-revise.

### Step 1 — Orient

Identify the **upstream-most document** (the originating brief / requirements document) — it is the **traceability root** that anchors the "carried downstream" checks. Note each document's declared **upstream dependencies**. Assume each document already passed its own gate, so you are looking only for cross-document defects. Judge the set you are **handed** — you do not need a separate list of "intended" documents. Also note any **stated change** handed in with the set (a delta, a version bump, a changelog) — its presence triggers the amend re-review (Dimension 7); its absence means a greenfield first-pass (Dimension 7 is n/a).

### Step 2 — Judge the eight dimensions

For each dimension, collect findings (a defect is always *between* documents):

1. **Cross-document consistency (incl. key terms).** The same fact, number, decision, scope boundary, or named entity is described the same way in every document that touches it. Two finding classes: **substantive** (a value/decision/scope stated differently) and **key-term** (the same core entity given different names across documents — "members" here, "accounts" there, with no statement they are the same). Flag both. Do **not** flag prose style, tone, or harmless synonyms.
2. **Completeness & traceability (anchored on the root).** Every goal/requirement in the root document is **carried forward** into the documents that should elaborate or realize it; nothing is silently dropped. Flag a **dropped requirement** (in the root, absent downstream), an **orphan** (a document nothing references and that references nothing upstream), and unresolved **TBD/placeholder** intent.
3. **Contradiction detection.** No two documents assert facts/decisions that **cannot both be true**. This is consistency's hard edge — logically incompatible, not merely worded differently.
4. **Dependency integrity.** Each document faithfully elaborates the documents it declares as upstreams — same entities, decisions, and scope, adding detail without contradicting or quietly re-scoping them.
5. **No unnecessary duplication.** A fact/decision/definition that belongs to one document should live there once and be referenced, not copied where the copies can drift. Flag **divergent** duplication (the same thing stated in two places that disagree, or substantial unowned redundancy that will).
6. **Ready-to-plan.** Taken together, is the corpus sufficient and coherent enough that a planner could derive defensible milestones **without going back to ask?** Apply the **Definition-of-Ready backbone** as the concrete "blocks planning" test: **dependencies named** (every cross-document or external dependency the corpus relies on is identified somewhere in the set — a named dependency never specified is a blocker), **testable acceptance somewhere** (every load-bearing requirement has testable acceptance *in some document of the set* — the corpus, not one doc, must carry it), and **no blocking TBD** (no unresolved decision a later phase depends on). Also flag a **referenced-but-absent load-bearing document** — a document the *handed-in set itself references but does not contain* (the api-spec says "see the data-model" but there is no data-model; three docs assume a security model no document specifies). Infer this gap from the **dangling reference inside the set** — never demand a document from an external "ideal list" the project may not need (no data-model for a stateless CLI tool is not a defect). This is the difference between `approve` and `revise`.
7. **Amend / delta-scoped re-review.** *Applies only when a document in the set changed* (a stated delta, version bump, or changelog was handed in); **n/a on a greenfield first-pass** set. Two triggers, one method: the change may be (a) the producers fixing a prior `revise`, or (b) an upstream document changing independently. For either: **(1)** identify the changed document(s); **(2)** trace the ripple to the documents that **declare the changed doc as an upstream** (its dependents — the at-risk edges); **(3) propagation check** — for each affected edge, was the change *propagated* into the dependent, or is the dependent now **stale**?; **(4) delta-scoped** — re-validate only the affected edges and their second-order ripples; do **not** re-litigate unchanged, already-coherent relationships. A dependent the ripple never reached is a finding. **The "changed but no stated delta" case:** if the set clearly changed but no delta is handed in, the *dynamic* trace is n/a — rely on Dimension 8 (the static skew check) on the full pass to catch any stale dependent.
8. **Version skew (stale cross-reference).** For each **explicit cross-reference** (document A cites a decision/value/entity/version of document B), confirm A reflects B's **current** state, not a superseded one (A elaborates B's v1 decision but B moved to v2; A names an entity B has since renamed). **Overlap guard (do not double-flag):** Dimension 8 fires **only** for a *staleness/currency* defect — a document built on a **superseded version/decision** of another. A plain value-disagreement with no version dimension stays Dimension 1; a flat impossibility stays Dimension 3; a quiet re-scoping stays Dimension 4. Do **not** revise under Dimension 8 a defect already named under 1/3/4. **n/a on a single-version set** (every document on its first version — no prior state to be stale against). Dimension 8 is the *static* twin of Dimension 7's *dynamic* propagation check: 7 finds a freshly-created skew when a change is announced; 8 names a skew on any pass, signal or not.

### Step 3 — Decide and emit

Weigh the findings. **Approve** a corpus that is consistent, complete, traceable, current (no version skew), ripple-complete (any change propagated), and ready-to-plan — do not false-revise a coherent set over nits, and do not false-revise a **thin** (few-edge), **single-version**, or **greenfield first-pass** set for lacking the proportionally-n/a dimensions (7, 8). **Revise** on any real, named cross-document gap. Emit the output contract below.

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
- **Version skew double-flagged (Dimension 8 overlap).** A stale cross-reference is a *currency* defect (Dimension 8) — do not also flag it as a plain inconsistency (1), contradiction (3), or dependency defect (4). One defect, one dimension; Dimension 8 owns the "superseded version/decision" case.
- **Amend run as a full re-review.** When a document changed, re-validating the *whole* corpus (not just the edges the change touched) is both wasteful and a false-revise risk — Dimension 7 is **delta-scoped**. Conversely, when the set clearly changed but no delta was handed in, the dynamic trace is n/a — lean on Dimension 8, do not invent a change history.
- **Demanding a document from an external list.** A "missing document" finding is legitimate only when the **set itself references** the absent doc (Dimension 6, referenced-but-absent). Demanding a doc the project may not need (a data-model for a stateless CLI) is fabrication — there is no manifest here.

## Anti-patterns

- **A verdict per document** instead of one for the corpus.
- **Free-prose attribution** ("the PRD and the architecture doc disagree") with no bracketed ids — a caller cannot act per document.
- **Flagging style** — synonyms, tone, formatting — as inconsistency.
- **Rubber-stamping** because the document count looks complete, without tracing requirements or comparing decisions.
- **Rewriting the documents** instead of returning findings.
- **False-revising a thin / single-version / greenfield set** for lacking the proportionally-n/a dimensions (7 amend, 8 version-skew) — proportionality judges the corpus, not a fixed checklist.

## Output

A findings report: zero or more per-document-attributed finding lines (each starting `- [id, …]`), followed by **exactly one** terminal `VERDICT: approve|revise`. On `revise`, the findings are the actionable list a caller turns into one fix per affected document. The abstract consumers are the orchestrator that routes the fixes and the producers who revise.

## Related

- A single-document **design review** skill — the per-document analog; this skill is its corpus-level complement, run *after* each document passes its own gate.
- **Per-type document review** skills — judge one document's internal quality; this judges how documents relate as a set.
- The practice this operationalizes — requirements traceability (RTM, forward/backward/bidirectional), single-source-of-truth / terminology consistency, IEEE 830 consistency & completeness, the agile Definition of Ready (Dimension 6), and Change Impact Analysis (Dimension 7, the amend ripple) — see `references/sources.md`.

## Progressive disclosure

- `references/coherence-bar.md` — the eight dimensions' per-dimension pass/gap signals + worked cross-document findings (load esp. for Dimensions 6/7/8).
- `references/sources.md` — research provenance for the eight-dimension bar.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap; the combined `description` + `when_to_use` is truncated at 1,536 chars in the listing).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn; heavy content lives in `references/`.

## Changelog

- **1.1.0** (2026-06-15) — production-grade redesign: the bar grows **6 → 8 dimensions**. Dimensions 1–5 kept verbatim; **Dimension 6 deepened** (Definition-of-Ready backbone + the referenced-but-absent load-bearing-document finding); **Dimension 7 minted** (amend / delta-scoped re-review — corpus-level Change Impact Analysis, covering both the post-`revise` and upstream-changed triggers, proportionally n/a on a greenfield set); **Dimension 8 minted** (version-skew / stale cross-reference, with a staleness-axis overlap guard so it never double-flags 1/3/4, proportionally n/a on a single-version set); + an explicit small-corpus proportionality guard. Additive — the input + `VERDICT` output contracts are unchanged.
- **1.0.0** (2026-06-05) — initial reviewed release (the six-dimension cross-document bar).
