# Reference — I/O & data, states, decision tables, NFRs, archetypes, amend

Depth for the skill body's structural + archetype + amend method. Load when a feature is stateful, combinatorial, archetype-specific, or being amended.

## Inputs / outputs as a data contract

Enumerate the contract a producer and a consumer both validate against:

- **Inputs:** per input — source, type, allowed range/format, **validation rule**, required/optional. For each, name the valid set, the invalid set, and the boundary.
- **Outputs:** per output — response shape/format, side effects, **error codes**. Name what the caller/UI observes.
- **Data:** entities read/written, the schema/example, persisted vs transient.

Framing it as a schema (required/optional fields, types, validation rules — like an OpenAPI schema or a data-contract) makes "what's valid / what's not / what's the boundary" a discipline, not a checklist.

## State-transition table

For a stateful feature, specify the grid — current state × event → next state — with a **dash (`-`) for an illegal transition**, and name the **initial** + **terminal** states. The table form makes illegal transitions checkable (the reviewer confirms every (state, event) cell is a defined next-state or an explicit illegal-marker) and is directly testable (one test per legal transition + attempts on illegal ones).

```
Current ↓ \ Event →   submit    cancel    pay
draft (initial)       placed     -        -
placed                -          cancelled paid
paid (terminal)       -          -         -
```

## Decision table (combinatorial rules)

When the response depends on a *combination* of conditions, tabulate it — conditions as rows, each column a rule (a combination), the action(s) at the bottom. It exposes:

- **missing rules** (a combination with no action),
- **contradictory rules** (the same combination → two actions),
- **redundant rules** (collapsible columns).

For N independent booleans there are 2^N combinations; the table makes the completeness obligation visible (and shows where conditions are not actually independent — mark impossible combinations "n/a, because …"). The reviewer checks the rule-set is complete (no input combination leaves the behavior undefined), never "did you draw a table".

## Feature-level NFR taxonomy

List the **applicable** categories for the feature, each with a **numeric/checkable target**. Proportional — a trivial feature needs none.

| Category | Target form | Applies when |
|---|---|---|
| Performance | p95/p99 latency, throughput, payload size | a latency-sensitive path |
| Reliability / idempotency | retry/timeout behavior, idempotent-on-retry | calls a dependency / writes data |
| Security / authorization | who may invoke; authz rule; input sanitization | access control or untrusted input |
| Privacy / data-handling | PII fields, retention, masking | touches personal data |
| Accessibility | WCAG 2.2 AA (contrast, focus, target size, keyboard) | a UI feature |
| Limits / quotas | rate-limit, max size, pagination cap | an API / resource-bounded feature |
| Compatibility | supported clients/versions/locales | an external surface |

"Should be fast/secure" is not an NFR — give the number.

## Archetype overlays

Identify the feature's archetype(s) — a feature can be several — and cover that overlay's emphases to the implementability bar. Proportional; the reviewer judges the outcome via the existing conditions (a missing error model → I/O/edge gap; "works" on a model → untestable AC), never a named-section demand.

| Archetype | Emphasis to be sure to cover | Hands off to |
|---|---|---|
| **UI** | per-state behavior (empty/loading/populated/error/success), input validation + inline errors, microcopy intent, accessibility, keyboard/focus | user-flows / wireframes / design-system upstreams |
| **REST/API** | request/response schema, status codes + complete error model, idempotency, pagination, rate-limits, auth/authz, versioning | the wire contract → api-spec |
| **Data/ML** | data requirements (sources, formats, ranges, relevance/completeness/accuracy/balance), probabilistic threshold AC, evaluation metrics, drift/monitoring, low-confidence fallback | the largest overlay; deterministic specs mis-fit ML |
| **Batch / async-job** | trigger/schedule, idempotency + at-least/exactly-once, partial-failure + retry/backoff, ordering, observability/alerting | technical-design owns the mechanism |
| **Integration / webhook** | delivery semantics (ordering, replay/dedup), payload contract + versioning, failure + retry, signature/auth | api-spec / technical-design |
| **CLI** | arguments/flags, exit codes, stdout/stderr contract, idempotency, non-interactive behavior | — |

### Probabilistic / ML acceptance criteria (the sharpest overlay)

A deterministic Given/When/Then mis-fits a model output. Write:

- the **metric** (precision / recall / F1 / accuracy / AUC / MAP / latency), the **threshold** (≥ X), and the **dataset/slice** it's measured on;
- separate **expected** performance (on eval data) from **desired** runtime performance;
- the **low-confidence / fallback** behavior (the deterministic part you *can* pin — e.g. "confidence < 0.4 → recency sort");
- the **data requirements** (sources, formats, ranges, relevance/completeness/accuracy/balance).

"The model is accurate" / "results are relevant" is a non-spec.

## Amend an approved spec (the ripple procedure)

A feature spec is a living document; the common operation is a DELTA. The scope unit is a feature / behavior / acceptance-criterion / I/O field / state-transition cell.

1. **Scope the change** — what this delta touches, what is deliberately untouched.
2. **Edit in place** — change only the affected blocks; never regenerate the whole spec (loses provenance, risks silent drift).
3. **Re-make the feature's internal chain consistent** — after a behavior change, update its AC, state table, I/O, edge cases.
4. **Bidirectional ripple analysis:**
   - **Upstream → PRD:** does the change still trace to a PRD line? If it adds an un-traced feature, the **PRD must be amended first** (the spec→plan→impl order — the PRD is upstream).
   - **Internal → the feature's chain:** which AC / state cells / I/O fields / edge-cases are now stale (fixed in step 3).
   - **Downstream → derived docs:** which **technical-design** decisions, **test-plan** cases, **api-spec** entries are now stale — list them as the affected set the flow must propagate.
5. **Version + changelog** — bump the document's own version header; add an entry (who/when/what/why).
6. **Mark superseded content** — mark outdated behaviors/criteria/states superseded with the reason; don't silently delete, so a downstream reader sees the decision.

The skills own the amend METHOD + the delta review; deciding to amend, choosing which spec to feed in, amending the PRD when needed, and propagating downstream are the flow's job — the skill assumes the existing spec + the change request (+ relevant upstream/downstream docs for the ripple check) are handed in.
