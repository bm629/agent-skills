# The nine-condition plan-quality bar — pass/gap signals + worked findings

Depth for `reviewing-document-discovery`'s Step 2. Each condition lists what a **pass** looks
like, what a **gap** looks like, and a worked finding. The bar is **single-sourced 1:1 with
`project-document-discovery`'s Step-6 Self-check** (same nine items, same order). The body
SKILL.md carries the method; this file carries the per-condition detail — load esp. for the three
that drive most verdicts (1 proportionality, 6 the orphan exception, 9 amend).

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

## The verdict (the no-false-revise pivot)

**Approve** a plan that is proportional, complete, producible, and acyclic — including a **lean**
plan that is right-sized for a thin archetype (the most important no-false-revise case). **Revise**
only on a real, named gap, with each finding actionable in one pass (what + which document(s) +
how to fix). Never demand an archetype-irrelevant document, never demand a named standard, never
flag a leaf deliverable as an orphan.
