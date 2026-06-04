# The implementability + testability bar — expanded

Load this when a Step-2 condition is borderline and you need a sharper pass/gap call. The eight conditions below are the single-sourced bar — identical to the one a feature-spec author produces to. Each entry gives the **pass signal**, the **gap signal**, and the **failure-spotting move**.

---

## 1. Traced to the upstream need (both directions)

- **Pass:** every feature in the spec names the PRD goal / requirement / metric it serves, and every upstream feature line has a corresponding spec section.
- **Gap — orphan:** a feature with no upstream line behind it. This is scope creep; the spec is building something the product doc never asked for.
- **Gap — coverage:** an upstream feature line with no spec section. The build will silently drop a required capability.
- **Spotting move:** read the upstream feature list and tick each one off against a spec section (forward — catches coverage gaps); then read each spec section and find its upstream line (backward — catches orphans). An empty cell in either direction is the signal.

## 2. Unambiguous + observable behavior

- **Pass:** each behavior reads one way only, is stated as an observable response to a named input/interaction, and says *what* happens, not *how* it is coded.
- **Gap — ambiguous:** the same sentence could be built two different ways (e.g. "the list updates" — sorted how? including pending items?).
- **Gap — unobservable:** the behavior describes an internal effect with no output a tester could see.
- **Gap — implementation leak:** the spec dictates a data structure, algorithm, or library the requirement has no reason to fix.
- **Spotting move:** for each behavior, ask "could two engineers build this differently from these words?" and "what would a tester *see*?" If the first is yes or the second has no answer, it is a gap.

## 3. Complete inputs / outputs / states

- **Pass:** every input enumerated with source, type, validation rule, required/optional; every output enumerated with shape/response and side effects; stateful features list states + legal/illegal transitions.
- **Gap:** an input with no validation rule or unclear required/optional status; an output with no defined shape; a stateful feature missing a transition so the builder must guess what happens on (state × event).
- **Spotting move:** for each input ask "what is valid, what is rejected, what is the boundary?"; for each output ask "what does the caller/UI observe and what changes as a side effect?"; for state, build the (state × event) grid in your head and find the cell the spec never names.

## 4. Edge cases + error handling — each with its response

Run the spec against this standard checklist. The rule is **each applicable case must name its expected handling/error**, not merely appear.

| Edge case | What to confirm is specified |
|---|---|
| Null / empty / missing input | The defined response (reject with which error? default? skip?) |
| Duplicate / repeat / idempotency | Whether a repeat is rejected, deduplicated, or returns the original result |
| Concurrency / race | Behavior under simultaneous operations (lock, last-writer-wins, conflict error) |
| Permissions / visibility | What an unauthorized or partially-authorized actor sees or is denied |
| Limits / overflow / max size | Behavior at and past the boundary (reject, truncate, paginate, error) |

- **Pass:** every *applicable* case is present **and** states its response.
- **Gap — absent:** an applicable case is not addressed at all.
- **Gap — listed but unhandled:** the case is named but no response is given ("handle duplicates" with no defined behavior). This still fails — the builder is left to invent it, which is rarely what was intended.
- **Spotting move:** for each row, find where the spec says *what the system does*. A row with a mention but no response is the most common real gap here.
- **Proportionality:** a feature with no failure surface legitimately has fewer rows — judge applicability, not row count.

## 5. Independently testable acceptance criteria

- **Pass:** each behavior and edge case has pass/fail criteria a tester could execute without asking the author — Given/When/Then (context → action → observable result) or a rule-based checklist.
- **Gap — vague/subjective:** "fast", "user-friendly", "intuitive", "works well" — no measurable pass/fail. The fix is to quantify ("results return within 200 ms") or to define the observable outcome ("checkout completes in ≤ 3 steps with no error").
- **Gap — missing:** a behavior with no acceptance criterion at all.
- **Smell (flag, do not auto-block):** four or more acceptance criteria on one section usually means two features are fused — recommend a split.
- **Spotting move:** for each criterion ask "could a tester turn this into a pass/fail check without calling the author?" If not, it is not yet specified.

## 6. Singular + consistent

- **Pass:** one idea per requirement; consistent terminology; no internal contradictions.
- **Gap — compound:** a requirement joined by "and" that bundles two testable ideas — split it.
- **Gap — inconsistent:** a term that shifts meaning between sections, or two sections that contradict.
- **Spotting move:** scan for "and"/"or" inside a single requirement; track each domain term and confirm it means one thing throughout; cross-check sections that touch the same data or flow.

## 7. Feasible + plannable

- **Pass:** the feature is buildable within the spec's own stated constraints (time, platform, data, dependencies), and its inputs/outputs + acceptance criteria are concrete enough that a planner can cut tasks/milestones from them.
- **Gap — infeasible:** a behavior the spec's stated constraints make impossible.
- **Gap — unplannable:** the spec is so abstract a planner cannot estimate or sequence the work (no concrete I/O, criteria that don't pin down "done").
- **Spotting move:** ask "given only this spec, could a planner break this into estimable tasks?" and "do the stated constraints actually permit the required behavior?"

## 8. Open questions surfaced, not buried

- **Pass:** genuine unknowns and unresolved decisions are stated openly.
- **Gap:** the spec reads as falsely complete — an obvious undecided point is absent, or an assumption is asserted as a settled decision.
- **Spotting move:** look for the decision the spec *should* have had to make but never mentions; an honestly-labelled "open question / to decide" is a pass signal, not a gap.

---

## Worked findings

**Good (actionable — failed condition + location + fix):**

> **revise** — Behavior (cond. 2), "Search results" section: "the list updates after typing" is ambiguous — it does not say the sort order or whether results filter on each keystroke or on submit. Fix: state the trigger and ordering, e.g. "on each keystroke after the 3rd character, results re-query and render newest-first."

> **revise** — Acceptance criteria (cond. 5), "Upload" section: "the upload should be reliable" has no pass/fail. Fix: give testable criteria, e.g. "Given a 10 MB file, When uploaded, Then a success response returns within 5 s and the file appears in the listing."

> **revise** — Edge cases (cond. 4), "Transfer funds": the concurrency case (two simultaneous transfers from the same account) is not addressed. Fix: name the expected handling, e.g. "concurrent transfers are serialized; the second sees the balance after the first and is rejected if funds are insufficient."

**Bad (vague — do not emit):**

> The spec could be clearer in places. *(Which place? Which condition? What fix?)*

> Consider adding more detail to the error handling. *(Which error? Why a gap? What response is expected?)*

---

## Calibration reminders

- **No false-revise.** A condition is a gap only on a *named, real* deficiency. "I would have phrased it differently" is not a gap. Reviewers — especially when also asked to propose fixes — drift toward over-flagging sound specs; the bar, not your preference, decides.
- **No false-approve.** A genuine blocker (orphan feature, ambiguous behavior, unhandled edge case, untestable criterion) is always a `revise`, however small.
- **Proportional.** Completeness-of-decisions, not word count. A thin but complete spec passes.
