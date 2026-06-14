# Execution readiness + amend — depth

Loaded on demand. The body's Step 6 + Step 8 carry the method; this file carries the detail. Provenance: `sources.md`.

## Test-data management

Each level names where it runs AND the data it needs + how that data is provisioned/reset + how sensitive data is handled. Choose deliberately:

- **Synthetic data** — manufactured, statistically realistic, zero re-identification risk. The default for the bulk: unit/integration/CI runs and edge-case construction. You control the shape exactly.
- **Masked production data** — de-identified real data preserving scale, realism, and referential integrity. For the cases where realism is non-negotiable: regression, UAT, production-bug reproduction. PII/PHI fields are masked or replaced; never raw production PII in a test environment.
- **Hybrid (common production strategy)** — synthetic for the ~80% (privacy/speed/edge coverage), masked-production for the ~20% where realism is essential.
- **Fixture lifecycle** — how each fixture/seeded account is provisioned before a run and reset/torn down after, so runs are repeatable and isolated.
- **Data-driven testing** — where one case runs over a data table (named inputs → expected outputs); note the table or its source so the case stays traceable.

Bar: each level's environment + data + provisioning/reset + sensitive-data handling is stated. A case assuming fixtures the plan never specifies is a gap.

## Defect severity vs priority + the exit tie

Defects are classified on **two independent axes**:

- **Severity** — the technical impact (Critical / High / Medium / Low): how badly it breaks the system.
- **Priority** — the business urgency to fix (Critical / High / Medium / Low): how soon it must be addressed.

They are independent (a typo on the landing page = low severity, possibly high priority; a crash in an unused admin corner = high severity, low priority). **Triage** assigns both, maps the defect back to the failing case + its upstream behavior, and decides whether it blocks release.

The link to the plan: the **exit criteria tie to an open-defect threshold** — e.g. "no open Critical/High defect" — so "done" is mechanically decidable. Without it, "testing complete" is unverifiable.

## Amend — the versioned-delta procedure (Step 8 detail)

A test plan is a living document. It amends on TWO triggers: (a) an **upstream change** (a feature-spec/api-spec behavior added/changed/removed) and (b) a **discovered defect** (which earns a regression case). Procedure:

1. **Scope the change.** Identify the smallest unit touched — a coverage-map row, a case, a level/type, an entry/exit criterion, a non-functional approach.
2. **Edit, don't redraw.** Amend the affected rows/cases in place. A full regeneration masquerading as an amend loses the audit trail.
3. **Re-trace the coverage map.** A changed/added behavior re-maps its row(s); a **removed** behavior retires its case(s). Coverage integrity holds — no behavior left without a case, no orphan case left behind.
4. **Select the regression set by impact + risk.** Run change-impact analysis to pick the *existing* cases that must re-run because they touch the changed area:
   - **Impact-based** — the cases covering the modified behavior + the modules/areas that depend on it (e.g. an auth change → the payment + profile cases that depend on auth).
   - **Risk/priority-based** — prefer the high-risk, high-business-value, and historically-flaky cases.
   - **Hybrid (default)** — impact-based to scope, risk-based to order/trim.
   The selection is justified (why these, not all, not none).
5. **Defect → regression case.** A discovered defect earns ≥1 new regression case traced to the behavior it broke, so it cannot silently recur.
6. **Version + changelog.** Bump the plan's **own** version + a changelog row (who/when/what/why); **mark superseded/retired cases** (don't silently delete — the audit trail matters for a verification artifact).

On iteration the flow hands the existing plan + the change request in — no input-mechanism change. The reviewer reviews the delta **delta-scoped** (only what it touched + coverage/trace integrity + the regression selection), not a full re-review of the unchanged plan.
