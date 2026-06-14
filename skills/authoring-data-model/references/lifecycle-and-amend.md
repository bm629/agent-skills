# Data lifecycle & amend — depth

> Depth for `authoring-data-model`. The SKILL.md body carries the lifecycle + amend method; this file carries the procedures. Load on a lifecycle or amend/delta task.

## Data lifecycle

- **Retention / archival per entity** — how long data lives, then archived (cold storage), anonymized, or hard-deleted. An unbounded-growth entity (events/audit/logs) with no retention plan is a gap. Key retention to the classification (PII/sensitive → tighter).
- **Soft vs hard delete** — a tombstone (`deleted_at`/`is_deleted`) preserves history + referential safety but forces *every* query to filter it and interacts with unique constraints (a partial unique index, or include `deleted_at` in the key); hard delete physically removes. State the choice + its query/constraint consequence per entity that needs it (you don't physically delete a posted invoice).
- **Derived/computed/materialized data** — every stored derived value (aggregate, cached count, materialized view, denormalized copy) names its **source of truth** + **how it stays current** (recompute-on-read, trigger, scheduled refresh, app-maintained). A stored `Account.balance` with no recompute/consistency mechanism is a staleness bug.
- **Temporal / audit / versioning / SCD** — where history matters: effective-dated rows (valid-from/valid-to), audit tables / an append-only change log, a slowly-changing-dimension strategy (type-2 history rows vs type-1 overwrite), row versioning for optimistic concurrency.

## Migration & seeding plan (the plan, not the DDL)

How the schema is created, evolved, **backfilled**, and seeded. Production-grade schema change follows **expand-and-contract / parallel-change** — never rename/remove in place:

1. **Expand** — add the new structure (a new nullable column / table / index); the app writes to both old + new.
2. **Migrate/backfill** — copy existing data to the new structure (a background job for a populated table).
3. **Transition** — switch reads to the new structure (still writing both).
4. **Contract** — stop writing the old, then remove it once nothing reads it.

Each step is independently revertible and **backward-compatible with the running app**, so old + new code coexist during a rolling deploy. **Additive** changes (a new nullable column/table/index) are backward-compatible without the full dance; **breaking** changes (a dropped/renamed/narrowed column, a cardinality change, a NOT NULL added to existing data, a key change) require it. Worked: renaming `users.fullname` → `full_name` in place breaks the running app mid-deploy — expand (add `full_name`, write both), backfill, transition reads, contract (drop `fullname`).

**Backward/forward compatibility** (Kleppmann framing) — *backward* = new code reads old data; *forward* = old code reads new data; under rolling upgrades both hold simultaneously. Practical rules: new fields optional/defaulted; never reuse/renumber a removed field (reserve it); a removed column is deprecated-then-dropped, not yanked.

## Amend — a schema-change delta (Step 6)

When the input is a change request against an approved model:

1. **Scope the delta (edit-not-redraw)** — amend only the touched entities + their relationships/constraints/indexes, in place; do NOT regenerate the whole model. Scope = the touched entities + their relationships + the indexes/constraints on them.
2. **Classify additive vs breaking** — additive (a new nullable column / table / index / optional relationship) vs breaking (a dropped/renamed/narrowed column, a cardinality change 1:M→M:N, a key change). A mis-classified breaking change is the cardinal amend defect (it breaks the running app or existing data).
3. **Migration plan** — a breaking change carries the expand → backfill → transition → contract sequence; an additive change a simple forward migration. Plan the backfill for populated tables.
4. **Compatibility analysis** — state which readers/writers coexist during the change + the backward/forward stance.
5. **Version + changelog** — bump the doc's own version + record who/when/what/why; mark removed entities/attributes/indexes as **superseded/deprecated** (reserved, not silently deleted).
6. **Forward/downward ripple** — a data model is mid-stream (it consumes the feature-spec, it feeds the api-spec). Flag the downstream impact: the **api-spec** resources mapping onto changed entities, the impl/test-plan touching the schema, any migration/runbook; the upstream **feature-spec is amended first** (spec→plan→impl order). "Regression" for a stored schema = a change that breaks a running reader/writer or silently loses/corrupts data.

Worked amend: "an `Order` can have many `Tag`s and a `Tag` many `Order`s." Classify additive (a new junction `OrderTag(order_id, tag_id)` + a new `Tag` entity, no change to existing columns) → forward migration (create `tag`, `order_tag`; no backfill) → backward-compatible (old code ignores the new tables) → ripple (api-spec gains tag resources mapping onto these entities; impl + test-plan touch the new tables) → version bump + changelog. The new junction carries cardinality + a PK + an on-delete rule; the new entity is typed + keyed.

On a **greenfield first build** the amend step is n/a — do not invent a changelog or a migration for a first draft.
