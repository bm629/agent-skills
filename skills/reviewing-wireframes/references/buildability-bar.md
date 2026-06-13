# Buildability + Coverage + Composition Bar — expanded checklist

The thirteen conditions `reviewing-wireframes` asserts, each with its **pass** signal, **gap** signal, and a worked finding. This is the single-sourced bar the `authoring-wireframes` sibling produces to (same list, no drift). Load when a borderline condition needs a sharper pass/gap call.

The reviewer is given the wireframes doc and, when available, the **upstream user-flows** (coverage cross-check) and the **design-system** (component-consistency cross-check). When a cross-check input is absent, judge from the doc's own screen inventory / component references and note the missing input once — never invent the comparison.

Every condition is **proportional to the screen's archetype**: a thin/static screen legitimately collapses conditions it doesn't need. Manufacturing a gap from brevity is the most common reviewer error. Conditions marked *baseline* do not collapse.

---

## 1. Full screen coverage *(baseline)*
- **Pass:** every flow-named screen + implied state-transition has a wireframe; the screen-inventory table maps screen/state → section and is complete.
- **Gap:** a flow-named screen/transition has no wireframe (orphan); or the inventory omits screens the flows require.
- **Finding:** *revise — Coverage (cond. 1): the user-flows name a "Forgot password" screen (F2 step 4) with no wireframe. Fix: add it, or surface it as an open question if its content is undefined.*

## 2. All applicable per-screen states + quality
- **Pass:** empty/loading/populated/error + success where a state-change occurs (+ partial where relevant); each with quality — loading = skeleton mirroring the layout (not a bare spinner) where known; empty = reason + guide-to-action; error = plain-language cause + recovery.
- **Gap:** an applicable state missing, or a present state is an empty shell (a bare spinner on a known layout; a blank empty panel; an error with no recovery).
- **Finding:** *revise — States (cond. 2): the Search Results screen documents only the populated list; empty/loading/error are missing and the "saved" success cue is absent. Fix: add empty ("no matches, try X" + CTA), loading (skeleton mirroring the list), error (retry), and the success confirmation.*
- **Collapse:** a static info screen has only populated.

## 3. Layout & composition unambiguous
- **Pass:** regions + content priority clear enough to build without guessing; on a grid; in the ONE shared app-shell.
- **Gap:** two engineers would build two different structures; or a screen re-invents/drops the shared shell.
- **Finding:** *revise — Layout (cond. 3): the Dashboard names a "sidebar" and a "panel" but neither the sketch nor the text says which side or which holds the primary content, and it uses a different header than every other screen. Fix: place the regions on the grid in the sketch; sit it in the shared app-shell.*
- **Collapse:** a one-element screen needs no grid discussion.

## 4. Layout quality (objective)
- **Pass:** primary action on the scan path; related elements grouped; no gratuitous region/element; consistency with sibling screens.
- **Gap (objective only):** the primary action is buried below the fold / off the scan path; unrelated items jammed into one group; a redundant region; a sibling screen laid out inconsistently. **Subjective taste ("a nicer layout exists", "I'd use cards") is NOT a gap.**
- **Finding:** *revise — Layout quality (cond. 4): the Create-Invoice screen places the primary "Send" action at the bottom-right below a long optional-notes field, off the scan path. Fix: move the primary action onto the scan path (top-right or a sticky action bar).*
- **Collapse:** a trivial screen trivially holds.

## 5. Components identified + consistent + real *(baseline: no-invention)*
- **Pass:** each notable element names its DS component (where one exists); reused components consistent; nothing invented; anatomy used.
- **Gap:** an unidentified blob; inconsistent naming across screens; or an invented component/token presented as decided.
- **Finding:** *revise — Components (cond. 5): the Settings screen references a "MegaToggle" the design-system does not define, presented as final. Fix: reference the DS's real toggle, or flag "MegaToggle" as an open question for the DS owner.*

## 6. Affordances + data-display annotated
- **Pass:** every interactive element's behavior + destination + edge cases annotated; data-dense screens specify table/list/card choice + controls (sort/filter/paginate/density/expansion) + progressive disclosure; forms use structured inputs (no serialized-string fields).
- **Gap:** a control whose behavior must be guessed; a data table as an unstructured "a table goes here"; a form field requiring a hand-authored `key=value`/JSON string.
- **Finding:** *revise — Affordances/data-display (cond. 6): the Orders screen shows a table with no columns, sort, filter, pagination, or row-density stated, and the "Save" button has no behavior annotation. Fix: specify the table's columns + which controls apply; annotate what Save validates + its success/error destinations.*
- **Collapse:** a static screen has no data/forms.

## 7. Content & microcopy intent
- **Pass:** load-bearing text slots state their intent; no raw data-model identifier as a label (human label + description); persistent labels (placeholder ≠ label); terminology consistent across screens; i18n expansion room where localized.
- **Gap:** a raw identifier (`manifest_docs`) shown as a label; a placeholder used as the only label; the same concept named two ways across screens.
- **Finding:** *revise — Microcopy (cond. 7): the Sync screen labels a field `control_plane_repo` (a raw data-model id) and uses placeholder text as its only label. Fix: give it a human label + one-line description ("Control-plane repository — where your project config is stored"); add a persistent label.*
- **Baseline:** the no-data-model-leak label rule + terminology consistency don't collapse; i18n collapses for single-locale (stated reason).

## 8. Responsive considered
- **Pass:** for screens where form-factor matters, the reflow mechanism (stack/collapse/hide/reorder) + mobile content-priority + adaptive nav + touch-target reservation are stated.
- **Gap:** a screen that clearly reflows says nothing about how.
- **Finding:** *revise — Responsive (cond. 8): the multi-column Dashboard says nothing about mobile. Fix: state how the columns stack, what the nav collapses to (hamburger/off-canvas), and the content-priority change on small screens.*
- **Collapse:** a single-form-factor surface (stated reason) or a screen with no meaningful reflow.

## 9. Screen-composition accessibility *(baseline: landmarks + one h1 + names + keyboard)*
- **Pass:** landmarks per region, one-h1 heading order, reading/focus order, accessible names (incl. icon-only), keyboard-operability, ≥24px target-size **reservation**, focus-not-obscured (where sticky), non-color-only intent.
- **Gap:** a screen with interactive controls has no composition-a11y annotation; an icon-only control has no accessible name; a required action is mouse-only; targets crammed below 24px.
- **Out-of-lane (NOT a gap here):** pixel **contrast** (4.5:1 / 3:1), **focus-appearance** (SC 2.4.13), and the component's own target-size/keyboard — those are the **design-system's** per-component contract. Revising because a contrast ratio isn't stated is out-of-lane.
- **Finding:** *revise — Composition a11y (cond. 9): the Checkout form's icon-only "remove" buttons have no accessible name and the focus order through the fields isn't stated. Fix: annotate accessible names + the focus/reading order. (Do NOT ask for contrast ratios — that's the design-system's.)*

## 10. Annotation, handoff & sketch-sync *(baseline)*
- **Pass:** notation legend defined; every load-bearing element annotated (how-it-works); elements map to DS components (design-to-code handoff); the sketch and its annotations agree.
- **Gap:** a static un-annotated sketch; an annotation referencing an element not in the sketch, or a drawn element with no annotation.
- **Finding:** *revise — Annotation/sync (cond. 10): the Detail screen's annotation table lists a "bulk-actions bar" that does not appear in the box sketch. Fix: add the bar to the sketch (or remove the annotation) so the two agree.*

## 11. Gaps surfaced, not invented *(baseline)*
- **Pass:** undefined screens/content, missing DS components, and deferred component-contract a11y (no DS/hi-fi) are explicit assumptions/open-questions.
- **Gap:** the doc papers over an undefined screen/component by inventing one as decided. (An honestly-labelled assumption is **not** a gap.)
- **Finding:** *revise — Gaps (cond. 11): the Onboarding "welcome" content is undefined by the flows, yet the doc invents a full layout as final. Fix: mark it an assumption to validate, or request the missing flow detail.*

## 12. Structural, not hi-fi *(baseline)*
- **Pass:** lo-to-mid fidelity — layout + annotation; no final pixels, color, or type.
- **Gap:** it overshoots into hi-fi (exact hex, type scale, pixel spacing), stepping on the hi-fi/design-system scope.
- **Finding:** *revise — Fidelity (cond. 12): the Landing screen specifies exact hex colors and a 16px type scale — hi-fi decisions the design-system/hi-fi pass own. Fix: drop the visual specifics; keep the structural layout + annotations.*

## 13. Delta-scoped review (amended docs only)
- **Pass:** the review is confined to the diff; a shared-region change reached **all** reusing screens; no inventory row orphaned, no flow-named screen newly uncovered, no component-name drift; sketch⇄annotations still in sync; the doc's own version bump matches the change class; a breaking removal carries deprecation; the changelog matches the diff.
- **Gap:** an untouched screen was needlessly re-drawn; a shared-region change hit one screen but not its siblings; a removed screen still referenced in the inventory; a wrong/absent version bump or changelog entry; a breaking removal with no deprecation.
- **Finding:** *revise — Delta (cond. 13): the amendment changed the global nav on the Dashboard but left the other four screens' nav as-was, and bumped only PATCH for a removed "Export" screen. Fix: apply the nav change to all reusing screens; bump MAJOR for the removed screen + add a deprecation/changelog entry; prune it from the inventory.*
- **N/A:** a greenfield first build (not an amendment).

---

## Verdict mapping
- **approve** — every *applicable* condition passes; the structure is buildable, every flow-named screen + state is covered, and the composition meets the objective bar. Approve even with imaginable layout improvements; the bar is buildability + coverage + objective composition, not perfection.
- **revise** — one or more conditions have a real, named gap. Each revise finding is actionable: failed condition + location (screen/state) + concrete fix. Never revise on subjective layout taste (cond. 4) or on pixel-contrast the design-system owns (cond. 9).
