# Sources — research provenance

Forged 2026-06-11 via `skill-forge`. Topic: a DB-backed ready-set job scheduler on SQLAlchemy 2.x — multi-dialect (SQLite + PostgreSQL + MySQL), single-box, embeddable, no broker. Every fact is paraphrased from the sources below — no text copied. All external reads were intended to pass through `external-content-sanitizer` (§5).

## There is no source skill — this is a novel synthesis

`find-skills` (run with many query variations, official-preferred, ~1K install gate) surfaced **no adoptable skill** for this shape. Every published candidate either constrains the dialect (Postgres-only queue libraries) or is the wrong shape (a broker wrapper, a time-trigger scheduler, or a heavy orchestrator). The skill is therefore **synthesized fresh** from the patterns behind the prior art plus the official locking docs — not adopted from, or improved over, any existing skill.

## Pattern prior art — the Postgres-native queues (borrowed patterns, not code)

The atomic-lease core is borrowed from the well-established **`SELECT ... FOR UPDATE SKIP LOCKED` + `LISTEN/NOTIFY`** pattern that the Postgres-native job queues popularized:

- **Procrastinate** (`procrastinate.readthedocs.io`) — a PostgreSQL-backed task queue. Its claim-a-job approach (`FOR UPDATE SKIP LOCKED` to grab-and-skip contended rows) and its `LISTEN/NOTIFY` wake strategy ground the lease (Step 4 PG branch) and the wake section (Step 8). Postgres-only by design — the multi-dialect generalization (the MySQL and SQLite branches) is this skill's own synthesis, not Procrastinate's.
- **PGQueuer** (`github.com/janbjorge/pgqueuer`) — a PostgreSQL job queue built on the same `FOR UPDATE SKIP LOCKED` + `LISTEN/NOTIFY` primitives. Reinforces the claim + notify pattern grounding Steps 4 and 8.

Both are **Postgres-only**; they are pattern sources, never installed or adopted. The "borrow SKIP LOCKED + LISTEN/NOTIFY, re-host on a thin portable loop" framing in Step 1 / the Overview comes from reading what these libraries do and generalizing it.

## Primary grounding — the SQLAlchemy / PostgreSQL / MySQL / SQLite locking docs

The per-dialect lease detail (the load-bearing portability point) traces to the official docs:

- **SQLAlchemy 2.x — `with_for_update`** (`docs.sqlalchemy.org`): `select(...).with_for_update(skip_locked=, nowait=, read=, of=)` emits `SELECT ... FOR UPDATE [SKIP LOCKED]`. Grounds the claim statements in Step 4 and the dialect-detection branch (`engine.dialect.name`). The *primitive* + its full support matrix is the `sqlalchemy` sibling's; this skill cites it and composes it.
- **PostgreSQL — explicit row locks** (`postgresql.org/docs` — Explicit Locking / `SELECT FOR UPDATE`): `FOR UPDATE SKIP LOCKED` grabs-and-skips locked rows without blocking; default transaction isolation is **READ COMMITTED**. Grounds Step 4 Branch 1.
- **MySQL 8.0 — locking reads** (`dev.mysql.com/doc` — Locking Reads / InnoDB): `SELECT ... FOR UPDATE SKIP LOCKED` requires **MySQL 8.0+ / InnoDB** (a syntax error on 5.7); default isolation is **REPEATABLE READ**; plain `FOR SHARE SKIP LOCKED` **is** valid MySQL 8 SQL, but SQLAlchemy's `with_for_update(read=True, skip_locked=True)` emits the legacy `LOCK IN SHARE MODE SKIP LOCKED` which MySQL rejects (SQLAlchemy issue #10134) — use the exclusive `FOR UPDATE` for the claim regardless. Grounds Step 4 Branch 2 and its three MySQL caveats.
- **SQLite — transaction / locking** (`sqlite.org` — Transaction / locking model): SQLite has **no row-level locks** — locking is database/file-level; `BEGIN IMMEDIATE` acquires the write lock at transaction start so the claim serializes, and a contending writer gets `SQLITE_BUSY`. `with_for_update` is a silent no-op on SQLite. Grounds Step 4 Branch 3 and the SQLite gotchas.

## Established patterns (general distributed-systems / queueing literature)

The non-dialect patterns — **lease / heartbeat / stale-lease reclaim** for crash-resume, the **at-least-once** delivery contract and its **state-machine idempotency guard**, and **weighted fair-share** scheduling — are standard distributed-systems / queueing constructs. They are paraphrased from general practice (lease-based fault tolerance, at-least-once vs exactly-once delivery, weighted fair queueing), not from any single proprietary source, and re-expressed against the generic `jobs`/`job_deps` model. The **hung-but-alive-worker per-dispatch timeout** as a failure distinct from a dead worker is called out explicitly because the lease/heartbeat mechanism alone does not cover it.

## Sibling skills referenced (in-repo, not duplicated)

`sqlalchemy` (the data layer + the `with_for_update(skip_locked=...)` locking primitive + its per-dialect support matrix) and `alembic` (schema migrations). Their scope is referenced in the SKILL body's `## Related` and the boundary "Do NOT activate" list; their content is not restated here. This skill teaches only the *composition* — the claim transaction, the dialect branch, the double-dispatch guard, crash-resume, fair-share, the tick loop, wake, and idempotency.

## Portability note

The patterns were distilled to a **project-agnostic** form: the data model is generic (`jobs` / `job_deps`, `type` / `group_key` / `weight`), and no consumer-specific naming (no ticket/costume/phase/workspace/process_ticket/State-seam concepts) appears in the body. Internal repo paths are deliberately kept out of the published skill.

## Degradation note

A fresh reviewer should spot-check the load-bearing claims against the live docs before flipping `forge.status` to `reviewed`: the MySQL 8.0+/InnoDB `SKIP LOCKED` floor, the `REPEATABLE READ`-vs-`READ COMMITTED` isolation defaults, the SQLAlchemy share-mode emit (`with_for_update(read=True, skip_locked=True)` → legacy `LOCK IN SHARE MODE SKIP LOCKED`) that MySQL rejects (#10134, while plain `FOR SHARE SKIP LOCKED` is valid MySQL 8), the SQLite no-row-lock / `BEGIN IMMEDIATE` claim path, and the `with_for_update` SQLite no-op (this last is the `sqlalchemy` sibling's, reused here).
