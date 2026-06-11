# SQLAlchemy multi-dialect — extras

Fuller worked examples for the cross-dialect gotchas summarized in `SKILL.md`. Load when implementing a specific gotcha and the in-body snippet isn't enough. All examples assume the `Base`/`Job` models from the SKILL body.

## Shared in-memory SQLite for tests (StaticPool)

A plain `sqlite://` engine gives each pooled connection its own empty database. For a single shared in-memory DB across a test, force one connection with `StaticPool`:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},  # allow use from the test thread pool
    poolclass=StaticPool,                        # ONE shared connection -> one shared DB
)
Base.metadata.create_all(engine)                 # tables now visible to every checkout
```

Pool selection summary:

| Target | Pool | Why |
|---|---|---|
| File SQLite | `QueuePool` (2.0+ default) | normal pooled access to one file |
| `:memory:` (default) | `SingletonThreadPool` | per-thread in-memory DB |
| Shared in-memory / tests | `StaticPool` | one connection so the DB persists across checkouts |
| PostgreSQL / MySQL | `QueuePool` + `pool_pre_ping=True` | pooled, with dead-connection recycling |

## Upsert, end-to-end, per dialect

There is no portable upsert. Pick the import by the engine you're running against. A common pattern: insert-or-update a row keyed by its primary (or unique) key.

### PostgreSQL / SQLite (ON CONFLICT)

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert  # or: from sqlalchemy.dialects.sqlite import insert

def upsert_job_pg(session, id_, name, data):
    stmt = pg_insert(Job).values(id=id_, name=name, data=data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],                 # the conflict target (PK or unique cols)
        set_={"data": stmt.excluded.data,      # excluded = the row that would have been inserted
              "name": stmt.excluded.name},
    )
    session.execute(stmt)

# Do-nothing variant (idempotent insert):
stmt = pg_insert(Job).values(id=1, name="x", data={}).on_conflict_do_nothing(index_elements=["id"])
```

SQLite uses the exact same API — only the import changes (`from sqlalchemy.dialects.sqlite import insert`).

### MySQL (ON DUPLICATE KEY UPDATE)

```python
from sqlalchemy.dialects.mysql import insert as mysql_insert

def upsert_job_mysql(session, id_, name, data):
    stmt = mysql_insert(Job).values(id=id_, name=name, data=data)
    stmt = stmt.on_duplicate_key_update(
        data=stmt.inserted.data,    # inserted = the proposed row (MySQL's analog of excluded)
        name=stmt.inserted.name,
    )
    session.execute(stmt)
```

MySQL has no explicit conflict target — it triggers on **any** duplicate PRIMARY/UNIQUE key. There is no direct `do_nothing`; emulate it with `INSERT IGNORE` semantics or set a column to itself.

## JSON vs JSONB

```python
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

class Doc(Base):
    __tablename__ = "docs"
    id: Mapped[int] = mapped_column(primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)      # portable: JSON on PG/MySQL, TEXT(JSON1) on SQLite
    # payload: Mapped[dict] = mapped_column(JSONB)   # PG-ONLY: binary, indexable, containment ops
```

Portable subset = store and retrieve whole documents. The moment you want to **query inside** the JSON (containment, path extraction, GIN indexing), you're in dialect-specific territory — `JSONB` `@>`/`->>` on PG, `JSON_EXTRACT` on MySQL, `json_extract` on SQLite. Keep those queries behind a dialect branch, or push the queryable fields out into real columns.

## Transaction isolation

```python
from sqlalchemy import create_engine

# Per-engine (applies to every connection from this engine):
engine = create_engine(url, isolation_level="REPEATABLE READ")

# Per-connection / per-block override:
with engine.connect() as conn:
    conn = conn.execution_options(isolation_level="SERIALIZABLE")
    conn.execute(...)
    conn.commit()
```

Valid levels: `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, `SERIALIZABLE`, `AUTOCOMMIT`.

Dialect defaults that bite a portable layer:

| Dialect | Default isolation | Note |
|---|---|---|
| PostgreSQL | READ COMMITTED | |
| MySQL / InnoDB | REPEATABLE READ | stricter default than PG — same code can behave differently |
| SQLite | serializable-ish | SQLAlchemy ships built-in support for only `AUTOCOMMIT` as a settable `isolation_level`; the engine is otherwise serializable-ish |

If correctness depends on the level (e.g. avoiding a phantom read), set it explicitly rather than inheriting the per-engine default.

## Dropping to Core for RETURNING

When you need the server-generated values back from an `INSERT`/`UPDATE` without a follow-up `SELECT`, use Core's `.returning()` (supported on PG, modern SQLite, and MariaDB; MySQL's support is limited):

```python
from sqlalchemy import insert

stmt = insert(Job).values(name="ingest", data={}).returning(Job.id, Job.created_at)
row = session.execute(stmt).one()      # (id, created_at) without a second round-trip
```

This is one of the few places the spec sanctions dropping below the ORM — `RETURNING` and the dialect-specific upsert are Core's domain because the ORM can't express them portably.

## with_for_update — full option reference

```python
select(Job).where(...).with_for_update(
    skip_locked=True,   # SKIP LOCKED: omit rows another txn already locks (claim-next)
    nowait=False,       # NOWAIT: True -> raise immediately instead of blocking on a locked row
    read=False,         # FOR SHARE (read=True) vs FOR UPDATE (read=False)
    of=Job,             # OF <table>: restrict the lock to one table in a multi-table select
    key_share=False,    # PG FOR KEY SHARE (weaker lock); PG-only
)
```

Support: PostgreSQL (all options), MySQL 8.0+ InnoDB (`SKIP LOCKED`/`NOWAIT` from 8.0). **SQLite has no row-level locks** — the clause is accepted and emitted as a no-op, so a "locking" read does not actually serialize concurrent claimers there. Composing this into a safe claim loop (and the SQLite `BEGIN IMMEDIATE` alternative) belongs to `sql-job-queue`.
