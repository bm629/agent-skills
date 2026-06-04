---
name: authoring-data-model
description: >
  Use when authoring a data model document — the persistence/domain model of a
  system's stored data: entities + typed attributes, relationships + cardinality,
  keys + constraints, indexes, normalization decisions, the storage choice, and
  the data lifecycle. Guides the producer through the METHOD, not the outline:
  deriving entities from the feature-spec's nouns + the access patterns,
  detecting the paradigm and modeling in it (relational ER + tables +
  normalization, or document/NoSQL access-pattern-first), making integrity rules
  explicit (keys, constraints, cardinality + referential rule), and justifying
  each index by an access pattern — so an engineer can build the schema and
  query it correctly. Composes with a separate data-model template
  tool and a deep-research capability. Assumes the upstream feature-spec (+
  architecture-doc) — never a blank page. Not the API wire contract (the api-spec
  references these entities downstream, one-directional), not the
  implementation/DDL, and not reviewing a finished data model.
extensions:
  claude: {}
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# authoring-data-model — SKILL.md

> **Variant:** standard · **When to use:** authoring a data model document. This skill supplies the producer METHOD and the integrity/queryability BAR; the section STRUCTURE comes from a separate data-model template tool you compose with. Do not restate that template's outline here.

## Overview

A data model document is the **persistence/domain model** of a system's stored data — the design an engineer implements the schema from and everyone who queries the data reads. This skill guides a producer to author one: deriving entities from the upstream feature-spec, detecting the storage paradigm and modeling in it, making integrity rules explicit, and justifying every index by an access pattern. It teaches the *how-to* — the research method and the quality bar — and composes with a separate template tool that supplies the section structure. The bar is "an engineer can create the schema and write correct queries from it, and the model's integrity rules + tradeoffs are explicit."

It is paradigm-aware: the same modeling rigor (entities, relationships, integrity, justified indexes, stated tradeoffs) applies to **relational/SQL** and **document/NoSQL** stores; only the artifact adapts.

## When to activate

- Authoring or substantially revising a data model / schema design document for a system or feature, given an upstream feature-spec (and an architecture-doc naming the stores, where present).
- The producer needs the method (how to derive entities, model relationships, justify indexes, state tradeoffs) and the bar a buildable, queryable model must meet — not a blank page.

**Do NOT activate when:**

- Reviewing/judging a finished data model — that is a runtime review gate, not authoring.
- Authoring the **API wire contract** (operations + request/response DTOs) — that is the api-spec; it *references* this model's entities (downstream, one-directional), it does not redefine them.
- Designing the **persistence implementation** (ORM/repository/access-layer) — that is a technical-design doc; the system's data-store topology is an architecture doc.
- Producing the executable **DDL / migration scripts** — this is the design document (entities, constraints, migration *plan*), not the code.
- Authoring a different document type.

## Workflow

> The section structure comes from the data-model template tool you compose with. The steps below are the METHOD that fills it — apply them to whatever sections that template carries; never restate its outline.

### Step 1: Get the structure + ground the inputs

Obtain the data-model template's section set from the template tool. Read the upstream **feature-spec** (the data the features manipulate) and, where present, the **architecture-doc** (the chosen stores). You are elaborating these — never starting blank. Ground modeling decisions in established practice (ER modeling, normalization theory, the chosen paradigm's idioms) via a research capability rather than inventing.

### Step 2: Detect the paradigm and pick the track

From the architecture-doc / chosen store, decide the paradigm per store (a system may use more than one — model each in its own track). Apply the same rigor either way; the artifact differs:

- **Relational/SQL** — entities map to tables; ER diagram + per-attribute spec tables; primary/foreign keys + referential integrity; normalize, then denormalize deliberately.
- **Document/NoSQL** — **access-pattern-first** (model from the query list, not the entities, because ad-hoc query flexibility is limited); collections + document shapes; embedding vs referencing; co-locate entities read together.

### Step 3: Enumerate access patterns, then model

List the reads/writes the system must serve against this data first. For relational they justify the indexes; for NoSQL they *determine the schema*. Then:

- **Entities** — derive from the feature-spec's **nouns**. Type every attribute; mark required/optional; give defaults where they exist; record value constraints. Keep the persistence entity distinct from the api-spec's wire DTO — they often differ; model the stored shape, not the DTO.
- **Relationships** — every one states its **cardinality** (1:1 / 1:M / M:N), the foreign key or reference realizing it, which side **owns** the lifecycle, and the **referential rule** (on-delete: restrict/cascade/set-null — or, for NoSQL, embed-vs-reference and how referential consistency is held without DB-enforced FKs). Keep the ER diagram and the relationship list in sync with the entity catalog.
- **Keys + constraints** — a primary key per entity (natural vs surrogate, with the reason; for NoSQL the partition+sort key and any overloaded-key strategy); uniqueness (incl. multi-column); check/domain constraints; cross-field invariants. Explicit, not implied.

### Step 4: Justify indexes, state tradeoffs, address lifecycle

- **Indexes** — each one traces to an access pattern from Step 3 (the columns in WHERE/JOIN/ORDER BY and the foreign keys those queries hit). An index with no justifying access pattern is removed; over-indexing bloats storage and slows writes.
- **Normalization/denormalization** — state the form (relational: typically 3NF/BCNF) or the NoSQL embedding strategy, and record **every deliberate denormalization** with the read pattern it serves, the write-cost/staleness tradeoff accepted, and how the redundant copy is kept consistent. The core tradeoff: normalization favors write efficiency + integrity; denormalization favors read performance.
- **Data lifecycle** — retention/archival per entity (soft vs hard delete); any stored derived/computed value with its source of truth and how it stays current; the migration/seeding *plan* (how the schema is created and evolved, backfill, seed data) — the plan, not the DDL.

### Step 5: Surface gaps, then self-check against the bar

Record unknowns as **explicit assumptions/open-questions** — never invent. Then verify the document against the quality bar in `## Output` before handing off. Express everything **textually** (a Mermaid `erDiagram`, attribute/constraint spec tables, index/relationship lists, and a fenced document-shape example for NoSQL) — the method and bar are independent of the medium.

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

A data model **document** (textual markdown) that meets this integrity + queryability bar — what a runtime review gate checks:

1. **Every entity has typed attributes + a key** (primary, or partition+sort for NoSQL).
2. **Every relationship has cardinality + the referential rule** (FK/reference + ownership + on-delete, or embed-vs-reference + consistency strategy).
3. **Constraints + uniqueness explicit** — not implied.
4. **Each index justified by an access pattern.**
5. **Storage choice + normalization tradeoffs stated** — store + paradigm with rationale; normal form / embedding strategy named; each deliberate denormalization records its tradeoff + consistency strategy.
6. **ER diagram + tables in sync.**
7. **Data lifecycle addressed** — retention, derived data (with source of truth), migration/seeding plan.
8. **Grounded, not boilerplate** — reflects the feature-spec's data; gaps are explicit assumptions.
9. **Usable downstream** — an engineer creates the schema + writes correct queries, and the api-spec maps its resources onto these entities, without asking the author.

The abstract consumer: the engineers who implement persistence and write queries, a downstream api-spec author whose resources map onto these entities, and a review gate that checks the doc against the bar above.

## Related

- A **content-template tool** — supplies the data-model section structure this skill composes with (the structure; this skill is the method + bar).
- A **deep-research capability** — grounds modeling decisions in established practice (ER modeling, normalization theory, the paradigm's idioms) instead of inventing.
- The upstream **feature-spec** (+ **architecture-doc** where present) — the input context; this model designs the persistence the feature-spec'd behavior needs.
- An **api-spec** authoring concern — a *downstream consumer*: its resources map onto this model's entities (one-directional). Distinct artifact — the wire contract, not the stored schema.
- A **design-review / acceptance gate** — judges the finished model against the `## Output` bar at runtime; there is no separate data-model review skill.

## Progressive disclosure

Heavy content lives in subfolders, loaded only on demand:

- `references/sources.md` — research provenance for the method + bar. Load when verifying a claim's grounding.

This skill ships no `scripts/` or `assets/`.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k, error >50k.
