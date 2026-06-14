# Archetype overlays + amend procedure — `authoring-prd`

Depth for Step 2 (name the archetype) and Step 6 (amend an existing PRD). The body carries the method; this file carries the per-archetype emphasis and the full amend procedure.

## Archetype overlays (key the section emphasis to the product type — proportional, not additive bloat)

The PRD's emphasis shifts by archetype, like sizing an MVP boundary. The bar ADAPTS — it does not bolt every overlay onto every PRD. These are authoring aids; the reviewer judges archetype-appropriate completeness, never the presence of a named section.

| Archetype | Emphasize |
|---|---|
| Consumer | funnel/engagement/retention metrics, onboarding, virality; HEART/AARRR fit. |
| B2B / enterprise | roles & permissions, admin, SLAs, security/compliance, multi-tenant, audit. |
| Internal tool | lighter; the specific team's workflow + job; efficiency metrics, not growth. May legitimately omit Market, GTM, heavy NFRs. |
| Platform / API | the contract surface, versioning, rate-limits, backward-compat, governance/auditability (defers wire detail to an api-spec). |
| Data / ML | business problem + data understanding (sources, labels, feedback loop), offline + online eval metrics, **guardrail metrics**, and a drift/monitoring + retraining plan (data drift vs concept drift). Data considerations belong in the PRD because they shape product design + feedback. |
| Regulated | compliance, auditability, data lineage, validation; heavier PRDs are legitimate here. |

## GTM / launch / support / analytics readiness

Prompt for these *by archetype* (a consumer launch needs GTM; an internal tool usually doesn't). They are proportional authoring aids — NOT a universal required section. Do not add a GTM section to a PRD whose archetype doesn't need one.

## Amend procedure (Step 6 — editing an existing PRD as a versioned delta)

A PRD is a living document; the most common real operation is a delta on an approved PRD, not a first draft. The scope unit of a PRD change is a requirement / goal / success-metric / feature / scope-boundary line.

1. **Scope the change.** State what this amendment touches and what is deliberately untouched, so a reviewer can bound the review to the delta.
2. **Edit in place, don't rewrite.** Change only the affected lines. Do NOT regenerate the whole PRD — regeneration destroys change provenance and risks silent drift on untouched sections.
3. **Version + changelog.** Bump the PRD's own doc version; add a change-history entry answering who / when / **what changed / why** (and who requested it). This must be answerable from the doc, not reconstructed.
4. **Mark superseded content.** Outdated requirements/metrics are explicitly marked superseded (with the reason), not silently deleted — downstream readers see the decision, not a hole.
5. **Analyze ripple (blast radius).** When a requirement/goal/metric/feature changes, trace its downstream impact: which acceptance criteria, which metrics, which other requirements, and which downstream docs (feature-spec, technical-design) are now stale. Surface the affected set (or "no downstream impact" with reason) — a change that silently breaks a traceability link (drops a feature but leaves its metric/AC dangling) is a defect.

The skill owns the amend METHOD + the delta. Deciding to amend, choosing which PRD to feed in, and propagating downstream are the surrounding flow's job — the skill assumes the existing PRD + the change request are handed in.

## Sources (portable)

Archetype overlays — Productboard (PRD-vs-spec, technical PRDs), ChatPRD (doc types); ML-product PRD — Derck (RE in MLOps), Clemens Mewald (data as a key ML requirement), EvidentlyAI + Datadog + Aerospike (model monitoring, data vs concept drift), AWS ML Lens; regulated/API — Salt, MuleSoft, Speakeasy, Treblle API governance. Amend/versioning — Cagan/SVPG (living doc), Productboard + Jama + Perforce (change history who/when/what), Omniflow (PRD versioning with diffs), Wikipedia living-document. Triangulated ≥3 sources for the ML + amend claims.
