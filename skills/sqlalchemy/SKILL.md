---
name: sqlalchemy
description: >
  Use when standing up a relational data layer with SQLAlchemy 2.x (2.0/2.1) ORM
  that must run on more than one dialect — SQLite, PostgreSQL, and MySQL — from a
  single codebase. Covers the typed 2.x ORM (DeclarativeBase / Mapped[...] /
  mapped_column), engine + connection-string + pooling, short-lived sessions and
  transaction scope, the sync-first / async (AsyncSession / await) split with a
  per-dialect driver matrix, and the cross-dialect gotchas that bite when one
  schema runs on all three engines: row locking (with_for_update / SKIP LOCKED),
  JSON columns, upsert (ON CONFLICT vs ON DUPLICATE KEY UPDATE), autoincrement /
  identity, and transaction isolation. Multi-dialect, portable, ORM-first. Not
  migrations (see alembic), not job-queue/lease patterns (see sql-job-queue), not
  a full API reference.
forge:
  status: reviewed
  forged: 2026-06-11
  reviewed: 2026-06-11
---

# `sqlalchemy` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, produces a working multi-dialect SQLAlchemy data layer (or the relevant slice of one), and control returns to the caller.

## Overview

This skill teaches an agent to build a **portable relational data layer with SQLAlchemy 2.x** — one codebase whose models, sessions, and queries run unchanged against **SQLite, PostgreSQL, and MySQL**. It leads with the **typed 2.x ORM** (`DeclarativeBase`, `Mapped[...]`, `mapped_column(...)`) and drops to **Core only** for the few things the ORM can't express portably (the dialect-specific upsert, `RETURNING`). It is **sync-first**: the primary worked path is synchronous, with async as a short aside. The load-bearing content is the **cross-dialect gotcha matrix** — the handful of behaviors (row locking, `JSON`, upsert, identity, isolation) that silently differ per engine and break a "write once, run on three databases" assumption if you don't branch on them.

## When to activate

- ✅ Constructing a SQLAlchemy `Engine` + typed `DeclarativeBase`/`Mapped` model + session-scoped transaction for an app that targets SQLite, PostgreSQL, and/or MySQL.
- ✅ Choosing a DBAPI driver (sync or async) for a dialect and writing the connection URL.
- ✅ Configuring pooling, transaction scope, or isolation level for a portable data layer.
- ✅ Hitting a "works on SQLite, fails on Postgres" (or vice-versa) gotcha — row locking, `JSON`, upsert, autoincrement, isolation.

**Do NOT activate when:**

- Authoring/running schema **migrations** or `ALTER TABLE` change → `alembic`.
- Building a **job queue / scheduler** — the ready-set query, atomic lease loop, heartbeat, fair-share → `sql-job-queue`. (This skill teaches the `with_for_update(skip_locked=...)` *primitive* only.)
- Validating/serializing data with **Pydantic** → `pydantic-v2`.
- Using a different ORM (Django ORM, Tortoise, SQLModel) or raw DBAPI.

## Workflow

### Step 1: Pick the dialect + driver, write the URL

URL form is `dialect+driver://user:password@host:port/dbname`. Pick the **default** driver per dialect (matrix in Step 5); the driver is the `+driver` segment.

```python
# SQLite — file (the +pysqlite / sqlite3 stdlib driver is the default)
"sqlite+pysqlite:///./app.db"          # relative file
"sqlite:///./app.db"                    # same thing — sqlite3 is the default driver
"sqlite:////absolute/path/app.db"       # note the 4th slash = absolute path
"sqlite://"                             # in-memory (also sqlite:///:memory:)

# PostgreSQL — psycopg (v3, the modern maintained driver)
"postgresql+psycopg://user:pw@localhost:5432/appdb"

# MySQL / MariaDB — PyMySQL (pure-Python, no C build step)
"mysql+pymysql://user:pw@localhost:3306/appdb"
```

### Step 2: Build ONE engine per process

The `Engine` owns the connection pool. Create it **once at process start**, share it everywhere; do not create an engine per request/task.

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://user:pw@localhost/appdb",
    pool_pre_ping=True,      # recycle dead connections (server DBs — PG/MySQL)
    pool_size=5,             # persistent pooled connections
    max_overflow=10,         # extra burst connections beyond pool_size
)
```

Pooling defaults differ by dialect — see Gotchas. For server DBs (PG/MySQL) keep `pool_pre_ping=True` so a connection killed by the server's idle timeout is detected and replaced instead of erroring mid-query.

### Step 3: Define typed 2.x ORM models

Subclass `DeclarativeBase`; annotate columns with `Mapped[...]` and configure with `mapped_column(...)`. **Never** the legacy `Column = ...` / `declarative_base()` form.

```python
from datetime import datetime
from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)          # autoincrements on all 3
    name: Mapped[str] = mapped_column(index=True)              # NOT NULL (no Optional)
    data: Mapped[dict] = mapped_column(JSON)                   # portable JSON (Step 7)
    note: Mapped[str | None]                                   # NULLable (Optional -> nullable)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    runs: Mapped[list["Run"]] = relationship(back_populates="job")

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    job: Mapped[Job] = relationship(back_populates="runs")
```

A bare `Mapped[str]` is NOT NULL; `Mapped[str | None]` is nullable — SQLAlchemy derives nullability from the annotation. The integer PK autoincrements on every dialect (Step 9).

### Step 4: Bootstrap schema (dev/test only), then session + query

```python
Base.metadata.create_all(engine)   # DEV/TEST bootstrap ONLY — see Anti-patterns
```

For any **managed** schema change in a real project, defer to `alembic` — do not ship `create_all()` as your migration story.

Use a **short-lived** session per unit of work, with an explicit transaction:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

SessionLocal = sessionmaker(engine)   # a factory; bind the engine once

# Per unit of work: open, transact, close.
with Session(engine) as session, session.begin():   # begin() = commit on exit, rollback on error
    session.add(Job(name="ingest", data={"src": "s3"}))
    # block exit commits automatically

# Reads
with Session(engine) as session:
    job = session.get(Job, 1)                                    # typed Job | None by PK
    rows = session.execute(
        select(Job).where(Job.name == "ingest").order_by(Job.id)
    ).scalars().all()                                            # list[Job]
```

`session.execute(select(...))` returns `Row` tuples; call `.scalars()` to unwrap to ORM entities. `session.get(Model, pk)` is the by-primary-key fast path (checks the identity map first).

### Step 5: Choose sync vs async + driver (matrix)

**Sync is the primary path.** Reach for async only when the surrounding stack is already async (e.g. an ASGI app). The `+driver` in the URL selects sync vs async — there is no flag.

| Dialect | Default sync driver | URL prefix | Default async driver | Async URL prefix | Alternatives (one-line rationale) |
|---|---|---|---|---|---|
| **SQLite** | `sqlite3` (pysqlite, stdlib) | `sqlite+pysqlite://` / `sqlite://` | `aiosqlite` | `sqlite+aiosqlite://` | — (stdlib driver is the only mainstream sync choice) |
| **PostgreSQL** | `psycopg` (v3) | `postgresql+psycopg://` | `asyncpg` | `postgresql+asyncpg://` | `psycopg2` (legacy, mature, sync-only — only for existing v2 deployments); `psycopg` v3 also drives async if you want one driver for both |
| **MySQL / MariaDB** | `PyMySQL` | `mysql+pymysql://` | `aiomysql` | `mysql+aiomysql://` | `mysqlclient` (C-extension, faster, needs a build toolchain); `asyncmy` (faster async, Cython build) |

Defaults chosen for: **maintained + least friction** — `psycopg` v3 is the modern actively-maintained PG driver; `PyMySQL` is pure-Python so it installs with no compiler; `asyncpg` is the fastest async PG driver.

### Step 6: Async aside (short)

Same model classes; swap the engine/session families and `await` the I/O.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

aengine = create_async_engine("postgresql+asyncpg://user:pw@localhost/appdb")
ASessionLocal = async_sessionmaker(aengine, expire_on_commit=False)

async with ASessionLocal() as session:
    async with session.begin():
        session.add(Job(name="async-ingest", data={}))
    res = await session.execute(select(Job))
    jobs = res.scalars().all()
```

Async runs the sync DBAPI work through a greenlet bridge — you write `await`, SQLAlchemy handles the hop. The one trap: after commit, attribute access can trigger a **lazy load**, which raises in async (no implicit I/O). Set `expire_on_commit=False` and/or eager-load (`selectinload`) the relationships you'll touch after commit. Never share one `AsyncSession` across concurrent tasks (same rule as sync sessions across threads).

### Step 7: Cross-dialect gotchas — branch where they differ

This is the load-bearing section. See `references/sqlalchemy-extras.md` for fuller worked examples of each. The portable rules:

**Row locking — the support matrix (load-bearing).** `select(...).with_for_update(...)` emits `SELECT ... FOR UPDATE`.

```python
stmt = select(Job).where(Job.name == "ingest").with_for_update(
    skip_locked=True,   # skip rows another txn holds (claim-next pattern)
    nowait=False,       # True = error instead of waiting if a row is locked
    read=False,         # True = FOR SHARE instead of FOR UPDATE
    of=Job,             # lock only this table's rows in a multi-table select
)
```

| Dialect | `FOR UPDATE` | `SKIP LOCKED` / `NOWAIT` |
|---|---|---|
| **PostgreSQL** | yes | yes |
| **MySQL** | yes (InnoDB) | yes — **MySQL 8.0+** only |
| **SQLite** | **no** — no row-level locks (file/DB-level locking); `with_for_update` is effectively a **no-op** |

A data layer that must run on SQLite **cannot rely on row locking**. What to do instead on SQLite (the `BEGIN IMMEDIATE` claim strategy) is the `sql-job-queue` sibling's concern — branch to it, don't implement it here.

**JSON.** Use the generic `sqlalchemy.JSON` for portability — stored as native JSON on PG/MySQL and as TEXT (via SQLite's JSON1) on SQLite. The **portable subset** is store/retrieve whole documents. For Postgres-native indexing/containment use `sqlalchemy.dialects.postgresql.JSONB` instead — but that's PG-only. Path/containment query operators differ per dialect; don't assume a JSON `WHERE` written for one engine runs on another.

**Upsert — no portable form; branch per dialect.** Import `insert` from the dialect module:

```python
# PostgreSQL (and SQLite — same API, different import)
from sqlalchemy.dialects.postgresql import insert   # or .sqlite import insert
stmt = insert(Job).values(id=1, name="ingest", data={})
stmt = stmt.on_conflict_do_update(index_elements=["id"], set_={"data": stmt.excluded.data})
# stmt.on_conflict_do_nothing(index_elements=["id"])   # the do-nothing variant
# index_elements must name a real UNIQUE / PK constraint (or partial-index cols), else no conflict is detected

# MySQL
from sqlalchemy.dialects.mysql import insert
stmt = insert(Job).values(id=1, name="ingest", data={})
stmt = stmt.on_duplicate_key_update(data=stmt.inserted.data)
```

Note `excluded` (PG/SQLite) vs `inserted` (MySQL) for "the row that would have been inserted".

**Autoincrement / identity.** An integer PK (`Mapped[int] = mapped_column(primary_key=True)`) autoincrements on all three — PG via IDENTITY/SERIAL, MySQL via AUTO_INCREMENT, SQLite via ROWID. The portable default just works; don't hand-roll sequence logic.

**Transaction isolation.** Set per-engine or per-connection:

```python
engine = create_engine(url, isolation_level="REPEATABLE READ")
# or per-connection / per-block:
with engine.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
    ...
```

Valid levels: `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`, `AUTOCOMMIT`. **Defaults differ**: PostgreSQL = READ COMMITTED, MySQL/InnoDB = REPEATABLE READ. On SQLite, SQLAlchemy ships built-in support for only `AUTOCOMMIT` as a settable `isolation_level` (the engine is otherwise serializable-ish) — don't expect `isolation_level="SERIALIZABLE"` to take there. If correctness depends on a level, set it explicitly — don't inherit the dialect default.

## Rules

**Hard rules (never violate):**

- **2.x typed ORM only.** `DeclarativeBase` + `Mapped[...]` + `mapped_column(...)`. Never the legacy `Column =` / `declarative_base()` form.
- **One engine per process.** It owns the pool; create once, share everywhere.
- **Sessions are short-lived and not shared.** One `Session`/`AsyncSession` per unit of work; never share a session across threads or async tasks.
- **`create_all()` is dev/test bootstrap only.** Managed schema change → `alembic`.
- **Branch on the cross-dialect gotchas.** Never assume row locking, a single upsert form, a JSON query operator, or an isolation default ports across SQLite/PG/MySQL.

**Preferences (override-able):**

- Prefer the **default driver** per dialect (Step 5) unless a stated constraint (existing psycopg2 deployment, perf-critical async path) justifies an alternative.
- Prefer the ORM; drop to Core only for what it can't express portably (dialect upsert, `RETURNING`).
- Keep `pool_pre_ping=True` for PG/MySQL; for SQLite it's unnecessary.
- Sync-first; reach for async only inside an already-async stack.

## Gotchas

- **`sqlite:///path` slash count.** Three slashes + relative path is relative to CWD; an **absolute** path needs four (`sqlite:////abs/path.db`). In-memory is `sqlite://` or `sqlite:///:memory:`.
- **A fresh `sqlite://` is empty per connection.** A plain in-memory engine gives each pooled connection its **own** database — tables created on one are invisible to the next. For a shared in-memory DB (tests), use `StaticPool` (one shared connection): `create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)`.
- **Pool defaults differ by dialect.** File SQLite → `QueuePool` (the 2.0+ default); `:memory:` → `SingletonThreadPool`; shared in-memory/tests → `StaticPool`. Server DBs use `QueuePool`. Don't assume the same pool everywhere.
- **`with_for_update` silently no-ops on SQLite.** It does NOT error — it just doesn't lock. Code that "works" on SQLite can race; verify on the real target engine.
- **Async lazy-load after commit raises.** Accessing an un-loaded relationship/attribute after an async commit triggers implicit I/O, which async forbids. `expire_on_commit=False` and/or eager-load.
- **`.execute(select(Model))` returns rows, not entities.** Forgetting `.scalars()` gives you 1-tuples (`(Job,)`), not `Job`.
- **MySQL `SKIP LOCKED` needs 8.0+.** On 5.7 it's a syntax error, not a silent no-op.

## Anti-patterns

- **Don't ship `create_all()` as your migration strategy** because "it's simpler" — it can't evolve a schema. Use `alembic`.
- **Don't write a "portable upsert" helper** that pretends one API spans all dialects — `excluded`/`ON CONFLICT` (PG/SQLite) and `inserted`/`ON DUPLICATE KEY UPDATE` (MySQL) are genuinely different. Branch on the dialect.
- **Don't build a claim-next-job loop on `with_for_update` alone** assuming SQLite locks rows — it doesn't. That's `sql-job-queue`'s job.
- **Don't reach for the legacy `Column =`/`declarative_base()` style** because a tutorial or source skill showed it — it's pre-2.0 and loses the typing.
- **Don't open one long-lived `Session` for the app** ("to avoid the overhead") — sessions are cheap; long-lived ones leak stale identity-map state and break concurrency.
- **Don't create an engine per request/task** — you lose pooling and exhaust connections.

## Output

A working multi-dialect SQLAlchemy 2.x data layer (or the requested slice): a per-process `Engine`/`AsyncEngine` with a correct URL + pool config, typed `DeclarativeBase`/`Mapped` models, short session-scoped transactions, a sync-or-async driver chosen with a stated reason, and per-dialect branches for each cross-dialect gotcha. The artifact is consumed by the next layer — a migrations tool (`alembic`) for schema evolution, or a higher-level pattern (e.g. `sql-job-queue`) that composes these primitives.

## Related

- `alembic` — schema migrations / managed `ALTER` change (incl. the SQLite no-`ALTER` batch move-and-copy gotcha). This skill stops at `create_all()` for dev/test bootstrap and defers managed change there.
- `sql-job-queue` — job-store/scheduler patterns: the ready-set query, atomic-lease loop, heartbeat/crash-resume, fair-share, and what to do on SQLite where `with_for_update` doesn't lock. This skill teaches only the `with_for_update(skip_locked=...)` primitive + its support matrix.
- `pydantic-v2` — data validation/serialization at the app boundary (not ORM column types).

## Progressive disclosure

- `references/sqlalchemy-extras.md` — fuller worked examples of the cross-dialect gotchas (per-dialect upsert end-to-end, `JSON`/`JSONB`, isolation, the `StaticPool` test setup, Core drop-down for `RETURNING`). **Load when** implementing a specific gotcha and the in-body snippet isn't enough.
- `references/sources.md` — research provenance for this skill. **Load when** verifying a claim's origin or during a fresh review.

## Body budget

- `description` ≤ 1,024 chars.
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
