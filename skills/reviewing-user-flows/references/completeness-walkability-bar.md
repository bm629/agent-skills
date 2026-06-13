# The production-grade bar — expanded (13 conditions)

> Load when a borderline condition needs a sharper pass/gap call. This is the
> single-sourced bar: the same conditions a user-flows author produces to, so the
> produce-bar and the review-bar do not drift. Judge each as pass/gap against the
> finished document; revise only on a real, named gap. New conditions (9–13) each carry
> a proportionality collapse so a thin flow is never false-revised; four conditions are
> non-collapsing baseline.

A user-flows document meets the bar when ALL **applicable** conditions hold.

---

## Kept core (completeness + walkability)

### 1. Goal/persona coverage — no orphans

**Pass:** every PRD goal (framed as the job the persona is getting done) maps to exactly
one flow; every flow traces back; standard flows (auth/checkout/reset/onboarding) follow
their established pattern or state the deviation; a coverage map is present.
**Gap:** a goal with no flow; a flow serving no goal; a solved-problem flow reinvented
with no rationale; no coverage map.
**Finding:** "Coverage (cond. 1): PRD goal G4 ('re-order a past purchase') has no flow.
Fix: add a re-order flow tracing to G4, or note it out-of-scope with a reason."

### 2. Defined entry + exit  *(non-collapsing baseline: a concrete success state)*

**Pass:** every flow names all entry points (homepage, deep link, email, notification —
each may start a different state) and a **concrete success/confirmation state** (a
confirmation screen / reference / receipt), not just an abstract "success"; alternate
exits are clean.
**Gap:** a flow with no named entry; no concrete end state (only an abstract "done"); an
alternate exit that strands the user.
**Finding:** "Entry/exit (cond. 2): Flow 1 (Checkout) ends at 'order placed' with no
confirmation state. Fix: add the order-confirmation screen (with the reference number)
as the success state."

### 3. Every decision branch resolved

**Pass:** each decision lists **all** outgoing branches; each resolves to a step, a flow,
or an exit.
**Gap:** a dangling side; a branch pointing nowhere.
**Finding:** "Branch (cond. 3): Flow 2's 'email already registered?' shows 'No' but not
'Yes'. Fix: add the 'Yes' branch (→ login flow or 'use a different email')."

### 4. Every error/edge state has a recovery — no dead ends

**Pass:** where applicable — empty/null, invalid+extreme input, timeout/network/
integration, interruption/session-loss, permission/auth, back/cancel — each routes back;
**plus** the loading/in-progress state on every async step and the success/confirmation
state. No state strands the user; load-bearing states carry **message intent** (error =
cause+fix, empty = guide-to-action, success = the result).
**Gap:** an applicable state missing; an error path dead-ends; an async step leaps to
success with no loading state; an error with no recovery; a load-bearing state's message
intent unspecified where it matters.
**Proportionality:** *where applicable* — a flow with no network call needs no timeout
path.
**Finding:** "States (cond. 4): Flow 3 jumps from 'Submit payment' straight to success
with no in-progress state. Fix: add the processing/loading state the path passes through
and put it in the screens index."

### 5. Steps unambiguous + walkable

**Pass:** a reader follows the narrative without guessing; each step names its
screen/state + the user action; labels present.
**Gap:** an ambiguous step; an unlabelled node/connector; unexplained jargon.
**Finding:** "Walkability (cond. 5): Flow 2 step 4 says 'proceed' with no screen/action.
Fix: 'User taps Continue → Address screen.'"

### 6. Both notations in sync

**Pass:** every flow has a Mermaid flowchart AND a numbered narrative + branch/error
list, same graph; **multi-actor flows use swimlanes** (subgraph per actor).
**Gap:** one notation missing; a node/branch drifts between them; a multi-actor flow in
one undifferentiated lane where the hand-off matters.
**Finding:** "Notation (cond. 6): Flow 2's diagram has a 'Verify email' node the
narrative omits. Fix: add the numbered step (or remove the node)."

### 7. Screens enumerable for wireframing  *(non-collapsing baseline: naming + index)*

**Pass:** the screens index is the complete union of every flow's screens/states (incl.
loading + success), each with **one canonical name** used identically across diagram/
narrative/index; nothing orphaned.
**Gap:** a referenced screen missing from the index; a name that drifts ("Cart" vs
"Basket"); an orphaned index entry; no index.
**Finding:** "Enumeration (cond. 7): Flow 3 step 6 references 'Order confirmation' absent
from the index. Fix: add it so wireframing covers it."

### 8. Assumptions/open questions surfaced; flow not journey  *(non-collapsing baseline)*

**Pass:** thin-PRD assumptions stated (challengeable); open questions listed; no silent
product decision; the doc stays the interaction graph (no emotion/channel per step).
**Gap:** a buried/invented decision; journey content presented as the flow.
**Finding:** "Assumptions (cond. 8): the guest-checkout path assumes guests can save an
address (the PRD doesn't decide this). Fix: state it as an assumption or open question."

---

## New (structure, resilience, accessibility, quality, amend)

### 9. Navigation & IA frame

**Pass:** the nav/app-shell model + wayfinding present for a multi-surface product;
deep-linking (+ prereq guard/resume) and cross-device path divergence addressed where
they apply; every cross-flow hand-off resolves to a defined flow; no orphan flow
(unreachable + exits nowhere).
**Gap:** a hand-off to a removed/undefined flow; a multi-surface product whose flows
ignore the nav model or a real device path-divergence; a deep-link into a prereq-missing
state with no guard.
**Collapse:** a single-screen / single-flow tool has no app shell, one entry, no
cross-flow graph, one form factor — not a gap.
**Finding:** "Nav & IA (cond. 9): Flow 4 hands off to 'Guest upgrade', a flow not defined
in the doc. Fix: define the target flow or correct the hand-off."

### 10. Interaction resilience

**Pass:** every irreversible/destructive action carries a **confirm or undo**; each
multi-step flow states resume-vs-restart; state-changing steps show **what changed**;
optimistic actions define a revert+feedback path and aren't used for payments/deletes.
**Gap:** an unguarded irreversible action; a silent state-change; a long flow with no
stated interruption behavior; an unsafe or revert-less optimistic action.
**Collapse:** a read-only/browse flow has nothing to guard/persist/confirm — not a gap.
**Finding:** "Resilience (cond. 10): Flow 3 'Delete account' goes button→success with no
confirm/undo. Fix: add a confirm step (or recoverable soft-delete + undo) before the
irreversible deletion."

### 11. Flow-level accessibility  *(non-collapsing baseline: keyboard-operable)*

**Pass:** every path keyboard-completable (no trap) and AT-completable (**errors
announced**, not color/position-only); focus-order managed on step/route change (WCAG 2.2
SC 2.4.3); no required step is mouse-only/gesture-only.
**Gap:** a mouse-only required step; an error perceivable only visually (AT user
stranded); unmanaged focus on step change.
**Boundary:** per-screen pixel WCAG (contrast/target-size/focus-appearance) is
wireframes/DS, NOT this condition. Path-length is cond. 12, not here.
**Collapse:** a single-screen flow has lighter cross-step focus concern but the path must
still be keyboard/AT-completable (baseline).
**Finding:** "Flow a11y (cond. 11): Flow 2's 'reorder' step is drag-only — a keyboard/AT
user can't complete the path. Fix: add a keyboard-operable reorder + manage focus."

### 12. Flow quality (objective only)

**Pass:** no gratuitous step (path no longer than the job needs — **path-length judged
here, once**); irreversible actions **prevented** (guard before the act), not only
recovered; no step forces **recall** of what a prior step established without
carry-forward; like jobs use **consistent** paths.
**Gap:** a materially over-long path with no reason; an unprevented irreversible action;
a cross-step recall burden; unjustified inconsistency between like flows.
**Not a gap:** subjective preference ("a nicer flow exists") — NEVER triggers a revise.
**Collapse:** a trivial flow trivially holds.
**Finding:** "Quality (cond. 12): Flow 1 (Search) routes results → detail → back → detail
across 3 reloads where a single results-with-preview pane serves the job. Fix: collapse
the gratuitous round-trip, or state why the longer path is needed."

### 13. Delta-scoped review (only when judging an amendment)

**Pass:** the review is scoped to the **diff + its ripple**: untouched flows unchanged
(no unscoped regenerate); no cross-flow hand-off points at a removed/renamed flow; no
screens-index entry orphaned/missing; no previously-reachable path newly stranded;
diagram⇄narrative synced on the edit; the doc's version bump matches the change class
(MAJOR removed/renamed flow or removed reachable path · MINOR added · PATCH wording) and
the changelog matches the diff; breaking removals carry deprecation.
**Gap:** any of the above — including an unscoped regenerate (churn outside the delta).
**Collapse:** a greenfield first build does not exercise this condition.
**Finding:** "Delta (cond. 13): the amendment renamed 'Cart' → 'Bag' in Flow 2's diagram
but not its narrative or the screens index, and bumped PATCH for a rename. Fix: propagate
the name to all four places and bump MAJOR (a rename is breaking)."

---

## Calibration notes

- **No false-revise.** A small, complete doc for a simple product that satisfies every
  *applicable* condition passes. The new conditions (9–13) collapse on a thin archetype;
  judge completeness/quality-of-paths, not flow count.
- **No false-approve.** A dead-end path, an orphan goal, an unguarded irreversible action,
  an AT-stranded error, or a screen missing from the index is always a `revise`.
- **Non-collapsing baselines** (apply at every size): cond-2 concrete success state,
  cond-7 canonical naming + enumeration, cond-8 flow-not-journey, cond-11
  keyboard-operability.
- **Stay in your lane.** Layout + per-screen pixel WCAG (wireframe review) and
  goal-worthiness (PRD review) are out of scope. Path-length is cond. 12 only; pixel a11y
  is never cond. 11.
- **Subjective taste is never a gap** (cond. 12 is objective only).
