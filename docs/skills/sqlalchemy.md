# sqlalchemy

> Build a **portable relational data layer with SQLAlchemy 2.x** — one codebase
> whose typed `DeclarativeBase` / `Mapped[...]` / `mapped_column(...)` models,
> short-lived sessions, and queries run unchanged against **SQLite, PostgreSQL,
> and MySQL**. Leads with the typed 2.x ORM (drops to Core only for what the ORM
> can't express portably — the dialect upsert, `RETURNING`), is **sync-first**
> (async is a short aside), and carries a **driver matrix** plus the
> **cross-dialect gotcha set** — row locking, `JSON`, upsert, autoincrement /
> identity, isolation — that silently differs per engine. ORM-first,
> multi-dialect, portable. Not migrations (`alembic`), not the job-queue/lease
> loop (`sql-job-queue`).

**Skill file:** [`skills/sqlalchemy/SKILL.md`](../../skills/sqlalchemy/SKILL.md)
**Version:** 1.0.0

## Purpose

A "write once, run on three databases" data layer is only true if you branch on
the handful of behaviors that genuinely differ per engine. This skill gives an
agent the current 2.x typed-ORM idiom (`DeclarativeBase`, `Mapped[...]`,
`mapped_column(...)` — never the legacy `Column =` / `declarative_base()` form),
the one-engine-per-process + short-lived-session discipline, the sync/async driver
matrix, and — load-bearing — the **cross-dialect gotcha matrix**: row locking
(`with_for_update` / `SKIP LOCKED`), `JSON` vs PG `JSONB`, upsert (`ON CONFLICT`
vs `ON DUPLICATE KEY UPDATE`), autoincrement/identity, and transaction isolation.
It is the data-layer floor the `alembic` and `sql-job-queue` siblings build on; it
stops at `create_all()` for dev/test bootstrap and defers managed schema change to
`alembic`.

## When to activate

- ✅ Constructing an `Engine` + typed `DeclarativeBase`/`Mapped` model + session-scoped transaction for SQLite/PostgreSQL/MySQL.
- ✅ Choosing a sync or async DBAPI driver for a dialect and writing the connection URL.
- ✅ Configuring pooling, transaction scope, or isolation level for a portable data layer.
- ✅ Hitting a "works on SQLite, fails on Postgres" gotcha — row locking, `JSON`, upsert, autoincrement, isolation.

### When NOT to activate

- **Authoring/running schema migrations** or `ALTER TABLE` change → `alembic` (this skill stops at `create_all()` dev/test bootstrap).
- **Building a job queue / scheduler** — ready-set query, atomic-lease loop, heartbeat, fair-share → `sql-job-queue` (this teaches only the `with_for_update(skip_locked=...)` primitive).
- **Validating/serializing at the app boundary** with Pydantic → `pydantic-v2`.
- A different ORM (Django ORM, Tortoise, SQLModel) or raw DBAPI.

## Workflow

| Step | Does |
|---|---|
| 1 URL | `dialect+driver://user:pw@host:port/dbname`; pick the default driver per dialect (the `+driver` segment). |
| 2 Engine | One `create_engine(...)` per process (it owns the pool); `pool_pre_ping=True` for server DBs. Never an engine per request/task. |
| 3 Models | `DeclarativeBase` + `Mapped[...]` + `mapped_column(...)`; a bare `Mapped[str]` is NOT NULL, `Mapped[str \| None]` is nullable. |
| 4 Bootstrap + session | `create_all()` for **dev/test only**; a short-lived `Session(engine)` + `session.begin()` per unit of work; `.scalars()` to unwrap entities. |
| 5 Sync/async + driver | The driver matrix selects sync vs async via the URL `+driver` (no flag); sync is the primary path. |
| 6 Async aside | Same models; swap `create_async_engine` / `async_sessionmaker` / `AsyncSession` and `await` the I/O. |
| 7 Cross-dialect gotchas | Branch where engines diverge: row locking, `JSON`/`JSONB`, upsert, identity, isolation. |

## Hard rules it enforces

- **2.x typed ORM only** — `DeclarativeBase` + `Mapped[...]` + `mapped_column(...)`; never the legacy `Column =` / `declarative_base()` form.
- **One engine per process** — it owns the pool; create once, share everywhere.
- **Sessions are short-lived and not shared** — one `Session`/`AsyncSession` per unit of work; never across threads or async tasks.
- **`create_all()` is dev/test bootstrap only** — managed schema change goes to `alembic`.
- **Branch on the cross-dialect gotchas** — never assume row locking, a single upsert form, a `JSON` query operator, or an isolation default ports across SQLite/PG/MySQL.

## Cross-dialect gotchas (the load-bearing set)

- **Row locking** — `with_for_update(skip_locked=...)` emits `SELECT ... FOR UPDATE` on PostgreSQL and MySQL 8.0+ (InnoDB), but is a silent **no-op on SQLite** (file/DB-level locking, no row locks). A data layer that must run on SQLite cannot rely on row locking; the `BEGIN IMMEDIATE` strategy is `sql-job-queue`'s concern.
- **JSON** — the generic `sqlalchemy.JSON` is portable (native JSON on PG/MySQL, TEXT via JSON1 on SQLite) for whole-document store/retrieve; PG-native `JSONB` indexing/containment is PG-only, and JSON `WHERE` operators differ per dialect.
- **Upsert** — no portable form: `insert(...).on_conflict_do_update(...)` with `excluded` (PG/SQLite) vs `on_duplicate_key_update(...)` with `inserted` (MySQL). Import `insert` from the dialect module and branch.
- **Autoincrement / identity** — an integer PK autoincrements on all three (PG IDENTITY/SERIAL, MySQL AUTO_INCREMENT, SQLite ROWID); the portable default just works.
- **Isolation** — defaults differ (PG = READ COMMITTED, MySQL/InnoDB = REPEATABLE READ; SQLite only ships settable `AUTOCOMMIT`). If correctness depends on a level, set it explicitly.

## Progressive disclosure (`references/`)

- `references/sqlalchemy-extras.md` — fuller worked examples of each gotcha: per-dialect upsert end-to-end, `JSON`/`JSONB`, isolation, the `StaticPool` shared-in-memory test setup, and the Core drop-down for `RETURNING`.
- `references/sources.md` — research provenance (the SQLAlchemy 2.x ORM / dialect docs).

## Limitations

- **Multi-dialect across SQLite / PostgreSQL / MySQL** — confirmed against the SQLAlchemy 2.x docs at forge; exact driver names and dialect caveats (e.g. MySQL `SKIP LOCKED` needing 8.0+) are version-pinnable.
- **ORM-first, sync-first** — drops to Core only for the non-portable bits; async is covered as a short aside, not the primary path.
- **Data layer only** — managed schema change is `alembic`'s job and the lease/scheduler loop is `sql-job-queue`'s; this skill provides the primitives they compose.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
