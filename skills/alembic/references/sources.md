# Sources — research provenance

Forged 2026-06-11 via `skill-forge`. Topic: Alembic database migrations on a SQLAlchemy 2.x data layer, multi-dialect (SQLite + PostgreSQL + MySQL), sync-first. Targets Alembic 1.18 on SQLAlchemy 2.x. Every fact is paraphrased from the sources below — no text copied. All external reads were intended to pass through `external-content-sanitizer` (§5).

## Primary grounding — official Alembic docs

`alembic.sqlalchemy.org/en/latest` (the Alembic 1.x documentation set). The specific pages that ground each claim:

- **Tutorial / "The Migration Environment"** — `alembic init <dir>` scaffold (`alembic.ini`, `env.py`, `script.py.mako`, `versions/`), `script_location` / `version_locations`, `sqlalchemy.url`, `config.set_main_option("sqlalchemy.url", ...)`, online vs offline modes (`run_migrations_online()` on a live connection vs `run_migrations_offline()` emitting SQL with `literal_binds`). Grounds Steps 1–4 and the offline `--sql` recipe.
- **"Auto Generating Migrations"** — `alembic revision --autogenerate` diffs `target_metadata` against the live DB; `compare_type` / `compare_server_default` config; `include_object` / `include_name` filters. Grounds Step 5 and extras §5.
- **"What does Autogenerate Detect (and what does it not detect?)"** — the documented blind spots: column/table **renames** are seen as drop+add; **server_default** changes mostly not detected; **CHECK** and some named constraints not detected; some index and type changes need `compare_type`; anything outside `target_metadata` is invisible. Grounds the load-bearing "autogenerate drafts, you review" rule + the Gotchas/Anti-patterns.
- **"Running Batch ('Move and Copy') Migrations for SQLite and Other Databases"** — SQLite cannot `ALTER` most schema; `op.batch_alter_table(...)` does move-and-copy (create tmp table, `INSERT ... SELECT`, drop, rename); `render_as_batch=True` in `context.configure`; the same batch code emits ordinary `ALTER` on PG/MySQL; `copy_from`, `recreate` ("auto"/"always"/"never"), and the importance of a `naming_convention` so the recreate preserves named constraints. Grounds Step 7 + extras §3.
- **"The Naming Convention"** (Alembic + SQLAlchemy `MetaData(naming_convention=...)`) — the `ix`/`uq`/`ck`/`fk`/`pk` token patterns so constraints have deterministic names for batch recreate. Grounds the Step 4 convention.
- **Operations reference (`alembic.op`)** — `op.create_table` / `drop_table` / `rename_table` / `add_column` / `drop_column` / `alter_column` (incl. `new_column_name`, `existing_type`), `create_index`, `create_unique_constraint`, `create_check_constraint`, `bulk_insert`, `execute`, `inline_literal`. Grounds the revision examples + extras §1–§3.
- **"Working with Branches" / commands** — `upgrade` (`head`/`+1`), `downgrade` (`-1`/`base`), `current`, `history`, `heads`, `merge` for multiple heads; `stamp <rev>`/`head` marking a revision applied without running it. Grounds Step 6, Step 8, the baseline-stamp path, and the extras command table.
- **"Using Asyncio with Alembic"** — the async `env.py` shape: `async_engine_from_config`, `asyncio.run(run_async_migrations())`, `await connection.run_sync(do_run_migrations)` greenlet bridge to the sync migration context; migrations are commonly run sync even for async apps. Grounds Step 9.
- **SQLAlchemy `MetaData.create_all`** (`docs.sqlalchemy.org`) — documented as a one-shot `CREATE TABLE` convenience (no versioning / incremental change / downgrade), i.e. dev/test/greenfield bootstrap. Grounds the create_all-vs-Alembic decision + baseline-stamp adoption path.

## find-skills candidates (inputs only — neither adopted)

Per the project's sourcing dossier, `find-skills` surfaced **no clean, official, ≥1K adoptable Alembic skill**; the two gate-relevant hits were used as **source material only**, never installed verbatim:

- `manutej/luxor-claude-marketplace@alembic` (325 installs, **sub-1K**) — Alembic command/workflow source material.
- `wispbit-ai/skills@sqlalchemy-alembic-expert-best-practices-code-review` (~1K installs) — **code-review framed** and unofficial; only its **Alembic half** was mined (its SQLAlchemy half went to the sibling `sqlalchemy` skill), reframed from review rules into authoring guidance.

Both are below the adoption bar (one sub-1K, one wrong-framing/unofficial), so this skill was **synthesized fresh** from the official Alembic 1.18 docs and the design-reviewed spec rather than adopted.

## Sibling skills referenced (in-repo, not duplicated)

`sqlalchemy` (the data layer: `DeclarativeBase`/`Mapped` models, `Engine`/URL, sessions, cross-dialect ORM gotchas — provides the `Base.metadata` this skill wires Alembic to, and uses `create_all()` for dev/test bootstrap) and `sql-job-queue` (job-store/scheduler/lease patterns built on a migrated schema). Their scope is referenced in the SKILL body's `## Related` and the "Do NOT activate" list; their content is not restated here.

## Degradation note

This synthesis ran from the handed-in verified-facts brief and the design-reviewed spec for this skill, not a live forge-worker fetch. Every API name, command, and mechanism traces to the verified-facts brief, which was itself grounded against the official Alembic 1.18 docs. A fresh reviewer should spot-check the load-bearing claims against the live Alembic docs before flipping `forge.status` to `reviewed`:

- the **batch / move-and-copy** mechanism and that the SAME batch code emits ordinary `ALTER` on PG/MySQL;
- the **autogenerate blind spots** (renames seen as drop+add, server_default mostly undetected, CHECK/named constraints, out-of-`target_metadata`);
- the **`render_as_batch` / `naming_convention`** interaction for constraint preservation on SQLite recreate;
- the **`stamp`** baseline-adoption semantics (records a revision applied without running it);
- the async **`run_sync(do_run_migrations)`** greenlet bridge shape.
