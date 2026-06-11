# Sources — research provenance

Forged 2026-06-11 via `skill-forge`. Topic: SQLAlchemy 2.x (2.0/2.1) as a portable multi-dialect (SQLite + PostgreSQL + MySQL) data layer, ORM-first and sync-first. Every fact is paraphrased from the sources below — no text copied. All external reads were intended to pass through `external-content-sanitizer` (§5).

## Primary grounding — official SQLAlchemy 2.1 docs

`docs.sqlalchemy.org/en/21` (the 2.1 documentation set). The specific pages that ground each claim:

- **ORM Quickstart / Declarative** — `class Base(DeclarativeBase)`, `Mapped[...]` + `mapped_column(...)` typed models, nullability derived from `Mapped[str]` vs `Mapped[str | None]`, `relationship(back_populates=...)`. Grounds Steps 3–4 and the "2.x typed ORM only" hard rule.
- **2.0-style querying** — `select()` + `session.execute(...).scalars().all()`, `session.get(Model, pk)`. Grounds Step 4 reads.
- **Engine / connection URL** — `create_engine`, the `dialect+driver://` URL form, SQLite file vs `:memory:` slash semantics, `create_async_engine`. Grounds Steps 1–2 and Step 6.
- **Connection pooling** — `QueuePool` (2.0+ default), `SingletonThreadPool`, `StaticPool`, `pool_pre_ping`, `pool_size`/`max_overflow`, and the per-dialect default-pool differences. Grounds Step 2, the pool table in extras, and the Gotchas.
- **Session / transaction** — `Session`, `sessionmaker`, `with Session(engine) as s, s.begin():`, one-engine-per-process, short-lived non-shared sessions. Grounds Step 4 and the session hard rules.
- **Asyncio extension** — `create_async_engine`, `AsyncSession`, `async_sessionmaker`, `await session.execute(...)`, the greenlet bridge, `expire_on_commit=False` and the lazy-load-after-commit trap. Grounds Step 6.
- **Dialects — PostgreSQL** — `with_for_update` options (`skip_locked`, `nowait`, `read`, `of`, `key_share`), `dialects.postgresql.insert(...).on_conflict_do_update`/`on_conflict_do_nothing` with `.excluded`, `JSONB`, IDENTITY/SERIAL, READ COMMITTED default, `isolation_level`. Grounds Step 7 + extras.
- **Dialects — MySQL** — `dialects.mysql.insert(...).on_duplicate_key_update` with `.inserted`, `SELECT ... FOR UPDATE SKIP LOCKED` requiring MySQL 8.0+ InnoDB, AUTO_INCREMENT, REPEATABLE READ default. Grounds Step 7 row-locking matrix + upsert branch.
- **Dialects — SQLite** — `dialects.sqlite.insert(...).on_conflict_do_update` (same API as PG), no row-level locks (file/DB-level locking → `with_for_update` is a no-op), JSON-as-TEXT via JSON1, ROWID autoincrement, limited isolation modes, `StaticPool` shared-in-memory pattern, the `sqlite:///` vs `sqlite:////` slash rule. Grounds Step 7 + the SQLite Gotchas.
- **Driver/DBAPI support pages** — the recommended/maintained driver per dialect: `sqlite3`(pysqlite) / `aiosqlite`; `psycopg` (v3) / `asyncpg` (+ `psycopg2` legacy); `PyMySQL` / `aiomysql` (+ `mysqlclient`, `asyncmy`). Grounds the Step 5 driver matrix and its rationales.
- **`MetaData.create_all`** — documented as a convenience for emitting `CREATE TABLE` (dev/test bootstrap); managed change is Alembic's job. Grounds the `create_all()`-is-dev-only rule.

## find-skills candidates (inputs only — neither adopted)

Per the project's sourcing dossier, `find-skills` surfaced no clean, official, ≥1K adoptable SQLAlchemy authoring skill. The two gate-relevant hits were used as **source material only**, never installed verbatim:

- `wispbit-ai/skills@sqlalchemy-alembic-expert-best-practices-code-review` (~1K installs) — **code-review framed** and unofficial; its best-practice rules were reframed as authoring guidance and its Alembic half deliberately dropped (→ sibling `alembic` skill).
- `bobmatnyc/claude-mpm-skills@sqlalchemy-orm` (883 installs, **sub-1K**) — ORM-pattern source material.

Both are below the adoption bar (one wrong-framing/unofficial, one sub-1K), so this skill was **synthesized fresh** from the official 2.1 docs and design-reviewed spec rather than adopted.

## Sibling skills referenced (in-repo, not duplicated)

`alembic` (migrations / managed schema change), `sql-job-queue` (job-store/scheduler/lease patterns + the SQLite `BEGIN IMMEDIATE` claim strategy), `pydantic-v2` (app-boundary validation). Their scope is referenced in the SKILL body's `## Related` and the boundary "Do NOT activate" list; their content is not restated here.

## Degradation note

This synthesis ran from the handed-in verified-facts brief and the design-reviewed spec for this skill, not a live forge-worker fetch. Every API name, URL form, dialect default, and support-matrix entry traces to the verified-facts brief, which was itself grounded against the official 2.1 docs. A fresh reviewer should spot-check the load-bearing claims (the `with_for_update` SQLite no-op, MySQL 8.0+ `SKIP LOCKED` floor, the `excluded` vs `inserted` upsert attributes, and the dialect isolation defaults) against the live 2.1 docs before flipping `forge.status` to `reviewed`.
