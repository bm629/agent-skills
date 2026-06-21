# The fourteen-condition plan-quality bar — pass/gap signals + worked findings

Depth for `reviewing-document-discovery`'s Step 2. Each condition lists what a **pass** looks
like, what a **gap** looks like, and a worked finding. The bar is **single-sourced 1:1 with
`project-document-discovery`'s Step-9 Self-check** (same fourteen items, same order). The body
SKILL.md carries the method; this file carries the per-condition detail — load esp. for the
conditions that drive most verdicts (1 proportionality, 6 the orphan exception, 9 amend, 13+14
manifest completeness).

## Condition 1 — Proportional to the archetype

- **Pass:** the set is sized to the project — a thin CLI tool gets a handful (README + a short
  design note + API ref); a UI SaaS gets the fuller bands + its overlays.
- **Gap:** **over-selection** (a PRD + wireframes + a design system for a CLI tool) OR
  **under-selection** (a load-bearing doc cut to look lean).
- **Worked:** `the plan lists a PRD, user flows, wireframes, and a design system for a "git-log one-liner CLI" — over-selected for the archetype; trim to a README + a brief design note.`

## Condition 2 — Load-bearing present

- **Pass:** the feature-defining documents (PRD / feature specs; for UI, the design docs) are in
  the set.
- **Gap:** a load-bearing document cut "to look lean" — nothing downstream can define the features.
- **Worked:** `a web-app plan has wireframes + a test plan but no PRD or feature specs — the features are undefined; add the load-bearing requirements band.`

## Condition 3 — Production requirements per document

- **Pass:** every document has a producer role + tools/providers + skills.
- **Gap:** a document with no producer or no tools — it cannot be produced as planned.
- **Worked:** `[d-architecture] has no producer role or tools attached — assign a producer (systems architect) + tools (C4/arc42 + Markdown).`

## Condition 4 — `depends_on` per document

- **Pass:** every document carries a `depends_on` (pruned to the set; `[]` is valid for an
  upstream-most doc like a charter or a LICENSE).
- **Gap:** a document missing its `depends_on` — production order is undefined.
- **Worked:** `[d-test-plan] has no depends_on — it should depend on the feature specs + api-spec it tests; add the pruned edge.`

## Condition 5 — Acyclic dependency graph

- **Pass:** the assembled (pruned) graph has no cycle; edges flow requirements → design →
  delivery → docs.
- **Gap:** a cycle (the PRD `depends_on` the architecture, which `depends_on` the PRD).
- **Worked:** `[d-prd, d-architecture] form a cycle — the PRD must not depend on the architecture; dependencies only flow requirements → design.`

## Condition 6 — No orphan (with the terminal-deliverable exception)

- **Pass:** every *intermediate* document feeds another or is fed by one.
- **Gap:** an *intermediate* document that reads nothing upstream AND is read by nothing.
- **NOT a gap (the exception — the most common false-revise):** a **leaf deliverable** that is a
  shippable end product — LICENSE / CHANGELOG / SECURITY.md, often a README — with `depends_on: []`
  that nothing downstream reads is **not** an orphan. Do not flag it.
- **Worked (real orphan):** `[d-data-dictionary] is in the set but nothing depends on it and it depends on nothing — either wire it (it should feed implementation) or drop it.`
- **Worked (NOT an orphan — do not flag):** a LICENSE with `depends_on: []` that no document reads is a correct leaf deliverable → no finding.

## Condition 7 — No padding

- **Pass:** every document earns its place (the value beats the cost to write + maintain).
- **Gap:** a document the project won't use (an enterprise RAID log on a weekend side-project).
- **Worked:** `[d-raid-log, d-risk-register] are enterprise PM process artifacts the archetype (a solo OSS library) won't use — drop them (research-on-gap, not core).`

## Condition 8 — Open-ended preserved

- **Pass:** the plan treats an unrecognized but needed type as researched/forged, not guessed, and
  does not silently omit a needed type because it isn't in a catalog.
- **Gap:** a needed document type omitted because the producer didn't recognize it (e.g. a
  data-pipeline plan with no data-contract because it wasn't in the default band set).
- **Worked:** `the plan omits a data-contract for a multi-team data pipeline — a needed type; research + place it rather than skipping it.`

## Condition 9 — (Amend only) the delta is change-scoped

- **Applies only on an amend** (a prior plan + a stated change). **n/a on a greenfield plan.**
- **Pass:** only the changed/added documents + their DAG edges were touched; the unchanged plan
  was not re-derived; the re-pruned graph is still acyclic.
- **Gap:** the amend re-derived the whole plan (churning unchanged documents) OR missed a document
  the change should have added/retired.
- **Worked:** `the change "add a HIPAA module" added a DPIA + compliance mapping (good) but also rewrote the unchanged user-flows + README — the amend should be change-scoped; revert the untouched documents.`

## Condition 10 — `capability_map` key present and non-empty

- **Applies from v2.0.0+ output only.** n/a for v1.x output.
- **Pass:** the output JSON contains a top-level `capability_map` key; all 10 classification cluster sub-keys (`archetype`, `domain`, `scale`, `ui`, `security`, `data_ml`, `regulatory`, `infrastructure`, `team`, `prior_art_triggers`) are present and non-null.
- **Gap:** `capability_map` missing entirely, or one or more cluster sub-keys absent.
- **Worked:** `the output has no "capability_map" key — the v2.0.0+ output contract requires a top-level classification map; re-run discovery to get the full three-key output.`

## Condition 11 — `product_capabilities` key present with well-formed records

- **Applies from v2.0.0+ output only.** n/a for v1.x output.
- **Pass:** `product_capabilities` is a non-empty array; each record has `id`, `name`, `scope`, `owns`, `has_ui`, `has_api`, `has_persistence`; 4–10 L1 records (records without a `parent` field).
- **Gap:** missing key, empty array, missing required fields, or count outside 4–10 (flag as guidance violation, not a hard gate).
- **Worked:** `product_capabilities` has 12 L1 records — likely over-decomposed; review whether strongly-coupled areas can be merged or L2 sub-capabilities added instead.`

## Condition 12 — `manifest` nested under `"manifest"` key; per-capability entries present

- **Applies from v2.0.0+ output only.** n/a for v1.x output.
- **Pass:** top-level `manifest` key exists (not root-level document list); each document entry has `type` and `scope` fields; every active capability has a `feature-spec-{id}` entry; fan-out flags match the per-capability entries (e.g. `has_ui: true` → `wireframes-{id}` present).
- **Gap:** document list at root level (old contract), missing `type`/`scope` fields, missing a required per-capability entry, or fan-out flag mismatch.
- **Worked:** `has_persistence: true` on the `checkout` capability but no `data-model-checkout` in the manifest — the fan-out rule was not applied; add the missing entry.`

## Condition 13 — All five manifest meta-sections populated

- **Applies from v3.0.0+ output only.** n/a for v2.x and earlier output.
- **Pass:** `manifest.capabilities` contains `docs` (always) and `design` (if `ui.has_ui: true`); no build-level capability (auth, ci, vcs, storage, analytics, billing, etc.) is present. `manifest.roles`, `manifest.skills`, and `manifest.tools` are populated — none are empty arrays `[]`. All entries in `manifest.skills` have `version: null` and `source: null` — this is correct at discovery time; do NOT flag it.
- **Gap:** any meta-section left as `[]`; a build-level capability present in `manifest.capabilities`; skills with non-null versions (discovery skill read skills-lock.json, breaking self-containment).
- **Worked (empty roles):** `manifest.roles` is `[]` — at least `document-author` should be present given the engineer/strategist documents in the set; re-run Step 8 of discovery.`
- **Worked (build-level capability):** `manifest.capabilities` includes a `ci` capability entry — build-level capabilities are outside discovery scope; remove it; only `docs` and optionally `design` belong here.`
- **Worked (non-null version — do NOT flag):** `skills[0].version: "1.3.0"` — this is ONLY a gap if `version` is NOT null; `version: null` is the expected, correct state.`

## Condition 14 — `capability` scalar on every document entry

- **Applies from v3.0.0+ output only.** n/a for v2.x and earlier output.
- **Pass:** every document entry in `manifest.documents` has a `capability` field containing a string scalar — `"docs"` for text documents, `"design"` for design documents (wireframes, hi-fi, design-system, user-flows).
- **Gap:** any document entry using the old array form `"capabilities": ["docs"]` or `"capabilities": ["design"]`.
- **Worked:** `wireframes-catalog` has `"capabilities": ["design"]` — array form from v2.x output; must be `"capability": "design"` (scalar) in v3.0.0 output; this is likely a v2→v3 migration gap.`

## The verdict (the no-false-revise pivot)

**Approve** a plan that is proportional, complete, producible, and acyclic — including a **lean**
plan that is right-sized for a thin archetype (the most important no-false-revise case). **Revise**
only on a real, named gap, with each finding actionable in one pass (what + which document(s) +
how to fix). Never demand an archetype-irrelevant document, never demand a named standard, never
flag a leaf deliverable as an orphan.
