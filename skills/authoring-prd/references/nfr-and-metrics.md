# NFR taxonomy + metric frameworks — `authoring-prd`

Depth for the Requirements (NFR) and Goals & Success Metrics sections. The SKILL.md body carries the method; this file carries the category set, the numeric bars, and the framework details. All targets are proportional to the product archetype (see `archetype-and-amend.md`) — a deliberately best-effort NFR may say so; don't bolt every category onto a thin PRD.

## Non-functional requirement taxonomy (each load-bearing category gets a numeric/checkable target)

Aligned to ISO/IEC 25010 quality characteristics.

| Category | What it bounds | Example numeric target |
|---|---|---|
| Performance | latency, throughput | web p95 ~1s / p99 ~2.5s; API p95 < 500ms (B2B SaaS), < 100ms high-frequency. Design for p95, protect p99. |
| Availability / reliability | uptime, error budget | an SLO: "99.9% of requests served within 300ms over a rolling 30-day window" (99.9% ≈ 43.8 min/month downtime). |
| Security | authn/authz, data protection | per-role permissions; data encrypted at rest + in transit; session timeout stated. |
| Privacy / data-handling | PII, retention, regional law | PII fields classified; retention period; GDPR/regional handling where personal data is processed. |
| Accessibility | inclusive use | WCAG 2.2 AA floor; testable, e.g. "screen-reader happy-path success ≥ 95%". |
| Scalability | growth headroom | "sustains 10× current load with < 20% p95 degradation". |
| Maintainability | change cost | stated where the system is long-lived (e.g. module/test coverage expectations). |
| Compatibility / portability | environments | supported browsers/OS/devices/versions. |
| Localization / i18n | locale reach | locales supported; RTL where relevant. |
| Compliance | regulatory bar | the specific standard (SOC2/HIPAA/PCI/etc.) where the archetype requires it. |

Rule of thumb: NFRs missed early cause expensive rewrites — name the archetype-applicable categories at PRD time, each with a target. "Should be fast/secure" is not a requirement.

## Success-metric frameworks (aids to pick the right few — not a deliverable)

- **North Star Metric (NSM)** — the single metric capturing the core value delivered; pair with a small set of input levers + guardrails.
- **OKRs** — Objective + Key Results; cascade the NSM into team-level measurable KRs.
- **HEART** (Google) — Happiness, Engagement, Adoption, Retention, Task-success — UX-centric products.
- **AARRR** (pirate metrics) — Acquisition → Activation → Retention → Revenue → Referral — funnel/growth products.

Pick the framework that fits the archetype; the OUTCOME (a few measurable metrics, each with target + method) is the bar, not the use of a named framework.

## Leading vs lagging + guardrail/counter-metrics

- **Lagging** (outcome) metrics show up late: revenue, retention. **Leading** (input) metrics give early signal: activation events. Pair them so progress is steerable.
- **Guardrail / counter-metrics** are secondary metrics that must NOT degrade while chasing the headline metric — they prevent gaming and unintended harm. Example: a chat app's North Star "messages sent" guarded by "% messages reported spam/harmful ≤ X". Name a guardrail wherever the headline metric is gameable or could harm another stated goal.
- **Anti-patterns:** vanity metrics (impressions, raw signups untied to value); the unprioritized metric-dump (ten KPIs, no priority). A few that matter beats many.

## Sources (portable)

ISO/IEC 25010 NFR taxonomies (forasoft 2026 playbook, DOOR3, altexsoft, BrowserStack); NFR numeric bars (radview, SLO-first latency budgets, oneuptime p50/p95/p99); WCAG 2.2 AA; metric frameworks (Google HEART; North Star / OKR / AARRR comparisons — hyperact, Product School); guardrail/counter-metrics (Mixpanel, Eppo, intrico); leading-vs-lagging + input metrics (towardsai, agileinsider). Triangulated ≥3 sources per load-bearing claim.
