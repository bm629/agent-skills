---
name: authoring-user-flows
description: >
  Use when authoring a user-flows document — the map of the paths a user takes
  through a product to accomplish each goal: entry points, the happy path, the
  decision branches, the error/recovery paths, the screens/states traversed, and
  the success criteria, each flow traced back to a product goal/persona. Guides the
  METHOD, not the outline: deriving flows from upstream goals + personas (never
  inventing them), enumerating every branch and error path so no path dead-ends, and
  rendering each flow as a synced diagram + numbered narrative. Composes with a
  separate user-flows template tool (which supplies the section structure) and a
  research capability. Assumes an approved PRD as upstream input — never a blank page.
  Not for reviewing a finished user-flows doc, not for screen layout/wireframes, and
  not for authoring the PRD itself.
extensions:
  claude:
    when_to_use: "authoring a user-flows / task-flow / interaction-flow document from a PRD"
    argument-hint: "<the PRD whose goals + personas to map into user flows>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `authoring-user-flows` — SKILL.md

> **Variant:** standard · **When to use:** a producer is authoring the user-flows
> document for a product/feature and needs the derivation method + the walkability
> bar, composing the section structure from a separate template tool.

## Overview

This skill guides authoring a **user-flows document**: the navigation/interaction
graph of a product — where users enter, the happy path they walk, where the path
forks, the screens/states they pass through, and what happens when things go wrong.
It carries the *judgment* (how to derive flows from upstream goals instead of
inventing them, how to make sure no path dead-ends, how to keep a diagram and a
narrative in sync), not a section list — the structure comes from a template tool.
The document sits below an approved PRD (which supplies the goals + personas this
realizes) and above wireframing (every screen a flow names becomes a wireframe
target). Scope is the interaction graph, not pixels and not the PRD's product
decisions.

## When to activate

- Authoring a user-flows / task-flow / interaction-flow document for a product or
  feature, given an approved PRD with goals + personas.
- Mapping the paths (entry → steps → branches → error/recovery → exit) a user
  takes to accomplish each product goal, so a downstream wireframing pass can
  enumerate every screen.

**Do NOT activate when:**

- Reviewing/judging a *finished* user-flows doc — that is the review-side gate
  (`reviewing-user-flows`), which asserts the same bar this skill produces to.
- Designing screen layout / pixels — that is `authoring-wireframes`, which consumes
  these flows.
- Authoring the upstream PRD itself, or re-deciding the product goals/personas —
  those are inputs, not outputs, here.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream documents discovery determined inform this one) — and trace this document's content back to them. Do not assume a fixed input: the typical upstreams this skill names are method guidance, not a cap on what you receive. Be **self-contained** — produce the document from *whatever* context you actually receive; when an expected informing document is absent, proceed on what you have and surface the gap as an explicit assumption, never fabricate to fill it. And **use a research capability where one is available** (deep-research) to make the document comprehensive and exhaustive, not merely to fill the template.

## Workflow

> **Compose with the template tool first.** Before drafting, obtain the user-flows
> section structure from the content-template tool (the `content-template-gateway`
> capability, or whatever template provider is installed). It supplies the
> per-flow slots (goal/PRD tie-back, entry points, steps, decision branches,
> error/recovery paths, screens/states, success criteria) and the coverage map /
> screens-index sections. **Never hardcode a competing outline** — this skill fills
> the template's slots with derived content; it does not redefine them. Use a
> research capability (the `deep-research` capability, else web search) to ground any
> domain conventions you are unsure of.

### Step 1: Derive one flow per goal/persona — don't invent

Treat each PRD goal as a **job** the persona is trying to get done, and produce one
flow per goal/persona pairing. Different personas may approach the same goal
differently — give each its own flow rather than collapsing them. This is the
no-orphan guarantee: every PRD goal/persona ends up with a flow, and every flow
points back to a PRD goal/persona. Fill the template's coverage map with that
mapping first; it is the spine the rest hangs on.

### Step 2: Map the happy path first

For each flow, lay down the critical path most users follow — entry point → the
ordered steps → the success exit — in plain language, with no errors or edge cases
yet. Name every screen/state each step traverses with a stable name you will reuse
verbatim in the diagram, the narrative, and the screens index. Layer complexity onto
this skeleton; do not start from the edge cases.

### Step 3: Enumerate every decision branch

At each point where the user can go more than one way, name **all** outgoing
branches and resolve each to a step, another flow, or a clean exit. A decision with
one side unmapped is the gap that surfaces late in build. No dangling "Yes/No" with a
missing arm.

### Step 4: Walk a fixed edge-case checklist at every step — no dead ends

Do not enumerate error paths from inspiration; walk this checklist at each step so
coverage is systematic:

- **Empty / null states** — empty lists, no search results, unpopulated fields.
- **Invalid + extreme inputs** — boundary analysis (try 0, 1, max, max+1), long
  strings, special characters, pasted content.
- **Network / timeout / integration errors** — slow connections, a dependency that
  returns an error.
- **Interruption / session loss** — user closes the tab and returns: resume or
  restart?
- **Permission / auth denial** — the user lacks access mid-flow.
- **Back / cancel** — every reverse and abort routes somewhere clean.

For each applicable case, give the user a state and a **recovery path back to a
productive step** — never strand them. Every error state must tell the user two
things: *what went wrong* and *how to fix it*.

### Step 5: Render both notations, kept in sync

Render each flow **twice**: a Mermaid flowchart (terminals for start/end, rectangles
for screens/states, diamonds for decisions, arrows labelled with the choice/
condition) **and** a numbered narrative plus an explicit branch/error-path list. The
diagram gives the visual graph; the narrative makes it walkable and reviewable by
non-technical readers (frame it as the user's story: goal = plot, persona =
character, friction = the decisions). The two must describe the *same* graph — a
node or branch present in one but absent from the other is a defect to fix before
handoff.

### Step 6: Surface thin-PRD gaps as assumptions / open questions

Where the PRD did not specify something a flow needs, state the **assumption** you
made (so a reviewer can challenge it) and list any unresolved decision as an **open
question** — never silently invent a product decision and bury it inside a flow.

### Step 7: Self-check against the walkability bar (below) before handoff

Run the quality bar. Fix every miss before handing the document to review or to
wireframing.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** The section structure comes from the template tool;
  this skill never ships a competing outline.
- **Derive, don't invent.** Every flow traces to a PRD goal/persona; every PRD
  goal/persona has a flow. No orphans either direction.
- **No dead ends.** Every decision branch resolves, and every error/edge state has a
  recovery path back to a productive step.
- **Both notations, in sync.** Each flow has a Mermaid flowchart AND a numbered
  narrative + branch/error list, describing the same graph.
- **Screens enumerable.** The screens index is the complete union of every flow's
  screens/states, so downstream wireframing can enumerate them all.

**Preferences (override-able):**

- One flow per goal/persona pairing; split a shared goal when personas diverge.
- Plain language in the narrative; expand abbreviations; label every diagram edge.
- Proportion the document to the PRD's goal/persona set — neither pad nor truncate.

## Gotchas

- **Happy-path-only flows.** They look complete but are brittle — most real users
  eventually leave the ideal path. The edge-case checklist (Step 4) exists so error
  coverage is systematic, not inspirational.
- **Diagram and narrative drift.** Editing one and forgetting the other ships a
  contradiction. Treat them as one artifact in two renderings; reconcile on every
  change.
- **Inventing product decisions inside a flow.** A flow built on an unstated
  assumption is a hidden risk. Lift the assumption out into the assumptions/open-
  questions section where it can be challenged.
- **Screen names that drift across sections.** If a screen is "Cart" in the diagram
  and "Basket" in the narrative, wireframing can't resolve it. Use one stable name
  everywhere.
- **Collapsing distinct personas into one flow.** Hides the way different users take
  different paths to the same goal. Give each its own flow when they diverge.

## Anti-patterns

- **"The diagram is enough."** A flowchart alone isn't walkable or reviewable in
  text; the numbered narrative + branch list is not optional.
- **"I'll bake the section list into the doc myself."** That duplicates the template
  and drifts from it. Always compose the structure from the template tool.
- **"Edge cases are an edge concern — happy path ships."** Missing branches and
  unhandled error states are the defects that surface in build and strand users.
- **"The PRD didn't say, so I'll just decide."** Silent product decisions belong in
  the assumptions/open-questions section, surfaced, not buried in a step.
- **"Layout while I'm here."** Screen layout is a separate downstream document; this
  is the navigation graph only.

## Walkability quality bar

A user-flows document is **complete + walkable** when ALL hold (this is the same bar
the review-side gate asserts):

1. **Goal/persona coverage — no orphans.** Every PRD goal (and persona) maps to a
   flow; every flow traces back to one.
2. **Defined entry + exit.** Every flow names all entry points and at least one
   success exit; every alternate exit (cancel/abandon/hand-off) is clean.
3. **Every decision branch resolved.** Each decision lists all outgoing branches;
   each resolves to a step, a flow, or an exit.
4. **Every error/edge state has a recovery — no dead ends.** Empty, invalid-input,
   timeout, integration-error, interruption, and permission-denied states are
   present where applicable and route back to a productive step; error states say
   what went wrong AND how to fix it.
5. **Steps are unambiguous + walkable.** A reader follows the narrative end-to-end
   without guessing; each step names its screen/state + the user action.
6. **Both notations in sync.** Every flow has a flowchart AND a narrative + branch/
   error list describing the same graph.
7. **Screens enumerable for wireframing.** The screens index is the complete union
   of every flow's screens/states.
8. **Assumptions/open questions surfaced.** Thin-PRD assumptions are stated and
   unresolved blockers listed, not silently decided.

## Output

A user-flows document in markdown: a coverage map (PRD goal/persona → flow), one
section per flow (each rendered as a synced Mermaid flowchart + numbered narrative +
branch/error list, with its entry points, decision branches, error/recovery paths,
screens/states, and success criteria), a cross-flow transition list, a screens index,
and an assumptions/open-questions section — composed onto the template tool's
structure. The artifact is consumed by the review-side gate (which judges it against
the walkability bar above) and by the downstream wireframing document (which
enumerates every screen the flows name). The method + bar are medium-independent: a
future design-tool backend changes only the rendering, not the derivation or the bar.

## Related

- **Template provider** (`content-template-gateway` capability) — supplies the
  user-flows section structure this skill composes onto; never duplicated here.
- **Research capability** (`deep-research`, else web search) — grounds domain
  conventions and the derivation evidence.
- **Upstream input — the PRD.** Required context: its goals + personas are what the
  flows realize. This is never authored from a blank page.
- **`reviewing-user-flows`** — the review-side gate that asserts the same
  walkability bar; produce-side and review-side are single-sourced.
- **`authoring-wireframes`** — the downstream consumer; each screen a flow names
  becomes a wireframe target, so a complete screens index is the handoff contract.

## Progressive disclosure

- `references/sources.md` — research provenance for the section set, the derivation
  method, and the walkability bar. Load when verifying a claim's grounding.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k.
