---
name: sql-job-queue
description: >
  Use when building a DB-backed job queue / task scheduler on SQLAlchemy 2.x
  whose readiness is dependency-driven, whose jobs are long-running and stateful,
  and whose only durable substrate is the relational DB — single box, embeddable,
  no broker, multi-dialect (SQLite / PostgreSQL / MySQL). Covers the generic
  jobs/job_deps model, the ready-set query, the per-dialect atomic lease (FOR
  UPDATE SKIP LOCKED on PostgreSQL + MySQL 8 vs BEGIN IMMEDIATE on SQLite, with
  dialect detection), crash-resume via heartbeat + lease expiry + stale-lease
  reclaim, the hung-but-alive per-dispatch timeout, weighted fair-share over
  group_key, the scan→rank→lease→dispatch→persist→reclaim tick loop, polling vs
  LISTEN/NOTIFY wake, and the at-least-once idempotency contract. Keywords: job
  queue, task scheduler, ready-set, SKIP LOCKED, lease, crash-resume,
  multi-dialect, SQLAlchemy, background jobs. Sync-first. Not the SQLAlchemy data
  layer or locking primitive (sqlalchemy), not migrations (alembic).
forge:
  status: reviewed
  forged: 2026-06-11
  reviewed: 2026-06-11
---

# `sql-job-queue` — SKILL.md

> **Variant:** standard · **When to use:** the skill is invoked, produces a working DB-backed ready-set scheduler (or the relevant slice of one) on SQLAlchemy 2.x, and control returns to the caller.

## Overview

This skill teaches an agent to build a **DB-backed ready-set job scheduler on SQLAlchemy 2.x** — a thin tick loop you own, where the relational database is the *only* durable substrate (no broker, no second source of truth) and a job becomes runnable as its dependencies finish. It is for **long-running, stateful** jobs whose concurrency is capped by **external** limits (resources / rate / budget), running on a **single box** as an **embeddable** library, portable across **SQLite, PostgreSQL, and MySQL**. The load-bearing content is the **per-dialect atomic lease** — `SELECT ... FOR UPDATE SKIP LOCKED` on PostgreSQL and MySQL 8+ vs a `BEGIN IMMEDIATE` write-lock claim on SQLite — and the crash-resume / fair-share / idempotency patterns layered on top of it. It is **sync-first**: the worked path is synchronous, async is a short aside. It builds *on* the `sqlalchemy` sibling's data layer and locking primitive — it does not re-teach them.

## When to activate

- ✅ Building an embeddable, single-box work queue whose readiness is **dependency-driven** (a DAG of jobs, each runnable once its upstreams are `done`), persisted in a relational DB, portable across SQLite/PostgreSQL/MySQL.
- ✅ Composing the **atomic claim** that stops two workers (processes / threads / async tasks) on one box from dispatching the same job — and needing the per-dialect branch.
- ✅ Making the queue **crash-safe with no broker** — heartbeat, lease expiry, stale-lease reclaim, and bounding a hung job.
- ✅ Allocating slots across job groups by **weighted fair-share**, or building the scan→rank→lease→dispatch→persist→reclaim **tick loop**.

**Do NOT activate when:**

- You need the SQLAlchemy **data layer** itself — engine/URL, `DeclarativeBase`/`Mapped`, sessions, JSON columns, or the `with_for_update(skip_locked=...)` **primitive** + its dialect support matrix → `sqlalchemy`. This skill *composes* that primitive; it does not teach it.
- You need schema **migrations** → `alembic`.
- A **broker** fits — short fire-and-forget tasks, static enqueue, multi-machine fan-out → Celery / Dramatiq / RabbitMQ (see Anti-patterns for why they're wrong *here*).
- You need a **time-triggered** scheduler (cron-like) → APScheduler; or a heavy **orchestrator** platform → Airflow / Prefect / Dagster.

## Workflow

### Step 1: Confirm the shape — is this actually the right tool?

Build a DB-backed ready-set loop **only** when the shape matches: long-running stateful jobs · dynamic dependency-driven readiness · concurrency capped by *external* limits (not a fixed worker pool) · single box · embeddable · the DB is the sole durable state. If the work is short fire-and-forget tasks with static enqueue and you'd accept a second datastore, a broker is simpler — don't build this. The wrong-tool reasoning is in **Anti-patterns**; the borrowed core (SKIP LOCKED + lease) comes from the Postgres-native queues (Procrastinate, PGQueuer) — you re-host it on a thin portable loop.

### Step 2: Define the data model — `jobs` + `job_deps`

One generic `jobs` row plus a `job_deps` edge table expressing the acyclic DAG. Keep it **project-agnostic** — no domain columns.

```python
from datetime import datetime
from sqlalchemy import ForeignKey, Index, JSON, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]                                   # handler key — which function runs it
    args: Mapped[dict] = mapped_column(JSON)            # input payload
    result: Mapped[dict | None] = mapped_column(JSON)   # output, written atomically with `done`
    state: Mapped[str] = mapped_column(default="ready") # ready|leased|running|done|failed
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"))  # container; leaves run
    group_key: Mapped[str]                              # fair-share dimension
    weight: Mapped[int] = mapped_column(default=1)      # fair-share weight
    lease_owner: Mapped[str | None]                     # worker id holding the claim
    lease_expires: Mapped[datetime | None]             # claim TTL — reclaim past this
    in_flight: Mapped[bool] = mapped_column(default=False)
    heartbeat_at: Mapped[datetime | None]              # last liveness bump
    run_after: Mapped[datetime | None]                 # time gate — not ready until now >= this
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Partial/filtered index so the per-tick scan stays cheap when the table
    # holds many done/parked rows. SQLite + PG honor the WHERE; MySQL ignores it
    # (no partial indexes) and falls back to a plain (state, run_after) index.
    __table_args__ = (
        Index("ix_jobs_ready", "state", "run_after",
              # text() predicate, not a bare `state` ref — the mapped column isn't
              # reliably resolvable at class-body time for the partial-index WHERE.
              postgresql_where=text("state = 'ready'"),
              sqlite_where=text("state = 'ready'")),
    )

class JobDep(Base):
    __tablename__ = "job_deps"
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
    depends_on_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), primary_key=True)
```

- **`parent_id` = container.** A job with children is a **container** — it never dispatches; it **rolls up** (transitions to `done`/`failed`) when its last child completes. Only **leaves** run. The roll-up is **event-driven** — computed on a child's completion, **not** inside the ready-set query (which only *filters out* containers, so the per-tick scan never walks the whole DAG).
- **`job_deps`** is the readiness DAG: a job is dependency-ready only when **every** row pointing at it (`depends_on_id`) is `done`.
- **The partial index** is what keeps the scan O(ready-set), not O(table). On MySQL — no partial indexes — accept a plain composite index; the `state` predicate still prunes well.

### Step 3: The ready-set query — what is runnable *right now*

A job is in the ready-set when it is: state-actionable (`ready`), **dependency-complete** (no `job_deps` row points at a non-`done` upstream), **leaf-only** (has no children), **time-gated open** (`run_after IS NULL OR run_after <= now`), and **not live-leased** (no unexpired lease). Express it portably; **defer the locking** to Step 4 (the query *selects candidates*; the lease *claims one atomically*).

```python
from sqlalchemy import and_, exists, not_, or_, select

def ready_set(now):
    Child = Job.__table__.alias("child")
    Dep = JobDep.__table__
    Up = Job.__table__.alias("up")

    has_child = exists().where(Child.c.parent_id == Job.id)
    has_open_dep = exists().where(and_(
        Dep.c.job_id == Job.id,
        Up.c.id == Dep.c.depends_on_id,
        Up.c.state != "done",
    ))
    return (
        select(Job)
        .where(Job.state == "ready")
        .where(or_(Job.run_after.is_(None), Job.run_after <= now))
        .where(not_(has_child))           # leaf-only — containers roll up, never dispatch
        .where(not_(has_open_dep))        # all deps done
        .where(or_(Job.lease_expires.is_(None), Job.lease_expires <= now))  # no live lease
        .order_by(Job.id)
    )
```

This is dialect-portable SQLAlchemy. The one place dialects diverge is the **claim** in Step 4.

### Step 4: The atomic lease — THREE full per-dialect branches (load-bearing)

This is the single most load-bearing portability point. The claim must be **atomic**: one transaction reads a ready row and writes `lease_owner` + `lease_expires` + `in_flight` before any other worker can. The locking *primitive* (`with_for_update(skip_locked=...)`) and its support matrix are the `sqlalchemy` sibling's — assume them. This skill teaches the **composition**: the claim transaction, **dialect detection**, and the **double-dispatch guard**. Detect the dialect once and branch:

```python
def claim(engine, worker_id, ttl):
    name = engine.dialect.name          # "postgresql" | "mysql" | "sqlite"
    if name == "postgresql":
        return _claim_pg(engine, worker_id, ttl)
    if name == "mysql":
        return _claim_mysql(engine, worker_id, ttl)
    if name == "sqlite":
        return _claim_sqlite(engine, worker_id, ttl)
    raise RuntimeError(f"unsupported dialect: {name}")
```

**Branch 1 — PostgreSQL: `SELECT ... FOR UPDATE SKIP LOCKED`.** Grab a ready row, skipping any row another claim already holds (no blocking), then flip it to leased in the same transaction. PostgreSQL's default isolation is **READ COMMITTED**, which is exactly what a claim wants — each statement sees freshly-committed rows.

```python
from datetime import timedelta
from sqlalchemy import update
from sqlalchemy.orm import Session

def _claim_pg(engine, worker_id, ttl):
    now = _now()
    with Session(engine) as s, s.begin():               # one atomic claim transaction
        row = s.execute(
            ready_set(now).with_for_update(skip_locked=True).limit(1)
        ).scalars().first()
        if row is None:
            return None
        s.execute(
            update(Job).where(Job.id == row.id).values(
                state="leased", lease_owner=worker_id,
                lease_expires=now + timedelta(seconds=ttl),
                in_flight=True, heartbeat_at=now,
            )
        )
        return row.id
```

`FOR UPDATE SKIP LOCKED` is the double-dispatch guard: two concurrent claims lock **disjoint** rows, so they can never pick the same job.

**Branch 2 — MySQL 8.0+ (its own worked branch).** Same `FOR UPDATE SKIP LOCKED` statement, but with MySQL-specific caveats that bite:

- **Requires InnoDB + MySQL 8.0+.** On 5.7 `SKIP LOCKED` is a **syntax error**, not a silent no-op. Gate on the version.
- **Default isolation is `REPEATABLE READ`** (vs PostgreSQL's `READ COMMITTED`). Under REPEATABLE READ a plain `SELECT` reads a consistent snapshot taken at transaction start — so it can *miss* rows another transaction committed after your txn began, and the claim can look "empty" while work waits. **Set `READ COMMITTED` for the claim transaction** so each statement sees fresh commits. (`FOR UPDATE` itself reads the latest committed row — "current read" — but pinning READ COMMITTED keeps the whole claim txn consistent with the PG branch.)
- **SQLAlchemy's share-mode emit is rejected by MySQL.** `with_for_update(read=True, skip_locked=True)` emits the legacy `LOCK IN SHARE MODE SKIP LOCKED`, which MySQL rejects (SQLAlchemy issue #10134) — *not* a MySQL SQL-level invalidity (plain `FOR SHARE SKIP LOCKED` is valid on MySQL 8). Use the exclusive `FOR UPDATE` form for the claim regardless — a shared lock wouldn't give you an exclusive claim anyway.

```python
def _claim_mysql(engine, worker_id, ttl):
    now = _now()
    # READ COMMITTED for THIS txn — override MySQL's REPEATABLE READ default so
    # the claim sees rows committed after the txn began (see caveat above).
    with engine.connect().execution_options(isolation_level="READ COMMITTED") as conn:
        with conn.begin(), Session(bind=conn) as s:
            row = s.execute(
                ready_set(now).with_for_update(skip_locked=True).limit(1)  # exclusive — NOT read=True
            ).scalars().first()
            if row is None:
                return None
            s.execute(update(Job).where(Job.id == row.id).values(
                state="leased", lease_owner=worker_id,
                lease_expires=now + timedelta(seconds=ttl),
                in_flight=True, heartbeat_at=now,
            ))
            return row.id
```

**Branch 3 — SQLite: `BEGIN IMMEDIATE`.** SQLite has **no row-level locks** — locking is **database/file-level**, and `with_for_update` is a silent **no-op** there (it does not error, it just doesn't lock). So two workers could both read the same ready row and both claim it. The fix: take SQLite's **write lock up front** with `BEGIN IMMEDIATE`, which reserves the DB for writing at transaction start. The whole claim then serializes — only one worker holds the write lock at a time; the others get `SQLITE_BUSY` and retry the tick.

```python
from sqlalchemy import text

def _claim_sqlite(engine, worker_id, ttl):
    now = _now()
    with engine.connect() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")          # reserve the write lock NOW
        try:
            row = conn.execute(ready_set(now).limit(1)).first()  # no with_for_update — no-op on SQLite
            if row is None:
                conn.exec_driver_sql("COMMIT")
                return None
            job_id = row.id
            conn.execute(
                text("UPDATE jobs SET state='leased', lease_owner=:o, "
                     "lease_expires=:e, in_flight=1, heartbeat_at=:h WHERE id=:i"),
                {"o": worker_id, "e": now + timedelta(seconds=ttl), "h": now, "i": job_id},
            )
            conn.exec_driver_sql("COMMIT")
            return job_id
        except Exception:
            conn.exec_driver_sql("ROLLBACK")
            raise
```

A fuller end-to-end scheduler showing all three branches plus the tick loop lives in `references/sql-job-queue-extras.md`.

### Step 5: Crash-resume — heartbeat, lease expiry, reclaim, hung-job timeout

The lease is what makes the queue **crash-safe with no broker**. Two distinct failure modes:

- **Dead worker (crash / kill).** While a job runs, its worker **renews the lease** — periodically bumps `lease_expires` (and `heartbeat_at`) forward. A dead worker stops renewing; its `lease_expires` falls into the past. A **stale-lease reclaim sweep** (run every tick) returns expired-lease jobs to the ready-set:

```python
def reclaim(engine, now):
    with Session(engine) as s, s.begin():
        s.execute(update(Job).where(
            Job.state.in_(("leased", "running")),
            Job.lease_expires < now,
        ).values(state="ready", lease_owner=None, in_flight=False))
```

- **Hung-but-alive worker (distinct failure).** The worker is *still renewing* the lease, but the **job itself is wedged** (stuck network call, infinite loop). The reclaim sweep never fires because the lease never expires. Bound it with a **per-dispatch timeout**: when a job has been `running` longer than its allowed duration, time it out and fail/reclaim it — independent of the lease. The escalation/park *policy* on a timed-out job is the consumer's concern, not this skill's.

**The TTL-vs-duration tension.** Lease TTL too short → a live long job gets **prematurely reclaimed** and double-dispatched while still running. Too long → a dead worker's job sits unrecoverable for ages. Pick TTL comfortably above one heartbeat interval but well below "users notice the stall"; the heartbeat is what lets TTL be short without false reclaims.

### Step 6: Weighted fair-share — don't let one group starve the rest

When the ready-set spans multiple `group_key`s, allocate the available slots **proportional to `weight`** rather than strict priority — a busy high-weight group must not starve a low-weight one. Concrete rule: given `free` slots and the ready-set grouped by `group_key`, give each present group `round(free * weight_g / sum(weight))` slots (at least 1 each so nobody is fully starved), then fill any remainder by largest fractional leftover.

```python
def fair_share(ready_rows, free):
    groups = {}
    for r in ready_rows:                                 # bucket the ready-set by group
        groups.setdefault(r.group_key, []).append(r)
    weights = {g: rows[0].weight for g, rows in groups.items()}
    total = sum(weights.values())
    chosen = []
    for g, rows in groups.items():
        n = max(1, round(free * weights[g] / total))
        chosen.extend(rows[:n])
    return chosen[:free]                                 # cap at the slot budget
```

The DAG bounds parallelism naturally; fair-share only decides *which* ready jobs win the scarce slots.

### Step 7: The tick loop — scan → rank → lease → dispatch → persist → reclaim

One tick re-evaluates the whole picture; nothing is enqueued statically.

```python
def tick(engine, worker_id, handlers, ttl, max_concurrency):
    now = _now()
    reclaim(engine, now)                                          # 1. RECLAIM stale leases
    free = max_concurrency - count_in_flight(engine)             # cap = min(external limits)
    if free <= 0:
        return
    with Session(engine) as s:
        candidates = s.execute(ready_set(now)).scalars().all()  # 2. SCAN ready-set
    for job in fair_share(candidates, free):                     # 3. RANK by fair-share
        job_id = claim(engine, worker_id, ttl)                   # 4. LEASE (atomic, per-dialect)
        if job_id is None:
            break                                                # someone else took them
        dispatch(engine, job_id, handlers, ttl)                  # 5. DISPATCH → 6. PERSIST inside
```

- **Concurrency cap = `min(external limits)`** (resource / rate / budget) — *not* a worker-pool size. The DAG plus the cap bound how much runs at once.
- **Re-evaluate every tick** — a job that became ready since the last scan is picked up on the next one.
- Steps 1–6 (the `dispatch`/`persist` step that runs the handler and writes the result atomically) are shown end-to-end in `references/sql-job-queue-extras.md`.

### Step 8: Wake strategy — polling by default, LISTEN/NOTIFY as a PG-only boost

**Default: bounded polling.** Sleep a short interval, run a tick, repeat. Works on **every** dialect; the only cost is up-to-one-interval latency on a newly-ready job. Keep the interval short enough to feel responsive, long enough not to hammer the DB.

**PostgreSQL optimization (optional): `LISTEN/NOTIFY`.** A worker `LISTEN`s on a channel; producers (or completing jobs) `NOTIFY` it on a state change, waking the loop immediately instead of waiting out the poll interval. Lower latency, **Postgres-only** — SQLite and MySQL have no equivalent and **stay on polling**. Present it as an enhancement layered on the polling baseline (still poll as a backstop so a missed notification can't stall the queue), never as the portable default.

### Step 9: Idempotency — at-least-once, and where the guarantee stops

The queue guarantees **at-least-once** dispatch: a reclaim (or the hung-job timeout) can **re-dispatch** a job whose prior attempt partly ran and committed side effects before dying. Name this contract explicitly to the consumer.

The state machine gates re-entry so the queue never **double-finalizes**: `ready → leased → running → done`, with the **`result` write committed atomically with the `done` transition** (one transaction). So a reclaimed job is detectably mid-flight (`leased`/`running`, not `done`) and re-running it can only re-reach `done` once — the done-write is all-or-nothing with the state flip.

```python
def finalize(engine, job_id, result):                    # result + done flip = ONE transaction
    with Session(engine) as s, s.begin():
        s.execute(update(Job).where(Job.id == job_id).values(
            state="done", result=result, in_flight=False, lease_owner=None,
        ))
```

**Where it stops:** the queue makes a job *reclaimable* and never double-*finalizes* — but it does **not** dedup the job's **side effects**. If attempt 1 sent an email then died, attempt 2 sends it again. **Handler idempotency is the consumer's responsibility** (idempotency keys, upserts, "did I already do this?" checks). This skill provides the state-machine guard, not business-level dedup.

### Step 10: Async aside (short)

The locking **semantics are identical** under async — `FOR UPDATE SKIP LOCKED` / `BEGIN IMMEDIATE` behave the same; only the session API changes. Swap `Session`→`AsyncSession`, `with`→`async with`, and `await` the I/O (the `AsyncSession` / `await` mechanics are the `sqlalchemy` sibling's, referenced not re-taught). The whole tick loop, lease branches, reclaim, and finalize translate one-to-one. **Sync is the primary path**; reach for async only when the surrounding stack is already async.

## Rules

**Hard rules (never violate):**

- **The claim is one atomic transaction.** Reading the ready row and writing `lease_owner`/`lease_expires`/`in_flight` happen in a single transaction — never read-then-update across two.
- **Branch the lease on dialect.** `FOR UPDATE SKIP LOCKED` (PostgreSQL, MySQL 8.0+ InnoDB) vs `BEGIN IMMEDIATE` (SQLite). Detect via `engine.dialect.name`. `with_for_update` is a silent no-op on SQLite — relying on it there races.
- **MySQL needs 8.0+ / InnoDB, READ COMMITTED for the claim, and exclusive `FOR UPDATE`.** `SKIP LOCKED` errors on 5.7; SQLAlchemy's `with_for_update(read=True, skip_locked=True)` emits the legacy `LOCK IN SHARE MODE SKIP LOCKED` which MySQL rejects (issue #10134) — so use exclusive `FOR UPDATE`; the REPEATABLE READ default must be overridden for the claim txn.
- **Finalize atomically.** The `result` write and the `done` transition are one transaction, so a reclaimed job never double-finalizes.
- **Containers roll up, only leaves run.** The ready-set query filters out any job with children; container completion is event-driven, not in the scan.

**Preferences (override-able):**

- Default to **polling**; add PostgreSQL `LISTEN/NOTIFY` only when latency demands it, and keep polling as a backstop.
- Keep the lease **TTL** above one heartbeat interval and below the user-noticeable stall.
- Prefer a **partial index** on `(state, run_after)` for the ready-state; fall back to a plain composite index on MySQL.
- Sync-first; reach for async only inside an already-async stack.

## Gotchas

- **`with_for_update` silently no-ops on SQLite.** It does not error — it just doesn't lock, so two workers can claim the same job. Use `BEGIN IMMEDIATE` on SQLite; verify on the *real* target engine, not only SQLite.
- **MySQL `SKIP LOCKED` is a syntax error pre-8.0**, not a no-op. And MySQL's `REPEATABLE READ` default can make a claim `SELECT` *miss* freshly-committed ready rows — set READ COMMITTED for the claim transaction.
- **SQLAlchemy's `with_for_update(read=True, skip_locked=True)` is rejected by MySQL** — it emits the legacy `LOCK IN SHARE MODE SKIP LOCKED` (SQLAlchemy issue #10134), not the modern `FOR SHARE SKIP LOCKED` (which is valid MySQL 8 SQL). Use the exclusive `FOR UPDATE` form for the claim.
- **A naive full-table scan per tick does not scale.** Once the table fills with `done`/`parked` rows, an unindexed ready-set scan walks them all every tick. The partial/filtered index on the ready state is what keeps each tick O(ready-set).
- **Premature reclaim double-dispatches a live job.** A TTL shorter than the job's real duration (with no heartbeat to extend it) makes the reclaim sweep yank a *still-running* job back into the ready-set. Heartbeat while running; size the TTL above the heartbeat interval.
- **A hung-but-alive worker never trips the reclaim sweep** — its lease keeps getting renewed. Only a separate per-dispatch timeout bounds it.
- **At-least-once means side effects can repeat.** The state machine stops double-*finalize*, not double-*side-effect*. The handler must be idempotent; the queue can't make it so.
- **Container roll-up belongs on completion, not in the query.** Computing roll-up inside the ready-set scan makes every tick walk the DAG. Compute it event-driven when a child finishes.

## Anti-patterns

- **Don't reach for a broker (Celery / RabbitMQ / Dramatiq / Taskiq) for this shape.** Brokers use a short-task **ack / visibility-timeout** model — a long job that outlives the visibility timeout gets **redelivered and double-executed**. They want **static enqueue**, not a dynamic dependency-DAG. Their concurrency is a **worker-pool size**, not your external caps. And the broker is a **second source of truth** plus heavy infra for one box. Brokers win for multi-machine fan-out of short tasks — not here.
- **Don't reach for APScheduler.** It's a **time-triggered** scheduler (run X at time T / every N), not a **dependency-DAG work queue with leasing**. Multi-dialect store, wrong model.
- **Don't reach for Airflow / Prefect / Dagster.** Heavy orchestration **platforms** that bring their **own metadata DB** — a second source of truth and far more infra than a single embeddable box wants.
- **Don't build the claim on `with_for_update` alone** assuming SQLite locks rows — it doesn't. Detect the dialect and use `BEGIN IMMEDIATE` on SQLite.
- **Don't read-then-update in two transactions** ("it's clearer") — that's the double-dispatch race the atomic claim exists to close.
- **Don't fold the MySQL branch into the PostgreSQL one** because the SQL string matches — the isolation default and the version/share-mode caveats genuinely differ; show it as its own branch.
- **Don't drop polling once you add `LISTEN/NOTIFY`** — a missed notification with no poll backstop silently stalls the queue.

## Output

A working DB-backed ready-set scheduler (or the requested slice) on SQLAlchemy 2.x: a generic `jobs` + `job_deps` schema with the ready-state index, a portable ready-set query, a **dialect-branched atomic lease** (PostgreSQL / MySQL 8+ `FOR UPDATE SKIP LOCKED` vs SQLite `BEGIN IMMEDIATE`), crash-resume via heartbeat + lease-expiry reclaim + a hung-job timeout, weighted fair-share over `group_key`, the scan→rank→lease→dispatch→persist→reclaim tick loop, a polling (optionally `LISTEN/NOTIFY`) wake, and the at-least-once idempotency contract with its atomic-finalize guard. The artifact embeds in a single-box application; the consumer supplies the handlers (and their idempotency) and the external concurrency cap.

## Related

- `sqlalchemy` — the data layer this builds on: engine/URL, `DeclarativeBase`/`Mapped` models, sessions, `JSON`, and the **`with_for_update(skip_locked=...)` primitive + its per-dialect support matrix**. This skill *composes* that primitive into a claim loop; it does not re-teach it.
- `alembic` — schema migrations for the `jobs`/`job_deps` tables and the partial index (incl. the SQLite batch move-and-copy gotcha). This skill assumes the schema already exists.
- `pydantic-v2` — validating the `args`/`result` JSON payloads at the application boundary (not the ORM column types).

## Progressive disclosure

- `references/sql-job-queue-extras.md` — a fuller worked end-to-end minimal scheduler: all three lease branches, the `dispatch`/heartbeat/finalize step, and the polling run loop as one runnable listing. **Load when** the in-body snippets aren't enough to assemble the whole loop.
- `references/sources.md` — research provenance (Procrastinate / PGQueuer prior art + the SQLAlchemy / Postgres / MySQL locking docs). **Load when** verifying a claim's origin or during a fresh review.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the skill listing.
- Body ≤ ~500 lines / 5,000 tokens.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
