# Sources — reviewing-data-model

Research provenance for the review method + the nine-condition integrity + queryability bar. The bar is single-sourced with `authoring-data-model` (the same nine conditions); this file records the practice each condition rests on. External content reviewed clean (descriptive DB-design terminology, no embedded commands/URLs lifted); claims rest on ≥2 independent reputable sources.

## ER modeling, relationships, referential integrity (cond-1/2)

- GeeksforGeeks — "Introduction of ER Model"; Wikipedia — "Entity–relationship model" (entities, attributes, 1:1/1:M/M:N cardinality, associative entities).
- SQL-standard referential actions — `RESTRICT` / `CASCADE` / `SET NULL` / `SET DEFAULT` (PostgreSQL + MySQL docs corroborate the on-delete semantics).
- MongoDB Docs — "Embedded Data Versus References" (embed read-together/bounded; reference large/shared); consistency held in the application without DB FKs.

## Keys, constraints, index justification (cond-3)

- Microsoft Learn — "Index Architecture and Design Guide — SQL Server" (index the WHERE/JOIN/ORDER BY columns + FKs; analyze the query workload).
- AWS — "Best Practices for Designing and Using Partition Keys Effectively" (partition+sort key; avoid hot partitions; GSI/LSI only for unsupported patterns).
- Over-indexing cost (write-amplification + storage) — standard query-optimization practice.

## Normalization & storage paradigm (cond-4)

- Wikipedia — "Database normalization" (1NF–BCNF); DigitalOcean — "Database Normalization … 1NF/2NF/3NF/BCNF".
- Martin Kleppmann, *Designing Data-Intensive Applications* (storage-engine + replication chapters: relational vs document vs wide-column vs graph; consistency models; polyglot persistence).
- Neo4j (graph modeling: nodes + edges for traversal) and Apache Cassandra/DataStax (model-by-query: partition + clustering key) — the non-relational idioms cond-4 judges in their own terms.

## Lifecycle, migration, schema evolution (cond-5/9)

- Tim Wellhausen — "Expand and Contract" (zero-downtime breaking-change migration: never rename/remove in place; each step revertible + backward-compatible).
- Martin Kleppmann — backward vs forward compatibility under rolling upgrades (DDIA ch.4).

## Cross-cutting data quality (cond-7)

- Forcepoint — "GDPR Data Classification"; Ground Labs — "What is PII for GDPR" (tiered classification; data minimization; retention).
- At-rest encryption / secret handling (hash+salt, tokenize) — standard data-layer security practice.

## Review-method lineage (cond-8 + the contract)

- Adapted from the canonical sibling `reviewing-technical-design`: the `VERDICT: approve|revise` contract, judge-against-given-upstreams, the consistency-with-shipped-code verify-against-the-code discipline (the design-review Step-4 lineage) + its greenfield clause, and the proportionality / no-false-revise / inventing-conditions anti-patterns.

## Notes

- Vendor-specific limits (item-size caps, etc.) are cited to the vendor doc only — verify against the project's actual store/version before relying on them.
- This file is the portable provenance shipped with the skill; the skill is self-contained and points at no project-internal research path.
