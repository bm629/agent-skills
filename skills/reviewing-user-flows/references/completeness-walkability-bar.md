# The completeness + walkability bar — expanded

> Load when a borderline condition needs a sharper pass/gap call. This is the
> single-sourced bar: the same eight conditions a user-flows author produces to,
> so the produce-bar and the review-bar do not drift. Judge each as a pass/fail
> against the finished document; revise only on a real, named gap.

A user-flows document is **complete + walkable** when ALL eight conditions hold.

---

## 1. Goal/persona coverage — no orphans

**Pass:** every PRD goal, and the persona pursuing it, maps to exactly one flow; every flow traces back to a PRD goal/persona. A coverage map (goal/persona → flow) is present and lets you check the mapping at a glance.

**Gap signals:**

- A PRD goal with no flow realizing it.
- A flow that serves no stated goal (invented scope).
- No coverage map, so the mapping cannot be verified.

**Why it matters:** flows are *derived* from goals, not imagined; an orphan goal means a user need with no path, and an orphan flow means scope the PRD never asked for.

**Finding example:** "Goal coverage (cond. 1): PRD goal G4 ('a returning user re-orders a past purchase') has no flow. Fix: add a re-order flow tracing to G4, or, if intentionally deferred, note it as out-of-scope with a reason."

---

## 2. Defined entry + exit

**Pass:** every flow names all its entry points (homepage, deep link, email link, push notification — note that different entries may start the flow in a different state) and at least one success/exit state. Every alternate exit (cancel, abandon, hand-off to another flow) is clean.

**Gap signals:**

- A flow with no named entry — it starts in mid-air.
- A flow with no defined end state — it trails off.
- An alternate exit (cancel/abandon) that leaves the user nowhere.

**Finding example:** "Entry/exit (cond. 2): Flow 1 (Sign-up) lists only the homepage entry, but the PRD mentions an email-invite path. Fix: add the email-invite entry point and the state it lands the user in."

---

## 3. Every decision branch resolved

**Pass:** each decision point lists **all** its outgoing branches, and each branch resolves to a step, another flow, or an exit.

**Gap signals:**

- A "Yes/No" (or N-way) decision with a side missing.
- A branch that points nowhere / to an undefined target.

**Why it matters:** unmapped branches are the gaps that surface late in development, after wireframing has already missed the screen the branch needed.

**Finding example:** "Branch resolution (cond. 3): Flow 2's 'Is the email already registered?' decision shows the 'No' path but not the 'Yes' path. Fix: add the 'Yes' branch and resolve it (e.g. route to the login flow or to a 'use a different email' state)."

---

## 4. Every error/edge state has a recovery — no dead ends

**Pass:** where applicable, the doc covers empty/null states, invalid input, timeout/network errors, integration errors, interruption/session-loss, and permission/auth denials, and **each routes the user back to a productive step**. No state strands the user. Error states carry **two** pieces of information: what went wrong **and** how to fix it.

**Walk the fixed edge-case checklist** at each step rather than relying on inspiration:

- empty / null states (no data yet)
- invalid + extreme inputs (boundary values: 0, 1, max, max+1)
- slow connections / timeouts / integration errors
- interruptions + session persistence (close tab → resume or restart?)
- permission / auth denials
- back / cancel

**Gap signals:**

- An edge state clearly applies but is absent.
- An error path dead-ends (a terminal node that is not a clean success/exit).
- An error message states only the failure, with no recovery action.

**Proportionality:** *where applicable* — a flow with no network call need not invent a timeout path. Do not manufacture an inapplicable edge state.

**Finding example:** "Error recovery (cond. 4): Flow 3 (Checkout) 'payment failed' ends at a terminal node. Fix: route it back to the payment-entry step (or a 'retry / change method' state) and have the error state name both the failure and the next action."

---

## 5. Steps are unambiguous + walkable

**Pass:** a reader can follow the numbered narrative end-to-end without guessing; each step names its screen/state and the user action; labels/annotations are present; no unexplained abbreviations.

**Gap signals:**

- A step ambiguous enough that two readers would walk it two different ways.
- An unlabelled connector or node.
- Unexplained jargon/abbreviations.

**Finding example:** "Walkability (cond. 5): Flow 2 step 4 says 'proceed' without naming the screen or action. Fix: name the destination screen and the user action, e.g. 'User taps Continue → Address screen.'"

---

## 6. Both notations in sync

**Pass:** every flow has **both** a Mermaid flowchart **and** a numbered narrative + explicit branch/error list, and they describe the same graph — same screens, same branches, same exits.

**Gap signals:**

- One notation missing (diagram-only or narrative-only).
- A node/branch present in one notation but absent from the other (drift).

**How to check:** read both notations and diff them — a node in the diagram with no matching numbered step (or vice-versa) is a defect.

**Finding example:** "Notation sync (cond. 6): Flow 2's diagram includes a 'Verify email' node the narrative omits. Fix: add the corresponding numbered step (or remove the node) so the two describe the same graph."

---

## 7. Screens enumerable for wireframing

**Pass:** the union of every flow's screens/states (the screens index) is complete, so a downstream wireframing pass could enumerate every screen the flows touch with nothing missing.

**Gap signals:**

- A step references a screen/state that never appears in the screens index.
- No screens index exists, so the screen set cannot be enumerated.

**Why it matters:** this is the downstream contract — wireframing turns every screen the flows name into a wireframe target; a screen missing from the index is a screen that never gets designed.

**Finding example:** "Screen enumeration (cond. 7): Flow 3 step 6 references a 'Order confirmation' screen absent from the screens index. Fix: add it to the index so wireframing covers it."

---

## 8. Assumptions/open questions surfaced

**Pass:** where the PRD was thin, the assumptions made are stated (and thus challengeable), and unresolved blockers are listed — not silently decided.

**Gap signals:**

- The doc invents a product decision the PRD never made and presents it as settled.
- An obvious open question is buried or absent.

**Finding example:** "Assumptions (cond. 8): the guest-checkout path assumes guests can save an address, a decision the PRD does not make. Fix: state it as an assumption to validate, or list it as an open question."

---

## Calibration notes

- **No false-revise.** A small, complete doc for a simple product that satisfies every *applicable* condition passes. Judge completeness-of-paths, not flow count.
- **No false-approve.** A dead-end path, an orphan goal, or a screen missing from the index is always a `revise`, however polished the happy paths look.
- **Stay on the navigation graph.** Layout (wireframe review) and goal-worthiness (PRD review) are out of scope for this gate.
