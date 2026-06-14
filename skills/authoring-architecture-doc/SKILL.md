---
name: authoring-architecture-doc
description: >
  Use when authoring a software/system architecture document — the
  whole-system structure: context and scope, the major components/services and
  their responsibilities, the interaction topology and integration boundaries,
  the significant technology choices and their rationale, and how the system
  realizes its non-functional/quality targets. Guides the producer through the
  METHOD, not the outline: scoping the boundary first, naming a responsibility
  per component, justifying each significant tech choice, giving every NFR
  target a realization, and recording each key decision as a STANDALONE,
  LINKED ADR file (the doc carries only a decisions index). Composes with a
  separate architecture-doc template tool AND an ADR template tool (section
  structure), plus a deep-research capability. Assumes the approved PRD +
  product direction as input — never a blank page. Not for reviewing a finished
  architecture doc, not for one feature's implementation design (a
  technical-design doc), and not for the API contract or data schema.
extensions:
  claude:
    when_to_use: "authoring a whole-system architecture document from an approved PRD"
    argument-hint: "<the approved PRD / product direction to derive the architecture from>"
version: "1.2.0"
forge:
  status: unreviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-architecture-doc` — SKILL.md

> **Variant:** standard · **When to use:** producing a whole-system architecture document from an approved PRD, to a quality bar a new engineer can grasp the system from and a feature's technical-design can be placed within.

## Overview

This skill is the *how-to* of writing a strong, whole-system architecture document — the judgment a producer applies, not the section list. It assumes three collaborators: an **architecture-doc template tool** that supplies the section *structure*, an **ADR template tool** that supplies the standalone decision-record shape, and a **deep-research capability** to ground each choice in evidence and established practice. The producer is handed the **approved PRD + product direction** (the scope, the personas, the non-functional targets) and **elaborates** it — never generic boilerplate. The altitude is the **whole system**: the components, topology, boundaries, tech, and NFR realization the entire system is built on. The bar to clear: a new engineer grasps the structure and the *why* of its major decisions, and a feature's technical-design can locate itself within it.

## When to activate

- Authoring a new architecture doc for a system or product from an approved PRD.
- Expanding a thin product direction into a whole-system architecture (sized to the product).
- Filling an architecture-doc template with researched, decision-complete content, recording the key decisions as linked ADR files.

**Do NOT activate when:**

- Reviewing or grading a finished architecture doc → use `reviewing-architecture-doc`, its dedicated reviewer (NOT the generic design-review, which is carved out of architecture-doc artifacts).
- Designing *one feature's* implementation → use a technical-design (TDD) skill; it lives at a lower altitude and references this doc.
- Specifying the wire contract (every endpoint) → an API-spec skill; the persistence model (every table) → a data-model skill. This doc names the major service interfaces and data stores *structurally*, not exhaustively.
- A one-line note or a trivial change that needs no architecture doc.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

### Step 1: Take the structure from the template tools — don't invent an outline

Get the section structure from your architecture-doc template tool (comprehensive variant), and the standalone decision-record shape from your ADR template tool. Do **not** restate or re-derive a section list here; this skill supplies the method that *fills* those sections well. If no template is available, obtain a comprehensive architecture structure (request/forge one, or fall back to a canonical architecture-documentation section set) and a canonical ADR shape, then proceed.

### Step 2: Load the PRD + direction; discover gaps; commit to elaborating it

Read the approved PRD and product direction. **Before drafting, fill knowledge gaps** — the real components the scope needs, the external dependencies, the stack actually in use, the NFR targets the PRD sets. Every component, boundary, and decision must trace back to *this* product — not a generic template fill. Where the input is thin, make assumptions **explicit** (an open question or stated assumption), never silently generic.

### Step 3: Research to ground each choice in established practice

Use a deep-research pass to ground the structure in established architecture practice (a recognized documentation model such as C4, well-known reference architectures, and the project's actual stack) rather than invent. Research the specific domain and the candidate technologies — not "architecture in general." **If no research capability is available, do NOT fabricate** a topology, a benchmark, or a rationale — flag the unresearched choice as an assumption to validate.

### Step 4: Apply the per-section method (the delta over the headings)

Fill the template's sections to this method:

- **Boundary first.** Before any component, draw the scope: what is in, what is explicitly **out** (and who owns it instead), the actors, and every **external dependency** with a one-line note on what it provides. The boundary is the first thing a new reader needs.
- **Stakeholders + concerns (the coverage spine).** Identify the stakeholders and the concern each brings (ISO/IEC/IEEE 42010), then make sure **every named concern is framed by some later section/view** — this is the completeness yardstick that lets the doc be checked against a concern set, not by feel. Proportional: a thin product has few stakeholders/concerns; the discipline is "no named concern left un-addressed", not a mandated matrix.
- **One responsibility per component.** Every major component/service the reader meets later is named once with its **single responsibility** and its kind (service / data store / client / worker / queue). No unexplained boxes downstream.
- **Protocol per arrow; diagram and narrative in sync.** In the topology, state which component talks to which, in which direction, over which style (sync request/response vs async event/message). Every box and arrow in a diagram is named in the prose and vice versa — no orphan elements; add a sequence view only for a non-obvious runtime flow.
- **Failure semantics per boundary.** For each integration seam: what crosses it (link the API-spec/data-model, don't inline the schema), the communication style, who owns the contract and how it versions, and **what happens when the far side is slow or down** (timeout / retry / fallback / degrade).
- **Rationale per significant tech choice.** Only the choices a reader would question or that shape the architecture (runtime, datastore, messaging, hosting/framework) — not every library. Each carries the **driver** (a requirement or NFR) it serves and what it was chosen **over**. "Team default" is acceptable *if stated*.
- **A realization per NFR target.** The **PRD owns the targets**; the architecture owns the **how**. For each quality target — scalability, availability, security, observability, deployment topology — document the mechanism that meets it. A restated target with no mechanism is a gap; a mechanism serving no target is candidate over-engineering. For a **load-bearing** target, make it measurable as a **quality-attribute scenario** (source / stimulus / artifact / environment / response / **response-measure**) — the response-measure ("p99 < 200ms at 1000 rps") is the testable constraint; plain prose suffices for a thin system.
- **Observability as a first-class system concern.** Beyond "we log" — name the **system-level** signals (the golden signals, the health/SLO-monitoring strategy, the key metrics/traces/alerts) an operator uses to diagnose the system in production. This is the system posture, distinct from one feature's signals (a TDD's concern).
- **Name the quality-attribute tradeoffs.** Where two attributes conflict (latency vs consistency, cost vs availability, security vs performance), state the tradeoff and **which way it was resolved + why** (the ATAM sensitivity/tradeoff framing). A tension the architecture clearly faces but never names is a gap.
- **Ground, don't invent; surface gaps.** Reflect the actual product and stack; surface unknowns as explicit assumptions/open-questions rather than inventing answers.

### Step 5: Record each key decision as a standalone, linked ADR (the central mechanism)

Architecture **decisions are not embedded inline.** Record each significant decision as a **standalone ADR file** (one decision per file, from the ADR template — Status / Context / Decision / Alternatives / Consequences), and carry only a **summary index** in the architecture doc that **links** each ADR. The discipline:

- **One decision per file.** A record bundling two decisions is wrong — split it.
- **Trace + alternative.** Each decision traces to a **driver** (a requirement or NFR) and names a **real alternative** with the trade-off it lost on. A decision with no considered alternative reads as unconsidered.
- **Immutable once accepted.** A changed decision is a **new** ADR that *supersedes* the old one (the old one's Status becomes "superseded by …"); you do not rewrite an accepted record. This keeps the index a faithful append-only history.
- **Index and files stay in sync.** Every indexed decision has a live ADR link; every accepted ADR appears in the index. A drifting index is a defect.

### Step 6: Amend an approved architecture doc (the delta path)

An architecture doc is a **living document** — it evolves by **delta, not rewrite**. When you are handed an approved doc + a change request (a new significant decision, a component split/merge, a swapped dependency, a moved NFR target), do NOT regenerate the whole doc. The method:

- **Scope the change** to the affected decision / component / boundary / NFR realization / cross-cutting stance — and edit in place, preserving stable section/decision IDs + review history.
- **Decisions change via supersede, never edit-in-place.** A changed decision is a **new ADR that supersedes** the old one (old Status → "superseded by NNNN" + reciprocal "supersedes NNNN" note); the **decisions index is updated** to reflect the new ADR + the superseded status. Rewriting an accepted ADR is the cardinal amend defect — it destroys the history.
- **Re-make the internal chain.** Does the topology still hold; do the diagrams still agree with the prose; do the NFR realizations still meet the targets; are the affected boundaries' failure semantics still stated?
- **Bump the doc's own version + changelog** (who / when / what / why — the produced doc's Version, distinct from this skill's semver).
- **Analyze the downward-broad ripple.** The distinctive architecture-doc ripple is **down to the fleet of per-feature technical-design docs** that located themselves within the changed structure (each may need its own amend), plus the **api-spec / data-model / deployment / release-runbook** the change touches. Upstream: a requirement-driven change means the **PRD/product-direction is amended first** (the spec→plan→impl order). Flag each affected downstream doc; never silently leave them stale.

### Step 7: Self-check against the usability bar before handing off

Confirm all hold (this is the bar `reviewing-architecture-doc` — the dedicated reviewer — asserts; the 10 conditions are single-sourced with this check):

1. **Structure graspable; boundary + concerns covered** — a new engineer can read context + components + topology and explain what the system is and how its parts fit; the boundary (in/out + owner) is explicit, every external dependency is named, and every identified stakeholder concern is addressed by some section/view.
2. **Components + boundaries named with responsibilities** — every major component AND every integration boundary is named with a stated responsibility / what crosses it. An unexplained box or seam fails. Kept at whole-system altitude (not feature-TDD detail, not api-spec/data-model enumeration).
3. **Diagram + narrative in sync** — every box/arrow appears in the prose and vice versa; diagrams read standalone; a runtime/deployment view where load-bearing.
4. **Key decisions as linked standalone ADRs, indexed + immutable** — each significant decision is its own ADR file (one per file) and appears in the index with a live link; index and files in sync; an accepted ADR is never rewritten (changes supersede). Inline-embedded full records, an index linking nothing, or a rewritten accepted ADR fail.
5. **Significant tech choices justified** — each carries a rationale (driver + a real alternative it beat). An unjustified significant choice fails.
6. **Each NFR target has a realization; tradeoffs named** — every quality target the PRD names has a documented mechanism (measurable scenario where load-bearing); quality-attribute tradeoffs are named + resolved. A restated target with no mechanism fails.
7. **Cross-cutting concerns addressed where the system has the surface** — resilience stance per integration boundary, security (trust boundaries/authn/secrets), privacy where sensitive data flows, and a system-level observability strategy.
8. **Requirements / ASR coverage** — every architecturally-significant requirement has a realizing structure/decision; no orphan structure. Usable downstream: a feature's technical-design can place itself within the architecture without asking the author.
9. **Grounded, not boilerplate; assumptions explicit; consistent with reality** — structure/tech reflect the actual product, grounded in established practice; unknowns surfaced as assumptions/open-questions (never silently defaulted, never fabricated); claims about what the system IS match the real code/topology.
10. **(Amend only) delta well-scoped** — on a change request, the delta is scoped + edited-in-place, decisions changed via supersede (index in sync), the doc version + changelog updated, and the downward ripple (dependent TDDs + api-spec/data-model/deployment) flagged. Not exercised on a greenfield first build.

**Proportionality governs every condition:** a thin product legitimately collapses what it lacks (one component → no topology; single-process → no deployment view; no hard NFR → light §6; first draft → no changelog). The non-collapsing baselines: no-fabrication, the boundary + external set, whole-system altitude, an accepted ADR never rewritten, and a realization for every target that DOES exist.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** Take the section structure from the template tool and the decision-record shape from the ADR template tool; this skill is the method that fills them. Do not paste a competing outline.
- **Decisions are linked, not embedded.** Every significant decision is a standalone ADR file; the doc carries only a linked index. Never inline a full decision record.
- **One responsibility per component, one decision per ADR.** No unexplained boxes; no record bundling two decisions.
- **Justify significant choices.** A significant technology choice with no rationale (driver + alternative) is not done.
- **Realize every NFR target.** The PRD owns the targets; restating a target without a mechanism is a gap. Never set targets here.
- **Stay at whole-system altitude.** Name major data stores and service interfaces structurally; do not enumerate every endpoint (API-spec) or every table (data-model), and do not slip into one feature's implementation design (technical-design).
- **Never fabricate.** Do not invent a topology, a benchmark, a vendor claim, or a rationale to fill a section. Flag the unknown as an assumption to validate. An invented mechanism is worse than an honest gap.
- **Elaborate the given input.** The specifics come from the PRD + research, never generic boilerplate.
- **Keep the diagram and narrative in sync.** Every diagram element is named in prose and vice versa.
- **Amend by delta + supersede, never rewrite.** On a change request, scope the delta and edit in place; change decisions via a new superseding ADR (never edit an accepted one), keep the index in sync, bump the doc version + changelog, and flag the downward ripple to the dependent technical-design docs + api-spec/data-model/deployment.

**Preferences (override-able):**

- "Comprehensive" sets the output *ambition*, but stay **proportional** — completeness of decisions + the surface-area floor, not word count. A thin product legitimately collapses sections it doesn't need (one component, no messaging, a trivial deployment).
- Express everything textually in the current medium — prose + component/container/deployment diagrams + a decision-index table; a future design-tool backend changes only the medium, not this method or bar.
- Prefer the smallest set of diagrams that conveys the structure (a context view + a container/topology view is usually enough); add a sequence view only where runtime behavior is non-obvious.

## Gotchas

- **Embedded decisions.** Pasting full context/alternatives/consequences inline instead of a linked ADR makes each decision un-addressable and the doc bloated — index + link standalone ADR files.
- **Editing an accepted ADR.** Rewriting an accepted decision destroys the history — write a new ADR that supersedes it instead.
- **Unexplained boxes.** A component appears in a diagram but is never given a responsibility — name it once in the components section.
- **Restated targets.** Copying the PRD's "99.9% uptime" into the doc without a redundancy/failover mechanism is restating, not realizing — give every target a how.
- **Over-engineering a thin product.** Inventing a message bus, a cache tier, and three environments a CLI tool will never use — size to the actual scope; a mechanism serving no target is a red flag.
- **Altitude slip.** Drifting into "this function calls that class" (feature-TDD) or "GET /v1/users returns …" (API-spec) — keep it whole-system; name the interface, link the contract.
- **Diagram/narrative drift.** The prose describes a worker the diagram omits (or vice versa) — they must agree.

## Anti-patterns

- **"I'll write the outline myself."** Duplicates the template tool — take the structure from it and the ADR shape from the ADR template tool.
- **"I'll list the decisions in a section here."** Embeds what should be standalone linked ADRs — one decision per file, indexed and linked.
- **"The stack is whatever; I'll pick something sensible."** Unjustified significant choices — each needs a driver and a real alternative, grounded in the actual product.
- **"The PRD says 100ms p99, so I'll write that down."** Restating a target is not realizing it — document the mechanism that achieves it.
- **"I'll add a queue and a cache to be safe."** Speculative structure for hypothetical needs — size to the product's real scope.
- **"Skip the research, I know architecture."** The research grounds *this product's* topology and tech in established practice — not architecture theory.
- **"I'll detail how each feature is built."** That is a technical-design doc at a lower altitude — this doc defines the whole-system structure those docs work within.

## Output

A **whole-system architecture document** that meets the **Step 7 usability bar** (graspable structure + concern coverage; components + boundaries named with responsibilities; diagram + narrative in sync; key decisions as standalone linked immutable ADRs, indexed and in sync; justified tech choices; a realization per NFR target + named tradeoffs; cross-cutting concerns addressed; ASR coverage; grounded-not-boilerplate + consistent with reality; delta-amendable), plus a set of **standalone ADR files** the doc's key-decisions index links. The **abstract consumer** is every engineer building within the system, the downstream per-feature technical-design docs (which place themselves within it), and `reviewing-architecture-doc` (which asserts the same 10-condition bar). The doc's *structure* comes from the template tools; this skill supplies the *content quality* and the decision-recording mechanism.

## Related

- An **architecture-doc template tool** (e.g. a content/template gateway) — supplies the comprehensive architecture section structure this skill fills.
- An **ADR template tool** — supplies the standalone decision-record shape (Status / Context / Decision / Alternatives / Consequences) the linked decision files use; there is no separate decision-authoring skill, the shape is formulaic.
- A **deep-research capability** — grounds the structure and the technology choices in established practice and evidence.
- The upstream **PRD + product direction** — the input context (scope, personas, NFR targets) this skill elaborates; never a blank page.
- The downstream per-feature **technical-design docs** — the consumers that locate themselves within this architecture.
- `reviewing-architecture-doc` — the **dedicated reviewer** that asserts this skill's Step-7 bar (the 10-condition gate, single-sourced with the self-check) and emits `VERDICT: approve|revise`. A finished architecture doc (+ its linked ADR files) routes there — NOT to the generic `design-review`, which is carved out of the architecture-doc artifact (it still gates generic design docs, RFCs, standalone ADRs, specs, and plans).

## Progressive disclosure

- `references/architecture-method.md` — the boundary+concerns / decomposition+topology / diagram-sync / ADR-mechanism / NFR-realization+measurable-scenarios / observability+resilience depth (load when filling those sections).
- `references/amend.md` — the supersede-convention amend procedure + index-sync + the downward-broad ripple (load when amending an approved doc).
- `references/sources.md` — research provenance for the method, the ADR mechanism, and the quality bar (load only to audit where the guidance came from).

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens.
- Heavy content lives in `references/`, loaded on demand.

## Changelog

- **1.2.0** (2026-06-14) — production-grade restructure: added the iteration/amend method (Step 6 — delta + ADR supersede + downward-broad ripple), the stakeholders/concerns coverage spine, measurable quality-attribute scenarios, observability as a first-class system concern, and quality-attribute tradeoffs; extended the self-check (Step 7) to the 10-condition bar single-sourced with the new dedicated reviewer `reviewing-architecture-doc`; routed reviews to the twin (design-review is carved out of architecture-doc artifacts). Additive — the whole prior method (boundary-first, one-responsibility components, the standalone-linked-ADR mechanism, justify-significant-choices, realization-per-NFR, diagram/narrative sync, altitude rule) is unchanged.
- **1.1.0** (2026-06-04) — prior reviewed release.
