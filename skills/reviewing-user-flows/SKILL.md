---
name: reviewing-user-flows
description: >
  Use when reviewing/judging a finished user-flows document to decide whether a
  downstream wireframing pass can enumerate every screen from it — an acceptance
  gate, not authoring. A user-flows doc is the navigation/interaction graph: the
  paths a user takes to accomplish each goal, with entry points, decision
  branches, error/recovery paths, and screens traversed. Judges it against a
  completeness + walkability bar: every PRD goal/persona maps to a flow (no
  orphans), every flow has a defined entry + exit, every branch resolves, every
  error state has a recovery (no dead ends), steps are walkable, the Mermaid
  diagram and numbered narrative stay in sync, and the screens index is
  enumerable. Emits exactly `VERDICT: approve|revise` with actionable findings
  (failed condition + the fix). Approves a doc meeting the bar (no false-revise),
  revises only on a named gap. Not for authoring a user-flows doc, not for
  screen layout/wireframes (use a wireframes-review skill), not for the upstream
  PRD (use a PRD-review skill).
extensions:
  claude:
    when_to_use: "judging a finished user-flows document against the completeness + walkability bar and emitting an approve/revise verdict"
    argument-hint: "<the finished user-flows document to review>"
version: "1.1.0"
forge:
  status: reviewed
  forged: 2026-06-04
  reviewed: 2026-06-04
---

# `reviewing-user-flows` — SKILL.md

> **Variant:** standard · **When to use:** judging a finished user-flows document as an acceptance gate — checking it is complete + walkable, then emitting `VERDICT: approve|revise` with actionable findings.

## Overview

This skill is the *review* half of a producing/judging user-flows pair. Loaded by a reviewer who has a **finished user-flows document** in hand, it judges that document against one question: **can a downstream wireframing pass enumerate every screen from it?** A user-flows doc maps the navigation/interaction graph — the paths a user takes to accomplish each goal: entry points, the happy path, decision branches, error/recovery paths, the screens/states traversed, and the success criteria. This skill applies a fixed **completeness + walkability checklist** (the same bar a user-flows author produces to, so the produce-bar and review-bar do not drift), then emits a single machine-parseable verdict plus findings the author can act on in one revision pass. It is an acceptance gate — it does **not** author, fix, or redraw the flows; it judges and returns findings, and the producer revises.

## When to activate

- A finished user-flows document needs an accept/revise decision before downstream wireframing begins.
- You are the independent reviewer / gate for a user-flows doc a producer just authored.
- Re-judging a revised user-flows doc after a prior `revise` verdict.

**Do NOT activate when:**

- Authoring or repairing a user-flows doc → use a user-flows-authoring skill. This skill never writes the flows.
- Reviewing **screen layout / structure** — region layout, content hierarchy, components per screen → use a wireframes-review skill. That gate judges what each screen *looks like*; **this** gate judges how the screens *connect* (the navigation graph), not their layout.
- Reviewing the **upstream PRD** — product goals, personas, success metrics → use a PRD-review skill. The PRD decides *what* and *why*; the user-flows doc realizes those goals as paths. This skill checks that every PRD goal has a flow, but it does not re-judge the goals themselves.
- Checking template/section conformance → that is a template concern. This skill judges *quality against the bar*, not whether every heading is present.
- Reviewing any other document type.

## Workflow

### Step 1: Read the whole document with fresh, independent eyes

Read the user-flows doc end to end as if encountering it for the first time, without the author's framing. Hold the upstream PRD (goals + personas) alongside it — coverage is judged against those goals. Your stance is a gatekeeper for the *next* step (wireframing): a finding carries weight only when it shows the screens cannot be enumerated, or a path cannot be walked, as written. Note where a flow, branch, or exit is load-bearing — those are the spots Step 2 scrutinizes.

### Step 2: Run the completeness + walkability checklist — judge each condition

For each condition below, decide **pass** or **gap**. A condition fails only on a *real, named* deficiency — "I'd have drawn it differently" is not a gap. For each gap, capture the exact location (which flow, which step/branch/node) and what is missing (Step 4 turns it into an actionable finding).

1. **Goal/persona coverage — no orphans.** Every PRD goal, and the persona pursuing it, maps to a flow; every flow traces back to a PRD goal/persona. A coverage map (goal/persona → flow) should be present and complete. *Gap* when a PRD goal has no flow, a flow serves no stated goal, or no coverage map lets you check the mapping.
2. **Defined entry + exit.** Every flow names all its entry points (homepage, deep link, email, notification — different entries may start in a different state) and at least one success/exit state; every alternate exit (cancel/abandon/hand-off) is clean. *Gap* when a flow begins or ends in mid-air — no named entry, or no defined end state.
3. **Every decision branch resolved.** Each decision point lists **all** its outgoing branches, and each branch resolves to a step, another flow, or an exit. *Gap* when a decision has a dangling side — a "Yes/No" with one branch missing, or a branch that points nowhere. Unmapped branches are the gaps that surface late in development.
4. **Every error/edge state has a recovery — no dead ends.** Where applicable, the doc covers empty/null states, invalid input, timeout/network errors, integration errors, interruption/session-loss, and permission/auth denials, and **each routes the user back to a productive step**. No state strands the user. Error states say **what went wrong AND how to fix it** (two pieces of information). *Gap* when an edge state is missing where it clearly applies, an error path dead-ends, or an error message only states the failure with no recovery.
5. **Steps are unambiguous + walkable.** A reader can follow the numbered narrative end-to-end without guessing; each step names its screen/state and the user action; labels/annotations are present; no unexplained abbreviations. *Gap* when a step is ambiguous enough that two readers would walk it two different ways, or a connector/node is unlabelled.
6. **Both notations in sync.** Every flow has **both** a Mermaid flowchart **and** a numbered narrative + explicit branch/error list, and they describe the same graph — same screens, same branches, same exits. *Gap* when one notation is missing, or a node/branch present in one is absent from the other (a drift between the diagram and the narrative is a defect).
7. **Screens enumerable for wireframing.** The union of every flow's screens/states (the screens index) is complete, so a downstream wireframing pass could enumerate every screen the flows touch with nothing missing. *Gap* when a step references a screen/state that never appears in the screens index, or the index is absent so the screen set cannot be enumerated.
8. **Assumptions/open questions surfaced.** Where the PRD was thin, the assumptions made are stated (challengeable) and unresolved blockers are listed, not silently decided. *Gap* when the doc invents a product decision the PRD never made and presents it as settled, or buries an obvious open question.

**Proportionality.** "Complete enough to wireframe from" scales with the product. A simple product legitimately has few flows and few edge states — a small, complete doc that satisfies every *applicable* condition **passes**. Condition 4 is *where applicable*: a flow with no network call need not invent a timeout path. Judge completeness-of-paths, not flow count. Do not manufacture a gap from brevity.

### Step 3: Decide the verdict

- **approve** — every applicable condition passes. A wireframing pass can enumerate every screen and walk every path from this doc as written. Approve it even if you can imagine stylistic improvements; the bar is completeness + walkability, not perfection.
- **revise** — one or more conditions have a real, named gap (an orphan goal, a flow with no entry, a dangling branch, a dead-end error path, the diagram and narrative out of sync, a screen missing from the index, etc.).

Do not revise to signal effort or to request nice-to-haves. A condition is either met or it isn't.

### Step 4: Emit the verdict + actionable findings

Emit the verdict as a single line — the literal text `VERDICT: approve` or `VERDICT: revise`, on its own line, with **no** surrounding code fences, quotes, or extra words (the fences here are illustration only):

```
VERDICT: approve
```

Then, on the following lines, list findings. On `revise`, every finding is **actionable** — the failed condition, the exact location, and **how to fix it** — so the author can resolve it in one pass. On `approve`, findings are optional non-blocking notes; do not let them imply a revision is required.

A good finding names the gap and the fix:

> **revise** — Error recovery (cond. 4): in Flow 3 (Checkout), the "payment failed" branch ends at a terminal node with no outgoing edge. Fix: route it back to the payment-entry step (or to a "retry / change method" state) so the user is not stranded, and have the error state state both the failure and the next action.

> **revise** — Notation sync (cond. 6): Flow 2's Mermaid diagram includes a "Verify email" node that the numbered narrative omits. Fix: add the corresponding numbered step to the narrative (or remove the node from the diagram) so the two describe the same graph.

A bad finding is vague and unactionable:

> The error handling could be stronger. *(Which flow? Which state? What fixes it?)*

## Rules

**Hard rules (never violate):**

- **Emit exactly one verdict line, `VERDICT: approve` or `VERDICT: revise`** — that literal token, on its own line, nothing else on it. Downstream tooling parses it.
- **Judge, never author.** Return findings; do not redraw, fix, or fill in the flows. The producer revises.
- **Single-sourced bar.** Judge against the eight completeness + walkability conditions in Step 2 — the same bar the author produces to. Do not invent extra conditions or a stricter private standard.
- **No false-revise.** A doc that meets every applicable condition is approved, even a small one for a simple product. Revise only on a real, named gap.
- **No false-approve.** Never approve over a genuine gap to be agreeable. A dead-end path, an orphan goal, or a screen missing from the index is a `revise`.
- **Dead ends are blocking.** A path that strands the user — an unresolved branch or an error state with no recovery — is always a `revise` until the path routes back to a productive step.
- **Judge against the upstreams the document was given.** Assess the document against its `depends_on` set (the upstream documents the project actually produced). A **not-produced** upstream is **never** a revise trigger — never invent an expectation of a document the project didn't make. But a document that **ignored a produced upstream** it should have drawn on (e.g. a `depends_on` feature-spec whose behaviors the flows don't reflect) **is** a fair finding.
- **Every revise finding is actionable** — failed condition + location (which flow/step/branch) + concrete fix. No vague notes.

**Preferences (override-able):**

- Order findings by severity — blocking gaps (dead ends, orphan goals, missing screens) first, then minor ones.
- Reference the condition number/name in each finding so the author maps it back to the bar.
- When citing a location, name the flow and the specific node/step/branch, not just "the diagram."
- Keep approve-notes few and clearly non-blocking.

## Gotchas

- **Approving for completeness instead of walkability.** Every flow can be present and the doc still un-walkable — a branch with one side missing, an error state with no recovery, a diagram that drifts from the narrative. Judge whether *every path can be walked and every screen enumerated*, not whether the *template is filled*.
- **Missing the dead-end.** A dead end hides at the end of an *unhappy* path — the happy path always looks complete. Trace every branch and every error state to its terminus; a branch or error node with no outgoing edge (and that is not a clean success/exit) strands the user and is a blocking gap.
- **One notation only.** A reviewer who reads the Mermaid diagram and skips the narrative (or vice-versa) will miss a sync defect by construction. Condition 6 requires checking that the two describe the *same* graph — read both and diff them.
- **False-revise on a simple product.** A simple product's flows are correctly few, and an inapplicable edge state (a timeout path for a flow with no network call) is not a gap. Condition 4 is *where applicable*; manufacturing a gap from brevity is the most common reviewer error here — calibrate to the product's size.
- **Drifting the bar.** Reviewing against your personal preferences instead of the eight conditions silently raises the bar above what the author produced to, causing avoidable revise loops. Stick to the shared checklist.
- **Confusing this with wireframe or PRD review.** This gate judges the navigation graph — *how screens connect*. It does **not** judge what a screen looks like (that is wireframe review) or re-decide the product goals (that is PRD review). Don't apply a layout standard or a goals standard to a flows doc.
- **Verdict token drift.** "Approved", "LGTM", "needs work", or a verdict buried mid-paragraph will not parse. Emit the literal `VERDICT: approve|revise` on its own line.

## Anti-patterns

- **Rubber-stamp approve.** Skimming the happy paths and approving without tracing the unhappy ones — the gate exists to catch stranded users and uncovered branches; a dead-end error path waved through becomes a missing screen in wireframing and a hole in the build.
- **Nit-pick revise.** Blocking on diagram styling, node shape, or wording dressed up as gaps. Revise is for real completeness/walkability blockers only.
- **Silent redraw.** "It was easier to just fix the flow" — authoring inside a review collapses the produce/judge separation and removes the author's chance to learn the gap.
- **Inventing conditions.** "It should also map emotions / channels per step" (that is a user *journey*, not a user *flow*) when that isn't in the bar — adding private requirements drifts the review-bar off the produce-bar.
- **Judging layout or goals.** Critiquing where a button sits (wireframe concern) or whether a goal is worth building (PRD concern) inside a flows review. Stay on the navigation graph.
- **Hedged verdict.** "Mostly approve but…" or two verdict lines. Exactly one decision, exactly one token.

## Output

A single review result for one user-flows document:

- **One verdict line** — `VERDICT: approve` or `VERDICT: revise`, verbatim, on its own line.
- **Findings** — on `revise`, one actionable finding per blocking gap (failed condition + location + concrete fix); on `approve`, optional non-blocking notes.

The abstract consumer is whatever orchestrates the produce→review loop: `approve` accepts the user-flows doc for the next phase (wireframing); `revise` returns the findings to the producer for a bounded revision pass.

## Related

- A **user-flows-authoring** skill — the produce half of the pair; it writes the flows to the same completeness + walkability bar this skill judges against. Pairing them single-sources the bar so produce and review do not drift.
- A **wireframes-review** skill — the sibling gate for the *next* document down: it judges per-screen layout/structure. Distinct gate, distinct bar; this skill judges the navigation graph that feeds it the screen list.
- A **PRD-review** skill — the gate for the *upstream* document: it judges product plannability (goals, personas, metrics). This skill checks coverage against those goals but does not re-judge them.
- A **user-flows template / content-template** tool — owns the section *structure* (and the dual-notation rendering); this skill judges *quality against the bar*, not structural conformance.

## Progressive disclosure

- `references/completeness-walkability-bar.md` — the eight checklist conditions expanded with per-condition pass/gap signals and worked finding examples. Load when a borderline condition needs a sharper pass/gap call.
- `references/sources.md` — research provenance for the review method, the flow-vs-journey boundary, and the dead-end / edge-case guidance.

## Body budget

- `description` ≤ 1,024 chars (agentskills.io cap). Claude truncates the combined `description` + `when_to_use` at 1,536 chars in the listing.
- Body ≤ ~500 lines / 5,000 tokens — kept in context every turn.
- Per reference file: warn >10k tokens, error >25k. Total references: warn >25k tokens, error >50k.
