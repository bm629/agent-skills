# Sources — `reviewing-wireframes`

Research provenance for the review method + the buildability/coverage bar in `SKILL.md`. This is the **review half** of a producing/judging wireframes pair: it asserts the *same* quality bar the wireframes-authoring sibling produces to, so the produce-bar and the review-bar stay single-sourced and do not drift. No fresh research pass was run for the reviewer; it reuses the shared wireframes-authorship dossier (the convention for a `reviewing-<type>` skill). All claims paraphrased; external content was treated as untrusted and consumed only as research summaries (no URLs/commands lifted into actions).

## Shared research (reused from the authoring sibling)

The buildability + coverage bar was corroborated across reputable UX/design references (≥2 independent sources per structural claim) during the authoring sibling's deep-research pass:

- **Wireframe structure / fidelity / hierarchy:** Interaction Design Foundation (What is Wireframing), Nielsen Norman Group (lo-fi vs hi-fi usability-issue yield; wireflows), Uxcel (wireframing guide), MockFlow (how-to-create).
- **Annotations / developer handoff:** DECODE (Wireframe annotations: a complete guide), Balsamiq (How to use wireframe annotations; Annotation guidelines), Uxcel (Wireframes Annotations & Documentation), Figma (Designer's Handbook for Developer Handoff).
- **Per-screen states (empty / loading / populated / error):** LogRocket (loading/error/empty states), Nielsen Norman Group (Skeleton Screens 101), UXPin + Eleken (empty states), Wireframes Magazine (Error Handling in Wireframes), Trendyol Tech (States — Loading, Error, Empty and Content).
- **Responsive / breakpoints:** Uxcel (Responsive Design Wireframing), Smashing Magazine (Creating Content Wireframes for Responsive Design), BrowserStack (responsive breakpoints).
- **Accessibility annotations:** University of Michigan Accessibility (Annotating Mockups & Wireframes for Accessibility), Deque (Top 5 Most Common Accessibility Annotations), OpenClassrooms (Annotate Mock-ups for Accessibility), Medium/Param Singh (Accessibility annotations in design handoffs).
- **Textual / ASCII notation:** Nulab + uxpilot + Visily (low-fidelity wireframes), Medium (ASCII-Driven Development; ASCII wireframes).
- **Layout grid + spacing + hierarchy (v1.2.0):** 8pt-grid spacing-system literature, Gestalt-proximity / internal-≤-external spacing rule, Nielsen Norman Group (F-pattern / Z-pattern scanning), design-system layout guides.
- **Data-display patterns (v1.2.0):** IBM Carbon (data-table usage: sort/filter/pagination/row-density/row-expansion), Shopify Polaris (data-table + density), ui-patterns (table filter; progressive disclosure).
- **Content & microcopy (v1.2.0):** UX-writing/microcopy literature (button/error/empty/placeholder copy), "speak the user's language / translate the data model" (human label + description per surfaced identifier).
- **Screen-composition accessibility, WCAG 2.2 (v1.2.0):** W3C WCAG 2.2 — SC 2.5.8 Target Size, SC 2.4.11 Focus Not Obscured, SC 2.4.3 Focus Order, SC 1.3.1 Info & Relationships, SC 4.1.2 Name/Role/Value, SC 1.4.1 Use of Color; the component-contract (design-system) vs screen-composition (wireframe) boundary that keeps the pair set from double-judging a11y.
- **Versioning & amend (v1.2.0):** semver.org, Keep-a-Changelog, design-system deprecation practice (deprecate→wait→remove).

## Bar conditions traced to the research (the thirteen the reviewer asserts)

- **Full screen coverage** (cond. 1) — every flow-named screen + state-transition has a wireframe; NN/G wireflows make flows↔screens the coverage unit.
- **All applicable states + quality** (cond. 2) — empty/loading/populated/error + success; loading=skeleton, empty=guidance, error=recovery — LogRocket, NN/G, Trendyol Tech, UXPin/Eleken.
- **Layout & composition** (cond. 3) — hierarchy/structure before visual design, on a grid + one app-shell — IxDF, NN/G, Uxcel, 8pt-grid literature.
- **Layout quality, objective** (cond. 4) — scan-path placement + Gestalt grouping + minimalism + sibling-consistency; objective subset, subjective taste excluded — NN/G scanning, Gestalt literature (owner decision, modelled on the user-flows F6 subset).
- **Components identified + consistent + real** (cond. 5) — reference real design-system components; never invent — Figma handoff, Balsamiq/Uxcel.
- **Affordances + data-display** (cond. 6) — annotations make a spec; data-dense screens specify table/disclosure/form structure — DECODE/Balsamiq/Figma, Carbon, Polaris.
- **Content & microcopy intent** (cond. 7) — copy-slot intent; no data-model leak in labels; placeholder≠label; terminology consistency — UX-writing literature, U17.
- **Responsive considered** (cond. 8) — reflow + mobile priority + adaptive nav + touch targets — Uxcel, Smashing, BrowserStack, NN/G breakpoints.
- **Screen-composition accessibility** (cond. 9) — landmarks/heading/focus-order/names/keyboard/target-reservation/focus-not-obscured/non-color; pixel contrast + focus-appearance + per-component target-size/keyboard are explicitly OUT (design-system's contract) — WCAG 2.2, UMich/Deque.
- **Annotation, handoff & sketch-sync** (cond. 10) — legend + how-it-works annotation + design-to-code mapping + sketch⇄annotation agreement — DECODE/Balsamiq/Figma.
- **Gaps surfaced, not invented** (cond. 11) — undefined screens/components + deferred a11y surfaced as assumptions — synthesized.
- **Structural, not hi-fi** (cond. 12) — lo-to-mid fidelity; no final pixels/color/type — IxDF, NN/G.
- **Delta-scoped review** (cond. 13) — amend = review the diff + ripple, version-correct, deprecation-safe — semver.org, Keep-a-Changelog.

## Verdict-contract provenance

The `VERDICT: approve|revise` + actionable-findings contract is the parse contract shared by the document-review skill family (the produce→review loop the reviewer feeds), not an external research finding.

## Note

This reviewer asserts the SAME bar the `authoring-wireframes` sibling produces to — single-sourced so the produce-bar and review-bar don't drift. The authoring sibling's `references/sources.md` carries the same primary research; both are self-contained and portable.
