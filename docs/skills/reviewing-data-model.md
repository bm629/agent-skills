# reviewing-data-model

Judge a **finished data-model document** — the persistence/domain model (entities, keys, relationships, indexes, normalization, lifecycle) — and decide whether an engineer can build the schema and query it correctly — an acceptance gate, not authoring. The review half of the data-model pair; it single-sources its bar from the same conditions as `authoring-data-model`, and is **paradigm-aware** (relational / document / graph / wide-column / key-value, never a relational reflex).

## Purpose

A data model is the persistence design an engineer implements the schema from and everyone who queries the data reads. Before that happens, something has to decide whether the schema can be built and queried correctly, and whether its integrity rules + tradeoffs are explicit. This skill is that gate: it judges the model against an **integrity + queryability bar** and emits a machine-parseable verdict. The author's *techniques* (the ER notation, the conceptual/logical/physical levels, the normal-form derivation) are judged by **outcome** — but access-pattern-justified indexes, referential integrity, and the normalization/paradigm reasoning are real load-bearing conditions: this IS the persistence design.

## When to activate

- ✅ A finished data-model doc needs an accept/revise decision before an engineer builds the schema.
- ✅ You are the independent reviewer / gate for a data model a producer just authored.
- ✅ Re-judging a revised model after a prior `revise`, or reviewing an **amend** as a delta-scoped review.

### When NOT to activate

- **Authoring or repairing a data model** → `authoring-data-model`.
- **Reviewing the api-spec** (the wire contract — a downstream consumer that references this model) or the **feature-spec** → those are their own documents with their own gates.
- **Reviewing the persistence implementation** (ORM/repository) or the executable DDL/migration code → this gate judges the *design document*, not code.
- **A generic / ad-hoc design doc, RFC, ADR, spec, or plan** → `design-review`. This gate is for the doc-library data-model artifact (authoritatively the `template: data-model` frontmatter; a `# Data Model` heading is a fallback only when frontmatter is absent).
- **Template/section conformance** → a template concern.

## The bar (10 conditions)

Detect the paradigm(s) first, then judge each in its own idiom, pass/gap, proportional to the store: (1) **entities & attributes** — every entity typed + keyed, the *stored* shape (not the api-spec DTO), traced to the domain; (2) **relationships & referential integrity** — cardinality stated, M:N via a junction/edge, the on-delete rule (relational) or embed-vs-reference + consistency strategy (NoSQL); (3) **keys, constraints & access-pattern-justified indexes** (signature) — access patterns enumerated, every index traces to one, no unjustified or missing-but-needed index; (4) **normalization & storage paradigm** — the normal form / embedding strategy + the paradigm chosen with rationale, each denormalization recording its tradeoff + consistency strategy; (5) **data lifecycle & migration** — retention, soft-vs-hard delete, derived-data freshness, an expand-and-contract migration plan; (6) **diagram ⇄ catalog ⇄ tables in sync**; (7) **cross-cutting data quality** — PII classification, at-rest security (no plaintext secrets), viable at the target scale; (8) **grounded, honest & consistent** — no fabrication, one-directional vs the api-spec, consistent with the shipped schema (`file:line`; greenfield clause — N/A when no schema exists); (9) **(amend only) delta well-scoped, classified, ripple-clean, versioned** (n/a greenfield). A NoSQL/graph/wide-column model legitimately has no normal form and no FK — never revise it for that.

## Output

Exactly `VERDICT: approve` or `VERDICT: revise` on its own line, plus findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it**. On `approve`, findings are optional non-blocking notes. **Approves** a model an engineer can build + query (no false-revise on a thin store); **revises** only on a real, named integrity/queryability gap.

## Key guarantees

- **Gate, not author** — judges and returns findings; never rewrites the model.
- **Single-sourced bar** — the same 10 conditions the author produces to; no private stricter standard.
- **Paradigm-aware, no relational reflex** — never revises a NoSQL/graph/wide-column model for lacking a normal form or an FK; judges its embed-vs-reference / edge / partition strategy. The cardinal drift this gate guards against.
- **Every index traces to an access pattern** — an unjustified index is a real gap (write-amplification), and a missing index for a hot query is a real gap.
- **One-directional vs the api-spec** — the model derives from the feature-spec; the api-spec is a downstream consumer, never reverse-engineered into the model.
- **Greenfield consistency is N/A, not a gap** — absence of a shipped schema to verify is never itself a blocker.
- **capability-record-aware** — when a `capability_record` is injected by the authoring caller, judgment includes a capability-boundary condition (`owns`/`refs`/event tables); n/a when no record was injected.
- **Machine-parseable verdict** — the exact `VERDICT:` line a loop can read.

## License

MIT © 2026 Bhushan Modi.
