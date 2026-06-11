---
name: alembic
description: >
  Use when running Alembic database migrations on top of a SQLAlchemy 2.x data
  layer that targets more than one dialect — SQLite, PostgreSQL, and MySQL — from
  a single migration history. Covers wiring env.py / alembic.ini to your models'
  Base.metadata (sourcing the DB URL from the environment, sync-first with a short
  async run_async_migrations note), the full revision -> autogenerate -> review ->
  upgrade/downgrade workflow, branching (history / current / heads / merge for
  multiple heads), and the load-bearing multi-dialect gotcha: SQLite cannot ALTER
  most schema, so write migrations in BATCH (move-and-copy) style — the same
  batch_alter_table code emits plain ALTER on PG/MySQL. Also owns the
  create_all-vs-Alembic decision and the baseline-stamp path off a create_all'd
  DB. Multi-dialect, portable, sync-first. Not SQLAlchemy model/engine authoring
  (see sqlalchemy), not job-queue/lease patterns (see sql-job-queue).
forge:
  status: reviewed
  forged: 2026-06-11
  reviewed: 2026-06-11
---

# `alembic` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, produces wired Alembic config + a reviewed migration script (or the relevant slice), and control returns to the caller.

## Overview

This skill teaches an agent to run **Alembic schema migrations** on top of an existing **SQLAlchemy 2.x** data layer, across **SQLite, PostgreSQL, and MySQL** from one migration history. It assumes a working `Base.metadata` already exists (that is the sibling `sqlalchemy` skill's job) and wires Alembic to it. The primary path is **sync** — the standard `run_migrations_online()` shape on a sync connection — with a short async aside. Two pieces are load-bearing: (1) **autogenerate drafts, you review** — it has documented blind spots that cause silent data loss if applied blindly; and (2) the **SQLite batch / move-and-copy** gotcha — SQLite can't `ALTER` most things, so migrations are written in `batch_alter_table` style that recreates the table on SQLite while emitting ordinary `ALTER` on PG/MySQL. This skill also owns the **`create_all()` vs Alembic** decision and the **baseline-stamp** path for adopting Alembic on an already-created database.

## When to activate

- ✅ Wiring Alembic (`env.py` + `alembic.ini`) to an existing SQLAlchemy `Base.metadata` so autogenerate can diff the live schema against your models.
- ✅ Authoring a migration — empty (`revision`) or drafted (`revision --autogenerate`) — and reviewing/editing it before applying.
- ✅ Running `upgrade` / `downgrade`, inspecting `history` / `current` / `heads`, or resolving multiple heads with `merge`.
- ✅ Writing ONE migration that must apply on SQLite, PostgreSQL, and MySQL — reaching for batch (move-and-copy) operations.
- ✅ Deciding `Base.metadata.create_all()` vs Alembic for a project, or stamping a baseline to adopt Alembic on a `create_all`'d database.

**Do NOT activate when:**

- Defining SQLAlchemy models / `Engine` / connection URLs / sessions → `sqlalchemy`. This skill only wires Alembic to a `Base.metadata` that already exists.
- Building a job queue / scheduler / lease loop on the migrated schema → `sql-job-queue`.
- Writing raw SQL DDL by hand with no version history — Alembic exists to give you that history; if you genuinely don't need it, see the `create_all()` decision in Step 6.

## Workflow

### Step 1: Initialize the migration environment

`alembic init` scaffolds the layout next to your project.

```bash
alembic init alembic        # creates alembic.ini + alembic/ (env.py, script.py.mako, versions/)
```

This gives you `alembic.ini` (config), `alembic/env.py` (the runtime hook), `alembic/script.py.mako` (the revision template), and `alembic/versions/` (where revision files land). `script_location` in `alembic.ini` points at the `alembic/` dir; `version_locations` (optional) lets you split revisions across multiple dirs.

### Step 2: Source the DB URL from the environment (don't hardcode)

The scaffolded `alembic.ini` has a literal `sqlalchemy.url = driver://...`. Do **not** commit a real URL there. Either leave it blank and set it in `env.py` from the environment, or interpolate. Setting it in `env.py` keeps one source of truth shared with the app:

```python
# alembic/env.py
import os
from alembic import context

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DB_URL"])
```

`set_main_option` overrides whatever is in `alembic.ini` at runtime, so the same migration history runs against SQLite locally and PostgreSQL/MySQL in other environments just by changing `DB_URL`.

### Step 3: Point `target_metadata` at your models' `Base.metadata`

This is the link that makes `--autogenerate` work — it diffs the live DB against the `MetaData` you hand it. Import your models' `Base` (so every table is registered on its `metadata`) and assign:

```python
# alembic/env.py (continued)
from myapp.models import Base   # your DeclarativeBase subclass — sqlalchemy sibling owns this

target_metadata = Base.metadata
```

Importing the module that defines the models is required — a table that is never imported is invisible to `target_metadata`, so autogenerate won't see it (a blind spot — Step 5).

### Step 4: The env.py online runner (sync-first) with batch + naming-convention

The scaffold ships an offline and an online runner. **Online** uses a live connection (and is the common path); **offline** emits SQL to stdout/a file without a DB (`--sql` mode), for hand-applied or review-gated deploys. Edit the online runner to enable batch mode so SQLite migrations work (Step 7), and define a `naming_convention` so batch table-recreate can reference constraints by name:

```python
# alembic/env.py (continued)
from sqlalchemy import engine_from_config, pool, MetaData

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
# Best applied on Base.metadata itself in the models module so live + autogen agree;
# shown here for visibility. If set in models: MetaData(naming_convention=NAMING_CONVENTION)

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,          # makes SQLite migrations move-and-copy (Step 7)
            compare_type=True,             # also diff column TYPE changes (still review them)
            compare_server_default=True,   # attempt server_default diffs (imperfect — Step 5)
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()   # the scaffold guards this with context.is_offline_mode()
```

`render_as_batch=True` is the global switch that wraps emitted alters in batch mode. `NullPool` is the right pool for a short-lived migration process. (The scaffold's offline runner — `run_migrations_offline()` — calls `context.configure(url=..., literal_binds=True)` and emits SQL; keep it for `--sql` deploys.)

### Step 5: Author a revision — autogenerate DRAFTS, you REVIEW

Two ways to create a revision:

```bash
alembic revision -m "add jobs table"              # EMPTY — you write upgrade()/downgrade() by hand
alembic revision --autogenerate -m "add jobs table"   # DRAFTS ops by diffing target_metadata vs DB
```

Autogenerate is a **draft generator, not a source of truth**. It compares `target_metadata` against the live DB and writes its best guess — but it has documented blind spots. **Always open the generated file and review/edit it before applying.** What autogenerate does NOT reliably detect:

- **Table / column RENAMES** — it sees a drop of the old + an add of the new. Apply that blindly and you **lose the data**. Rewrite it as `op.rename_table(...)` / a batch column rename by hand.
- **Most `server_default` changes** — even with `compare_server_default=True`, many are missed or mis-rendered.
- **`CHECK` constraints and some named constraints** — frequently not detected.
- **Some index changes and some column-TYPE changes** — `compare_type=True` helps but is not exhaustive; verify the rendered type.
- **Anything not reachable from `target_metadata`** — a model you forgot to import, or schema objects Alembic isn't told to compare (other schemas, certain object types). Out of sight, out of diff.

A reviewed autogenerated file looks like this — note the explicit, reversible `downgrade()`:

```python
"""add jobs table"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = None        # first migration; otherwise the prior revision id
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("data", sa.JSON(), nullable=True),
    )
    op.create_index("ix_jobs_name", "jobs", ["name"])

def downgrade() -> None:
    op.drop_index("ix_jobs_name", table_name="jobs")
    op.drop_table("jobs")
```

Write `downgrade()` as the true inverse of `upgrade()` — reverse order, reverse each op. A migration with a wrong or `pass` downgrade can't be rolled back. See `references/alembic-extras.md` for a rename done safely and a data migration.

### Step 6: Apply / roll back / inspect

```bash
alembic upgrade head        # apply every unapplied revision up to the latest
alembic upgrade +1          # apply the next one only
alembic downgrade -1        # roll back the most recent revision
alembic downgrade base      # roll back everything (empty schema)

alembic current             # which revision the DB is stamped at
alembic history             # the revision graph, newest first
alembic heads               # the current head(s) — more than one means a branch to merge
```

### Step 7: Multi-dialect — write migrations in BATCH style

This is the load-bearing multi-dialect rule. **SQLite cannot `ALTER` most schema elements** — you cannot drop a column, alter a column's type/nullability, or add most constraints with a plain `ALTER TABLE`. Alembic's **batch operations** work around this with **move-and-copy**: create a new table with the target schema, `INSERT ... SELECT` the rows across, drop the old table, then rename the new one into place. On **PostgreSQL and MySQL the exact same batch code emits ordinary `ALTER` statements** — so writing every alter in batch style gives you ONE migration script that applies on all three dialects.

```python
def upgrade() -> None:
    # Same code path on all three; SQLite does move-and-copy, PG/MySQL do ALTER.
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.add_column(sa.Column("priority", sa.Integer(), nullable=False, server_default="0"))
        batch_op.alter_column("name", existing_type=sa.String(200), nullable=True)
        batch_op.create_unique_constraint("uq_jobs_name", ["name"])

def downgrade() -> None:
    with op.batch_alter_table("jobs") as batch_op:
        batch_op.drop_constraint("uq_jobs_name", type_="unique")
        batch_op.alter_column("name", existing_type=sa.String(200), nullable=False)
        batch_op.drop_column("priority")
```

`render_as_batch=True` (Step 4) makes autogenerate emit `batch_alter_table` blocks for you. The **`naming_convention`** (Step 4) is what lets the SQLite move-and-copy recreate the table with its constraints intact — without named constraints, the recreate can drop unnamed ones. When reviewing the emitted SQL, expect a `CREATE TABLE _alembic_tmp_... / INSERT ... SELECT / DROP / ALTER ... RENAME` sequence on SQLite and a single `ALTER TABLE` on PG/MySQL. See `references/alembic-extras.md` for `batch_alter_table(..., copy_from=...)` when reflection isn't enough and for the recreate-mode controls.

### Step 8: Branching — resolve multiple heads with `merge`

When two people (or two feature branches) each add a revision off the same parent, `alembic heads` shows **two heads** and `upgrade head` errors (ambiguous). Stitch them with a merge revision — it has both as parents and applies no schema change itself:

```bash
alembic heads                              # shows e.g. two head ids: rev_a, rev_b
alembic merge -m "merge a and b" rev_a rev_b
alembic upgrade head                       # now unambiguous
```

### Step 9: Async note (short)

For an **async** SQLAlchemy stack, migrations are still commonly run **sync** — the simplest path is to point Alembic at a sync driver URL and use the Step 4 runner unchanged. If you must drive an async engine, `env.py`'s online runner becomes:

```python
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)   # greenlet bridge to Alembic's sync context
    await connectable.dispose()

asyncio.run(run_async_migrations())
```

`run_sync(do_run_migrations)` hops from the async connection into Alembic's sync migration context via the greenlet bridge. That's the only async-specific piece; everything else (revisions, batch, review) is identical.

## Rules

**Hard rules (never violate):**

- **Autogenerate drafts; you review and edit every generated script before applying.** Never `upgrade` an unreviewed autogenerated revision — renames and constraint changes will silently lose data.
- **Write migrations in batch style when SQLite is a target.** `render_as_batch=True` + `op.batch_alter_table(...)` for any alter that SQLite can't do as a plain `ALTER`. The same code stays correct on PG/MySQL.
- **Set `target_metadata = Base.metadata` and import the models** so autogenerate can see every table. An un-imported table is invisible.
- **Source the DB URL from the environment**, not a committed `alembic.ini` literal — one history, many dialects/environments.
- **Every `upgrade()` has a true-inverse `downgrade()`.** No `pass` downgrades on a reversible op.
- **Use a `naming_convention`** so batch move-and-copy on SQLite can reference and preserve named constraints.

**Preferences (override-able):**

- Prefer the **sync** runner; reach for the async `run_async_migrations` shape only when a sync driver URL genuinely isn't available.
- Prefer `--autogenerate` to seed a revision, then hand-edit — over writing ops from scratch — except for pure data migrations (write those by hand).
- Keep `compare_type=True` / `compare_server_default=True` on for better diffs, but treat their output as a draft, not a guarantee.
- Use `NullPool` for the migration process — it's short-lived and shouldn't hold a pool.

## Gotchas

- **Autogenerate sees a rename as drop+add → data loss.** The single highest-value review check. If a column/table was renamed, the generated `drop_column`+`add_column` (or `drop_table`+`create_table`) destroys the data. Rewrite as `op.rename_table(...)` or a batch `alter_column(..., new_column_name=...)`.
- **A new model that isn't imported produces an empty autogenerate.** Autogenerate "sees nothing to do" because the table never registered on `target_metadata`. Import the model module in (or before) `env.py`.
- **SQLite `ALTER` failures without batch.** `add_column` with some constraints, any `drop_column`/`alter_column`, most `add_constraint` raise on SQLite if not wrapped in `batch_alter_table`. The error often surfaces only when the migration actually runs on SQLite, not on the PG you developed against. Turn on `render_as_batch=True` from the start.
- **Unnamed constraints vanish on SQLite batch recreate.** The move-and-copy recreate rebuilds the table; constraints Alembic can't name (no `naming_convention`) may not survive. Define the convention before you have data to lose.
- **`alembic upgrade head` errors with "multiple heads".** Two unmerged branches. `alembic heads` to see them, `alembic merge` to join them (Step 8). Not a corruption — just an unresolved branch.
- **`server_default` diffs are unreliable.** Even with `compare_server_default=True`, a changed default is often missed or rendered wrong. Verify defaults by hand; don't trust autogenerate here.
- **`downgrade base` wipes the schema.** It runs every `downgrade()` to empty. Fine in dev, destructive in prod — know which DB `DB_URL` points at before running it.

## Anti-patterns

- **Don't apply an autogenerated migration without reading it** because "autogenerate is usually right" — its blind spots (renames, server defaults, CHECK/named constraints) are exactly the data-destroying cases.
- **Don't write a plain `op.alter_column` / `op.drop_column`** and assume it'll run everywhere "because it works on Postgres" — it raises on SQLite. Use `batch_alter_table`.
- **Don't ship `Base.metadata.create_all()` as your migration story** because "it's simpler" — it has no version history, no incremental change, no downgrade. See the decision below; once a schema is shipped, it's Alembic.
- **Don't hardcode the production URL in `alembic.ini`** because "it's just config" — it leaks a credential and pins one dialect. Source it from the environment.
- **Don't leave `downgrade()` as `pass`** because "we'll never roll back" — a non-reversible migration blocks every later rollback through it.
- **Don't hand-merge two heads by editing `down_revision`** — use `alembic merge`, which records both parents correctly.

## `create_all()` vs Alembic — the decision (this skill owns it)

`Base.metadata.create_all(engine)` emits `CREATE TABLE` for the current model state in one shot. It is the right call **only** for: greenfield / not-yet-shipped schemas, throwaway databases, and **test/dev bootstrap** (the `sqlalchemy` sibling uses it exactly there). Its limits are fatal for anything shipped: **no version history, no incremental change, no downgrade** — it can only create from scratch, never *evolve*.

Reach for **Alembic** the moment the schema is **shipped, runs in multiple environments, or evolves over time** (a DAG of changes a team applies in order). That's the whole point of a migration history.

**Adopting Alembic on a database that was built with `create_all()`** — don't re-run the creation. Instead:

1. Initialize Alembic (Steps 1–4) and author a **baseline** migration whose `upgrade()` creates the *current* schema (autogenerate against an empty DB, or hand-write it to match what `create_all` produced).
2. On the **existing** `create_all`'d DB, run `alembic stamp head` — this records the DB as already at the baseline revision **without running it** (no `CREATE TABLE` re-executed).
3. From then on, every change is a new revision applied with `upgrade`.

`alembic stamp <rev>` writes the `alembic_version` row to mark a revision as applied without executing its body — the bridge from an unmanaged `create_all`'d DB to a managed history.

## Output

Wired Alembic configuration (`alembic.ini` + an `env.py` whose `target_metadata = Base.metadata`, DB URL sourced from the environment, `render_as_batch=True`, and a `naming_convention`) plus reviewed, reversible revision files under `versions/` — written in batch style so one history applies on SQLite, PostgreSQL, and MySQL. The artifact is consumed by the next layer: a deploy step that runs `alembic upgrade head`, or a higher-level pattern (e.g. `sql-job-queue`) that builds on the now-migrated schema.

## Related

- `sqlalchemy` — the data layer this sits on top of: the `DeclarativeBase`/`Mapped` models, `Engine`/URL, sessions, and the cross-dialect ORM gotchas. This skill assumes its `Base.metadata` exists and only wires Alembic to it; `sqlalchemy` uses `create_all()` for dev/test bootstrap and defers the managed-change decision here.
- `sql-job-queue` — job-store/scheduler patterns (ready-set query, atomic lease, fair-share) built on a migrated schema. This skill produces the schema history; it does not teach the queue.
- `pydantic-v2` — app-boundary validation (not DB schema or migrations).

## Progressive disclosure

- `references/alembic-extras.md` — fuller worked migrations: a safe rename (preserving data), a data migration via `op.bulk_insert` / `op.execute`, `batch_alter_table(..., copy_from=..., recreate=...)` for when reflection isn't enough, offline `--sql` mode, and `include_object`/`include_name` to scope autogenerate. **Load when** the in-body snippet isn't enough for a specific migration shape.
- `references/sources.md` — research provenance for this skill. **Load when** verifying a claim's origin or during a fresh review.

## Body budget

- `description` ≤ 1,024 chars.
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
