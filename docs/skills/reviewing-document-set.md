# reviewing-document-set

Judge a **set of finished project documents as one corpus** and decide whether they are mutually coherent and ready to plan from — the corpus-level analog of a single-document design review. It assumes each document already passed its own gate and judges only how the documents relate.

## Purpose

A single-document review checks one document against its own bar. But a project ships a *set* of documents (idea → PRD → feature spec → architecture → data model → …), and the set can be incoherent even when every document is individually fine — they disagree on a decision, name the same thing three different ways, or quietly drop a requirement. This skill is the gate that runs *after* the per-document reviews: it judges cross-document coherence and emits a single machine-parseable verdict, so a produce → review → reconcile loop can run over the whole corpus.

## When to activate

- ✅ A finished set of related project documents needs an accept/revise decision on mutual coherence before downstream planning.
- ✅ The corpus-level review step after each document has passed its own per-type gate.
- ✅ Re-judging a corpus after fixes from a prior `revise`.

### When NOT to activate

- **Judging a single document's internal quality** → the matching per-document reviewer (e.g. `design-review`, `reviewing-prd`).
- **Authoring or fixing a document** → its authoring skill (the producer revises on the findings).
- **A single document** → there are no cross-document relationships to judge.

## The bar (six dimensions)

Judges the handed-in set across: (1) **cross-document consistency** — same fact/decision/scope, and one name per entity (members vs accounts), everywhere; (2) **completeness & traceability** anchored on the upstream-most document — every requirement carried downstream, no dropped/orphaned items or TBDs; (3) **contradiction detection** — no two documents assert what cannot both be true; (4) **dependency integrity** — each document faithfully elaborates its declared upstreams; (5) **no divergent duplication** — one source of truth, not drifting copies; (6) **ready-to-plan** — the corpus is sufficient and coherent to derive milestones from.

## Output

Exactly **one terminal** `VERDICT: approve|revise` for the whole corpus, plus findings where **each line begins with the affected document id(s) in brackets** — e.g. `- [d-prd, d-arch] auth model differs (PRD: OAuth, arch: SAML) — align both` — so a caller can route one fix per affected document. **Approves** a coherent corpus (no false-revise) and **revises** only on a real, named cross-document gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never edits a document.
- **Cross-document only** — never re-litigates a single document's internal quality (that ran earlier).
- **One verdict, per-document attribution** — a single corpus verdict; the bracketed ids make each finding actionable per document.
- **No false-revise** — approves a coherent set even if individual documents are stylistically improvable.

## License

MIT © 2026 Bhushan Modi.
