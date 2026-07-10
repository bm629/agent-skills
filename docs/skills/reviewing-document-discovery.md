# reviewing-document-discovery

Judge a **produced document PLAN** — a manifest of which documents a project will produce, each with its producer / tools / skills / `depends_on` — and decide whether it is sound enough to produce from — an acceptance gate, not authoring. The review half of the discovery pair; it single-sources its bar **1:1 with `project-document-discovery`'s Self-check**, asserting the same fourteen conditions independently (you cannot grade your own homework).

**Version: 1.2.0**

## Purpose

A document plan decides *which* documents a project needs, who produces each, and the order they depend on. Before the documents are produced, something has to decide whether the plan picked the right set — proportional to the archetype, complete, producible, and acyclic. This skill is that up-front gate: it judges the plan against a fixed **fourteen-condition bar** (nine content/DAG conditions + three v2.0.0 output-contract conditions + two v3.0.0 meta-section conditions) and emits a single machine-parseable verdict, so a discovery → review → produce loop can run. It is the plan-time analog of `reviewing-document-set` (which judges the *finished* corpus's coherence).

## When to activate

- ✅ A produced document plan / manifest needs an accept/revise decision before the documents are produced.
- ✅ You are the independent gate over a plan `project-document-discovery` (or any equivalent) produced.
- ✅ Re-judging a plan after fixes from a prior `revise`, or judging an **amend** (an existing plan + a stated change → a delta).

### When NOT to activate

- **Judging a single produced document's internal quality** (a PRD, an architecture doc) → that document's own per-type reviewer.
- **Judging whether a set of finished documents are mutually coherent** → `reviewing-document-set` (the produced-corpus gate; this is the up-front plan gate).
- **Authoring the plan** → `project-document-discovery` (this is review-only).

## The bar (14 conditions)

Note the archetype and whether this is greenfield or an amend, then judge each:

**Content / DAG conditions (1–9, all plans):**
(1) **proportional to the archetype** — no over-selection (a PRD + wireframes + a design system for a CLI tool) and no under-selection (a load-bearing doc cut to look lean); (2) **load-bearing present** — the documents that define the features (PRD / feature specs; for UI products, the design docs); (3) **production requirements per document** — every doc has its author + reviewer `roles` pair (two ids in `[author, reviewer]` order matching the archetype) + tools/providers + both the authoring and reviewing skills; (4) **`depends_on` per document** (pruned to the set); (5) **acyclic dependency graph** — edges flow requirements → design → delivery → docs; (6) **no orphan — with the terminal-deliverable exception** — a leaf deliverable (LICENSE / CHANGELOG / SECURITY.md, often README) with `depends_on: []` is NOT an orphan; only an *intermediate* doc reading nothing and read by nothing is; (7) **no padding** — no document the project won't use; (8) **open-ended preserved** — an unrecognized type is researched/forged, not guessed or silently omitted; (9) **(amend only) the delta is change-scoped** (n/a greenfield).

**Output-contract conditions (10–12, v2.0.0+ plans only; n/a for v1.x output):**
(10) **`capability_map` key present and non-empty** — top-level `capability_map` JSON key with all 10 classification cluster sub-keys present; (11) **`product_capabilities` key present with well-formed records** — top-level `product_capabilities` array; each record has required fields (`id`, `name`, `scope`, `owns`, `has_ui`, `has_api`, `has_persistence`); 4–10 L1 records (count outside 4–10 is a finding, not a hard gate); (12) **`manifest` nested under `"manifest"` key; per-capability entries present** — `manifest` key in the output (not root-level list); each entry has `type` and `scope` fields; per-capability entries (`feature-spec-{id}`) present for every active capability; fan-out flags match the per-capability document entries produced.

**Meta-section conditions (13–14, v3.0.0+ plans only; n/a for v2.x output):**
(13) **all five manifest meta-sections populated** — `capabilities:` contains `docs` (always) and `design` (if `ui.has_ui: true`); no build-level capability; `roles:`, `skills:`, `tools:`, `amendments:` all present and non-empty (except `amendments: []` which is an empty array by design at discovery time); `roles:` holds the full author/reviewer pair for every archetype present and every role entry is a pure persona (no `skills`/`tools`); every skill entry carries a populated `purpose` + non-empty `requirements` and `version: null`/`source: null`, and every skill and role entry carries `resolved_id`/`match_status` (both `null` at discovery — carved out as not-a-gap); (14) **`capability` scalar on every document entry** — each document entry has `capability: "docs"` or `capability: "design"` as a string scalar, not `capabilities: [...]` (array form from v2.x).

Judged against the archetype, never a fixed taxonomy.

## Output

A findings report: zero or more actionable findings (each naming the affected document(s) + the fix), followed by **exactly one** terminal `VERDICT: approve|revise` for the whole plan (a caller typically reads only the last `VERDICT:` line). **Approves** a plan that is proportional, complete, producible, and acyclic — no false-revise on a lean set right-sized for a thin archetype; **revises** only on a real, named gap.

## Key guarantees

- **Review-only** — never authors, fixes, or re-plans; reports findings, the producer revises.
- **Single-sourced bar** — the same fourteen conditions `project-document-discovery`'s Step-9 Self-check (v6.0.0) uses, asserted independently (nine content/DAG + three output-contract + two meta-section).
- **No false-revise** — a lean plan right-sized for a thin archetype is an approve; proportionality is judged against the archetype, not an absolute checklist.
- **No invented requirements** — never demands an archetype-irrelevant document (a data-model for a stateless CLI, wireframes for a library), never requires a named standard be cited.
- **The terminal-deliverable exception is load-bearing** — never flags a LICENSE/README/CHANGELOG as an orphan (the most common false-revise).
- **One terminal verdict** — exactly one `VERDICT:` line, last, the whole-plan decision a loop can read.

## License

MIT © 2026 Bhushan Modi.
