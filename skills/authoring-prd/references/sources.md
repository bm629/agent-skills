# Sources — `authoring-prd`

Research provenance for the method + quality bar in `SKILL.md`. Synthesized 2026-06-04 from a deep-research pass; external content passed through a content sanitizer (clean) before synthesis. All claims paraphrased.

## Primary research

A consolidated PRD-authorship research pass corroborated the per-section method and the plannability quality bar across 10+ reputable product-management references (≥2 independent sources per claim):

- Product School — "The Only PRD Template You Need (with Example)"
- Reforge — "Product Requirements Document … [with templates]"
- Atlassian — PRD guidance
- Pendo, airfocus, monday.com, altexsoft — PRD template guides
- Perforce, Leanware, Aakash Gupta ("Modern Guide"), Pharos, ClimbTheLadder — how-to-write guides
- Methodologies referenced: Lean PRD, Amazon PR/FAQ, agile feature specs

## Corroborated claims (used in the body)

- A PRD's canonical sections (overview, problem, goals + metrics, users/personas, scope/MVP, requirements, user stories + acceptance, assumptions/constraints, risks, open questions) — multiple sources; the structure itself is owned by the template tool, not this skill.
- Success metrics: 2–4 measurable outcomes, each with a target + measurement method/instrumentation, defined before building — Product School, Reforge, Leanware.
- MVP/scope: distinguish must-have-for-launch vs later + explicit exclusions/non-goals + release criteria to prevent scope creep — multiple sources.
- Problem must be evidenced, not asserted; jargon-free language for a cross-functional audience; eng+design feasibility review + stakeholder sign-off — Perforce, Leanware, Pharos.
- "Plannable" bar (features + acceptance criteria concrete enough to derive milestones) — synthesized from the requirements + acceptance-criteria guidance across sources.

## 2026-06-14 production-grade restructure (v1.2.0) — new angles

The restructure added eight angles + an amend method, grounded in a fresh deep-research pass (≥2 independent sources per claim; sanitized before synthesis). Depth lives in two companion references:

- `nfr-and-metrics.md` — NFR category taxonomy + numeric bars (ISO/IEC 25010; forasoft/DOOR3/altexsoft/BrowserStack; SLO/p95 latency budgets; WCAG 2.2 AA) and metric frameworks + guardrail/counter-metrics (Google HEART; North Star/OKR/AARRR; Mixpanel/Eppo guardrails).
- `archetype-and-amend.md` — per-archetype overlays (Productboard, ChatPRD; ML-PRD: EvidentlyAI/Datadog/AWS ML Lens; regulated/API: Salt/MuleSoft/Speakeasy) and the amend/versioning method (Cagan living-doc; Productboard/Jama/Perforce change history; Omniflow versioning).
- Traceability (problem→goal→metric→feature→AC) — RTM guides (smartgecko, projectmanager, abstracta, stell-engineering, agile-light traceability).
- JTBD problem framing + opportunity sizing — Christensen/HBS, Strategyn, thrv; AI-fabrication detection — psypost (~40%), NeurIPS-2025 fabricated-citation taxonomy (~66% wholesale).

## Note

The same research underpins the companion `reviewing-prd` skill (a 12-condition bar), so the author's quality bar and the reviewer's quality bar stay single-sourced and aligned.
