# Alembic — extended migration recipes

Load when the in-body `SKILL.md` snippet isn't enough for a specific migration shape. Every example targets Alembic 1.18 on SQLAlchemy 2.x and stays portable across SQLite, PostgreSQL, and MySQL.

## 1. A safe rename (preserve the data)

Autogenerate renders a column or table rename as drop + add, which destroys the data. Write the rename by hand instead. A **table** rename:

```python
def upgrade() -> None:
    op.rename_table("jobs", "tasks")

def downgrade() -> None:
    op.rename_table("tasks", "jobs")
```

A **column** rename must go through batch so it works on SQLite (which has no `ALTER COLUMN RENAME` before recent versions and can't alter most columns anyway):

```python
def upgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column("name", new_column_name="title", existing_type=sa.String(200))

def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.alter_column("title", new_column_name="name", existing_type=sa.String(200))
```

On SQLite this is a move-and-copy that carries the data into the renamed column; on PG/MySQL it's a plain `ALTER`. Pass `existing_type` (and `existing_nullable`/`existing_server_default` where relevant) so the recreate rebuilds the column faithfully.

## 2. A data migration (move/transform rows, not just schema)

For backfills or transforms, run a migration with no autogenerate — use `op.execute(...)` for set-based SQL or `op.bulk_insert(...)` for seed rows. Define a lightweight ad-hoc table so you don't import the live model (the model may have drifted past this revision):

```python
from sqlalchemy import table, column, String, Integer

def upgrade() -> None:
    jobs = table("jobs", column("id", Integer), column("status", String))
    # Set-based update — runs on all three dialects.
    op.execute(jobs.update().where(jobs.c.status == op.inline_literal("queued"))
                          .values(status=op.inline_literal("pending")))

def downgrade() -> None:
    jobs = table("jobs", column("id", Integer), column("status", String))
    op.execute(jobs.update().where(jobs.c.status == op.inline_literal("pending"))
                          .values(status=op.inline_literal("queued")))
```

Seed rows with `op.bulk_insert`:

```python
op.bulk_insert(jobs, [{"id": 1, "status": "pending"}, {"id": 2, "status": "pending"}])
```

Keep schema changes and data changes in separate revisions when you can — it makes review and partial rollback cleaner. Use the ad-hoc `table(...)` form, not your ORM model, so the migration is pinned to the schema as of this revision and won't break when the model evolves.

## 3. `batch_alter_table` controls — when reflection isn't enough

By default `batch_alter_table` reflects the existing table to rebuild it on SQLite. Two situations need help:

**`copy_from`** — give batch an explicit `Table` definition instead of relying on reflection (useful when reflection can't recover something, e.g. certain CHECK constraints):

```python
from sqlalchemy import Table, Column, Integer, String, MetaData

jobs_table = Table(
    "jobs", MetaData(),
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
)

with op.batch_alter_table("jobs", copy_from=jobs_table) as batch_op:
    batch_op.add_column(Column("priority", Integer, nullable=False, server_default="0"))
```

**`recreate`** — force or suppress the move-and-copy. `recreate="always"` rebuilds the table even for an op that SQLite could do in place (e.g. to apply a CHECK constraint); `recreate="never"` keeps a plain `ALTER` even on SQLite (only when you know the op is supported). Default `"auto"` recreates only when the op requires it:

```python
with op.batch_alter_table("jobs", recreate="always") as batch_op:
    batch_op.create_check_constraint("ck_jobs_priority", "priority >= 0")
```

**`naming_convention` on the batch block** — pass it explicitly if it isn't already on the `MetaData`, so the recreate can name and preserve constraints:

```python
with op.batch_alter_table("jobs", naming_convention=NAMING_CONVENTION) as batch_op:
    batch_op.drop_constraint("uq_jobs_name", type_="unique")
```

## 4. Offline mode (`--sql`) — emit SQL without a live DB

For review-gated or DBA-applied deploys, generate the SQL instead of connecting:

```bash
alembic upgrade head --sql                 # print SQL for all unapplied revisions
alembic upgrade <from>:<to> --sql > up.sql # bounded range to a file
```

Offline mode runs `env.py`'s `run_migrations_offline()` (`context.configure(url=..., literal_binds=True)`), which renders literal-bound SQL with no DB round-trip. Caveats: it can't reflect, so batch move-and-copy on SQLite and anything that depends on the live schema is limited; and `literal_binds` inlines parameters, so it's for trusted, reviewed SQL only.

## 5. Scope autogenerate with `include_object` / `include_name`

When the DB holds tables Alembic shouldn't manage (a shared schema, a third-party extension's tables), filter them out so autogenerate doesn't try to drop them. Hook these in `context.configure(...)` in `env.py`:

```python
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in {"spatial_ref_sys", "_legacy_audit"}:
        return False
    return True

context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,
    include_object=include_object,   # or include_name=... for a name-only, pre-reflection filter
)
```

`include_name` filters by name before reflection (cheaper, e.g. to restrict schemas); `include_object` filters the reflected object (richer, sees the type and the comparison target). Without one of these, an unmanaged table in the DB shows up in autogenerate as a spurious `drop_table` — review would catch it, but filtering prevents it.

## 6. Quick reference — commands

| Command | Effect |
|---|---|
| `alembic init <dir>` | scaffold `alembic.ini` + `env.py` + `versions/` |
| `alembic revision -m "msg"` | empty revision (hand-write `upgrade`/`downgrade`) |
| `alembic revision --autogenerate -m "msg"` | drafted revision (diff `target_metadata` vs DB — then REVIEW) |
| `alembic upgrade head` / `+1` | apply all / next revision |
| `alembic downgrade -1` / `base` | roll back one / everything |
| `alembic current` | revision the DB is stamped at |
| `alembic history` | revision graph, newest first |
| `alembic heads` | current head(s) — >1 means a branch |
| `alembic merge -m "msg" <a> <b>` | merge revision joining two heads |
| `alembic stamp <rev>` / `head` | mark a revision applied WITHOUT running it (baseline adoption) |
| `alembic upgrade <a>:<b> --sql` | emit SQL for a range, no live DB (offline) |
