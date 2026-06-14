# Data-model quality bar — per-condition pass/gap signals + worked findings

> Depth for `reviewing-data-model`. The SKILL.md body carries the nine conditions; this file sharpens each into pass/gap signals + a worked finding. Load when a borderline condition needs a sharper call. The bar is single-sourced with `authoring-data-model`'s `## Output`.

## cond-1 — Entities & attributes

- **Pass:** every entity has a key + every attribute a concrete type; nullability + load-bearing constraints recorded; the modeled shape is the stored shape; entities trace to the domain.
- **Gap:** an untyped attribute; a keyless entity; a wire-DTO modeled as if persisted (computed/flattened fields stored); a speculative entity no feature needs.
- **Worked:** "Entity `OrderSummary` stores `line_item_count` + `formatted_total` — these are response-projection fields (cond. 1: stored-shape-not-DTO). Fix: model `Order` + `LineItem`; let the api-spec compute the summary."
- *Non-collapsing:* typed + keyed holds at any size.

## cond-2 — Relationships & referential integrity

- **Pass:** every relationship carries cardinality; M:N has a junction entity; FK/reference + owner named; on-delete rule stated (relational) OR embed-vs-reference + consistency strategy stated (NoSQL/other).
- **Gap:** a relationship line with no cardinality; a bare M:N (no junction); a missing on-delete rule; an unbounded embed or an FK-less reference with no consistency strategy.
- **Worked:** "`Order`→`Customer` shows a line but no on-delete rule (cond. 2). Fix: state `ON DELETE RESTRICT` — you cannot delete a customer with existing orders — so integrity is not left to the engineer."
- *Paradigm-aware:* a NoSQL model has no FK — judge embed-vs-reference + the consistency strategy, not FK presence.

## cond-3 — Keys, constraints & access-pattern-justified indexes (the signature)

- **Pass:** a PK per entity (natural-vs-surrogate stated); uniqueness + check/cross-field constraints explicit; access patterns enumerated; every index traces to a pattern; hot queries are supported.
- **Gap:** an index with no justifying query; a frequent query with no supporting index; an unstated key choice; a business-uniqueness rule left unmodeled.
- **Worked:** "Index `idx_orders_notes` (free-text) has no access pattern in §1 and is never filtered on (cond. 3). Fix: drop it. Separately, the dashboard's main query 'orders by customer, newest first' has no composite index — add `(customer_id, created_at DESC)`."
- *Non-collapsing:* an index present is justified; the access patterns are enumerated even when no secondary index is needed.

## cond-4 — Normalization & storage paradigm

- **Pass:** normal form (relational) or embedding/single-table/edge/partition strategy (other) stated; paradigm chosen with rationale; each denormalization records read-pattern + tradeoff + consistency strategy.
- **Gap:** unexplained redundancy → update anomalies; a denormalized copy with no consistency strategy; an unstated store choice; a paradigm-mismatched model.
- **Worked:** "`Order.customer_name` duplicates `Customer.name` with no consistency note (cond. 4). Fix: state the read pattern it serves, the staleness window, and how it's kept current (update-on-rename, or point-in-time snapshot — say which)."
- *Paradigm-aware:* a NoSQL/graph/wide-column model has NO normal form — never revise it for "not being normalized"; judge its own idiom.

## cond-5 — Data lifecycle & migration

- **Pass:** retention/soft-delete where needed; derived data names its source-of-truth + freshness; temporal/audit where history matters; a migration plan (expand-and-contract for breaking change) + compatibility where rolling deploys apply.
- **Gap:** an unbounded-growth entity with no retention; a stored aggregate with no freshness mechanism; an implied in-place rename/drop on a populated table; no seeding/migration plan.
- **Worked:** "Renaming `users.fullname`→`full_name` is shown as an in-place change (cond. 5) — it breaks the running app mid-deploy. Fix: expand (add `full_name`, write both) → backfill → transition reads → contract (drop `fullname`)."
- *Collapse:* a thin/first-draft model has a trivial lifecycle — light is fine.

## cond-6 — Diagram ⇄ catalog ⇄ tables in sync

- **Pass:** every entity/relationship in the Mermaid `erDiagram` appears in the catalog + relationship/index lists and vice-versa.
- **Gap:** an element in one rendering but missing from another (drift = incomplete edit).
- **Worked:** "`Payment` appears in the ER diagram + relationship list but has no §2 attribute spec table (cond. 6). Fix: add the catalog entry or remove the box."

## cond-7 — Cross-cutting data quality

- **Pass:** sensitive attributes classified (PII/sensitive) + retention/residency where the data warrants; secrets protected at rest (no plaintext); viable at the target scale.
- **Gap:** plaintext credentials modeled as ordinary columns; PII stored with no classification/retention where personal data is clearly handled; a hot partition / unindexed hot query / unbounded row at scale.
- **Worked:** "`User.password` is a plain `varchar` (cond. 7). Fix: store a salted hash (`password_hash`), classify it `sensitive`, never the plaintext."
- *Collapse:* no PII → no classification; bounded data → light scale treatment.

## cond-8 — Grounded, honest & consistent

- **Pass:** entities/attributes reflect the feature-spec; assumptions explicit; nothing fabricated; one-directional vs the api-spec; consistent with the shipped schema where one exists.
- **Gap:** an invented entity/constraint/index; the api-spec-inversion; a documented table/column that contradicts the real schema.
- **Worked (consistency):** "The doc claims a `users.tenant_id` column, but `schema/migrations/0007.sql:12` shows tenant scoping via a join table `tenant_users` (cond. 8). Fix: model the real join-table structure or mark the proposed change as a flagged delta."
- *Non-collapsing:* no-fabrication + one-directional hold at any size. **Greenfield clause:** a new/proposed/fictional model has no shipped schema → consistency check is N/A, never a false-revise.

## cond-9 — Delta-scoped amend (amend only)

- **Pass:** changed entities meet cond-1–8 on what they touched; the change classified additive/breaking with a migration plan + compatibility; the forward/downward ripple flagged (api-spec/impl/test-plan/runbook); version bumped + changelog; superseded items marked.
- **Gap:** an un-scoped delta; a breaking change mis-classified as additive; an in-place breaking migration; an un-flagged ripple; a silent deletion.
- **Worked:** "The amend narrows `orders.status` from `varchar` to an enum but is filed as additive with no migration (cond. 9) — it's breaking (existing rows may violate the enum). Fix: classify breaking; expand (add the enum column, backfill+validate, transition), and flag the api-spec status field that maps onto it."
- *Collapse:* greenfield first build → cond-9 n/a (don't full-re-review; don't demand a changelog).
