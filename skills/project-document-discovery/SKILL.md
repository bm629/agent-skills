---
name: project-document-discovery
description: >
  Use when deciding which documents a software or product project needs to produce to ship to
  production — turning a project idea into a proportional document plan: which documents, who or
  what produces each, the order they depend on, and a self-check that the set is proportional,
  complete, and acyclic. Re-tailors an existing plan when the project changes (amend), not just
  greenfield. Covers the full SDLC document universe (seven lifecycle bands) plus domain overlays
  (data/ML, security/compliance, legal/governance, regulated/validation), keyed to the project
  archetype so a thin CLI tool gets a handful and a UI product gets many. Discovery only: it decides
  which documents and what it takes to produce them, not how to author them (a separate per-document
  authoring concern). Keywords: which documents does my project need, document discovery,
  documentation plan, SDLC documents, document manifest, proportional docs.

extensions:
  claude:
    when_to_use: "Deciding the set of documents a project needs (a document plan/manifest) from an idea, before producing any."
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}

version: "1.3.0"

forge:
  status: reviewed
  forged: 2026-06-03
  reviewed: 2026-06-15
---

# `project-document-discovery` — SKILL.md

> **Variant:** standard · **When to use:** invoked to turn a project idea into a proportional plan of the documents the project needs, each tagged with what it takes to produce it; returns the plan; control passes back to the caller.

## Overview

Given a software/product project idea, this skill decides **which documents the project needs to ship to production**, and **what it takes to produce each** — the producer role, the tools/providers, the skills, and which other documents it depends on. It is **discovery only**: it picks the *set* and describes *how each will be produced*, never how to author a document (that is a separate per-document authoring skill, composed with a template skill). The guiding discipline is **proportionality** — the document set is sized to the project, never a fixed taxonomy applied regardless of scale.

## When to activate

- ✅ Deciding which documents a new project needs *before* any document is produced.
- ✅ Producing a "document plan" / manifest that a later stage reads to produce the documents (and later to plan the build).
- ✅ Sizing a documentation set proportionally (a lean MVP vs a full product).

**Do NOT activate when:**

- **Authoring or templating a specific document** (writing the PRD, drafting the architecture doc) — use a per-document authoring skill + a content/template skill.
- **Discovering the build-time engineering roster** (what roles/tools/providers it takes to *build the product*) — that is a separate, later analysis done from the finished documents.
- The project already has an agreed document set.

## Workflow

Two modes. **Greenfield** (a fresh idea, no prior plan) runs the selection discipline in order, Steps 1–6. **Amend** (an existing plan + a stated project change) runs the **Iteration / amend** method below instead of re-deriving — re-tailoring the set for the change. The discipline grounds in **ISO/IEC/IEEE 15289** (the standard for life-cycle information items — items are tailored, "combined or subdivided … as needed," and "developed **and revised**") + the agile **right-sizing / "just barely good enough"** school; see `references/sources.md`.

The selection discipline (greenfield) — run it in order:

### Step 1: Classify the project archetype

Identify the kind of project (open-ended; research an unfamiliar kind): CLI tool · library/SDK · API service · web app · mobile app · data pipeline · … The archetype sets how large and design-heavy the document set should be.

### Step 2: Select a proportional document set

Consult `references/document-type-catalog.md` (the seven lifecycle bands + four domain overlays + a per-archetype load-bearing/skip table). Take the **load-bearing** documents for the archetype, add the bands the project actually needs, add any **domain overlay** the project triggers (data/ML, security/compliance, legal/governance, regulated/validation), and **skip** what it doesn't. A thin CLI tool may need only a README + a short design note and triggers no overlay; a UI product needs the fuller set. Open-ended: include a document type not in the catalog when the project needs it. This is **tailoring** in the ISO 15289 sense, sized for **ROI** ("just barely good enough"): a document earns its place only when the value of having it beats the cost to write + maintain it — under-selecting cuts a load-bearing doc, over-selecting pads. Judge by that outcome, never by a fixed taxonomy.

### Step 3: Attach each document's production requirements

For every chosen document, decide:
- **Producer role** — the specialist that produces it (e.g. product strategist → PRD, UX designer → wireframes/flows, systems architect → architecture/ADR, QA/SRE → test plan/runbook). Where the consumer uses an `archetype × domain` role model, express it that way (illustrative — see Output).
- **Tools/providers** — what it's produced with, **OSS-first** (oss → free → paid): e.g. wireframes → Penpot (or another open design tool), architecture → C4/arc42 + Markdown, API spec → OpenAPI, most prose → Markdown-in-repo. Name proprietary tools (Figma, Confluence) as options, not requirements.
- **Skills** — capabilities the producer will likely need.

### Step 4: Attach dependencies (the production DAG)

Give each document its `depends_on` — **every document that *informs* this one (and therefore must be produced before it)**, not only the strictly-blocking inputs. Include any upstream whose content materially sharpens this document, so its producer can read them all and the document comes out comprehensive (the producer is handed every `depends_on` document). Take each type's `depends_on` from its **catalog entry** (each entry carries an explicit `depends_on` list), then **prune it to the documents actually in this project's set** — an edge to a document the project isn't producing is simply dropped. Dependencies flow **requirements → design → delivery → docs**; every edge points from a later document to an earlier one. **Verify the assembled (pruned) graph is acyclic** — the catalog edges are pre-verified acyclic and pruning cannot introduce a cycle, so this is a safety check.

### Step 5: Research / forge-on-gap the unknowns

For a document type, archetype, or domain you don't recognize, **research it** (or forge a skill for it) before placing it — never guess its purpose, producer, or dependencies.

### Step 6: Self-check (the definition of done for the document plan)

Before returning the plan, confirm it passes the **nine-item self-check** — the plan's definition of done (a `reviewing-document-discovery` gate asserts the same nine, single-sourced):

1. **Proportional** to the archetype — no over-selection (padding) and no under-selection for the project's size/risk.
2. **Load-bearing present** — the documents that define the features (PRD / feature specs; for UI products, the design docs) are in the set; none cut "to look lean."
3. **Production reqs per document** — every chosen document has a producer role + tools/providers + skills (Step 3).
4. **`depends_on` per document** — every document carries its pruned `depends_on` (Step 4).
5. **Acyclic DAG** — the assembled (pruned) graph has no cycle.
6. **No orphan — with the terminal-deliverable exception.** Every *intermediate* document either feeds another or is fed by one. A **leaf deliverable** that is itself a shippable end product (a LICENSE / CHANGELOG / SECURITY.md, and often a README) with `depends_on: []` that nothing downstream reads is **NOT** an orphan — do not flag it. Only an *intermediate* document that reads nothing upstream AND is read by nothing is an orphan.
7. **No padding** — no document the project won't use.
8. **Open-ended preserved** — an unrecognized type is researched/forged, not guessed, and a needed type is not silently omitted just because it isn't in the catalog.
9. **(Amend only) the delta is change-scoped** — on an amend, only the changed/added documents + their DAG edges were touched; the unchanged plan was not re-derived.

If every item holds, **stop** and return the plan. If one fails, fix it (trim padding, restore a load-bearing doc, attach a missing producer/`depends_on`, break a cycle) before returning.

### Iteration / amend (re-tailoring an existing plan on a change)

When handed an **existing document plan + a stated project change** (a new feature, a pivot, a new domain/compliance trigger, an archetype shift), do **not** re-derive the plan — re-tailor it for the change:

1. **Identify + classify the change.** A new feature (usually revises existing docs); a pivot/scope change (may retire + add); a new domain/compliance trigger (adds an overlay); an archetype shift (re-tailors the band selection). If there is **no prior plan**, this is greenfield — run Steps 1–6 instead (amend is n/a).
2. **Re-tailor the set — the delta.** Proportionally and scoped to the change: **ADD** a newly-needed document, **RETIRE** one the change made irrelevant, **REVISE** the production requirements of one the change touches. Only what the change needs.
3. **Re-attach production requirements** for added/revised documents (Step 3).
4. **Re-prune the DAG** (Step 4) over the new set: drop a retired document's edges; add a new document's `depends_on`, pruned to the set; re-verify acyclic. Only the affected edges change.
5. **Run the Self-check on the delta only** (Step 6, item 9) — not a re-validation of the unchanged plan.

The amend decides *which documents change*. It is **not** the feature-routing layer (which capability area a change lands in), **not** the change-feeding flow, and **not** document authoring (how each changed document is re-written) — those are separate concerns the discovery skill composes with.

## Rules

**Hard rules (never violate):**

- **Discovery only.** Decide *which* documents and *what it takes* to produce them. Never author or template a document.
- **Proportional, never a fixed taxonomy.** Size the set to the archetype; a thin project gets few documents. Never apply a full enterprise document set regardless of project size.
- **Keep the load-bearing documents.** The documents that define the features (PRD / feature specs; for UI products, the design docs) are never cut to seem lean — everything downstream is read out of them.
- **Dependencies form a DAG.** Direction is requirements → design → delivery → docs; no cycles.
- **OSS-first tools/providers** (oss → free → paid); local/self-hostable preferred.
- **Research/forge-on-gap an unknown type;** never invent its purpose.

**Preferences (override-able):**

- Group the chosen set by lifecycle band.
- Name the producer as a role kind (titles vary by org); use `archetype × domain` where the consumer uses that model.
- For volatile detail (API endpoints, schemas), prefer **generate-and-link** over duplicating it in prose documents.

## Gotchas

- **Heavy fixed taxonomy on a small project.** Symptom: a dozen documents proposed for a CLI tool. Cause: skipping Step 1 (archetype classification). Fix: classify first, then size the set to it.
- **Cutting load-bearing docs to look lean.** Symptom: no PRD/feature spec, so downstream can't define the features. Fix: keep the load-bearing band; trim the optional bands instead.
- **Drifting into authoring.** Symptom: you start listing a document's sections or how to write it. Fix: stop at *which* document + *what it takes*; authoring is a separate skill.
- **Cyclic dependencies.** Symptom: the PRD `depends_on` the architecture. Fix: dependencies only flow requirements → design → delivery → docs.
- **Confusing production tools with build tools.** Symptom: listing the app's runtime database as a document-production provider. Fix: production tools *make the document* (Penpot for wireframes, OpenAPI for an API spec) — the product's own stack is out of scope here.

## Anti-patterns

- **"Every project needs the full SDLC document set."** No — the set is proportional to the archetype.
- **"While I'm deciding the set, I'll also outline how to write each one."** That is authoring; out of scope.
- **"I don't recognize this document type, I'll guess what it's for."** Research or forge-on-gap instead.
- **"Skip the PRD, we'll figure out features in code."** Features must be defined in documents first.
- **"Add a few more documents to be safe."** Padding; stop once the proportional set is complete.

## Output

A **document plan** (decision knowledge, not a fixed schema): a list of documents, each describing *what it is*, its *producer role*, *tools/providers*, *skills*, and `depends_on` — proportional to the project and forming an acyclic dependency graph. The exact serialization belongs to the consumer; this skill decides the *content* of each field. The abstract consumer is the next stage that produces the documents (and later reads them to plan the build).

Illustrative shape (one entry per document — adapt fields to the consumer's format):

```
- id: prd
  what: defines the product's goals, users, and features
  producer: product strategist            # e.g. archetype x domain: idea-strategist x product
  tools: [docs store]                      # OSS-first
  skills: [requirements-analysis]
  depends_on: []
- id: architecture
  what: system structure, key decisions (ADRs)
  producer: systems architect              # e.g. designer x system
  tools: [c4-or-arc42, markdown]
  depends_on: [prd]
- id: wireframes
  what: low-fidelity screen structure + flows
  producer: ux designer                    # e.g. designer x ux
  tools: [penpot]
  depends_on: [prd]
```

## Related

- A content/template skill (e.g. `content-template-gateway`) — the **authoring-time** counterpart that templates each chosen document. Composes with this skill: this one picks the *set*, that one templates *each*.
- A research skill (e.g. `deep-research`) — for researching an unfamiliar document type before placing it (Step 5).
- [`references/document-type-catalog.md`](references/document-type-catalog.md) — the document-type universe, the per-archetype proportionality table, and the typical dependency edges.

## Progressive disclosure

- `references/document-type-catalog.md` — the seven-band + four-overlay catalog (name + when-needed + what-it-feeds per type), the per-archetype load-bearing/skip table, and the common `depends_on` edges. **Load at Workflow Step 2** (selecting the document set).
- `references/sources.md` — research provenance for the catalog and the proportionality/dependency guidance.

No `scripts/` or `assets/` ship with this skill.

## Body budget

- `description` ≤ 1,024 chars (leads with "Use when …").
- Body kept well under the ~500-line / 5,000-token soft target; the heavy catalog lives in `references/` and loads on demand.

## Changelog

- **1.3.0** (2026-06-15) — production-grade redesign (additive). Step 6 "Re-check and stop" reshaped into an explicit **Self-check** (the nine-item definition of done for the plan, incl. the no-orphan terminal-deliverable exception), single-sourced with the new `reviewing-document-discovery` gate. Added the **Iteration / amend** method (re-tailor an existing plan on a stated project change — add/retire/revise + DAG re-prune, proportional, n/a greenfield). Named the proportionality method (ISO 15289 tailoring + ROI / "just barely good enough"). Re-grounded on ISO/IEC/IEEE 15289 (+ 12207). The catalog, the selection spine (Steps 1–5), the DAG model, and the discovery-only boundary are unchanged.
- **1.2.0 / 1.1.0** — catalog expansion (Band 0 + Band 6 + the four domain overlays; 5 → 7 lifecycle bands).
- **1.0.0** (2026-06-03) — initial reviewed release.
