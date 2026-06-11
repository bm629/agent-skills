# `sql-job-queue` — extras: a full worked minimal scheduler

**Load when** the in-body snippets aren't enough to assemble the whole loop end-to-end. This is one runnable listing showing all three lease branches, the `dispatch`/heartbeat/finalize step, the reclaim sweep, and the polling run loop wired together. It mirrors the SKILL body — the body teaches each piece in isolation; this assembles them. Same generic `jobs`/`job_deps` model; no consumer-specific naming.

This is a **reference listing**, not an executable script under `scripts/` — copy the parts you need. It assumes the `sqlalchemy` sibling's data-layer setup (engine, `DeclarativeBase`, sessions) already exists.

## The model (recap)

```python
from datetime import datetime
from sqlalchemy import ForeignKey, Index, JSON, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    args: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(default="ready")     # ready|leased|running|done|failed
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"))
    group_key: Mapped[str]
    weight: Mapped[int] = mapped_column(default=1)
    lease_owner: Mapped[str | None]
    lease_expires: Mapped[datetime | None]
    in_flight: Mapped[bool] = mapped_column(default=False)
    heartbeat_at: Mapped[datetime | None]
    run_after: Mapped[datetime | None]
    started_at: Mapped[datetime | None]                     # for the hung-job timeout
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

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

## Shared helpers

```python
from datetime import datetime, timedelta, timezone

def now():
    return datetime.now(timezone.utc)
```

## The ready-set query

```python
from sqlalchemy import and_, exists, not_, or_, select

def ready_set(ts):
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
        .where(or_(Job.run_after.is_(None), Job.run_after <= ts))
        .where(not_(has_child))
        .where(not_(has_open_dep))
        .where(or_(Job.lease_expires.is_(None), Job.lease_expires <= ts))
        .order_by(Job.id)
    )
```

## The atomic lease — all three branches

```python
from sqlalchemy import text, update
from sqlalchemy.orm import Session

def claim(engine, worker_id, ttl):
    name = engine.dialect.name
    if name == "postgresql":
        return _claim_pg(engine, worker_id, ttl)
    if name == "mysql":
        return _claim_mysql(engine, worker_id, ttl)
    if name == "sqlite":
        return _claim_sqlite(engine, worker_id, ttl)
    raise RuntimeError(f"unsupported dialect: {name}")

def _lease_values(worker_id, ttl, ts):
    return dict(
        state="leased", lease_owner=worker_id,
        lease_expires=ts + timedelta(seconds=ttl),
        in_flight=True, heartbeat_at=ts,
    )

# --- PostgreSQL: FOR UPDATE SKIP LOCKED, READ COMMITTED default is fine ---
def _claim_pg(engine, worker_id, ttl):
    ts = now()
    with Session(engine) as s, s.begin():
        row = s.execute(
            ready_set(ts).with_for_update(skip_locked=True).limit(1)
        ).scalars().first()
        if row is None:
            return None
        s.execute(update(Job).where(Job.id == row.id).values(**_lease_values(worker_id, ttl, ts)))
        return row.id

# --- MySQL 8.0+/InnoDB: same SQL, but force READ COMMITTED + exclusive FOR UPDATE ---
def _claim_mysql(engine, worker_id, ttl):
    ts = now()
    # REPEATABLE READ (MySQL's default) snapshots at txn start and can MISS rows
    # committed after — pin READ COMMITTED for the claim txn. Use exclusive
    # Use exclusive FOR UPDATE: with_for_update(read=True, skip_locked=True)
    # emits the legacy LOCK IN SHARE MODE SKIP LOCKED, which MySQL rejects
    # (SQLAlchemy issue #10134) — not a MySQL SQL-level invalidity.
    with engine.connect().execution_options(isolation_level="READ COMMITTED") as conn:
        with conn.begin():
            with Session(bind=conn) as s:
                row = s.execute(
                    ready_set(ts).with_for_update(skip_locked=True).limit(1)
                ).scalars().first()
                if row is None:
                    return None
                s.execute(update(Job).where(Job.id == row.id).values(**_lease_values(worker_id, ttl, ts)))
                return row.id

# --- SQLite: no row locks → BEGIN IMMEDIATE serializes the claim ---
def _claim_sqlite(engine, worker_id, ttl):
    ts = now()
    with engine.connect() as conn:
        conn.exec_driver_sql("BEGIN IMMEDIATE")     # reserve the write lock at txn start
        try:
            row = conn.execute(ready_set(ts).limit(1)).first()   # with_for_update is a no-op here
            if row is None:
                conn.exec_driver_sql("COMMIT")
                return None
            v = _lease_values(worker_id, ttl, ts)
            conn.execute(
                text("UPDATE jobs SET state=:state, lease_owner=:lease_owner, "
                     "lease_expires=:lease_expires, in_flight=:in_flight, "
                     "heartbeat_at=:heartbeat_at WHERE id=:id"),
                {**v, "id": row.id},
            )
            conn.exec_driver_sql("COMMIT")
            return row.id
        except Exception:
            conn.exec_driver_sql("ROLLBACK")
            raise
# A SQLite writer blocked on the write lock raises OperationalError ("database is
# locked" / SQLITE_BUSY); the worker treats that as "no claim this tick" and retries.
```

## Heartbeat, dispatch, finalize — the run step

```python
def heartbeat(engine, job_id, worker_id, ttl):
    # Renew the lease while the job runs. A DEAD worker stops calling this and
    # its lease_expires falls into the past → reclaim picks it up.
    with Session(engine) as s, s.begin():
        s.execute(update(Job).where(
            Job.id == job_id, Job.lease_owner == worker_id,
        ).values(lease_expires=now() + timedelta(seconds=ttl), heartbeat_at=now()))

def finalize(engine, job_id, result, ok):
    # The result write and the terminal transition are ONE transaction — so a
    # reclaimed job can never double-finalize (idempotency state-machine guard).
    with Session(engine) as s, s.begin():
        s.execute(update(Job).where(Job.id == job_id).values(
            state="done" if ok else "failed",
            result=result, in_flight=False, lease_owner=None,
        ))
        roll_up_parent(s, job_id)   # event-driven container roll-up (see below)

def dispatch(engine, job_id, handlers, worker_id, ttl, max_runtime):
    with Session(engine) as s, s.begin():
        job = s.get(Job, job_id)
        s.execute(update(Job).where(Job.id == job_id).values(state="running", started_at=now()))
        jtype, jargs, started = job.type, job.args, now()
    handler = handlers[jtype]
    try:
        # The consumer renews the heartbeat from inside a long handler (or a side
        # thread). HUNG-BUT-ALIVE guard: if it overruns max_runtime, fail it even
        # though the lease is still being renewed — a distinct failure from a crash.
        result = handler(jargs, deadline=started + timedelta(seconds=max_runtime))
        finalize(engine, job_id, result, ok=True)
    except TimeoutError:
        finalize(engine, job_id, {"error": "timed out"}, ok=False)
    except Exception as exc:
        finalize(engine, job_id, {"error": str(exc)}, ok=False)
```

## Container roll-up — event-driven, on child completion

```python
from sqlalchemy import func as sqlfunc

def roll_up_parent(session, job_id):
    # Called when a child finishes. If its parent has no remaining non-terminal
    # children, transition the parent. NOT done inside the ready-set scan.
    job = session.get(Job, job_id)
    if job.parent_id is None:
        return
    remaining = session.execute(
        select(sqlfunc.count()).select_from(Job.__table__).where(
            Job.parent_id == job.parent_id,
            Job.state.notin_(("done", "failed")),
        )
    ).scalar_one()
    if remaining == 0:
        any_failed = session.execute(
            select(sqlfunc.count()).select_from(Job.__table__).where(
                Job.parent_id == job.parent_id, Job.state == "failed",
            )
        ).scalar_one()
        session.execute(update(Job).where(Job.id == job.parent_id).values(
            state="failed" if any_failed else "done", in_flight=False,
        ))
        roll_up_parent(session, job.parent_id)   # roll up the chain
```

## Reclaim sweep — stale leases back to ready

```python
def reclaim(engine, ts):
    with Session(engine) as s, s.begin():
        s.execute(update(Job).where(
            Job.state.in_(("leased", "running")),
            Job.lease_expires < ts,
        ).values(state="ready", lease_owner=None, in_flight=False, lease_expires=None))
```

## Weighted fair-share over the ready-set

```python
def fair_share(rows, free):
    groups = {}
    for r in rows:
        groups.setdefault(r.group_key, []).append(r)
    weights = {g: rs[0].weight for g, rs in groups.items()}
    total = sum(weights.values())
    chosen = []
    for g, rs in groups.items():
        n = max(1, round(free * weights[g] / total))   # ≥1 so no group fully starves
        chosen.extend(rs[:n])
    return chosen[:free]                                 # cap at the slot budget
```

## The tick + the polling run loop

```python
import time
from sqlalchemy import func as sqlfunc

def count_in_flight(engine):
    with Session(engine) as s:
        return s.execute(
            select(sqlfunc.count()).select_from(Job.__table__).where(Job.in_flight.is_(True))
        ).scalar_one()

def tick(engine, worker_id, handlers, ttl, max_runtime, max_concurrency):
    ts = now()
    reclaim(engine, ts)                                  # 1. RECLAIM
    free = max_concurrency - count_in_flight(engine)     # cap = min(external limits)
    if free <= 0:
        return
    with Session(engine) as s:
        candidates = s.execute(ready_set(ts)).scalars().all()   # 2. SCAN
    for _ in fair_share(candidates, free):               # 3. RANK
        job_id = claim(engine, worker_id, ttl)           # 4. LEASE (per-dialect, atomic)
        if job_id is None:
            break
        dispatch(engine, job_id, handlers, worker_id, ttl, max_runtime)  # 5. DISPATCH → 6. PERSIST

def run(engine, worker_id, handlers, *, ttl=60, max_runtime=300,
        max_concurrency=4, poll_interval=1.0):
    # Default wake: bounded polling — works on every dialect. On PostgreSQL you
    # can additionally LISTEN on a channel and wake on NOTIFY for lower latency,
    # keeping this poll as a backstop so a missed notification can't stall the queue.
    while True:
        tick(engine, worker_id, handlers, ttl, max_runtime, max_concurrency)
        time.sleep(poll_interval)
```

## PostgreSQL LISTEN/NOTIFY — the optional low-latency wake

```python
import select as ioselect

def wait_for_notify(engine, channel, timeout):
    # Postgres-only enhancement layered on the polling baseline. A producer (or a
    # finishing job) runs NOTIFY <channel>; this wakes the loop early instead of
    # waiting out poll_interval. SQLite and MySQL have no equivalent → stay on polling.
    # Driver-specific/illustrative: this is the psycopg2 raw-connection API
    # (set_isolation_level / .poll() / .notifies list). psycopg v3 instead uses
    # `conn.autocommit = True` and the `conn.notifies()` generator (no .poll()/.notifies).
    raw = engine.raw_connection()
    try:
        raw.set_isolation_level(0)   # autocommit, so LISTEN takes effect immediately
        cur = raw.cursor()
        cur.execute(f"LISTEN {channel}")
        if ioselect.select([raw], [], [], timeout) != ([], [], []):
            raw.poll()
            while raw.notifies:
                raw.notifies.pop()   # drain; the tick re-scans the DB for truth
            return True
        return False
    finally:
        raw.close()
```

The notification is only a *wake* — the tick still re-scans the ready-set for the source of truth, so a dropped or coalesced notification only costs latency, never correctness.
