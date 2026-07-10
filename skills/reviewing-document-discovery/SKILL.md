---
name: reviewing-document-discovery
description: >
  Use when judging a produced document PLAN — a manifest of which documents a project will
  produce, each with producer/tools/skills/depends_on — to decide if it is sound enough to
  produce from. An acceptance gate, not authoring. Judges a fourteen-condition bar single-sourced
  with project-document-discovery's Self-check (v6.0.0): proportional; load-bearing present;
  production reqs + depends_on per doc; acyclic graph; no orphan (leaf deliverables like
  LICENSE/README exempt); no padding; open-ended preserved; change-scoped amend delta; skills carry
  purpose/requirements;
  capability_map + product_capabilities keys valid; manifest nested with fan-out entries matching
  flags; all five manifest meta-sections populated (capabilities/roles/skills/tools not empty,
  no build-level capabilities); capability scalar on every document entry (not array). Emits
  exactly one terminal VERDICT: approve|revise. Review-only — not a document's internal quality,
  not the coherence of finished documents (reviewing-document-set).
extensions:
  claude:
    when_to_use: "judging a produced document plan/manifest for soundness (proportional, complete, acyclic) and emitting one approve/revise verdict"
    argument-hint: "<the produced document plan + the idea/archetype it was made for (+ any stated change, for an amend)>"
version: "1.5.0"
forge:
  status: reviewed
  forged: 2026-06-15
  reviewed: 2026-07-10
---

# `reviewing-document-discovery` — SKILL.md

> **Variant:** standard · **When to use:** judging a produced document plan (a manifest of which documents a project will produce) — deciding whether it is sound enough to produce from, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the **acceptance gate over a produced document plan** — the independent reviewer for what `project-document-discovery` produces. Loaded by a reviewer holding the plan (and the idea/archetype it was made for), it answers one question: **is this the right set of documents — proportional, complete, and producible — sound enough to start producing from?** It applies a fixed **fourteen-condition bar** (nine original + three v2.0.0 output-contract conditions + two new v3.0.0 manifest-completeness conditions), then emits a single machine-parseable verdict plus actionable findings the producer acts on.

The bar is **single-sourced 1:1 with the discovery skill's Self-check** (its Step 9, v6.0.0): the discovery skill self-checks against these fourteen items so it produces a good plan; this skill asserts the same fourteen **independently** (you cannot grade your own homework). It is **review-only**: it never authors, fixes, or re-plans — it reports findings, the producer revises.

## When to activate

- A produced document plan / manifest needs an accept/revise decision before the documents are produced.
- You are the independent gate over a plan `project-document-discovery` (or any equivalent) produced.
- Re-judging a plan after fixes from a prior `revise`, or judging an **amend** (an existing plan + a stated change → a delta).

**Do NOT activate when:**

- You are judging a **single produced document's internal quality** (a PRD, an architecture doc) — use that document's own per-type reviewer.
- You are judging whether a set of **finished documents** are mutually coherent — use `reviewing-document-set` (that is the produced-corpus gate; this is the up-front plan gate).
- You are **authoring the plan** — that is `project-document-discovery`; this is review-only.

## Inputs

- **The produced document plan** in the discovery skill's output shape — a list of documents, each with `what` it is, its **producer role**, **tools/providers**, **skills**, and **`depends_on`**.
- **The idea + archetype** the plan was made for — needed to judge proportionality (what is load-bearing vs padding for *this* project).
- **(Amend only) the prior plan + the stated change** — to judge the delta is change-scoped.

A missing idea/archetype is a guidance gap (judge what you can, flag what you can't) — never fabricate the project's intent.

## Workflow

The method is fourteen conditions, then a verdict. Read the whole plan (and the idea/archetype) first.

### Step 1 — Orient

Note the **archetype** (a thin CLI tool vs a UI SaaS vs an ML product calls for very different sets) and whether this is a **greenfield** plan or an **amend** (a prior plan + a stated change). Assume the plan was produced by a capable discovery pass — you are the independent check, looking for the gaps it may have rubber-stamped.

### Step 2 — Judge the fourteen conditions

1. **Proportional to the archetype.** The set is sized to the project — no **over-selection** (a PRD + wireframes + a design system for a CLI tool) and no **under-selection** (a load-bearing doc cut to look lean). Judge against the archetype, never a fixed taxonomy.
2. **Load-bearing present.** The documents that define the features (PRD / feature specs; for UI products, the design docs) are in the set.
3. **Production requirements per document.** Every document has its **author + reviewer `roles` pair** (exactly two ids in `[author, reviewer]` order, matching the archetype — `[document-author, document-reviewer]` for engineer/strategist, `[designer, design-reviewer]` for designer) + **tools/providers** + **both the authoring and reviewing `skills`** (e.g. `[authoring-prd, reviewing-prd]`).
4. **`depends_on` per document.** Every document carries a `depends_on` (pruned to the set).
5. **Acyclic dependency graph.** The assembled (pruned) `depends_on` graph has **no cycle**; edges flow requirements → design → delivery → docs.
6. **No orphan — with the terminal-deliverable exception.** Every *intermediate* document either feeds another or is fed by one. A **leaf deliverable** that is itself a shippable end product — a LICENSE / CHANGELOG / SECURITY.md, and often a README — with `depends_on: []` that nothing downstream reads is **NOT** an orphan; do **not** flag it. Only an *intermediate* document that reads nothing upstream AND is read by nothing is an orphan.
7. **No padding.** No document the project won't use.
8. **Open-ended preserved.** The plan treats an unrecognized type as *researched/forged*, not guessed — it does not silently omit a needed type just because it isn't in a catalog.
9. **(Amend only) the delta is change-scoped.** On an amend, only the changed/added documents + their DAG edges were touched; the unchanged plan was not re-derived, and the re-pruned graph is still acyclic. (n/a on a greenfield plan.)
10. **`capability_map` key present and complete.** The output JSON contains a top-level `capability_map` key; all 10 v2 classification cluster sub-keys (`archetype`, `domain`, `regulatory`, `scale`, `security`, `integrations`, `ui`, `data_ml`, `infrastructure`, `business`) are present, plus the model-authored `prior_art_triggers` block. Presence + coherence only — the deterministic validator (`scripts/validate.py`) owns trigger correctness; do NOT re-derive the trigger formula here. (n/a for v1.x output; applies from 4.0.0 output.)
11. **`product_capabilities` key present with well-formed records.** The output JSON contains a top-level `product_capabilities` array; each record has the required fields (`id`, `name`, `scope`, `owns`, `has_ui`, `has_api`, `has_persistence`); the list contains 4–10 L1 records (records with no `parent` field or `parent: null`). If the count falls outside 4–10, flag it as a finding (guidance violation, not a hard gate). (n/a for v1.x output.)
12. **`manifest` nested under `"manifest"` key; per-capability entries present.** The output JSON has a `manifest` key (not root-level document list); each document entry has `type` and `scope` fields; per-capability entries (`feature-spec-{id}` for every active capability) are present; fan-out flags (`has_ui`, `has_api`, `has_persistence`) match the per-capability document entries produced. (n/a for v1.x output.)
13. **All five manifest meta-sections populated.** `manifest.capabilities` contains `docs` (always) and `design` (if `ui.has_ui: true`); no build-level capability (auth, ci, vcs, storage, etc.) is present. `manifest.roles`, `manifest.skills`, and `manifest.tools` are populated from the document set — none are empty arrays `[]`. `manifest.roles` holds the full author/reviewer pair for every archetype present (document-author + document-reviewer if any engineer/strategist doc; designer + design-reviewer if any designer doc), and every role entry is a **pure persona** (no `skills`/`tools` fields). Every entry in `manifest.skills` has `version: null`, `source: null`, a populated `purpose`, and a non-empty `requirements` list; every skill AND role entry carries `resolved_id` and `match_status`, both `null` at discovery time — do not flag the null `version`/`source`/`resolved_id`/`match_status` as gaps (the approval gate resolves them). (n/a for v2.x and earlier output.)
14. **`capability` scalar on every document entry.** Every document entry in `manifest.documents` has a `capability` field containing a string scalar (`"docs"` or `"design"`). An entry using the array form `"capabilities": [...]` fails this condition. (n/a for v2.x and earlier output.)

### Step 3 — Decide and emit

Weigh the findings. **Approve** a plan that is proportional, complete, producible, and acyclic — do not false-revise a **lean** plan that is right-sized for a thin archetype. **Revise** on any real, named gap (over/under-selection, a missing producer/`depends_on`, a cycle, an intermediate orphan, padding). Emit the output contract below.

## Rules

**Hard rules (never violate):**

- **One terminal verdict.** End with **exactly one** line — `VERDICT: approve` or `VERDICT: revise` — for the whole plan. (A caller typically reads only the last `VERDICT:` line.)
- **No false-revise.** Approve a proportional plan; a lean set that is right-sized for a thin archetype is an **approve**, not a revise. Revise only on a real gap, with findings **actionable in one pass** (what + which document(s) + how to fix).
- **No invented requirements.** Judge the OUTCOME (a proportional, sufficient, acyclic plan). **Never demand an archetype-irrelevant document** (a data-model for a stateless CLI, wireframes for a library), never demand a named standard be cited, never require a document just because a catalog lists it. The plan is open-ended by design.
- **Review-only.** Never author, fix, or re-plan — report findings, the producer revises.
- **The terminal-deliverable exception is load-bearing.** Never flag a leaf deliverable (LICENSE/README/CHANGELOG) as an orphan (condition 6).

## Gotchas

- **False-revising a lean plan.** A thin CLI tool's plan (a README + a short design note) is *correct*, not incomplete — proportionality is judged against the archetype, not an absolute checklist.
- **Flagging a leaf deliverable as an orphan.** A LICENSE/README/CHANGELOG with no `depends_on` and no downstream reader is a shippable end product, not an orphan (condition 6) — the most common false-revise.
- **Demanding the full taxonomy.** Requiring every catalog band/overlay regardless of the project recreates the heavy mandatory taxonomy the discovery skill exists to avoid — that is over-selection, which *you* should be catching, not causing.
- **Drifting into document review.** Judging whether the PRD is *good* is the PRD's own reviewer's job; here, judge only whether the *plan* picked the right set and wired its dependencies.
- **Re-validating the whole plan on an amend.** On an amend, judge the **delta** (condition 9) — do not re-litigate the unchanged, already-sound plan.

## Anti-patterns

- **A verdict that isn't the last line**, or more than one verdict.
- **Demanding a document the archetype doesn't need** ("every project needs a PRD") — invented requirement.
- **Revising a lean plan** for being small when it is proportional to a thin archetype.
- **Flagging a leaf deliverable as an orphan.**
- **Rewriting the plan** instead of returning findings.

## Output

A findings report: zero or more actionable findings (each naming the affected document(s) + the fix), followed by **exactly one** terminal `VERDICT: approve|revise`. On `revise`, the findings are the actionable list the producer turns into a fixed plan. The abstract consumers are the orchestrator that routes the fix and the discovery pass that revises.

## Related

- `project-document-discovery` — the **authoring** counterpart that produces the plan this skill gates; its Step-9 **Self-check** (v6.0.0) is the single source these fourteen conditions mirror 1:1 (author self-correction vs this independent gate).
- `reviewing-document-set` — the **produced-corpus** coherence gate (do the *finished* documents agree, after they are written); this skill is the **up-front plan** gate (is the *plan* sound, before they are written). They compose, no overlap.
- Per-type document reviewers (`reviewing-prd`, …) — judge one produced document's internal quality; this judges the plan that decided the set.
- `design-review` — gates generic design docs / specs / §15 implementation plans; it never gated a **document plan/manifest** (a different artifact), so there is no carve-out between them.
- The practice this operationalizes — ISO/IEC/IEEE 15289 (life-cycle information items + tailoring), right-sizing / "just barely good enough", the requirements→design→delivery DAG — see `references/sources.md`.

## Progressive disclosure

- `references/plan-quality-bar.md` — the fourteen conditions' per-condition pass/gap signals + worked findings (load esp. for conditions 1/6/9/10/11/12/13/14).
- `references/sources.md` — research provenance for the bar.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap; combined `description` + `when_to_use` truncated at 1,536 chars in the listing).
- Body ≤ ~500 lines / 5,000 tokens — heavy content lives in `references/`.

## Changelog

- **1.5.0** (2026-07-10) — additive update tracking `project-document-discovery` 6.0.0 (skill intent + resolution fields). Condition 13 now expects every `manifest.skills` entry to carry a populated `purpose` + a non-empty `requirements` list, and every skill AND role entry to carry `resolved_id` + `match_status` (both `null` at discovery time — carved out as not-a-gap, mirroring the existing `version: null` carve-out). Single-sourced 1:1 with the discovery Self-check item 13. Thirteen other conditions unchanged.
- **1.4.0** (2026-07-09) — additive update tracking `project-document-discovery` 5.0.0 (manifest review roles). Condition 3 now checks the author/reviewer `roles` pair (two ids in `[author, reviewer]` order, matching the archetype) + both the authoring and reviewing skill per document; condition 13 now requires `manifest.roles` to hold the full pair for every archetype present and every role entry to be a pure persona (no `skills`/`tools`). Single-sourced 1:1 with the discovery Self-check items 3 + 13. Twelve other conditions unchanged.

- **1.3.0** (2026-06-26) — update for `project-document-discovery` 4.0.0 (capability-map v2). Condition 10 rewritten to the 10 v2 classification clusters (drop `team`; add `business`, `integrations`) + the now model-authored `prior_art_triggers` block; presence/coherence only — trigger correctness is the deterministic validator's job (no formula re-derive). Single-sourced 1:1 with the producer's v2 classification. Other thirteen conditions unchanged.
- **1.2.0** (2026-06-21) — additive update for `project-document-discovery` v3.0.0. Two new conditions: 13 (all five manifest meta-sections populated — capabilities/roles/skills/tools not empty, no build-level capability, skills have version/source null) and 14 (capability scalar on every document entry — no array form). Description updated to "fourteen-condition bar." Twelve original conditions unchanged.
- **1.1.0** (2026-06-21) — additive update for `project-document-discovery` v2.0.0 output contract. Three new conditions added (10, 11, 12): capability_map key present with all 10 clusters; product_capabilities key present with 4–10 L1 records and required fields; manifest nested under "manifest" key with type/scope per entry and per-capability fan-out entries matching flags. Nine original conditions unchanged. Description updated to "twelve-condition bar."
- **1.0.0** (2026-06-15) — initial reviewed release. The independent gate over a produced document plan; nine conditions single-sourced 1:1 with `project-document-discovery`'s Self-check.
