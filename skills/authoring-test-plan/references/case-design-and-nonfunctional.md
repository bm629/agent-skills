# Case design + non-functional testing — depth

Loaded on demand. The body's Step 5 + Step 6 carry the method; this file carries the technique detail. Provenance: `sources.md`.

## Case-design techniques (authoring aids — pick the one that fits the behavior)

Use these to choose *representative* cases for a high-risk behavior without the input-permutation cross-product. The reviewer judges the OUTCOME (risk-weighted depth, no blow-up, no thin high-risk area), never the literal technique.

- **Boundary value analysis (BVA).** Test at and around each boundary: min, min−1, max, max+1, and just-inside/just-outside. Most defects cluster at boundaries.
- **Equivalence partitioning (EP).** Split inputs into classes that the system treats the same; one representative per class (plus one invalid-class representative). Pairs with BVA (boundaries of each partition).
- **Decision tables.** For a behavior whose action depends on a *combination* of conditions: enumerate the condition combinations × the resulting action. Exposes missing or contradictory rules; collapse don't-care cells. Use for authz matrices, pricing rules, eligibility logic.
- **State-transition testing.** For stateful behavior: cover every legal transition (state × event → next-state) and probe representative illegal ones. Pairs with the feature-spec's state-transition table. Cover the initial and terminal states.
- **Pairwise / combinatorial selection.** When many parameters interact, cover all *pairs* of values (a handful of cases) instead of 2^N. Most interaction defects involve only two parameters. Use a pairwise generator; add the high-risk individual values explicitly.
- **Negative testing.** For each behavior, the invalid-input path with the *exact* expected error/message — not just "it errors".

## Exploratory / session-based testing (SBTM) — a complement, never a replacement

Where scripted cases are not cost-effective (new functionality, UX/usability risk, edge exploration), add **chartered, time-boxed** sessions:

- **Charter** — a one-line mission + the area(s) in scope (e.g. "explore the checkout flow for state/back-button defects").
- **Time box** — typically 60–90 minutes.
- **Session report** — what was tested, what was found, what was NOT covered.

Scripted/automated coverage handles known scenarios + regression; exploratory investigates the unknown. A plan with strong scripted coverage and no exploratory tier is fine — the reviewer never demands one.

## ML / probabilistic case design (the test-oracle problem)

An ML/probabilistic system has **no fixed expected output** to compare against — a deterministic pass/fail "expected result" mis-fits it. Use:

- **Metric-threshold validation.** Accept on a measurable metric ≥ a threshold on a **named dataset/version**: precision/recall/F1/accuracy/AUC, and latency. The case's preconditions name the dataset; the expected result is the metric gate. Example: "Pre: dataset `rec-eval-v2`. Expected: precision@10 ≥ 0.85 AND p95 latency ≤ 120ms."
- **Metamorphic relations.** Assert an input-change → expected output-change that must hold without a fixed oracle (e.g. paraphrasing the query preserves the top result; scaling all prices preserves the ranking). A pseudo-oracle for non-testable functions.
- **Drift.** Where the model degrades as the world changes, add an ongoing data/model-drift check (a metric tracked against a baseline over time).
- **Fairness / bias.** Where warranted, metric parity across protected segments (e.g. false-positive-rate gap ≤ X across groups).

"The model is accurate" / "results are relevant" is the un-runnable criterion the executable-case bar already rejects — name the metric, the threshold, and the dataset.

## Non-functional testing taxonomy (per warranted type: approach + numeric/standard target)

Proportional — include only the types an NFR or the archetype warrants; omit a type with a one-line note when none does (never invent a target).

| Type | Approach | Numeric / standard target |
|---|---|---|
| Performance (load / stress / soak) | a load profile (concurrent users / request-rate / duration) + the tool (e.g. k6, Locust, JMeter) | p95/p99 latency ≤ X ms; throughput ≥ Y rps; error-rate ≤ Z% under load; soak = no leak over N hours |
| Security | a threat-derived set: authn/authz, input validation, injection, sensitive-data handling (OWASP-class for the surface) | the threat checklist passes; no High/Critical finding |
| Accessibility | automated scan + manual + assistive-tech checks | **WCAG 2.2 AA** — contrast, focus appearance, target size, keyboard operability |
| Usability | task-success / SUS where the archetype warrants | task-completion rate ≥ target; SUS ≥ target |
| Compatibility | a browser / device / OS support matrix | the named matrix passes |
| i18n / l10n | locale, RTL, pluralization, encoding cases | the supported-locale set passes |

Derive the targets from the handed-in NFRs/architecture-doc; where an NFR is absent, omit-with-a-note rather than fabricate. A warranted type present with no approach/target is a gap.
