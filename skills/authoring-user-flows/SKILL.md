---
name: authoring-user-flows
description: >
  Use when authoring a user-flows document — the map of the paths a user takes
  through a product to accomplish each goal: entry points + the navigation/IA frame,
  the happy path, decision branches, error/recovery + edge states (incl. loading +
  success), interaction resilience (undo/resume/system-status), flow-level
  accessibility, and the screens/states traversed, each flow traced to a goal/persona
  job. Guides the METHOD, not the outline: deriving flows from upstream goals +
  prior-art patterns (never inventing them), enumerating every branch + error path so
  no path dead-ends, judging flow quality with objective heuristics, rendering each
  flow as a synced diagram + numbered narrative, and amending an existing doc as a
  scoped versioned delta. Composes with a separate user-flows template tool and a
  research capability. Assumes an approved PRD as upstream input — never a blank page.
  Not for reviewing a finished user-flows doc, not for screen layout/wireframes, and
  not for authoring the PRD itself.
extensions:
  claude:
    when_to_use: "authoring a user-flows / task-flow / interaction-flow document from a PRD, to a production-grade walkability + structure + resilience + accessibility + quality bar"
    argument-hint: "<the PRD whose goals + personas to map into user flows (+ the existing doc, when amending)>"
version: "1.3.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-13
---

# `authoring-user-flows` — SKILL.md

> **Variant:** standard · **When to use:** a producer is authoring (or amending) the
> user-flows document for a product/feature and needs the derivation method + the
> production-grade bar (walkability + structure + resilience + accessibility +
> quality + amend), composing the section structure from a separate template tool.

## Overview

This skill guides authoring a **user-flows document**: the navigation/interaction
graph of a product — where users enter, the IA frame the flows live in, the happy
path they walk, where the path forks, the screens/states they pass through, what
happens when things go wrong, whether the path is resilient and accessible, and
whether it is a *good* flow. It carries the *judgment* (how to derive flows from
upstream goals + prior art instead of inventing them, how to make sure no path
dead-ends, how to keep a diagram and narrative in sync, how to amend without
redrawing), not a section list — the structure comes from a template tool. The
document sits below an approved PRD (which supplies the goals + personas) and above
wireframing (every screen a flow names becomes a wireframe target). Scope is the
interaction graph, not pixels, not the PRD's product decisions, and **not a journey
map** (emotion/channel/touchpoint-over-time is out of scope).

## When to activate

- Authoring a user-flows / task-flow / interaction-flow document for a product or
  feature, given an approved PRD with goals + personas.
- **Amending** an existing user-flows doc with a scoped change (add/change/remove a
  flow or path) — a versioned delta, not a regenerate (see Step 11).
- Mapping the paths (entry → steps → branches → error/recovery → exit) a user takes,
  so a downstream wireframing pass can enumerate every screen.

**Do NOT activate when:**

- Reviewing/judging a *finished* user-flows doc — that is the review-side gate
  (`reviewing-user-flows`), which asserts the same bar this skill produces to.
- Designing screen layout / pixels — that is `authoring-wireframes`, which consumes
  these flows. Per-screen pixel accessibility (contrast/target-size) is also theirs.
- Authoring the upstream PRD itself, or re-deciding the product goals/personas.
- Producing a **user journey** (emotion/channel/over-time) — a different artifact.

## Inputs

Read **every document the plan hands you** — your `depends_on` set (the upstream
documents discovery determined inform this one) — and trace this document's content
back to them. The typical upstream is the **PRD** (goals + personas); a **design
system** (if one exists) supplies the navigation/app-shell + component vocabulary the
flows reference; when **amending**, the **existing user-flows doc** is handed in as an
input. Do not assume a fixed input: the named upstreams are guidance, not a cap. Be
**self-contained** — produce from *whatever* context you actually receive; when an
expected informing document is absent, proceed on what you have and surface the gap as
an explicit assumption, never fabricate to fill it. And **use a research capability
where one is available** (deep-research) to ground domain conventions + prior-art flow
patterns, not merely to fill the template.

**Capability context (when provided):** If a `capability_record` (a record from `capability-map.yaml product_capabilities`) is injected by the caller, read it before Step 1. It defines your scope boundary: `owns` = entities you cover; `refs` = entities you reference but do not own; `publishes`/`consumes` = events you surface; `entry_points`/`exit_points` = how users arrive and leave; `has_ui`/`has_api`/`has_persistence` = which surfaces apply. When present, treat it as a hard constraint — do not stray outside the boundary it defines.

## Workflow

> **Compose with the template tool first.** Before drafting, obtain the user-flows
> section structure from the content-template tool (the `content-template-gateway`
> capability, or whatever template provider is installed). It supplies the per-flow
> slots (goal/PRD tie-back, entry points, flowchart, narrative, branches, error/
> recovery, resilience & system-status, accessibility, screens/states, success), plus
> the Navigation & IA, cross-flow transition, screens-index, assumptions, and
> versioning/changelog sections. **Never hardcode a competing outline** — this skill
> fills the template's slots with derived content; it does not redefine them.

If ALL capability records are injected: map cross-capability journeys using `exit_points → entry_points` chains. Label each flow with the capability IDs it traverses. Per-capability flows stay within the capability's `entry_points`/`exit_points`.

### Step 1: Derive one flow per goal/persona — frame as a job, ground in prior art

Treat each PRD goal as a **job** the persona is getting done (the goal in their words,
with its functional/social context), and produce one flow per goal/persona pairing.
Different personas may approach the same goal differently — give each its own flow,
and state *why* they diverge (mental model / context), rather than collapsing them.
This is the no-orphan guarantee: every PRD goal/persona ends up with a flow, and every
flow points back to one. **Ground each flow in the established interaction pattern**
for its job (standard auth / password-reset / checkout / onboarding / OAuth) and the
product's prior art — don't reinvent a solved flow; deviate only with a stated reason.
Fill the coverage map with that mapping first; it is the spine the rest hangs on. Keep
the doc a **flow, not a journey** — no emotion/channel per step.

### Step 2: Map the navigation & IA frame

Before drawing individual paths, establish the structural frame they live in (fill
proportionally — a single-screen tool collapses most of this):

- **Entry-point taxonomy** — every door (homepage, deep link, email/invite,
  notification, campaign), and the **state each entry lands in** (a deep-linked user
  may skip steps).
- **Navigation / app-shell model + wayfinding** — the persistent chrome the flows run
  within, where each flow sits in the IA, and how the user always gets back to a known
  place (never trapped away from the shell). Reference the design system's shell if
  one exists.
- **Deep-linking / routing** — for a routable product: the routes traversed + the
  **prereq-missing guard/resume** (deep-link into a state that needs prior steps →
  interstitial → resume).
- **Cross-device divergence** — where a *path* (not just layout) differs by form
  factor (an extra mobile step, a native sub-flow).

### Step 3: Map the happy path first

For each flow, lay down the critical path most users follow — entry → ordered steps →
the success exit — in plain language, no errors yet. Name every screen/state each step
traverses with a stable name you reuse verbatim in the diagram, narrative, and index.
Layer complexity onto this skeleton; do not start from the edge cases.

### Step 4: Enumerate every decision branch

At each point where the user can go more than one way, name **all** outgoing branches
and resolve each to a step, another flow, or a clean exit. A decision with one side
unmapped is the gap that surfaces late in build. No dangling "Yes/No" with a missing
arm. Where flows hand off to each other, record the hand-off in the cross-flow
transitions section and confirm the target flow exists (no hand-off to an undefined or
removed flow).

### Step 5: Walk the edge-case checklist + the states — no dead ends

Walk this fixed checklist at each step so coverage is systematic, not inspirational —
and treat the states as nodes the path traverses (they become wireframe targets):

- **Empty / null** · **invalid + extreme inputs** (boundary 0/1/max/max+1) ·
  **timeout / network / integration errors** · **interruption / session loss** ·
  **permission / auth denial** · **back / cancel**.
- **Loading / in-progress states** — every async/slow step passes through one
  (skeleton / spinner / progress); draw it (an async step = trigger → in-progress →
  success | error), so it lands in the screens index.
- **Success / confirmation states** — the concrete "goal accomplished" state the user
  sees (confirmation screen / reference / receipt), not just an abstract "success".

For each applicable case give the user a state and a **recovery path back to a
productive step** — never strand them. Every error state says *what went wrong* AND
*how to fix it*.

### Step 6: Add interaction resilience & system-status

Beyond error-recovery, make the path resilient (fill where applicable; see
`references/resilience-and-states.md` for depth):

- **Undo / confirm-on-irreversible** — every destructive or irreversible action
  (delete / pay / send / final submit) carries a **confirm or an undo**; reversible
  actions prefer undo over a modal confirm.
- **Resume vs restart** — each multi-step flow states its interruption behavior (what
  persists, for how long) — not a silent discard on reload.
- **"What changed" feedback** — each state-changing step shows its *result*, not just
  "done" (saved as draft, $X authorized, submitted as #1234).
- **Optimistic vs confirmed** — for an async action, state the stance; optimism is for
  low-risk only (never payments/deletes) and must define the **revert + feedback** on
  failure.

### Step 7: Check flow-level accessibility

Ensure every persona, **including assistive-tech users, can complete each path** (see
`references/flow-accessibility.md`). This is flow-level a11y, NOT per-screen pixel WCAG
(that is wireframes/design-system):

- **Keyboard-completable** end to end, no trap.
- **Focus order on step/route change** (WCAG 2.2 SC 2.4.3) — focus moves in a
  meaning-preserving order; on a step/route change it moves to the new content, not
  dropped.
- **AT-completability of every path** — happy and unhappy; **errors are announced**
  (programmatically determinable), not color/position-only.
- **No mouse-only / gesture-only** required step (each has a keyboard equivalent).

### Step 8: Apply the objective flow-quality heuristics

Make it a *good* flow, not only a complete one — the **objectively checkable** subset
(subjective taste is out of scope; see `references/flow-quality.md`):

- **Error prevention over recovery** — guard an irreversible action *before* it
  happens (confirm / preview / validate-before-enable), not only recover after.
- **Recognition over recall** — a step surfaces what a prior step established; no
  "remember the code from screen 2 and type it on screen 4" without carry-forward.
- **No gratuitous step** — the path is no longer than the job needs (path-length is
  judged here, once — not in accessibility).
- **Consistency** — like jobs use like paths across the flows; follow platform/DS
  conventions or state the deviation.

### Step 9: Render both notations, kept in sync

Render each flow **twice**: a Mermaid flowchart (terminals for start/end, rectangles
for screens/states, diamonds for decisions, labelled edges) **and** a numbered
narrative plus an explicit branch/error-path list. For a **multi-actor** flow (user ⇄
system ⇄ admin, a third-party provider, an approval hand-off), use **swimlanes**
(Mermaid `subgraph` per actor) so who-does-what is explicit. The two notations must
describe the *same* graph — a node/branch in one but not the other is a defect.
Specify the **message intent** of load-bearing states (error = cause+fix, empty =
guide-to-action, success = the result), and use **one canonical name** per screen
across diagram/narrative/index.

### Step 10: Surface thin-PRD gaps as assumptions / open questions

Where the PRD did not specify something a flow needs, state the **assumption** (so a
reviewer can challenge it) and list any unresolved decision as an **open question** —
never silently invent a product decision and bury it inside a flow. Keep journey-only
content (emotion/channel) out — lift it to an upstream reference if genuinely needed.

### Step 11: When amending — scope the ripple, edit don't redraw, version the doc

When handed an **existing** user-flows doc + a scoped change, treat it like versioned
source code (see `references/amend-method.md`):

1. **Scope the ripple** — which flow(s)/branch(es)/path(s) the change touches, AND the
   ripple: cross-flow hand-offs into a changed/removed flow, screens-index entries a
   removed path referenced, branch targets that moved.
2. **Edit, don't redraw** — minimal in-place edit; untouched flows (diagrams,
   narratives, index rows) stay byte-for-byte unchanged. No gratuitous re-numbering.
3. **Version + changelog** — bump the **doc's own** version (MAJOR = removed/renamed
   flow or removed reachable path; MINOR = added flow/branch/path; PATCH = wording/
   notation), add a Keep-a-Changelog entry at flow/path grain.
4. **Deprecate safely** — deprecate a flow/path in a MINOR (mark + name the
   replacement) before removing in a MAJOR; when a screen leaves, prune the index and
   confirm no remaining path references it.

### Step 12: Self-check against the bar (below) before handoff

Run the quality bar. Fix every miss before handing the document to review or to
wireframing.

## Rules

**Hard rules (never violate):**

- **Compose, don't duplicate.** The section structure comes from the template tool;
  this skill never ships a competing outline.
- **Derive, don't invent — both directions.** Every flow traces to a PRD goal/persona;
  every PRD goal/persona has a flow; standard flows follow their established pattern or
  state the deviation. No orphans, no reinvented-solved-flow.
- **No dead ends.** Every decision branch resolves, and every error/edge state has a
  recovery path back to a productive step.
- **Both notations, in sync.** Each flow has a Mermaid flowchart AND a numbered
  narrative + branch/error list describing the same graph; swimlanes for multi-actor.
- **One canonical name per screen.** Identical across diagram, narrative, per-flow
  list, and the index — and across amendments. Drift breaks enumeration.
- **Screens enumerable.** The screens index is the complete union of every flow's
  screens/states (incl. loading + success), so wireframing can enumerate them all.
- **Irreversible actions are guarded.** Every destructive/irreversible action carries
  a confirm or an undo.
- **Flow, not journey.** The interaction graph only; emotion/channel/over-time is out.
- **Amend, don't regenerate.** On a change, edit the affected flow in place + version
  the doc; never redraw untouched flows.
- **Capability boundary (when capability_record provided).** Scope the document output to that record's boundary. Producing content outside the boundary (covering a `refs` entity as if it were owned; designing flows past an `exit_point`) is a scope violation — equivalent to inventing content that isn't in the spec.

**Preferences (override-able):**

- One flow per goal/persona pairing; split a shared goal when personas diverge (state
  why).
- Plain language in the narrative; expand abbreviations; label every diagram edge.
- Proportion the document to the PRD's goal/persona set and the product's complexity —
  a thin utility fills few sections (no app shell, no resilience block); neither pad
  nor truncate. Fill Navigation & IA / resilience / accessibility *where applicable*.

## Gotchas

- **Happy-path-only flows.** Brittle — most real users leave the ideal path. The
  edge-case checklist (Step 5) + resilience (Step 6) exist so coverage is systematic.
- **Silent state-change.** A step that mutates state and advances with no "what
  changed" feedback (Step 6) reads complete but leaves the user guessing.
- **Missing the loading/success state.** A flow that leaps trigger→success hides the
  in-progress + confirmation screens wireframing must design (Step 5).
- **Diagram and narrative drift.** Editing one and forgetting the other ships a
  contradiction. One artifact, two renderings; reconcile on every change.
- **Inventing product decisions inside a flow.** Lift the assumption out (Step 10).
- **Screen names that drift across sections** (or across an amendment). One stable
  name everywhere — the #1 amend regression.
- **AT-stranded error.** An error state that is visually obvious but never announced
  leaves the screen-reader user stuck on a path the sighted user recovers from (Step 7).
- **Regenerating on a change.** Re-drawing untouched flows on an amendment churns the
  doc and corrupts the cross-flow graph (Step 11).

## Anti-patterns

- **"The diagram is enough."** A flowchart alone isn't walkable in text; the numbered
  narrative + branch list is not optional.
- **"I'll bake the section list into the doc myself."** Duplicates + drifts from the
  template. Always compose the structure from the template tool.
- **"Edge cases are an edge concern — happy path ships."** Missing branches, unhandled
  states, and unguarded irreversible actions are the defects that strand users.
- **"The PRD didn't say, so I'll just decide."** Silent product decisions belong in
  assumptions/open-questions.
- **"Layout while I'm here."** Screen layout is a downstream document; this is the
  navigation graph only. Same for per-screen pixel a11y (wireframes/DS own it).
- **"Map the feelings per step."** That is a user *journey*, not a user *flow*.
- **"Re-draw the whole doc for one new flow."** Amend the delta, version the doc.

## Production-grade quality bar

A user-flows document meets the bar when ALL hold (this is the same bar the review-side
gate asserts; each scales with the product — a thin doc satisfying every *applicable*
item passes):

1. **Goal/persona coverage — no orphans.** Every PRD goal/persona (framed as a job)
   maps to a flow; every flow traces back; standard flows grounded in their pattern.
2. **Navigation & IA frame** (where applicable). Entry-point taxonomy complete; the
   nav/app-shell model + wayfinding present for a multi-surface product; deep-linking +
   device divergence addressed where they apply; cross-flow hand-offs resolve.
3. **Defined entry + exit.** Every flow names all entry points (+ landing state) and a
   concrete success/confirmation state; alternate exits are clean.
4. **Every decision branch resolved.** Each decision lists all branches; each resolves.
5. **Every error/edge state has a recovery — no dead ends.** The checklist states
   (incl. loading + success) are present where applicable and route back; errors say
   what + how.
6. **Interaction resilience** (where applicable). Irreversible actions guarded; resume/
   restart stated for multi-step flows; "what changed" feedback on state-changing steps;
   optimistic actions carry a revert.
7. **Flow-level accessibility.** Every path keyboard- and AT-completable; focus-order
   on step/route change; errors announced; no mouse-only step.
8. **Flow quality (objective).** No gratuitous step; irreversible actions prevented not
   only recovered; no cross-step recall burden; like jobs consistent.
9. **Steps unambiguous + walkable.** A reader follows the narrative without guessing;
   each step names its screen/state + the user action.
10. **Both notations in sync.** Flowchart AND narrative + branch/error list, same graph;
    swimlanes for multi-actor.
11. **Screens enumerable for wireframing.** The index is the complete union (incl.
    loading + success); one canonical name per screen; nothing orphaned.
12. **Assumptions/open questions surfaced.** Thin-PRD assumptions stated; no silent
    product decision; no journey content.
13. **Amend-correct** (on iteration). The change is scoped + edited in place; untouched
    flows unchanged; the doc is versioned + changelogged; breaking removals deprecated.

## Output

A user-flows document in markdown: a per-doc version header + a coverage map (PRD
goal/persona → flow), a Navigation & IA section, one section per flow (each a synced
Mermaid flowchart + numbered narrative + branch/error list, with entry points,
resilience & system-status, flow-level accessibility, screens/states incl. loading +
success, and success criteria), a cross-flow transition list, a screens index, an
assumptions/open-questions section, and a versioning/changelog section — composed onto
the template tool's structure. Consumed by the review-side gate (which judges it
against the bar above) and by downstream wireframing (which enumerates every screen the
flows name). The method + bar are medium-independent: a future design-tool backend
changes only the rendering, not the derivation or the bar.

## Related

- **Template provider** (`content-template-gateway` capability) — supplies the
  user-flows section structure this skill composes onto; never duplicated here.
- **Research capability** (`deep-research`, else web search) — grounds domain
  conventions + prior-art flow patterns and the derivation evidence.
- **Upstream input — the PRD** (goals + personas the flows realize) and, where present,
  a **design system** (the nav/app-shell + components the flows reference). Never a
  blank page. On iteration, the **existing user-flows doc** is handed in.
- **`reviewing-user-flows`** — the review-side gate that asserts the same bar;
  produce-side and review-side are single-sourced.
- **`authoring-wireframes`** — the downstream consumer; each screen a flow names becomes
  a wireframe target, so a complete screens index is the handoff contract. Per-screen
  pixel accessibility is theirs, not this skill's.

## Progressive disclosure

- `references/resilience-and-states.md` — undo/confirm, resume/restart, system-status,
  optimistic-vs-confirmed, and the loading/success/state-matrix depth (Steps 5–6).
- `references/flow-accessibility.md` — WCAG 2.2 SC 2.1.1 / 2.4.3 applied to flows;
  focus-order on route change; AT-completability; the flow-vs-pixel boundary (Step 7).
- `references/flow-quality.md` — Nielsen's 10 heuristics mapped to flows; the objective
  subset; the no-false-revise boundary (Step 8).
- `references/amend-method.md` — scope-the-ripple, edit-not-redraw, doc versioning +
  changelog, deprecation (Step 11).
- `references/sources.md` — research provenance for the derivation method + the bar.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap).
- Body ~500 lines / 5,000 tokens (soft target — quality takes precedence; flag if consistently over 700 lines / 7,000 tokens) — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k.
