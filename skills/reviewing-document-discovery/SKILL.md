---
name: reviewing-document-discovery
description: >
  Use when judging a produced document PLAN — a manifest of which documents a project will
  produce, each with producer/tools/skills/depends_on — to decide if it is sound enough to
  produce from. An acceptance gate, not authoring. Judges a nine-condition bar single-sourced
  with project-document-discovery's Self-check: proportional to the archetype (no
  over/under-selection); load-bearing present; production reqs + a depends_on per doc; an acyclic
  dependency graph; no orphan (a leaf deliverable like LICENSE/README is NOT one); no padding;
  open-ended preserved (an unrecognized type is researched, not guessed); and on an amend, a
  change-scoped delta. Emits exactly one terminal VERDICT: approve|revise. Approves a proportional
  plan (no false-revise on a lean one); revises only on a real, named gap; never demands an
  archetype-irrelevant document. Review-only. Not a document's internal quality, not the coherence
  of finished documents (reviewing-document-set), not authoring the plan (project-document-discovery).
extensions:
  claude:
    when_to_use: "judging a produced document plan/manifest for soundness (proportional, complete, acyclic) and emitting one approve/revise verdict"
    argument-hint: "<the produced document plan + the idea/archetype it was made for (+ any stated change, for an amend)>"
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-15
  reviewed: 2026-06-15
---

# `reviewing-document-discovery` — SKILL.md

> **Variant:** standard · **When to use:** judging a produced document plan (a manifest of which documents a project will produce) — deciding whether it is sound enough to produce from, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the **acceptance gate over a produced document plan** — the independent reviewer for what `project-document-discovery` produces. Loaded by a reviewer holding the plan (and the idea/archetype it was made for), it answers one question: **is this the right set of documents — proportional, complete, and producible — sound enough to start producing from?** It applies a fixed **nine-condition bar**, then emits a single machine-parseable verdict plus actionable findings the producer acts on.

The bar is **single-sourced 1:1 with the discovery skill's Self-check** (its Step 6): the discovery skill self-checks against these nine items so it produces a good plan; this skill asserts the same nine **independently** (you cannot grade your own homework). It is **review-only**: it never authors, fixes, or re-plans — it reports findings, the producer revises.

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

The method is nine conditions, then a verdict. Read the whole plan (and the idea/archetype) first.

### Step 1 — Orient

Note the **archetype** (a thin CLI tool vs a UI SaaS vs an ML product calls for very different sets) and whether this is a **greenfield** plan or an **amend** (a prior plan + a stated change). Assume the plan was produced by a capable discovery pass — you are the independent check, looking for the gaps it may have rubber-stamped.

### Step 2 — Judge the nine conditions

1. **Proportional to the archetype.** The set is sized to the project — no **over-selection** (a PRD + wireframes + a design system for a CLI tool) and no **under-selection** (a load-bearing doc cut to look lean). Judge against the archetype, never a fixed taxonomy.
2. **Load-bearing present.** The documents that define the features (PRD / feature specs; for UI products, the design docs) are in the set.
3. **Production requirements per document.** Every document has a **producer role** + **tools/providers** + **skills**.
4. **`depends_on` per document.** Every document carries a `depends_on` (pruned to the set).
5. **Acyclic dependency graph.** The assembled (pruned) `depends_on` graph has **no cycle**; edges flow requirements → design → delivery → docs.
6. **No orphan — with the terminal-deliverable exception.** Every *intermediate* document either feeds another or is fed by one. A **leaf deliverable** that is itself a shippable end product — a LICENSE / CHANGELOG / SECURITY.md, and often a README — with `depends_on: []` that nothing downstream reads is **NOT** an orphan; do **not** flag it. Only an *intermediate* document that reads nothing upstream AND is read by nothing is an orphan.
7. **No padding.** No document the project won't use.
8. **Open-ended preserved.** The plan treats an unrecognized type as *researched/forged*, not guessed — it does not silently omit a needed type just because it isn't in a catalog.
9. **(Amend only) the delta is change-scoped.** On an amend, only the changed/added documents + their DAG edges were touched; the unchanged plan was not re-derived, and the re-pruned graph is still acyclic. (n/a on a greenfield plan.)

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

- `project-document-discovery` — the **authoring** counterpart that produces the plan this skill gates; its Step-6 **Self-check** is the single source these nine conditions mirror 1:1 (author self-correction vs this independent gate).
- `reviewing-document-set` — the **produced-corpus** coherence gate (do the *finished* documents agree, after they are written); this skill is the **up-front plan** gate (is the *plan* sound, before they are written). They compose, no overlap.
- Per-type document reviewers (`reviewing-prd`, …) — judge one produced document's internal quality; this judges the plan that decided the set.
- `design-review` — gates generic design docs / specs / §15 implementation plans; it never gated a **document plan/manifest** (a different artifact), so there is no carve-out between them.
- The practice this operationalizes — ISO/IEC/IEEE 15289 (life-cycle information items + tailoring), right-sizing / "just barely good enough", the requirements→design→delivery DAG — see `references/sources.md`.

## Progressive disclosure

- `references/plan-quality-bar.md` — the nine conditions' per-condition pass/gap signals + worked findings (load esp. for conditions 1/6/9).
- `references/sources.md` — research provenance for the bar.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap; combined `description` + `when_to_use` truncated at 1,536 chars in the listing).
- Body ≤ ~500 lines / 5,000 tokens — heavy content lives in `references/`.

## Changelog

- **1.0.0** (2026-06-15) — initial reviewed release. The independent gate over a produced document plan; nine conditions single-sourced 1:1 with `project-document-discovery`'s Self-check.
