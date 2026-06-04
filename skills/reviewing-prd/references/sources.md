# Sources — research provenance for `reviewing-prd`

The **plannability checklist** (the eight conditions) is single-sourced from an internal PRD-authorship dossier so the produce-bar and review-bar match. The web research below grounds the **review method** — how to *judge* each dimension, detect fabricated evidence, and phrase actionable findings — not the bar itself.

## Primary bar (single-source)

- Internal PRD-authorship dossier, §3 "plannability quality bar" (7 checkable conditions) + §2 "authoring method" (what a good fill looks like per dimension). The author produces to this bar; this skill judges against the same list. No competing bar was researched or invented.

## Existing skills inspected as source material (first-filter only, paraphrased)

- `vladm3105/aidoc-flow-framework@doc-prd-reviewer` — PRD content review / QA beyond structural validation (now deprecated/merged upstream). Confirms: review = quality-against-bar, not template conformance.
- `testany-io/testany-agent-skills@prd-reviewer` — "AI-driven requirements review meeting"; gatekeeper / fresh-eyes / independent stance; evidence-based critique (cite the specific problem + a fix); blocking verdict gates the next phase. Confirms the verdict-gates-downstream + actionable-finding shape.

(Both inspected via web summary, sanitized on read; low install counts; used only as method signal, never installed.)

## Web research — the review/judging method

Problem-evidence + review checklist + acceptance criteria:
- Perforce — How to Write a PRD (evidence-grounded problem; review rounds): https://www.perforce.com/blog/alm/how-write-product-requirements-document-prd
- aakashg — PRDs: A Modern Guide (concrete problem sizing; tie requirements to goals): https://www.news.aakashg.com/p/product-requirements-documents-prds
- Atlassian — Product requirements (goals, measurable metrics, in/out of scope): https://www.atlassian.com/agile/product-management/requirements
- altexsoft — Acceptance Criteria (independently testable; pass/fail; enables estimation): https://www.altexsoft.com/blog/acceptance-criteria-purposes-formats-and-best-practices/
- Atlassian — Acceptance Criteria (eliminate ambiguity; QA standard): https://www.atlassian.com/work-management/project-management/acceptance-criteria
- Product School — Acceptance Criteria in practice: https://productschool.com/blog/product-fundamentals/acceptance-criteria
- Given/When/Then acceptance criteria (testable, executable conditions): https://www.parallelhq.com/blog/given-when-then-acceptance-criteria

Metrics (measurable vs vanity):
- Reforge — PRD templates (measurable success criteria / KPIs vs vanity): https://www.reforge.com/blog/product-requirement-document-prd-templates

MVP boundary / non-goals / release criteria:
- airfocus — PRDo's and PRDon'ts (non-goals clarify what's out): https://airfocus.com/product-learn/prd-critical-communication-tool/
- Bolder Apps — MVP scope planning (defining what you will NOT build; non-goals as firewall): https://www.bolderapps.com/blog-posts/mvp-scope-planning
- propelius — PRD for your MVP (in/out of scope, release/definition-of-done): https://propelius.ai/blogs/how-to-write-product-requirements-document-prd-mvp/

Fabricated-evidence detection:
- Sourcely — Spotting AI hallucinated citations (verify before trusting): https://www.sourcely.net/resources/ai-hallucinated-citations-spot-fake-sources-before-submit
- Enago — ~1 in 5 AI references fabricated (scale of the problem): https://www.enago.com/responsible-ai-movement/resources/ai-generated-fake-references-scholarly-integrity

Actionable-finding phrasing + reviewer stance:
- HBR — Get Clearer, More Actionable Feedback (specific + concrete next step): https://hbr.org/2025/04/get-clearer-more-actionable-feedback
- Taylor & Francis — Giving and Responding to Feedback (reviewer guidelines; not pure gatekeeping): https://www.tandfonline.com/doi/full/10.1080/01924788.2024.2304948

## Verification + degraded-step notes

- **Fact-check pass:** run inline (no subagent-dispatch tool available in this environment) as a fresh adversarial review over the cited findings. Every method claim used in the body had ≥2 independent supporting sources; the bar itself is single-sourced from the dossier. PR-campaign (public-relations) metric results surfaced by one search query were out-of-domain and discarded — not used.
- **Degraded steps:** skill-discovery available (`find-skills` + ecosystem search ran); research available (`deep-research` skill invoked; supplemented with built-in WebSearch/WebFetch); reviewer-subagent dispatch unavailable → fact-check + self-review run inline by a fresh adversarial pass each cycle.
- External content (web + skill listings) sanitized on read; only paraphrased facts retained; no URLs/commands lifted into actions.
