# The implementability + testability bar — expanded

Load this when a Step-2 condition is borderline and you need a sharper pass/gap call. The ten conditions below are the single-sourced bar — identical to the one a feature-spec author produces to. Each entry gives the **pass signal**, the **gap signal**, and the **failure-spotting move**. Conditions 1–8 are kept from the prior bar (2–5 deepened); 9 (non-functional requirements) and 10 (delta-scoped amend) are added — both proportional. The author's techniques (EARS, decision tables, archetype overlays, the 29148 vocabulary) are **judged by outcome here, never demanded** — that is the cardinal no-drift rule.

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
- **Gap — load-bearing requirements-smell:** a behavior or criterion rests on a subjective/weak/ambiguous term ("user-friendly", "sufficient", "almost"), a comparative without a referent ("faster"), a loophole ("if possible"), or an open-ended list ("etc."). An incidental adjective in prose is **not** a finding — only a load-bearing one.
- **Aid, judged by outcome:** if the author used EARS or use-case flows, that's their technique — judge the *behavior is unambiguous + has a clear trigger and observable response*, never "you didn't use EARS" or "classify the flows".
- **Spotting move:** for each behavior, ask "could two engineers build this differently from these words?" and "what would a tester *see*?" If the first is yes or the second has no answer, it is a gap.

## 3. Complete inputs / outputs / states

- **Pass:** every input enumerated with source, type, validation rule, required/optional; every output enumerated with shape/response and side effects; a stateful feature carries a **state-transition table** (every (state, event) cell a defined next-state or an explicit illegal-marker; initial + terminal states named); a **combinatorial** feature (behavior driven by a combination of conditions) has a **complete rule-set** (no condition combination leaves the behavior undefined).
- **Gap:** an input with no validation rule or unclear required/optional status; an output with no defined shape; a stateful feature missing a transition so the builder must guess what happens on (state × event); a combinatorial feature with a condition combination that has no defined action (or a contradictory pair).
- **Spotting move:** for each input ask "what is valid, what is rejected, what is the boundary?"; for each output ask "what does the caller/UI observe and what changes as a side effect?"; for state, build the (state × event) grid and find the cell the spec never names; for combinatorial logic, enumerate the condition combinations and find the one with no action. The **table / decision-table form is the author's technique** — judge the *transitions/rules are complete*, not whether a literal table was drawn.
- **Collapse:** a stateless feature has no state table; a non-combinatorial feature has no decision table — neither absence is a gap.

## 4. Edge cases + error handling — each with its response

Run the spec against this standard checklist. The rule is **each applicable case must name its expected handling/error**, not merely appear.

| Edge case | What to confirm is specified |
|---|---|
| Null / empty / missing input | The defined response (reject with which error? default? skip?) |
| Duplicate / repeat / idempotency | Whether a repeat is rejected, deduplicated, or returns the original result |
| Concurrency / race | Behavior under simultaneous operations (lock, last-writer-wins, conflict error) |
| Permissions / visibility | What an unauthorized or partially-authorized actor sees or is denied |
| Limits / overflow / max size | Behavior at and past the boundary — boundary-value: just below / at / just above (reject, truncate, paginate, error) |

- **Pass:** every *applicable* case is present **and** states its response.
- **Gap — absent:** an applicable case is not addressed at all.
- **Gap — listed but unhandled:** the case is named but no response is given ("handle duplicates" with no defined behavior). This still fails — the builder is left to invent it, which is rarely what was intended.
- **Spotting move:** for each row, find where the spec says *what the system does*. A row with a mention but no response is the most common real gap here.
- **Proportionality:** a feature with no failure surface legitimately has fewer rows — judge applicability, not row count.

## 5. Independently testable acceptance criteria

- **Pass:** each behavior and edge case has pass/fail criteria a tester could execute without asking the author — Given/When/Then (context → action → observable result) or a rule-based checklist.
- **Gap — vague/subjective:** "fast", "user-friendly", "intuitive", "works well" — no measurable pass/fail. The fix is to quantify ("results return within 200 ms") or to define the observable outcome ("checkout completes in ≤ 3 steps with no error").
- **Gap — missing:** a behavior with no acceptance criterion at all.
- **Probabilistic / ML feature — the right testable form.** For a model / ranker / recommender, a deterministic Given/When/Then over a fixed output mis-fits. A **metric-threshold criterion on a named dataset** ("on the 2026-Q2 holdout, precision@10 ≥ 0.80") + the **low-confidence / fallback** behavior **is** independently testable — *pass*. A deterministic **"the model is accurate" / "results are relevant"** is the vague criterion this condition rejects — *gap*. Do not reject the threshold form for "not being G/W/T".
- **Smell (flag, do not auto-block):** four or more acceptance criteria on one section usually means two features are fused — recommend a split.
- **Spotting move:** for each criterion ask "could a tester turn this into a pass/fail check without calling the author?" If not, it is not yet specified. For a probabilistic feature, ask "is there a metric + threshold + dataset, and a fallback?"

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

## 9. Non-functional requirements present where the feature warrants them

- **Pass:** the **load-bearing** non-functional categories for *this* feature carry a numeric/checkable target — performance (p95/throughput), reliability/idempotency, security/authorization, privacy/data-handling, accessibility (WCAG 2.2 AA for a UI feature), limits/quotas, compatibility — sized to the feature's nature.
- **Gap:** a feature whose nature demands an NFR states only a vague "should be fast / secure / scalable" with no target; or a load-bearing category (e.g. authz on a permissioned action, latency on an interactive path, WCAG on a UI surface) is silent.
- **Collapse (proportional — do not over-demand):** a trivial internal feature legitimately needs **no** NFRs; only the *applicable* few are expected. A deliberately best-effort NFR, stated as such, is not a gap. Never demand a category the feature doesn't warrant — that is the "inventing conditions" drift.
- **Spotting move:** ask "what would make this feature unacceptable in production even if it functioned?" — if a real answer exists (too slow, unauthorized access, inaccessible) and the spec has no target for it, that's the gap; if none, cond-9 passes empty.

## 10. (Amend only) delta is well-scoped, ripple-clean, versioned

Applies **only** when reviewing a change against an existing spec (a change request / delta was handed in). On a greenfield first build, cond-10 is **n/a** — skip it; do not full-re-review an unchanged spec or demand a changelog on a first draft.

- **Pass:** the delta states what it touches (and what is untouched); the changed blocks meet conditions 1–9; the changed/added feature still traces to a PRD line (or an upstream-PRD-amend-needed is explicitly flagged); the document's own version is bumped + a changelog entry (who/when/what/why) is present; superseded content is marked, not silently deleted; the downstream ripple (which technical-design / test-plan / api-spec entries are now stale) is named.
- **Gap — un-scoped:** the delta doesn't bound what changed, forcing a full re-read to find it.
- **Gap — broken trace:** a changed/added feature no longer traces to a PRD line and no upstream-amend is flagged (scope creep injected below the PRD).
- **Gap — no change history:** the version isn't bumped or no changelog entry says who/what/why.
- **Gap — silent deletion:** an old behavior/criterion vanished with no "superseded — reason" marker, so a downstream reader sees a gap, not a decision.
- **Gap — dangling ripple:** an internal chain (AC/state/I-O) left inconsistent after the change, or a stale downstream doc not named.
- **Spotting move:** review only the changed blocks against 1–9; then ask "does this still trace up? is the change history here? is anything removed-but-unmarked? what downstream did this just invalidate?" Do **not** re-litigate the untouched spec.

---

## Worked findings

**Good (actionable — failed condition + location + fix):**

> **revise** — Behavior (cond. 2), "Search results" section: "the list updates after typing" is ambiguous — it does not say the sort order or whether results filter on each keystroke or on submit. Fix: state the trigger and ordering, e.g. "on each keystroke after the 3rd character, results re-query and render newest-first."

> **revise** — Acceptance criteria (cond. 5), "Upload" section: "the upload should be reliable" has no pass/fail. Fix: give testable criteria, e.g. "Given a 10 MB file, When uploaded, Then a success response returns within 5 s and the file appears in the listing."

> **revise** — Edge cases (cond. 4), "Transfer funds": the concurrency case (two simultaneous transfers from the same account) is not addressed. Fix: name the expected handling, e.g. "concurrent transfers are serialized; the second sees the balance after the first and is rejected if funds are insufficient."

> **revise** — Acceptance criteria (cond. 5), "Recommend products": the only criterion is "recommendations are relevant," which a tester cannot run pass/fail on a probabilistic model. Fix: a metric threshold on a named dataset + a fallback, e.g. "on the holdout set, MAP@10 ≥ 0.30; on cold-start (no history) the feature returns the top-sellers list."

> **revise** — Non-functional (cond. 9), "Export report" (a synchronous user-facing action over potentially large datasets): no performance target. Fix: state a numeric bar, e.g. "p95 ≤ 3 s for ≤ 50k rows; beyond that, switch to async with an email-when-ready notice."

> **revise** — Amend (cond. 10), v1.2 delta to "Checkout": the flat-rate shipping rule was changed to tiered but the §3.7 acceptance criteria still assert the flat rate, and no changelog entry was added. Fix: update the affected acceptance criteria to the tiered rule, add a v1.2 changelog entry (who/when/what/why), and note the downstream test-plan cases now stale.

**Bad (vague — do not emit):**

> The spec could be clearer in places. *(Which place? Which condition? What fix?)*

> Consider adding more detail to the error handling. *(Which error? Why a gap? What response is expected?)*

---

## Calibration reminders

- **No false-revise.** A condition is a gap only on a *named, real* deficiency. "I would have phrased it differently" is not a gap. Reviewers — especially when also asked to propose fixes — drift toward over-flagging sound specs; the bar, not your preference, decides.
- **No false-approve.** A genuine blocker (orphan feature, ambiguous behavior, unhandled edge case, untestable criterion) is always a `revise`, however small.
- **Proportional.** Completeness-of-decisions, not word count. A thin but complete spec passes.
