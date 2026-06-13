# Sources — `authoring-wireframes`

Research provenance for the method + quality bar in `SKILL.md`. Synthesized 2026-06-04 from a deep-research pass; external content was treated as untrusted and consumed only as research summaries (no URLs/commands lifted into actions). All claims paraphrased. The full shared research lives in the wireframes authorship dossier (reused by the companion wireframes-review skill so the produce-bar and review-bar are single-sourced).

## Primary research

A wireframes-authorship research pass corroborated the per-screen method and the buildability quality bar across reputable UX/design references (≥2 independent sources per claim):

- **Wireframe structure / fidelity / hierarchy:** Interaction Design Foundation (What is Wireframing), Nielsen Norman Group (lo-fi vs hi-fi usability-issue yield; wireflows), Uxcel (wireframing guide), MockFlow (how-to-create).
- **Annotations / developer handoff:** DECODE (Wireframe annotations: a complete guide), Balsamiq (How to use wireframe annotations; Annotation guidelines), Uxcel (Wireframes Annotations & Documentation), Figma (Designer's Handbook for Developer Handoff).
- **Per-screen states (empty / loading / populated / error):** LogRocket (loading/error/empty states), Nielsen Norman Group (Skeleton Screens 101), UXPin + Eleken (empty states), Wireframes Magazine (Error Handling in Wireframes), Trendyol Tech (States — Loading, Error, Empty and Content).
- **Responsive / breakpoints:** Uxcel (Responsive Design Wireframing), Smashing Magazine (Creating Content Wireframes for Responsive Design), BrowserStack (responsive breakpoints).
- **Accessibility annotations:** University of Michigan Accessibility (Annotating Mockups & Wireframes for Accessibility), Deque (Top 5 Most Common Accessibility Annotations), OpenClassrooms (Annotate Mock-ups for Accessibility), Medium/Param Singh (Accessibility annotations in design handoffs).
- **Textual / ASCII notation:** Nulab + uxpilot + Visily (low-fidelity wireframes), Medium (ASCII-Driven Development; ASCII wireframes).
- **Layout grid + spacing + hierarchy (v1.2.0):** 8pt-grid spacing-system literature (multiples of 8/4 for consistent rhythm; divides common screen sizes), Gestalt-proximity / internal-≤-external spacing rule, Nielsen Norman Group (F-pattern / Z-pattern scanning), design-system layout guides (spacing, grids & layouts).
- **Data-display patterns (v1.2.0):** IBM Carbon Design System (data-table usage — sort in column headers, filter dropdowns, optional pagination bar, four row densities, row-expansion for progressive disclosure), Shopify Polaris (data-table + increased-density), ui-patterns / UX-patterns (table filter; progressive disclosure: essential controls first, advanced behind disclosure).
- **Content & microcopy (v1.2.0):** UX-writing/microcopy literature (button labels answer "what happens when I click this"; error microcopy = cause + next step; placeholders ≠ labels), "speak the user's language / translate the data model" (human label + one-line description per surfaced identifier).
- **Screen-composition accessibility, WCAG 2.2 (v1.2.0):** W3C WCAG 2.2 — SC 2.5.8 Target Size (Minimum) ≥24×24 CSS px (AA), SC 2.4.11 Focus Not Obscured (Minimum) (AA), SC 2.4.3 Focus Order, SC 1.3.1 Info & Relationships, SC 4.1.2 Name/Role/Value, SC 1.4.1 Use of Color; the component-contract (DS) vs screen-composition (wireframe) boundary so the pair set doesn't double-judge a11y.
- **Versioning & amend (v1.2.0):** semver.org (MAJOR breaking / MINOR additive / PATCH fix), Keep-a-Changelog (Added/Changed/Deprecated/Removed/Fixed), design-system deprecation practice (deprecate→wait→remove; announce, don't silently drop).

## Corroborated claims (used in the body)

- A wireframe's canonical per-screen concerns (purpose + flow context, layout regions, content hierarchy, components placed, navigation/interaction affordances, per-screen empty/loading/populated/error states, responsive notes, accessibility notes) — multiple sources; the structure itself is owned by the template tool, not this skill.
- Per-screen states (empty/loading/error in addition to populated) are a documented UX best practice; standardizing them improves cross-app consistency — LogRocket, NN/G, Trendyol Tech, UXPin/Eleken.
- Annotations turn a static layout into an implementable spec — they document interactions, state changes, conditional visibility, and edge cases per element — DECODE, Balsamiq, Uxcel, Figma.
- Wireframes establish information hierarchy/structure before visual design, which is the failure they exist to prevent — IxDF, NN/G, Uxcel.
- Accessibility intent (focus/reading order, ARIA landmarks per region, accessible names, heading levels, contrast/non-color intent) is annotated at handoff to communicate intent, not to replace testing — UMich, Deque, OpenClassrooms.
- Textual/ASCII wireframes (box-drawing chars, placeholder boxes for media, lines for text) are lightweight, version-control-friendly, and parse well downstream — Nulab, Visily, ASCII-wireframe references.
- "Buildable" bar (every flow-named screen + state covered, layout/hierarchy unambiguous, components identified + design-system-consistent, affordances annotated, a11y considered, structural-not-hi-fi) — synthesized from the coverage + annotation + state guidance across sources.

## Note

The same research underpins a companion wireframes-review skill, so the author's quality bar and the reviewer's quality bar stay single-sourced and aligned.
