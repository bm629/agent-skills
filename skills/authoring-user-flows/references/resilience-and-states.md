# Interaction resilience & states — depth

> Loaded for Workflow Steps 5–6. The states a path traverses + the resilience
> qualities beyond error-recovery. Fill where applicable — a read-only / single-screen
> flow collapses most of this; a transactional / multi-step flow engages it all.

## States a path traverses (the state matrix)

Every async/data-touching step a flow walks implies a small set of states. Draw the
ones the path actually reaches (only those — a screen a path only ever hits populated
needs only that state):

- **Loading / in-progress.** Any step that waits on the system passes through one.
  Skeleton screens are the norm for full-content loads (best ~2–10s, must match the
  final layout, subtle motion to reduce perceived time); a spinner/progress for short
  or indeterminate waits; for very fast actions, consider no visible wait (or
  optimistic — below). Model an async step as **three nodes**: trigger → in-progress →
  (success | error). Drawing only trigger→success hides two screens wireframing must
  build.
- **Empty / null.** No data yet — reassure + guide to the action that fills it.
- **Error.** Human + recoverable — see the edge checklist in SKILL Step 5; every error
  says *what went wrong AND how to fix it*.
- **Success / confirmation.** The concrete "goal accomplished" state the user sees — a
  confirmation screen, a toast, a reference number, a receipt. A high-stakes completion
  (payment, submission) gets a **durable** confirmation (reference/receipt), not only a
  transient toast. This is the positive twin of the error state; do not leave the
  success exit as an abstract label.

All of these land in the screens index (SKILL Step 9 / the index section).

## Resilience qualities (Nielsen heuristics applied to the path)

### Undo, reversibility & the irreversible-action guard (Nielsen #3 + #5)

Users act by mistake; they need an emergency exit. Two distinct mechanisms:

- **Undo** — reverse a *completed, reversible* action. Prefer undo over a modal confirm
  for reversible actions (less friction).
- **Confirm / guard** — prevent an *irreversible* one. Every destructive / irreversible
  / high-stakes action (delete, pay, send, final submit, irreversible state change)
  carries a confirm step or an undo path. A "delete on single click, no undo" for a
  truly irreversible action is a defect.

Note the tension: over-confirming a trivially reversible action (a confirm dialog on a
one-click undoable toggle) is the *opposite* anti-pattern — guard the irreversible,
undo the reversible.

### Resume vs restart after interruption

Interruption is inevitable on a multi-step flow (close tab, lose session, switch
device, time out). State the answer per multi-step flow: does the user **resume** where
they left off (what is persisted, for how long) or **restart**? Long forms, checkouts,
and onboarding should generally persist; a quick one-screen action need not. A 6-step
flow that silently discards progress on a reload, with no stated decision, is a gap.

### Visibility of system status — "what changed" (Nielsen #1)

"The most basic guideline of UI design": keep the user informed with timely feedback.
Each **state-changing step shows its result** — not just "done" but *what* changed
(saved as draft, payment of $X authorized, 3 items added, request submitted as #1234).
A step that mutates state and advances with no confirmation of what happened leaves the
user unsure their action registered. Feedback is timely: immediate for instant actions;
an in-progress state for slow ones.

### Optimistic vs confirmed actions

- **Confirmed** — wait for the server (show the in-progress state), then advance. Use
  for anything with consequences.
- **Optimistic** — reflect the action immediately, reconcile on server response.
  Improves perceived performance for **low-risk, low-failure** actions (a like, a list
  reorder). **Never** for payments, deletions, or anything with serious consequences.
  An optimistic action MUST define its **revert path + feedback** — what the user sees
  when the update fails and rolls back (always show feedback on a failed optimistic
  update). An optimistic payment, or an optimistic action with no revert path, is a gap.

## Reviewer-side note (single-sourced)

These are conditions the review gate checks proportionally: irreversible-action-guarded,
resume/restart-stated, what-changed-feedback-present, optimistic-revert-defined,
loading + success states enumerable. Each collapses where inapplicable (a read-only flow
has nothing to guard/persist/confirm).

## Sources

- Nielsen Norman Group / Jakob Nielsen — *10 Usability Heuristics for User Interface
  Design*: #1 Visibility of system status, #3 User control & freedom (undo, emergency
  exit), #5 Error prevention (confirm before irreversible).
- Skeleton-screen practice — skeletons as the norm for full-page loads (~2–10s, match
  final layout, subtle motion); modern perceived-performance practice sometimes removes
  the visible wait.
- Optimistic-UI literature — optimistic update + reconcile; not for payments/deletions;
  always show feedback on a failed optimistic update that reverts.
