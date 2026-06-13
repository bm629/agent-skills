# Flow quality & heuristic soundness — depth

> Loaded for Workflow Step 8. Judging whether a flow is *good*, not only complete +
> walkable — the **objectively checkable** subset of Nielsen's heuristics. Subjective
> taste ("I'd design it differently", "a nicer flow exists") is explicitly OUT of
> scope, preserving the no-false-revise contract. Most quality conditions are
> restatements of the resilience/accessibility steps as a quality lens; the
> genuinely-new ones are error-prevention, recognition-over-recall, no-gratuitous-step,
> and cross-flow consistency.

## The scope rule (read first)

The pair is a machine-parseable gate. It judges quality through **objective** conditions
only — each can be answered yes/no by looking at the flow. It does NOT revise on
preference. If you cannot state a quality concern as an objective condition, it is not a
gate condition (it is, at most, an author-side nicety).

## Nielsen's 10 heuristics, mapped to flows

| # | Heuristic | Flow-level application | Objective? | Where it lives |
|---|---|---|---|---|
| 1 | Visibility of system status | each state-changing step shows what changed | yes | resilience (Step 6) |
| 2 | Match to the real world | flow follows the user's mental model / real sequence | partly | grounding (Step 1) |
| 3 | User control & freedom | irreversible action has confirm-or-undo; back/cancel clean | yes | resilience (Step 6) |
| 4 | Consistency & standards | like jobs use like paths; follow platform/DS convention | yes | F6.4 below |
| 5 | Error prevention | guard an irreversible action *before* it happens | yes | F6.2 below |
| 6 | Recognition over recall | a step surfaces what a prior step established | yes | F6.3 below |
| 7 | Flexibility & efficiency | path no longer than the job; expert shortcut where apt | yes (length) / opt (shortcut) | F6.1 below |
| 8 | Aesthetic & minimalist | no gratuitous step/screen | yes | F6.1 below |
| 9 | Help users recover from errors | error = cause + fix + recovery (kept) | yes | edge checklist (Step 5) |
| 10 | Help & documentation | help reachable where the job needs it | proportional | light |

The "yes" rows are the gate's quality conditions; the "partly"/"opt" rows are grounding/
nicety, not revise-triggers.

## The four genuinely-new quality conditions

### F6.1 Efficiency / no gratuitous step (#7, #8)

The path is **no longer than the job requires** — every step earns its place. A
gratuitous step/screen/confirmation that adds friction without value is a defect; a path
materially longer than the established pattern for the same job, with no stated reason,
is a gap. (Subjective "could be smoother" is NOT a gap.) Path-length is judged HERE,
once — not also in accessibility. Expert shortcuts (skip steps a returning user doesn't
need) are a bonus where the persona warrants — not required.

### F6.2 Error prevention over recovery (#5)

Preventing an error beats recovering from one. Guard the **irreversible / high-stakes**
action *before* it happens — a confirm step, a disabled-until-valid submit, a
preview-before-commit — rather than relying only on after-the-fact recovery. This is the
proactive twin of undo (Step 6) and recover (Step 5). A "delete-on-single-click,
undo-only" pattern for a truly irreversible action is a gap.

### F6.3 Recognition over recall (#6)

Minimize memory load — a step **surfaces what a prior step established** rather than
making the user remember it across screens. A flow that shows a code/value on screen 2
and asks the user to type it from memory on screen 4 (no carry-forward) forces recall;
carry context forward or keep it visible.

### F6.4 Consistency with platform & product convention (#4)

The same kind of job uses a **consistent** path across the doc's flows, and follows
platform / design-system conventions (or states the deviation). Two flows solving the
same sub-problem two different ways, with no reason, is a gap. This is the prior-art
grounding (Step 1) applied as a cross-flow consistency check.

## Boundary with the rest of the bar

- System-status (#1) and user-control/undo (#3) are produced in Step 6 (resilience) —
  F6 does not re-judge them; it relies on them.
- No-mouse-only / completability (#... accessibility) is Step 7 — F6 does not touch it.
- Path-length is F6.1 only (not accessibility) — judged once.

## Sources

- Nielsen Norman Group / Jakob Nielsen — *10 Usability Heuristics for User Interface
  Design* (the canonical list): error prevention > error messages; confirm before
  irreversible; recognition over recall; flexibility/efficiency (novice + expert,
  shortcuts); measurable via time-to-complete / clicks-to-complete / errors-detected.
- The objective-subset framing preserves the gate's no-false-revise contract: subjective
  critique (is it *delightful*?) is left to a separate usability-critique pass, not this
  pair.
