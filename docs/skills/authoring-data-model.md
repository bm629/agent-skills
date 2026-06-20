# authoring-data-model

Author a **data model document** — the persistence/domain model of a system's stored data: the entities + typed attributes, relationships + cardinality, keys + uniqueness, constraints + validation, indexes, normalization/denormalization decisions, the storage choice + rationale, and the data lifecycle (retention, derived data, migration/seeding plan). The how-to (a data-modeling method + an integrity/queryability bar), composed with a separate data-model template tool and a deep-research capability; targets a textual markdown artifact (a Mermaid ER diagram + per-entity attribute/constraint spec tables + index/relationship lists, or document shapes for NoSQL).

## Purpose

A data model is read by the engineers who implement persistence and by everyone who queries the data. This skill carries the producer's judgment — not the section list — guiding a producer to derive entities from the feature-spec's nouns + the access patterns, detect the storage paradigm and model in it (relational ER + tables + normalization, or document/NoSQL access-pattern-first), make integrity rules explicit (keys, constraints, cardinality + referential rule), and justify each index by an access pattern. The bar to clear: an engineer can create the schema and write correct queries from it, and the model's integrity rules + tradeoffs are explicit.

## When to activate

- Authoring or substantially revising a data model / schema design document for a system or feature, given an upstream feature-spec (and an architecture-doc naming the stores, where present).
- The producer needs the method (how to derive entities, model relationships, justify indexes, state tradeoffs) and the bar a buildable, queryable model must meet — not a blank page.

### When NOT to activate

- **The API wire contract** (operations + request/response DTOs) → `authoring-api-spec`; it *references* this model's entities downstream (one-directional), it does not redefine them.
- **The persistence implementation** (ORM/repository/access-layer) → `authoring-technical-design`; the data-store topology → `authoring-architecture-doc`.
- **The executable DDL / migration scripts** → this is the design document (entities, constraints, migration *plan*), not the code.
- **Reviewing a finished data model** → `reviewing-data-model` (its dedicated twin; a finished data-model artifact routes there, NOT to the generic `design-review`, which carves it out).

## Workflow

Take the section structure from the data-model template tool (don't invent an outline). Load the upstream feature-spec (the data the features manipulate) and the architecture-doc (the chosen stores) where present — never a blank page. Detect the storage paradigm per store and pick the track: relational/SQL (entities → tables; ER diagram + spec tables; keys + referential integrity; normalize then denormalize deliberately), document/NoSQL (access-pattern-first; collections + document shapes; embedding vs referencing; single-table design), or another paradigm in its own idiom — **graph** (typed/directed edges, traversal access patterns), **wide-column** (partition + clustering key, design-for-the-read), **key-value** (access by key; the value shape + key scheme). Enumerate the access patterns first, then model: derive entities from the feature-spec's nouns with every attribute typed; give every relationship its cardinality, the realizing key/reference, the owning side, and the referential rule; make keys, uniqueness, and constraints explicit. Justify each index by an access pattern; state the normalization form and record every deliberate denormalization with its tradeoff + consistency strategy; address the data lifecycle (retention, derived data with its source of truth, temporal/audit where history matters, data privacy/classification, the migration/seeding plan). Surface unknowns as explicit assumptions; self-check against the integrity/queryability bar before handoff. On an **amend** (a schema-change delta), edit-not-redraw: amend only the touched entities/relationships/constraints/indexes in place, classify the change additive vs breaking (a breaking change on a populated store runs as expand-and-contract, never an in-place rewrite) with a backward/forward compatibility analysis, mark superseded items deprecated, version + changelog, and flag the forward/downward ripple to the api-spec/impl/test-plan.

## Output

A data model document meeting the **integrity + queryability bar** (every entity typed + keyed; every relationship with cardinality + referential rule; constraints + uniqueness explicit; each index justified by an access pattern; storage choice + normalization tradeoffs stated; ER diagram + tables in sync; data lifecycle + cross-cutting data quality addressed; grounded-not-boilerplate; usable downstream; delta-scoped on an amend). Paradigm-aware (relational, document/NoSQL, graph, wide-column, key-value — the same rigor, only the artifact adapts). Textual markdown — the method and bar are medium-independent. Structure from the template; this skill supplies the content quality. The same ten-condition bar the `reviewing-data-model` gate asserts.

## Key guarantees

- **Composes, not duplicates** — defers structure to the template tool; supplies method + judgment.
- **Paradigm-aware** — the same modeling rigor applies to relational/SQL, document/NoSQL, graph, wide-column, and key-value stores; only the artifact adapts (ER + tables vs access-pattern-first collections vs the paradigm's own idiom).
- **Integrity explicit** — every entity typed + keyed, every relationship with cardinality + referential rule, every index traced to an access pattern.
- **One-directional vs the api-spec** — this is the stored schema; the api-spec is a downstream consumer that references these entities, never an input (no circular dependency); the stored entity is not the wire DTO.
- **Amends by migration** — on a schema-change delta, edits the touched entities in place, classifies additive/breaking (expand-and-contract for a breaking change), versions, and flags the forward/downward ripple.
- **Single-sourced bar** — shared with the dedicated `reviewing-data-model` twin (the ten-condition gate), so produce and review don't drift.
- **capability-record-aware** — when a `capability_record` is injected by the caller, scope boundaries for `owns` entities, `refs` tables, and event outboxes are drawn from it; graceful fallback when absent.

## License

MIT © 2026 Bhushan Modi.
