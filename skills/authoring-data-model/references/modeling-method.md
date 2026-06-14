# Modeling method — per-paradigm idioms + integrity depth

> Depth for `authoring-data-model`. The SKILL.md body carries the method + the nine-condition bar; this file carries the per-paradigm idioms and the integrity/queryability depth. Load when modeling a specific paradigm or resolving a borderline decision.

## Entities & attributes (every paradigm)

- **Derive entities from the feature-spec's nouns + the access patterns**, not from a blank page and never (the cardinal inversion) from the api-spec's wire DTOs. Three model *levels* are an authoring aid, not three deliverables: conceptual (entities + relationships, technology-free) → logical (fully attributed + keyed, paradigm-neutral) → physical (the concrete tables/collections + types + indexes for the chosen engine).
- **Type every attribute** with a concrete domain type (`string(255)`, `integer`, `decimal(12,2)`, `timestamptz`, `uuid`, `enum{…}`, `jsonb`). Mark **required/optional** (NOT NULL vs nullable — a semantic choice: absent vs unknown vs not-applicable). Record **defaults** + **value constraints/domain** (range, enum, format, length) where they matter — these become CHECK/domain constraints (relational) or app-enforced invariants (NoSQL).
- **Persistence entity ≠ wire DTO.** Model the *stored* shape. The api-spec's DTOs frequently differ (computed fields, omitted internals, flattened joins, denormalized read copies). Worked gap: an entity `OrderSummary` storing `line_item_count` + `formatted_total` is a response projection — model `Order` + `LineItem` and let the api-spec compute the summary.

## Relationships & referential integrity

Every relationship states four things or it is not buildable: **cardinality** · the **FK/reference** realizing it · which side **owns** the lifecycle · the **referential rule**.

- **Cardinality** — 1:1 / 1:M / M:N (crow's-foot: a min/max pair per end; the three-prong = many, the bar = one, the circle = zero/optional).
- **M:N → a junction/associative entity** holding the two FKs (often with its own attributes — `enrolled_at`, `role`, `quantity`); decide its PK (composite vs surrogate). A bare M:N line is not implementable relationally.
- **On-delete rule** (relational) — `RESTRICT`/`NO ACTION` (protect a referenced parent), `CASCADE` (child follows parent), `SET NULL` (orphan, FK nullable), `SET DEFAULT`. The choice encodes a domain rule (can't delete a customer with open orders → RESTRICT; delete an order → delete its lines → CASCADE). A relationship with no on-delete rule is a defect.
- **NoSQL embed-vs-reference** — embed (read-together, bounded, owned — e.g. order lines inside an order) vs reference (unbounded or shared — e.g. a user referenced by many orders), plus **how referential consistency is held without DB FKs** (application-enforced, transactional writes where supported, eventual reconciliation). Don't embed an unbounded collection (document-size blowup) or reference everything (relational reflex → multi-round-trip reads).

## Keys, constraints & access-pattern-justified indexes (the signature discipline)

Enumerate the access patterns **first**; let them justify every index (relational) or determine the schema (NoSQL); key + constrain every entity explicitly.

- **Primary key** — a PK per entity. Prefer a **surrogate** (uuid/auto-increment) unless a natural key is stable + meaningful + immutable; state the choice + reason. Composite PK where identity is genuinely multi-column. NoSQL: the partition+sort key.
- **Constraints explicit, not implied** — uniqueness incl. multi-column (`UNIQUE(tenant_id, slug)`); CHECK/domain; cross-field invariants (`end_date ≥ start_date`); NOT NULL.
- **Access patterns enumerated first** — each pattern: the entity, the filter/sort, expected cardinality + frequency. For NoSQL this is non-collapsing (the schema is derived from the patterns — query-driven modeling).
- **Every index → an access pattern** — the columns in WHERE/JOIN/ORDER BY + the FKs those queries hit; covering/partial/composite where the pattern warrants. **Over-indexing is a real cost** (each index slows writes + bloats storage), so an index with no justifying query is **removed**, and a frequent query with no supporting index is a **gap**.

## Paradigm idioms

- **Relational** — entities → tables; ER + per-attribute spec tables; PK/FK + referential integrity; normalize then denormalize deliberately.
- **Document/NoSQL** — access-pattern-first; collections + document shapes; embed-vs-reference; **single-table design** overloads a generic `PK`/`SK` across entity types into item collections, with a GSI/LSI only for a pattern the base key can't serve; avoid a hot (low-cardinality) partition key.
- **Graph** — nodes (entities) + first-class typed/directed **edges** (relationships, with edge properties); the access patterns are **traversals** (friends-of-friends, shortest-path); do NOT force a relational junction table — the edge *is* the relationship.
- **Wide-column** — a partition key + clustering key for wide, append-heavy rows; one table per query (denormalize freely), TTL-based retention, no joins; design for the read.
- **Key-value** — access strictly by key; model the value shape + the key scheme (composite keys, prefixes).

## Normalization & storage paradigm

- **Normal form** (relational) — functional-dependency-driven: 1NF (atomic values) · 2NF (no partial-key dependency) · 3NF (no transitive dependency) · BCNF (every determinant a superkey). Typically target 3NF/BCNF, then denormalize deliberately.
- **Each deliberate denormalization** records the read pattern it serves, the **write-cost/staleness tradeoff** accepted, and **how the redundant copy is kept consistent** (trigger, app write-both, recompute, materialized view). Worked: `Order.customer_name` duplicating `Customer.name` must state the read pattern (order list without a join), the staleness window, and the keep-current mechanism.
- **Storage paradigm chosen with rationale** — relational (rich relationships, ad-hoc queries, transactions) / document (aggregate-oriented, access-bounded) / key-value (lookup, cache) / wide-column (high write, time-series) / graph (traversal-heavy). Polyglot persistence (>1 store) is legitimate — model each in its own track + state the cross-store consistency boundary. Name the **consistency model** (strong vs eventual) where it bites.

## Data privacy & classification

- Classify sensitive attributes (`PII` / `sensitive` / `internal` / `public`) — the data-model template's §2 classification column. Key **retention + residency** to the classification; apply **data-minimization** (store only what's needed).
- **Security at the data layer** — encryption at rest, column/field-level protection (hash+salt passwords, tokenize cards — never plaintext credentials), access scope (row-level/tenant isolation) where the data warrants.

## Diagram ⇄ catalog ⇄ tables sync

The three renderings — the Mermaid `erDiagram`, the entity catalog (attribute spec tables), and the relationship/index lists — must agree. An element in one but missing from another is a drift finding and signals an incomplete edit.
