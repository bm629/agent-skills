---
name: authoring-data-model
description: >
  Use when authoring a data model document — the persistence/domain model of
  stored data: typed entities, relationships + cardinality, keys/constraints,
  indexes, normalization, the storage choice, and lifecycle. Guides the producer
  through the METHOD, not the outline: deriving
  entities from the feature-spec's nouns + access patterns, detecting the
  paradigm and modeling in it (relational, document/NoSQL access-pattern-first,
  graph, wide-column, key-value), making integrity rules explicit (keys,
  constraints, cardinality + referential rule), justifying each index by an
  access pattern, and amending an approved model as a versioned, migration-
  planned delta — so an engineer can build + query the schema. Composes with a
  data-model template tool + a deep-research capability. Assumes the upstream
  feature-spec (+ architecture-doc) — never a blank page. Not the API wire
  contract (the api-spec references these entities downstream, one-directional),
  not the implementation/DDL, and not reviewing a finished data model.
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.2.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-15
---

# authoring-data-model — SKILL.md

> **Variant:** standard · **When to use:** authoring a data model document. This skill supplies the producer METHOD and the integrity/queryability BAR; the section STRUCTURE comes from a separate data-model template tool you compose with. Do not restate that template's outline here.

## Overview

A data model document is the **persistence/domain model** of a system's stored data — the design an engineer implements the schema from and everyone who queries the data reads. This skill guides a producer to author one: deriving entities from the upstream feature-spec, detecting the storage paradigm and modeling in it, making integrity rules explicit, and justifying every index by an access pattern. It teaches the *how-to* — the research method and the quality bar — and composes with a separate template tool that supplies the section structure. The bar is "an engineer can create the schema and write correct queries from it, and the model's integrity rules + tradeoffs are explicit."

It is paradigm-aware: the same modeling rigor (entities, relationships, integrity, justified indexes, stated tradeoffs) applies to **relational/SQL**, **document/NoSQL**, **graph**, **wide-column**, and **key-value** stores; only the artifact adapts. Relational + document are the two detailed tracks below; the others are modeled in their own idioms (Step 2).

## When to activate

- Authoring or substantially revising a data model / schema design document for a system or feature, given an upstream feature-spec (and an architecture-doc naming the stores, where present).
- The producer needs the method (how to derive entities, model relationships, justify indexes, state tradeoffs) and the bar a buildable, queryable model must meet — not a blank page.

**Do NOT activate when:**

- Reviewing/judging a finished data model — that is a runtime review gate, not authoring.
- Authoring the **API wire contract** (operations + request/response DTOs) — that is the api-spec; it *references* this model's entities (downstream, one-directional), it does not redefine them.
- Designing the **persistence implementation** (ORM/repository/access-layer) — that is a technical-design doc; the system's data-store topology is an architecture doc.
- Producing the executable **DDL / migration scripts** — this is the design document (entities, constraints, migration *plan*), not the code.
- Authoring a different document type.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

> The section structure comes from the data-model template tool you compose with. The steps below are the METHOD that fills it — apply them to whatever sections that template carries; never restate its outline.

### Step 1: Get the structure + ground the inputs

Obtain the data-model template's section set from the template tool. Read the upstream **feature-spec** (the data the features manipulate) and, where present, the **architecture-doc** (the chosen stores). You are elaborating these — never starting blank. Ground modeling decisions in established practice (ER modeling, normalization theory, the chosen paradigm's idioms) via a research capability rather than inventing.

### Step 2: Detect the paradigm and pick the track

From the architecture-doc / chosen store, decide the paradigm per store (a system may use more than one — model each in its own track). Apply the same rigor either way; the artifact differs:

- **Relational/SQL** — entities map to tables; ER diagram + per-attribute spec tables; primary/foreign keys + referential integrity; normalize, then denormalize deliberately.
- **Document/NoSQL** — **access-pattern-first** (model from the query list, not the entities, because ad-hoc query flexibility is limited); collections + document shapes; embedding vs referencing; co-locate entities read together; **single-table design** — overload a generic partition+sort key across entity types into item collections, add a GSI/LSI only for an access pattern the base key can't serve, avoid a hot (low-cardinality) partition key.
- **Other paradigms (model in their idioms, proportional — not full tracks):** **graph** — entities are nodes, relationships are first-class typed/directed edges (with edge properties), and the access patterns are traversals (e.g. friends-of-friends); do NOT force a relational junction table. **Wide-column** — a partition key + clustering key for wide, append-heavy rows; design for the read, denormalize freely, TTL-based retention, no joins. **Key-value** — access strictly by key; model the value shape + the key scheme. The cross-cutting rules (typed entities, a key per entity, every index/secondary structure justified by an access pattern, stated tradeoffs, lifecycle) hold in every paradigm; `references/modeling-method.md` carries the per-paradigm idioms.

### Step 3: Enumerate access patterns, then model

List the reads/writes the system must serve against this data first. For relational they justify the indexes; for NoSQL they *determine the schema*. Then:

- **Entities** — derive from the feature-spec's **nouns**. Type every attribute; mark required/optional; give defaults where they exist; record value constraints. Keep the persistence entity distinct from the api-spec's wire DTO — they often differ; model the stored shape, not the DTO.
- **Relationships** — every one states its **cardinality** (1:1 / 1:M / M:N), the foreign key or reference realizing it, which side **owns** the lifecycle, and the **referential rule** (on-delete: restrict/cascade/set-null — or, for NoSQL, embed-vs-reference and how referential consistency is held without DB-enforced FKs). Keep the ER diagram and the relationship list in sync with the entity catalog.
- **Keys + constraints** — a primary key per entity (natural vs surrogate, with the reason; for NoSQL the partition+sort key and any overloaded-key strategy); uniqueness (incl. multi-column); check/domain constraints; cross-field invariants. Explicit, not implied.

### Step 4: Justify indexes, state tradeoffs, address lifecycle

- **Indexes** — each one traces to an access pattern from Step 3 (the columns in WHERE/JOIN/ORDER BY and the foreign keys those queries hit). An index with no justifying access pattern is removed; over-indexing bloats storage and slows writes.
- **Normalization/denormalization** — state the form (relational: typically 3NF/BCNF) or the NoSQL embedding strategy, and record **every deliberate denormalization** with the read pattern it serves, the write-cost/staleness tradeoff accepted, and how the redundant copy is kept consistent. The core tradeoff: normalization favors write efficiency + integrity; denormalization favors read performance.
- **Data lifecycle** — retention/archival per entity (soft vs hard delete, with the query/uniqueness consequence of a tombstone); any stored derived/computed value with its source of truth and how it stays current; **temporal/audit/versioning** where history matters (effective-dated rows, an audit/append-only log, a slowly-changing-dimension strategy, row versioning for optimistic concurrency).
- **Data privacy & classification** — classify sensitive attributes (`PII` / `sensitive` / `internal` / `public`), key retention + residency to that classification, and apply data-minimization (store only what's needed); protect secrets at the data layer (hash+salt passwords, tokenize cards — never plaintext). See `references/modeling-method.md`.
- **Migration & schema evolution** — the migration/seeding *plan* (how the schema is created and evolved, backfill, seed data) — the plan, not the DDL. Classify a change **additive** (backward-compatible) vs **breaking**; run a breaking change on a populated store as **expand-and-contract** (expand → backfill → transition reads → contract — never rename/remove in place), and state the **backward/forward compatibility** stance under rolling deploys. Depth + the amend procedure live in `references/lifecycle-and-amend.md`.

### Step 5: Surface gaps, then self-check against the bar

Record unknowns as **explicit assumptions/open-questions** — never invent. Then verify the document against the quality bar in `## Output` before handing off. Express everything **textually** (a Mermaid `erDiagram`, attribute/constraint spec tables, index/relationship lists, and a fenced document-shape example for NoSQL) — the method and bar are independent of the medium.

### Step 6: Amending an approved model (a schema-change delta)

When the input is a change request against an approved model (a new entity/attribute, a relationship/cardinality change, a denormalization, a key change), **edit-not-redraw**: amend only the touched entities + their relationships/constraints/indexes, in place. The migration **is** the amend mechanism — two data-model-specific properties:

- **Classify + migrate.** Classify the change **additive** (a new nullable column / table / index — backward-compatible) vs **breaking** (a dropped/renamed/narrowed column, a cardinality change, a key change); plan a breaking change as **expand-and-contract** (never an in-place rewrite) with a backward/forward compatibility analysis. Mark superseded entities/attributes/indexes as deprecated — never silently delete — and bump the doc version + changelog.
- **Forward/downward ripple.** A schema change ripples to the **downstream api-spec** (whose resources map onto changed entities), the impl/test-plan touching the schema, and any migration/runbook; the upstream feature-spec is amended first (spec→plan→impl order). Flag the ripple — don't silently break a downstream reader.

Full procedure in `references/lifecycle-and-amend.md`. On a greenfield first build this step is n/a.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** Take the section structure from the template tool; this skill supplies the method + bar. Never restate the template's outline in the produced doc or reason as if this skill owns the structure.
- **Every entity is typed and keyed; every relationship carries cardinality + the referential rule.** No untyped attribute, keyless entity, or relationship missing cardinality/referential behavior ships.
- **Every index traces to an access pattern.** No unjustified index; no missing-but-needed index.
- **Ground in the feature-spec (+ architecture-doc), never a blank page.** Entities and attributes reflect the real domain; gaps are surfaced as assumptions, not invented.
- **Persistence model, one-directional vs the api-spec.** This is the stored schema. The api-spec is a *downstream* consumer that references these entities — it is never an input here (treating it as one would create a circular dependency). The stored entity is not the wire DTO.

**Preferences (override-able):**

- Size proportionally: "comprehensive" sets ambition; a thin store collapses sections it does not need. The bar is integrity + queryability completeness + access-pattern coverage, not word count.
- Prefer a surrogate primary key unless a natural key is stable and meaningful; state the choice either way.

## Gotchas

- **Relational-only reflex on a NoSQL store.** Defaulting to tables + 3NF when the store is document/NoSQL produces an unusable model. Detect the paradigm first (Step 2) and model access-pattern-first for NoSQL.
- **Indexes added "to be safe."** An index with no access pattern behind it is dead weight — it slows writes and bloats storage. Tie each to a Step 3 query or drop it.
- **Relationship lines with no cardinality or on-delete rule.** An ER diagram that shows a line but not 1:M/M:N and not what happens on delete is not buildable. Every relationship needs both.
- **Modeling the wire DTO instead of the stored entity.** The api-spec's request/response shapes often differ from what is stored (computed fields, omitted internals, flattened joins). Model the persistence shape; let the api-spec map onto it.
- **ER diagram and tables drifting apart.** An entity or relationship present in one but absent in the other breaks the reader. Keep the Mermaid diagram, the entity catalog, and the relationship list in sync.
- **Emitting DDL/migration code.** The deliverable is the design (entities + constraints + migration *plan*), not executable schema scripts.

## Anti-patterns

- **"The api-spec already lists the fields, so I'll model from it."** That inverts the dependency and conflates wire DTO with stored entity. Model from the feature-spec; the api-spec references this model, not the reverse.
- **"I'll normalize everything to BCNF and stop."** Normal form is a starting point, not the goal — name the deliberate denormalizations the access patterns require, with their tradeoffs.
- **"I'll restate the template's sections so the doc looks complete."** Duplicating the outline is not authoring — supply the method-filled content the structure asks for.
- **"The store is obvious, no need to justify it."** State the storage choice and paradigm with the rationale (data shape, consistency, scale, access patterns) — a downstream reader cannot infer it.

## Output

A data model **document** (textual markdown) that meets this integrity + queryability bar. These **nine conditions are single-sourced with the `reviewing-data-model` gate** — its checklist IS this list, so produce-bar and review-bar do not drift. Self-check against them before handing off:

1. **Entities & attributes** — every entity has typed attributes + a key (primary, or partition+sort for NoSQL); the modeled shape is the **stored** shape, not the api-spec's wire DTO; entities trace to the feature-spec's domain.
2. **Relationships & referential integrity** — every relationship states cardinality; an M:N is realized by a junction entity (relational/document; a graph uses an edge); the FK/reference + owning side named; the **on-delete rule** stated (relational) or **embed-vs-reference + the consistency-without-FK strategy** stated (NoSQL/other).
3. **Keys, constraints & access-pattern-justified indexes** — a PK per entity (natural-vs-surrogate stated); uniqueness + check/cross-field constraints explicit; the access patterns enumerated; **every index traces to an access pattern** (no unjustified index, no missing-but-needed one).
4. **Normalization & storage paradigm** — the normal form (relational) or embedding/single-table strategy (NoSQL/other) stated; the **paradigm chosen with rationale**; each deliberate denormalization records its read-pattern + tradeoff + consistency strategy.
5. **Data lifecycle & migration** — retention/archival + soft-vs-hard delete where needed; derived data names its source-of-truth + freshness; temporal/audit where history matters; a migration & seeding **plan** (expand-and-contract for a breaking change; backward/forward compatibility where rolling deploys apply).
6. **Diagram ⇄ catalog ⇄ tables in sync** — every entity/relationship in the Mermaid `erDiagram` appears in the catalog + relationship/index lists and vice-versa; no orphan/drift.
7. **Cross-cutting data quality** — sensitive attributes classified (PII/sensitive) + retention/residency where the data warrants; at-rest security for secrets (no plaintext credentials); the model viable at the target scale (no hot partition / unindexed hot query / unbounded row) — addressed where the data warrants.
8. **Grounded, honest & consistent** — entities/attributes reflect the feature-spec (not invented/boilerplate); assumptions explicit (thin-input → a blocker, not an invented schema); **no fabrication**; **one-directional vs the api-spec** (derived from the feature-spec, the api-spec only a downstream consumer — never reverse-engineered from DTOs); consistent with the shipped schema where one exists.
9. **Delta-scoped amend (on a change request)** — the changed entities meet conditions 1–8 on what they touched; the change is classified additive/breaking with a migration plan + compatibility analysis; the forward/downward ripple flagged; the doc version bumped + changelog; superseded items marked. *(Greenfield first build → n/a.)*

**Proportionality:** a thin store legitimately collapses what it does not need (one entity, no M:N, no denormalization, no temporal history, no migration on a first draft, no PII). Judge integrity + queryability completeness, not word count.

The abstract consumer: the engineers who implement persistence and write queries, a downstream api-spec author whose resources map onto these entities, and the `reviewing-data-model` gate that checks the doc against the bar above.

## Related

- A **content-template tool** — supplies the data-model section structure this skill composes with (the structure; this skill is the method + bar).
- A **deep-research capability** — grounds modeling decisions in established practice (ER modeling, normalization theory, the paradigm's idioms) instead of inventing.
- The upstream **feature-spec** (+ **architecture-doc** where present) — the input context; this model designs the persistence the feature-spec'd behavior needs.
- An **api-spec** authoring concern — a *downstream consumer*: its resources map onto this model's entities (one-directional). Distinct artifact — the wire contract, not the stored schema.
- **`reviewing-data-model`** — the dedicated acceptance gate (the twin): it judges the finished model against the **same nine conditions** in `## Output` (single-sourced) and emits `VERDICT: approve|revise`. A finished data-model artifact routes there, **not** to the generic `design-review` (which carves it out, like the technical-design + architecture-doc artifacts).
- A **`references/`** pair: `references/modeling-method.md` (per-paradigm idioms + the entities/relationships/keys/index/normalization depth) and `references/lifecycle-and-amend.md` (retention/temporal/privacy + the expand-and-contract migration + the amend procedure + the forward/downward ripple).

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- `references/modeling-method.md` — the per-paradigm idioms (relational/document/graph/wide-column/key-value) + the depth on entities/attributes, relationships/referential-integrity, keys/constraints/access-pattern-justified-indexes, normalization/paradigm-choice, and data privacy/classification. Load when modeling a specific paradigm or a borderline integrity decision.
- `references/lifecycle-and-amend.md` — retention/soft-delete/derived-data/temporal depth + the expand-and-contract migration procedure + the amend method (classify additive/breaking, compatibility, the forward/downward ripple). Load on a lifecycle or amend/delta task.
- `references/sources.md` — research provenance for the method + bar. Load when verifying a claim's grounding.

This skill ships no `scripts/` or `assets/`.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k, error >50k.

## Changelog

- **1.2.0** (2026-06-15) — production-grade restructure: added the **iteration/amend method** (Step 6 — classify additive/breaking + expand-and-contract migration + backward/forward compatibility + the forward/downward ripple); deepened schema-evolution/migration, temporal/audit/SCD, and data privacy/classification in the lifecycle; broadened the paradigm coverage (graph/wide-column/key-value idioms + NoSQL single-table depth); restructured `## Output` to **nine conditions single-sourced 1:1 with the new `reviewing-data-model` twin** (added cross-cutting data quality + delta-scoped amend); routed the finished artifact to `reviewing-data-model` (not the generic `design-review`); split depth into `references/modeling-method.md` + `references/lifecycle-and-amend.md`. Method + input contract + medium unchanged (additive).
- **1.1.0** (2026-06-04) — initial reviewed release.
