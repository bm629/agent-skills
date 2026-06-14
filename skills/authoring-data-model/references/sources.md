# Sources — authoring-data-model

Research provenance for the method + integrity/queryability bar. Synthesized from a deep-research pass (2026-06-04); external content reviewed clean (descriptive DB-design terminology, no embedded commands/URLs lifted). Every claim below rests on >=2 independent reputable sources.

## ER modeling, entities, relationships, cardinality

- GeeksforGeeks — "Introduction of ER Model" (entities, attributes, relationships, 1:1 / 1:M / M:N cardinality).
- Wikipedia — "Entity–relationship model".
- Lucidchart — "What is an Entity Relationship Diagram (ERD)?".
- Visual-Paradigm — data-modeling guide, "What is Entity Relationship Diagram (ERD)?".
- IBM — "What is an Entity Relationship Diagram?".
- OpenTextBC — "Database Design, 2nd Edition, Ch.8 — The Entity Relationship Data Model".

## Normalization theory (relational)

- Wikipedia — "Database normalization" (1NF–BCNF, each form stricter than the last).
- DigitalOcean — "Database Normalization: 1NF, 2NF, 3NF & BCNF Examples".
- GeeksforGeeks — "Normal Forms in DBMS".

## Document / NoSQL data modeling (access-pattern-first)

- MongoDB Docs — "Embedded Data Versus References"; "Best Practices for Data Modeling" (embed contains/read-together/bounded; reference large/shared/independent).
- AWS — "Creating a single-table design with Amazon DynamoDB"; "First steps for modeling relational data in DynamoDB" (list access patterns before designing; co-locate entities accessed together).
- Alex DeBrie — "The What, Why, and When of Single-Table Design with DynamoDB".

## Index design (justify by access pattern)

- Microsoft Learn — "Index Architecture and Design Guide — SQL Server" (analyze queries; index WHERE/JOIN/ORDER BY columns + foreign keys).
- Hello Interview — "Database Indexing for System Design".
- Ben Nadel — "The Not-So-Dark Art Of Designing Database Indexes" (pave the cow-paths; over-indexing cost).

## Denormalization, derived data, lifecycle, migration

- Airbyte — "Data Denormalization: What It Is and Why It's Useful" (read-vs-write tradeoff; pre-computed redundancy).
- DataCamp — "Denormalization in Databases: When and How to Use It".
- Google Cloud — "Database migration: Concepts and principles (Part 1)".

## Schema evolution & zero-downtime migration (amend)

- Tim Wellhausen — "Expand and Contract: A Pattern to Apply Breaking Changes to Persistent Data with Zero Downtime" (the authoritative pattern paper: never rename/remove in place; expand → migrate → transition → contract; each step revertible + backward-compatible).
- Jasmin Fluri — "Expand and Contract Method for Database Changes".
- Martin Kleppmann, *Designing Data-Intensive Applications*, ch.4 (backward vs forward compatibility under rolling upgrades; new fields optional/defaulted; reserve removed fields) + his blog "Schema evolution in Avro, Protocol Buffers and Thrift".

## Data privacy & classification

- Forcepoint — "GDPR Data Classification" (tiered classification: public/internal/confidential/restricted).
- Ground Labs — "What is PII for GDPR" (data minimization; retain only as long as needed).

## Graph / wide-column idioms

- Neo4j — graph data modeling (nodes + first-class typed/directed edges; model for traversal access patterns).
- Apache Cassandra / DataStax — data modeling by query (partition + clustering key; one table per query; TTL retention; no joins).

## Notes

- Vendor-specific limits (e.g. MongoDB's per-document size cap, DynamoDB item-size cap) are cited to the vendor doc only — verify against the project's actual store/version before relying on them.
- This file is the portable provenance shipped with the skill; the skill is self-contained and does not point at any project-internal research path.
