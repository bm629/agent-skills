---
name: reviewing-data-model
description: >
  Use when reviewing/judging a finished data-model document (the persistence/
  domain model — entities, keys, relationships, indexes, normalization,
  lifecycle) to decide if an engineer can build the schema + query it correctly —
  an acceptance gate, not authoring. Judges it against a single-sourced
  9-condition integrity + queryability bar: entities typed + keyed (stored shape,
  not the api-spec DTO); relationships carry cardinality + a referential rule
  (on-delete / embed-vs-reference); every index traces to an access pattern;
  normalization + paradigm choice + tradeoffs; lifecycle + migration; diagram ⇄
  tables in sync; privacy/scale; one-directional vs the api-spec + consistent
  with the shipped schema; amend delta-scoped. Paradigm-aware
  (relational/document/graph/wide-column/key-value — never a relational reflex).
  Emits exactly `VERDICT: approve|revise` — approves a model meeting the bar,
  revises on a named gap. Not for authoring, the api-spec/feature-spec, or generic
  design docs (use design-review).
extensions:
  claude:
    when_to_use: "judging a finished data-model doc (greenfield or an amend) against the integrity + queryability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished data-model doc to review, or the amended model + its change request>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-15
  reviewed: 2026-06-15
---

# `reviewing-data-model` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished data-model document as an acceptance gate — checking an engineer can build the schema and write correct queries from it, then emitting `VERDICT: approve|revise` with actionable findings. Greenfield, or an amend (delta-scoped).

## Overview

This skill is the *review* half of a producing/judging data-model pair. Loaded by a reviewer who holds a **finished data-model document** — the persistence/domain model an engineer implements the schema from and everyone who queries the data reads — it judges that doc against one question: **can an engineer create the schema and write correct queries from it, and are the model's integrity rules + tradeoffs explicit?** It applies a fixed **9-condition integrity + queryability checklist** — the same bar a data-model author produces to (`authoring-data-model`'s `## Output`), so the produce-bar and the review-bar do not drift — then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or rewrite the model; it judges and returns findings, and the producer revises.

The bar is **single-sourced** with the author. The author's *techniques* — the ER notation (Chen / crow's-foot / Mermaid), the conceptual/logical/physical level framing, the normal-form-derivation procedure — are **aids the reviewer judges by OUTCOME** (is every entity typed + keyed? does every relationship carry cardinality + a referential rule? does every index trace to an access pattern?), never conditions to demand. **But note the boundary:** the access-pattern-justified-index discipline (cond-3), referential integrity (cond-2), and the normalization + paradigm reasoning (cond-4) ARE real, load-bearing conditions for a data model — this IS the persistence design, so do NOT under-review them as "implementation detail." What stays an aid is the *technique* (a named notation/level/derivation), not the *outcome* (a typed entity, a justified index, a stated tradeoff).

**Paradigm-aware (load-bearing).** The model may be relational, document/NoSQL, graph, wide-column, or key-value. Judge each in its own idiom: a NoSQL/graph/wide-column model legitimately has **no normal form and no FK** (it uses embed-vs-reference / edges / a partition+clustering key). Demanding a relational idiom of a non-relational model is the cardinal **relational-reflex false-revise** — do not do it.

## When to activate

- A finished data-model doc needs an accept/revise decision before an engineer builds the schema.
- You are the independent reviewer / gate for a data model a producer just authored.
- Re-judging a revised data model after a prior `revise` verdict.
- Reviewing an **amend** — an approved model + a change request — as a delta-scoped review (cond-9).

**Do NOT activate when:**

- Authoring or repairing a data model → use `authoring-data-model`. This skill never writes the model.
- Reviewing the **api-spec** (the wire contract) or the **feature-spec** (what the features do) → those are their own documents with their own gates. The api-spec is a *downstream consumer* that references this model's entities — never an input here.
- Reviewing the **persistence implementation** (ORM/repository) or the executable **DDL/migration code** → this gate judges the *design document*, not code.
- Reviewing a **generic / ad-hoc engineering design doc, RFC, ADR, spec, or plan** → use `design-review`. **This** gate is for the doc-library data-model artifact — identified **authoritatively** by the `template: data-model` frontmatter; a `# Data Model` heading is a fallback signal only when frontmatter is absent.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.

## Workflow

### Step 1: Read the whole model with fresh, independent eyes

Read the data-model doc end to end as if encountering it for the first time. Your stance is a gatekeeper for the *next* step (an engineer building + querying the schema): a finding carries weight only when it shows the schema cannot be **built or queried as designed**. Keep the upstream **feature-spec** (+ architecture-doc store choice) at hand where given — cond-1/cond-8 check the model against the domain. **Detect the paradigm(s) first** (relational / document / graph / wide-column / key-value, possibly polyglot) so you judge each in its own idiom. **The input is the doc itself** — the access-pattern list lives in it (a template section); no separate companion artifact is required. **Is this an amend?** If you were handed a change request / delta against an existing model, run the delta-scoped path (cond-9 active; scope to the changed entities + their migration + ripple). On a greenfield first build no change request is present — cond-9 is n/a.

### Step 2: Run the integrity + queryability checklist — judge each condition

For each condition, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have modeled it differently" is not a gap. The conditions are the single-sourced bar; do not add private ones.

1. **Entities & attributes.** Every entity has typed attributes + a key (primary, or partition+sort for NoSQL); the modeled shape is the **stored** shape, not the api-spec's wire DTO; entities trace to the feature-spec's domain. *Gap* on an untyped attribute, a keyless entity, a DTO modeled as if persisted (computed/flattened fields stored), or an entity serving no domain need. *(Non-collapsing baseline — every entity is typed + keyed at any size.)*
2. **Relationships & referential integrity.** Every relationship states cardinality; an M:N is realized by a junction entity (relational/document; a graph uses an edge); the FK/reference + owning side named; the **on-delete rule** stated (relational) or **embed-vs-reference + the consistency-without-FK strategy** stated (NoSQL/other). *Gap* on a relationship with no cardinality, a bare M:N line (no junction), a missing on-delete rule (relational), or an unbounded embed / FK-less reference with no consistency strategy (NoSQL). *(Collapse: a one-entity store has no relationships. Non-collapsing where a relationship exists: it carries cardinality + a referential rule/strategy.)*
3. **Keys, constraints & access-pattern-justified indexes.** A PK per entity (natural-vs-surrogate stated); uniqueness + check/cross-field constraints explicit; the **access patterns enumerated**; **every index traces to an access pattern** (no unjustified index, no missing-but-needed one). *Gap* on an index with no justifying query, a frequent query with no supporting index, an unstated key choice, or a business-uniqueness rule left unmodeled. *(The signature condition. Collapse: a tiny store may need no secondary index — but the access patterns are still enumerated, and any index present is justified.)*
4. **Normalization & storage paradigm.** The normal form (relational) or embedding/single-table strategy (NoSQL/other) stated; the **paradigm chosen with rationale**; each deliberate denormalization records its read-pattern + tradeoff + consistency strategy. *Gap* on unexplained redundancy causing update anomalies, a denormalized copy with no consistency strategy, an unstated/unjustified store choice, or a paradigm-mismatched model. *(Paradigm-aware: a NoSQL/graph/wide-column model has no normal form — judge its embedding/edge/partition strategy instead; never revise it for "not being normalized.")*
5. **Data lifecycle & migration.** Retention/archival + soft-vs-hard delete where needed; derived data names its source-of-truth + freshness; temporal/audit where history matters; a migration & seeding **plan** (expand-and-contract for a breaking change; backward/forward compatibility where rolling deploys apply). *Gap* on an unbounded-growth entity with no retention, a stored aggregate with no freshness mechanism, an implied in-place rename/drop on a populated table, or no plan to get from empty to running. *(Collapse: a thin/first-draft model has a trivial lifecycle — light is fine.)*
6. **Diagram ⇄ catalog ⇄ tables in sync.** Every entity/relationship in the Mermaid `erDiagram` appears in the entity catalog + the relationship/index lists and vice-versa; no orphan/drift. *Gap* on an element present in one rendering but missing from another. *(Collapse: a one-entity model has a trivial diagram.)*
7. **Cross-cutting data quality.** Sensitive attributes classified (PII/sensitive) + retention/residency where the data warrants; at-rest security for secrets (no plaintext credentials); the model viable at the target scale (no hot partition / unindexed hot query / unbounded row) — addressed where the data warrants. *Gap* on plaintext secrets, PII stored with no classification/retention where the domain clearly handles personal data, or a design that collapses at the stated scale. *(Collapse: no PII → no classification; bounded data → light scale treatment.)*
8. **Grounded, honest & consistent.** Entities/attributes reflect the feature-spec (not invented/boilerplate); assumptions explicit (thin-input → a blocker, not an invented schema); **no fabrication**; **one-directional vs the api-spec** (derived from the feature-spec, the api-spec only a downstream consumer — not reverse-engineered from DTOs); **consistent with the shipped schema** where one exists (claims about what IS stored verified against the real schema/migrations, `file:line`, marked unverified where unconfirmable). *Gap* on an invented entity/constraint/index, the api-spec-inversion, or a documented table/column/index that contradicts the real schema. *(Non-collapsing baselines — no-fabrication + one-directional hold at any size. **Greenfield clause:** a brand-new/proposed/fictional model has no shipped schema to verify against → the consistency check is **N/A**, never a false-revise.)*
9. **(Amend only) delta is well-scoped, classified, ripple-clean, versioned.** When reviewing a change against an existing model: the changed entities meet conditions 1–8 **on what they touched**; the change is **classified additive/breaking** with a migration plan (expand-and-contract for breaking) + a backward/forward compatibility analysis; the **forward/downward ripple** is flagged (the api-spec resources mapping onto changed entities, the impl/test-plan/runbook); the doc version bumped + a changelog present; superseded entities/attributes/indexes marked, not silently deleted. *Gap* on an un-scoped delta, a breaking change mis-classified as additive, an in-place rename/drop with no expand-contract plan, an un-flagged ripple, or a silent deletion. *(Collapse: on a greenfield first build this condition is n/a — do NOT full-re-review an unchanged model, and do NOT demand a changelog on a first draft.)*

**Proportionality.** "Buildable + queryable" scales with the store. A thin store legitimately collapses what it does not need — one entity → no relationships; no M:N → no junction; nothing denormalized → no consistency strategy; no history requirement → no temporal model; first draft → no migration/changelog; no PII → no classification. Judge **completeness of the integrity + queryability decisions**, not word count or template-section presence. A small, complete model that satisfies every *applicable* condition **passes**. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. An engineer can build the schema and write correct queries from it without asking the author; the integrity rules + tradeoffs are explicit. Approve even if you can imagine stylistic improvements; the bar is buildability + queryability, not perfection.
- **revise** — one or more conditions have a real, named gap that blocks building or querying (an untyped attribute, a relationship with no on-delete rule, an unjustified or missing index, a denormalized copy with no consistency strategy, a DTO-inversion, an in-place breaking migration, an un-scoped amend, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes.

A good finding names the gap and the fix:

> **revise** — Relationships & referential integrity (cond. 2), §3: the `Order`→`Customer` relationship shows a line but no on-delete rule. Fix: state `ON DELETE RESTRICT` (you cannot delete a customer with existing orders), so the integrity semantics are not left for the engineer to invent.

A bad finding is vague and unactionable:

> The relationships section could be tightened up. *(Which relationship? Why does it fail the bar? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not rewrite, fix, or fill in the model. The producer revises.
- **Single-sourced bar.** Judge against the nine conditions in Step 2 — the same bar the author (`authoring-data-model`'s `## Output`) produces to. Do not invent extra conditions or apply a stricter private standard.
- **Aids are judged by outcome, never demanded.** The ER notation, the conceptual/logical/physical levels, the normal-form-derivation procedure are the author's *techniques* — judge whether the entity is typed / the relationship carries a referential rule / the index is justified, NEVER "you didn't use crow's-foot / draw a conceptual model / show the FD derivation." (Access-pattern-indexes / referential-integrity / normalization OUTCOMES are real conditions cond-2/3/4 — only the techniques are aids.)
- **Paradigm-aware — no relational reflex.** Never revise a NoSQL/graph/wide-column model for lacking a normal form or an FK; judge its embed-vs-reference / edge / partition strategy instead. This is the cardinal drift this gate guards against.
- **No false-revise.** A model that meets every applicable condition is approved, even a thin one for a small store. Revise only on a real, named gap. A thin store legitimately omits relationships, denormalization, temporal history, a migration, a changelog.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A blocking gap is a `revise`.
- **Every index traces to an access pattern (cond. 3).** An unjustified index is a real gap (write-amplification + storage), not a style nit; a missing index for a hot query is a real gap.
- **Judge against the upstreams the document was given.** Assess the model against its `depends_on` set + the docs it references. A **not-produced / not-handed-in** upstream (e.g. an absent feature-spec) is **never** a revise trigger. A model that **ignored a produced upstream** it should have traced to **is** a fair finding.
- **Amend is delta-scoped.** When handed a change against an existing model, review the delta + its migration + ripple (cond-9) — do NOT full-re-review the unchanged model, and do NOT demand a changelog on a greenfield first draft.
- **Greenfield consistency is N/A, not a gap.** When there is no shipped schema to verify against (a new/proposed/fictional model), mark cond-8's consistency check N/A — absence of code to verify is never itself a blocker.
- **Every revise finding is actionable** — failed condition + location + concrete fix.

**Preferences (override-able):**

- Order findings by severity — blocking gaps first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of buildability.** Every section can be present and the schema still un-buildable (an untyped attribute, a relationship with no on-delete, an unjustified index that will slow writes). Judge whether the *schema can be built + queried*, not whether the *template is filled*.
- **The relational reflex.** Demanding 3NF or an FK of a document/graph/wide-column model is the dominant drift — a NoSQL model is correct with embed-vs-reference + access-pattern-first; a graph with edges; a wide-column with a partition+clustering key. Judge the paradigm's own idiom.
- **The unjustified index waved through.** A model that lists indexes looks thorough — but an index with no access pattern behind it is dead weight (cond. 3); tie each to a query or it is a gap.
- **The DTO-inversion.** A model reverse-engineered from api-spec response shapes (computed/flattened fields stored as if persisted) inverts the dependency and conflates wire DTO with stored entity (cond. 1/8).
- **The silent staleness.** A stored derived value (a cached count, a denormalized copy) with no stated source-of-truth + freshness mechanism is a latent bug (cond. 5).
- **Inventing conditions (the cardinal drift).** Adding a private requirement the bar does not carry ("you must use crow's-foot / normalize to BCNF / draw a conceptual ERD") drifts the review-bar off the produce-bar. The techniques are judged by outcome only.
- **Systematic over-flagging (false-revise).** A reviewer asked to find problems tends to over-correct. A condition is a gap only on a *named, real* deficiency, not a decision you'd have made differently.
- **Confusing this with the api-spec or design-review.** A data model is judged for *whether the schema is buildable + queryable* — distinct from the api-spec (the wire contract, a downstream consumer) and from `design-review` (which gates generic design docs/RFCs/ADRs/specs/plans). This gate is the doc-library data-model artifact's dedicated reviewer.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming and approving to avoid a revise loop — an unjustified index or a missing on-delete rule waved through becomes a slow query or a data-integrity bug.
- **Nit-pick revise.** Blocking on naming, notation, or nice-to-haves dressed up as gaps. Revise is for real buildability/queryability blockers only.
- **Relational-reflex revise.** Revising a NoSQL/graph/wide-column model for not being normalized or lacking FKs — the dominant data-model-specific drift.
- **Silent rewrite.** "It was easier to just fix the model" — authoring inside a review collapses the produce/judge separation.
- **Inventing conditions.** Adding a requirement the bar does not carry (a named notation/normal-form/derivation) — judged by outcome only.
- **Full-re-reviewing an amend.** Re-judging the whole unchanged model on a small delta — review the delta + its migration + ripple (cond. 9), proportionally.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one data-model doc:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the model for schema implementation; `revise` returns the findings to the producer for a bounded revision pass. **Medium:** the artifact judged is a **textual-markdown** data model today; the bar is medium-independent.

## Related

- **`authoring-data-model`** — the produce half of the pair; it writes the model to the same nine-condition bar this skill judges against (`## Output`). Pairing them single-sources the bar so produce and review do not drift.
- An **api-spec** (where it exists) — a *downstream consumer* whose resources map onto this model's entities (one-directional); cond-1/cond-8 check the model is the stored shape, not the DTO, and was not reverse-engineered from the api-spec.
- The upstream **feature-spec** (+ architecture-doc store choice) — the domain this model persists; cond-1/cond-8 trace to it (judged only when handed in).
- A **`design-review`** skill — the gate for *generic* engineering design docs, RFCs, ADRs, specs, and plans (it verifies claims against the codebase). This skill is the dedicated reviewer for the doc-library **data-model** artifact; `design-review` carves that artifact out.
- A **data-model template / content-template** tool — owns the section *structure*; this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/data-model-quality-bar.md` — the nine checklist conditions expanded with per-condition pass/gap signals and worked finding examples (the typed-keyed check, the cardinality+referential-rule check, the access-pattern-justified-index test, the paradigm-aware normalization check, the lifecycle/migration signals, the diagram-sync check, the cross-cutting privacy/security/scale signals, the grounded/one-directional/consistency signals, and the delta-scoped-amend signals). Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method (ER/normalization theory, NoSQL access-pattern design, index justification, expand-and-contract migration, schema-evolution compatibility, data classification).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap); combined `description` + `when_to_use` truncated at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.

## Changelog

- **1.0.0** (2026-06-15) — initial release. Net-new reviewer forged by adapting the canonical sibling `reviewing-technical-design`; the nine-condition integrity + queryability bar single-sourced 1:1 with `authoring-data-model`'s `## Output`; paradigm-aware (no relational reflex); inherits the `VERDICT: approve|revise` contract, judge-against-given-upstreams, the consistency-with-shipped-schema verify-against-code discipline + greenfield clause, and the proportionality / no-false-revise / inventing-conditions anti-patterns.
