# Buildability + Coverage Bar — expanded checklist

The nine conditions `reviewing-wireframes` asserts, each with its **pass** signal, its **gap** signal, and a worked finding. This is the single-sourced bar the wireframes-authoring sibling produces to (same list, no drift). Load this when a borderline condition needs a sharper pass/gap call.

The reviewer is given the wireframes doc and, when available, the **upstream user-flows** (the coverage cross-check) and the **design-system** (the component-consistency cross-check). When a cross-check input is absent, judge from the doc's own screen inventory / component references and note the missing input once in the findings — never invent the comparison.

---

## 1. Full screen coverage

- **Pass:** every screen the upstream user-flows name, and every state-transition they imply, has a wireframe. A screen-inventory table maps flow-named screen/state → wireframe section, and it is complete.
- **Gap:** a flow-named screen or implied transition state has no wireframe (an orphan); or the inventory omits screens the flows clearly require.
- **Finding:** *revise — Coverage (cond. 1): the user-flows name a "Forgot password" screen (flow F2, step 4) with no wireframe. Fix: add a wireframe for it, or surface it as an explicit open question if its content is undefined.*

## 2. All four per-screen states

- **Pass:** each screen documents empty, loading, populated, and error.
- **Gap:** a screen shows only the populated/happy view and omits one or more of empty / loading / error. This is the single most common wireframe defect.
- **Finding:** *revise — States (cond. 2): the Search Results screen documents only the populated list; empty (no results), loading (skeleton), and error (query failed) states are missing. Fix: add the three states — empty with the "no matches, try X" message + CTA, loading skeleton mirroring the list, error with retry.*

## 3. Unambiguous layout + content hierarchy

- **Pass:** layout regions and content priority are clear enough to build the structure without guessing.
- **Gap:** a region's arrangement or content ordering is ambiguous enough that two engineers would build two different structures.
- **Finding:** *revise — Layout (cond. 3): the Dashboard names a "sidebar" and a "panel" but neither the sketch nor the description says which side or which contains the primary content. Fix: place the regions in the sketch and order the content by priority.*

## 4. Components identified + consistent

- **Pass:** each notable element names its component (the design-system component where one exists); reused components are named consistently across screens; nothing is invented.
- **Gap:** an unidentified element blob; the same element named differently across screens; or a component/token invented that the design-system does not define, presented as decided.
- **Finding:** *revise — Components (cond. 4): the Settings screen references a "MegaToggle" component the design-system does not define, presented as final. Fix: reference the design-system's real toggle component, or flag "MegaToggle" as an open question for the design-system owner.*

## 5. Affordances annotated

- **Pass:** every interactive element's behavior and destination is annotated — interaction (tap/hover/validation/conditional visibility), where it leads, and relevant edge cases (truncation, overflow, sorting, pagination, dropdown contents).
- **Gap:** the sketch is a static picture with elements whose behavior a developer must guess.
- **Finding:** *revise — Affordances (cond. 5): the Profile screen's "Save" button has no annotation — no validation behavior, no success/error destination. Fix: annotate what Save validates, where it goes on success, and the error path.*

## 6. Responsive considered

- **Pass:** for screens where it matters, reflow across the target breakpoints is stated — what stacks, collapses, hides, or reorders.
- **Gap:** a screen that clearly reflows says nothing about how. (A screen with no meaningful reflow need not belabor it — do not manufacture a gap.)
- **Finding:** *revise — Responsive (cond. 6): the multi-column Dashboard says nothing about mobile reflow. Fix: state how the columns stack, what the nav collapses to, and any content-priority change on small screens.*

## 7. Accessibility considered

- **Pass:** focus/reading order, labels/landmarks, and contrast / non-color-only intent are annotated.
- **Gap:** a screen with interactive controls has no a11y annotation at all.
- **Finding:** *revise — Accessibility (cond. 7): the Checkout form has no a11y annotation — no focus order, no accessible names for the icon-only buttons. Fix: annotate focus order, accessible names, and the error-state non-color cue.*

## 8. Gaps surfaced, not invented

- **Pass:** undefined screens/content and missing design-system components are explicit assumptions/open-questions.
- **Gap:** the doc papers over an undefined screen or a missing component by inventing a plausible one and presenting it as decided. (An honestly-labelled assumption is **not** a gap.)
- **Finding:** *revise — Gaps (cond. 8): the Onboarding "welcome" screen content is undefined by the flows, yet the doc invents a full layout and presents it as final. Fix: mark the invented content as an assumption to validate, or request the missing flow detail.*

## 9. Structural, not hi-fi

- **Pass:** the doc stays low-to-mid fidelity — layout + annotation — with no final pixels, color, or type.
- **Gap:** it overshoots into hi-fi (exact colors, type, pixel spacing), stepping on the design-system's scope.
- **Finding:** *revise — Fidelity (cond. 9): the Landing screen specifies exact hex colors and a 16px type scale — hi-fi visual decisions the design-system owns. Fix: drop the visual specifics; keep the structural layout + annotations.*

---

## Proportionality note

"Buildable enough" scales with the screen. A trivial / static screen legitimately collapses conditions it does not need — a static info screen may have no meaningful loading/error state or reflow. Judge completeness-of-decisions for *that* screen, not a fixed word count. Manufacturing a gap from brevity is the most common reviewer error; calibrate to the screen and the project.

## Verdict mapping

- **approve** — every *applicable* condition passes; the screen structure is buildable and every flow-named screen + state is covered. Approve even with imaginable layout improvements; the bar is buildability + coverage, not perfection.
- **revise** — one or more conditions have a real, named gap (a missing state, an invented component, an uncovered flow-named screen, an ambiguous layout, no a11y annotation). Each revise finding is actionable: failed condition + location (screen/state) + concrete fix.
