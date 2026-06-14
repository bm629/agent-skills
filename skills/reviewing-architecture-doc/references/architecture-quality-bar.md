# architecture-quality-bar — per-condition pass/gap signals + worked findings

The ten Step-2 conditions expanded. Load when a borderline condition needs a sharper pass/gap call. Each is single-sourced with `authoring-architecture-doc` Step-7.

## cond-1 — Context, boundary + concerns
- **Pass:** a reader can state what the system is and is not responsible for; boundary (in/out + owner) explicit; every actor + external dependency named; context diagram agrees with prose; every stakeholder concern framed by a section/view.
- **Gap:** implied boundary; an external dependency referenced but never named ("calls the payment provider"); a named concern (operability, security) no section addresses.
- **Worked finding:** *revise — Context (cond. 1), §1: the doc lists components that call "the billing service" but billing is never named as an external dependency with what it provides. Fix: add it to the external-dependency list (+ the context diagram) with a one-line note; it also needs a failure stance in cond-7.*
- **Non-collapsing baseline:** boundary + external set always stated.

## cond-2 — Structure + altitude
- **Pass:** each component named once with one responsibility + kind; topology edges carry direction + protocol; integration boundaries name a contract owner; whole-system altitude held.
- **Gap:** a god-component; an unexplained box (in a diagram, no responsibility); an edge with no direction/protocol; altitude slip — an endpoint list (api-spec), a table schema (data-model), or "this function calls that class" (TDD).
- **Worked finding:** *revise — Altitude (cond. 2), §4: the API boundary inlines all 14 `/v1/orders` endpoints with params + response schemas. Fix: name the interface structurally and link the api-spec; the architecture doc states the boundary, not the contract.*

## cond-3 — Diagrams ⇄ narrative in sync
- **Pass:** every box/arrow in prose and vice-versa; diagrams standalone; runtime/deployment view where load-bearing.
- **Gap:** the prose describes a worker the diagram omits (or vice-versa); a multi-service/multi-env system with no deployment view.

## cond-4 — The ADR mechanism (signature)
- **Pass:** every significant decision is a standalone LINKED ADR (one per file); index⇄files in sync; no accepted ADR rewritten (changes supersede).
- **Gap signals:** (a) a significant decision pasted **inline** with full context/consequences instead of a linked ADR; (b) an ADR bundling two decisions; (c) a dangling index link or an accepted ADR missing from the index; (d) an **accepted ADR edited in place** rather than superseded by a new one (history destroyed).
- **Worked finding (embedded):** *revise — ADR mechanism (cond. 4), §5: "we chose Kafka over RabbitMQ" is written inline with its full rationale + alternatives. Fix: move to `adr/0004-messaging.md` and link it from the §7 index — one source, independently addressable.*
- **Worked finding (rewritten):** *revise — ADR mechanism (cond. 4), adr/0002: the accepted ADR-0002 was edited to change the datastore from MySQL to Postgres. Fix: restore ADR-0002, write a new ADR-0008 that supersedes it (ADR-0002 Status → "superseded by ADR-0008"), update the index — preserve the history.*
- **Unverifiable:** if the linked ADR files were not handed in, flag cond-4 unverifiable; do not fabricate their content.
- **Non-collapsing baseline:** a rewritten accepted ADR is broken at any size.

## cond-5 — Decisions traced + justified
- **Pass:** each significant choice names its driver (requirement/NFR/ASR) + a real alternative with the trade-off it lost on.
- **Gap:** a load-bearing choice with no driver; no alternative ("we chose X" by assertion); a strawman ("alternative: do nothing").

## cond-6 — NFR realization + tradeoffs
- **Pass:** every NFR target has a realizing mechanism (measurable scenario where load-bearing); tradeoffs named + resolved.
- **Gap:** a restated target with no mechanism ("99.9% uptime" with no failover); a "highly available" claim with an undiscussed SPOF; a clear tension (latency vs consistency, cost vs availability) never named.
- **Worked finding:** *revise — NFR realization (cond. 6), §6: the PRD's "p99 < 200ms at 1000 rps" is restated but no mechanism realizes it. Fix: state the caching/partitioning/async mechanism + a measurable quality-attribute scenario.*

## cond-7 — Cross-cutting concerns
- **Pass:** resilience stance per integration boundary; security (trust boundaries/authn/secrets); privacy where sensitive data flows; a system-level observability strategy.
- **Gap:** an external dependency with no slow/down stance; an external-facing system with no trust boundary; a multi-service system with no observability strategy.

## cond-8 — Requirements / ASR coverage
- **Pass:** every ASR has a realizing structure; no orphan structure; a feature's TDD can place itself within the architecture.
- **Gap:** an ASR with no realizing structure; a subsystem serving no requirement.

## cond-9 — Grounded, no fabrication, consistent with reality (+ greenfield clause)
- **Pass:** unknowns flagged as assumptions/open-questions; nothing invented; claims about what the system IS verified against the real code/topology (`file:line`) or marked unverified.
- **Gap:** a falsely-complete read; a fabricated limit/mechanism; a claim about existing behaviour that contradicts the code.
- **Greenfield clause:** when there is no existing code/system to verify against (brand-new system, or a fictional/example doc), consistency is **N/A and never a blocker** — mark unverified, do not false-revise.

## cond-10 — Amend (delta-scoped)
- **Pass:** the delta meets cond-1–9 on what it touched; decisions changed via a new superseding ADR (index in sync); the changed structure still traces to a driver (or upstream-amend flagged); the downward-broad ripple (dependent TDD fleet + api-spec/data-model/deployment/runbook) named; version + changelog present.
- **Gap:** an un-scoped delta; a rewritten accepted ADR; an out-of-sync index; an un-flagged ripple; missing change history.
- **Collapse:** n/a on a greenfield first build — do not full-re-review, do not demand a changelog on a first draft.
