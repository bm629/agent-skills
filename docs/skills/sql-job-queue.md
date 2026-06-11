# sql-job-queue

> Build a **DB-backed ready-set job scheduler on SQLAlchemy 2.x** — a thin tick
> loop you own, where the relational database is the *only* durable substrate (no
> broker, no second source of truth) and a job becomes runnable as its
> dependencies finish. For **long-running, stateful** jobs whose concurrency is
> capped by **external** limits, on a **single box**, as an **embeddable** library,
> portable across **SQLite, PostgreSQL, and MySQL**. Covers the generic
> `jobs`/`job_deps` model, the ready-set query, the **three per-dialect lease
> branches** (`FOR UPDATE SKIP LOCKED` on PostgreSQL + MySQL 8 vs `BEGIN IMMEDIATE`
> on SQLite, with dialect detection), crash-resume via heartbeat + lease-expiry
> reclaim + a hung-but-alive per-dispatch timeout, weighted fair-share over
> `group_key`, the scan→rank→lease→dispatch→persist→reclaim tick loop, polling vs
> `LISTEN/NOTIFY` wake, and the at-least-once idempotency contract. Sync-first.
> Not the SQLAlchemy data layer or locking primitive (`sqlalchemy`), not
> migrations (`alembic`).

**Skill file:** [`skills/sql-job-queue/SKILL.md`](../../skills/sql-job-queue/SKILL.md)
**Version:** 1.0.0

## Purpose

When the work is long-running, stateful, dependency-driven, single-box, and the DB
is the sole durable state, a broker is the wrong tool (its short-task
ack/visibility-timeout model redelivers and double-executes a long job). This skill
teaches the right shape: a generic `jobs` + `job_deps` DAG, a portable ready-set
query that selects what is runnable *right now*, and — load-bearing — the
**per-dialect atomic lease** that stops two workers on one box from dispatching the
same job. It composes (not re-teaches) the `sqlalchemy` sibling's
`with_for_update(skip_locked=...)` primitive into a claim transaction, and layers on
crash-resume (heartbeat + lease-expiry reclaim + a separate hung-job timeout),
weighted fair-share, the tick loop, the polling vs `LISTEN/NOTIFY` wake, and the
at-least-once idempotency contract with its atomic-finalize guard.

## When to activate

- ✅ Building an embeddable, single-box work queue whose readiness is **dependency-driven** (a DAG of jobs, each runnable once its upstreams are `done`), persisted in a relational DB, portable across SQLite/PostgreSQL/MySQL.
- ✅ Composing the **atomic claim** that stops two workers on one box from dispatching the same job — and needing the per-dialect branch.
- ✅ Making the queue **crash-safe with no broker** — heartbeat, lease expiry, stale-lease reclaim, bounding a hung job.
- ✅ Allocating slots across job groups by **weighted fair-share**, or building the scan→rank→lease→dispatch→persist→reclaim **tick loop**.

### When NOT to activate

- **The SQLAlchemy data layer itself** — engine/URL, `DeclarativeBase`/`Mapped`, sessions, `JSON`, or the `with_for_update(skip_locked=...)` **primitive** + its support matrix → `sqlalchemy` (this skill *composes* it).
- **Schema migrations** → `alembic`.
- **A broker fits** — short fire-and-forget tasks, static enqueue, multi-machine fan-out → Celery / Dramatiq / RabbitMQ.
- **A time-triggered (cron-like) scheduler** → APScheduler; or a heavy orchestrator platform → Airflow / Prefect / Dagster.

## Workflow

| Step | Does |
|---|---|
| 1 Confirm shape | Build this only when long-running · dependency-driven · external-capped · single-box · embeddable · DB-is-sole-state all hold; else a broker is simpler. |
| 2 Data model | Generic `jobs` (state, `parent_id` container, `group_key`, `weight`, lease fields, `run_after`, heartbeat) + `job_deps` edge table; a partial ready-state index. |
| 3 Ready-set query | Portable `select`: `ready`, dependency-complete, leaf-only, time-gated open, not live-leased — *select candidates*; defer locking. |
| 4 Atomic lease | THREE full per-dialect branches via `engine.dialect.name`: PG / MySQL 8+ `FOR UPDATE SKIP LOCKED` vs SQLite `BEGIN IMMEDIATE`. |
| 5 Crash-resume | Heartbeat + lease-expiry reclaim sweep (dead worker) **and** a separate per-dispatch timeout (hung-but-alive worker). |
| 6 Fair-share | Allocate free slots across `group_key`s proportional to `weight` (min 1 each), remainder by largest fractional leftover. |
| 7 Tick loop | scan → rank → lease → dispatch → persist → reclaim; concurrency cap = `min(external limits)`, re-evaluated every tick. |
| 8 Wake | Polling by default (every dialect); PG-only `LISTEN/NOTIFY` as a layered boost with polling as backstop. |
| 9 Idempotency | At-least-once dispatch; `result` write committed atomically with the `done` flip; handler-level dedup is the consumer's job. |

## Hard rules it enforces

- **The claim is one atomic transaction** — read the ready row and write `lease_owner`/`lease_expires`/`in_flight` in a single transaction; never read-then-update across two.
- **Branch the lease on dialect** — `FOR UPDATE SKIP LOCKED` (PG, MySQL 8.0+ InnoDB) vs `BEGIN IMMEDIATE` (SQLite); `with_for_update` is a silent no-op on SQLite, so relying on it there races.
- **MySQL needs 8.0+ / InnoDB, READ COMMITTED for the claim, and exclusive `FOR UPDATE`** — `SKIP LOCKED` errors on 5.7; `with_for_update(read=True, skip_locked=True)` emits the legacy `LOCK IN SHARE MODE SKIP LOCKED` MySQL rejects (issue #10134); the REPEATABLE READ default must be overridden for the claim txn.
- **Finalize atomically** — the `result` write and the `done` transition are one transaction, so a reclaimed job never double-finalizes.
- **Containers roll up, only leaves run** — the ready-set query filters out any job with children; container completion is event-driven, not in the scan.

## The three lease branches (the load-bearing point)

- **PostgreSQL** — `SELECT ... FOR UPDATE SKIP LOCKED` then flip to leased in the same transaction; default READ COMMITTED is exactly what a claim wants. Two concurrent claims lock disjoint rows → never the same job.
- **MySQL 8.0+** — same statement, its own branch: requires InnoDB + 8.0+ (5.7 errors), set READ COMMITTED for the claim txn (override the REPEATABLE READ default so the `SELECT` sees fresh commits), and use exclusive `FOR UPDATE` (the share-mode emit is rejected — issue #10134).
- **SQLite** — no row-level locks (`with_for_update` is a silent no-op), so take the write lock up front with `BEGIN IMMEDIATE`; the claim serializes (others get `SQLITE_BUSY` and retry the tick).

## Progressive disclosure (`references/`)

- `references/sql-job-queue-extras.md` — a fuller worked end-to-end minimal scheduler: all three lease branches, the `dispatch`/heartbeat/finalize step, and the polling run loop as one runnable listing.
- `references/sources.md` — research provenance (Procrastinate / PGQueuer prior art + the SQLAlchemy / Postgres / MySQL locking docs).

## Limitations

- **Single-box, embeddable, multi-dialect** — for multi-machine fan-out of short tasks, a broker is the right tool (it's an Anti-pattern here, and vice-versa); this is the DB-backed ready-set shape only.
- **Sync-first** — the locking semantics are identical under async (`AsyncSession` / `await`); async is covered as a short aside.
- **At-least-once, state-machine guard only** — the queue stops double-*finalize*, not double-*side-effect*; handler idempotency (keys, upserts) is the consumer's responsibility. It composes `sqlalchemy`'s locking primitive and assumes `alembic` (or `create_all` in dev) has created the schema.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
