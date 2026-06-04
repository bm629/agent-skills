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

## Bar conditions traced to the research (the nine the reviewer asserts)

- **Full screen coverage** (cond. 1) — every flow-named screen + implied state-transition has a wireframe; NN/G wireflows make the flows↔screens mapping the coverage unit.
- **All four per-screen states** (cond. 2) — empty/loading/populated/error are a documented best practice; happy-path-only is the most common gap — LogRocket, NN/G, Trendyol Tech, UXPin/Eleken.
- **Unambiguous layout + hierarchy** (cond. 3) — wireframes establish information hierarchy/structure before visual design, the failure they exist to prevent — IxDF, NN/G, Uxcel.
- **Components identified + consistent** (cond. 4) — reference real design-system components; never invent — Figma handoff guidance, Balsamiq/Uxcel annotation guides.
- **Affordances annotated** (cond. 5) — annotations turn a static layout into an implementable spec (interactions, state changes, conditional visibility, edge cases) — DECODE, Balsamiq, Uxcel, Figma.
- **Responsive considered** (cond. 6) — reflow across breakpoints stated where it matters — Uxcel, Smashing Magazine, BrowserStack.
- **Accessibility considered** (cond. 7) — focus/reading order, landmarks, accessible names, contrast/non-color intent annotated at handoff (communicates intent, does not replace testing) — UMich, Deque, OpenClassrooms.
- **Gaps surfaced, not invented** (cond. 8) — undefined screens/content + missing components surfaced as assumptions/open-questions, not silently filled — synthesized from the coverage + handoff guidance.
- **Structural, not hi-fi** (cond. 9) — stays lo-to-mid fidelity; no final pixels/color/type (downstream visual design) — IxDF, NN/G (lo-fi vs hi-fi).

## Verdict-contract provenance

The `VERDICT: approve|revise` + actionable-findings contract is the parse contract shared by the agent-flow document-review skills (the produce→review loop the reviewer feeds), not an external research finding.

## Note

The single-sourced shared dossier lives at `docs/superpowers/agent-flow/authoring-wireframes/research/wireframes-dossier.md` (its §3 is this reviewer's bar). The authoring sibling's `references/sources.md` carries the same primary research. Single-sourcing keeps the author's quality bar and the reviewer's quality bar aligned.
