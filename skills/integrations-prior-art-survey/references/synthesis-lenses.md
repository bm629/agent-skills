# The synthesis lenses

Eight lenses over the extracted records, producing `integration-register.yaml`. Each states its
formula AND the denominator it divides by, so the register is re-derivable rather than argued. A
thin run then yields a thin honest answer instead of a confident wrong one.

Every denominator comes from a RECORDED coverage cell — never assumed, never inferred from how
many records happen to exist. The draft's "appearing in 70%+ of similar products" was
unfalsifiable for exactly this reason: it named no denominator, so no run could contradict it.

| # | lens | the formula, and its denominator |
| --- | --- | --- |
| 1 | Table stakes | `presence_count / presence_denominator >= 0.6` **AND** `a3_directory_hits / a3_directories_reached >= 0.6`. TWO ratios, both recorded: the first over the six connector catalogs, the second over the comparable products' own `/integrations` directories that `a3` actually reached. Half a formula with one denominator declared is the same unfalsifiable claim in a shorter sentence. |
| 2 | Differentiators | Below the threshold on the `a3` ratio **AND** `presence_count >= 2`. The second clause is the listicle filter: two independent catalogs, not one blog post. |
| 3 | API-style convention | The distribution of `api_style` x `descriptor` over the records whose style was verified FIRST-PARTY. `conventions.api_style.denominator` IS that count, stated. A PARTITION — every extracted record carries exactly one `api_style` — so the distribution must sum to it, and the gate checks that. Phrase the verdict "k of n surveyed services in this domain expose REST with a published OpenAPI descriptor". |
| 4 | Auth convention | The distribution of the (`auth_scheme`, `oauth_flow`) PAIR, reported **against a base rate** — the same distribution measured over a connector catalog, carried in `conventions.auth.base_rate` with its source and its date. A domain figure without a base rate is unreadable: "mostly OAuth2" says nothing until you know what everything else looks like. The base rate is **not** a partition — it names the measured schemes and need not be exhaustive — which is why the sum rule applies to the domain distribution and not to it. |
| 5 | Event / webhook taxonomy | The union of event-type names across records with `emits_webhooks: true`, clustered by the **noun** each event acts on (`invoice.*`, `subscription.*`, `message.*`), plus the counts of `webhook_spec` and `webhook_signing`. `conventions.events.denominator` is the count of webhook-emitting records; the two count maps do NOT sum to it, because both fields are optional on a record and a service can emit webhooks and name neither. **An absent convention is a finding, not a blank.** |
| 6 | Complexity ranking | `score = auth_w + event_w + norm_w + sandbox_w`, published **with its components** so a reader can disagree with a weight rather than with the ranking. `auth_w` = 0 (`apiKey` / `http`) · 1 (`oauth2` + `clientCredentials`) · 2 (`oauth2` + `authorizationCode`) · 3 (`mutualTLS` / `openIdConnect` / per-tenant config). `event_w` = 0 (no webhooks) · 1 (signed, standard spec) · 2 (proprietary signing, or replay / ordering handling required). `norm_w` = 0 (a unified-API vendor already normalises it — `b4` evidence) · 1 (otherwise). `sandbox_w` = 0 (`sandbox: true`) · 1 (else). Range 0-7; **anything >= 4 gets its own milestone**. |
| 7 | Unavailable / gated | `pricing_model = quote-only` **OR** `compliance_gates != []` **OR** (`outcome: skipped` AND `cause` in {`no-public-api`, `access-gated`}), each with the SPECIFIC gate and its date in `gate_detail`. Include with a flag, never omit: a product team needs to know an enterprise-agreement-only integration exists even when it cannot ship in the MVP. Omitting it deletes the finding the team most needs. |
| 8 | Absence (MANDATORY) | Every zero-hit coverage cell, and every `not_run` / `vacated` angle with its cause. Phrased "no third-party service for X surfaced across the N angles that ran and the M terms searched, at their 2026-08 state" — **never** "no integration exists". Carries the named limits: the commercial catalog's paging bound, and the sources whose terms of service could not be verified. |

## Presence is counted FLAT, and the split is REPORTED

The six catalogs are counted flat — two commercial (Make, Zapier) and four developer-facing
(Pipedream, Nango, Activepieces, n8n) — and `presence_split` reports the two halves beside the
count. `presence_count` is a **corroboration count, ranking only, never a cut**.

*Rejected:* weighting the commercial catalogs against the developer-facing ones. A weighting scheme
is an unfalsifiable judgement the survey would then have to defend, and the raw `present_on`
membership list carries strictly more information than any weighted scalar. Reporting the split
lets a reader re-weight for their own purposes, and lets a service present only on the open-source
catalogs read as the different fact it is.

## `priority` is RE-DERIVED, not asserted

Lenses 1 and 2 are formulas, so the gate re-runs them: `blocked` where `availability` is anything
but `available` (a service nobody can obtain is not table stakes, whatever its ratios), then
`table-stakes` where both ratios clear 0.6, then `differentiator` where the `a3` ratio is below it
with two or more catalogs, then `future`. A `priority` the numbers do not yield is refused.

The register carries no `table_stakes[]` or `differentiators[]` list beside it. Two homes for one
fact inside one file is the drift a second machine file was rejected over.

## Every figure carries the record it came from

`evidence[]` is extract-record ids, and every fact on a register row is JOINED to that record by
the gate in both directions — a value that disagrees is refused, and so is a field the record
carries that the row left out. The register denormalizes the records deliberately, because the
register alone is the build-handoff index a downstream consumer reads; the join is what makes that
safe.

`--extracts` is therefore load-bearing. Without it the gate prints `SKIP extracts-crosscheck` and
exits 1 rather than passing quietly, and it does NOT report every citation as unresolvable — with
no records in hand, the author's artifact is not what needs repairing.

## The quality filter RANKS and never CUTS

Run inside extract, off the deep read. In real ecosystems the *most* table-stakes integrations are
frequently the *worst* by these signals: legacy enterprise systems with no descriptor, no sandbox,
no changelog and enterprise-agreement-only access are exactly the ones a product cannot ship
without. A quality filter that cut would systematically delete the integrations that matter most,
and the survey would confidently recommend a product nobody in the domain can adopt.

## `capability_tags` are checked against the project, and not by this validator

The synthesis child's FIRST deterministic check validates every `capability_tags` value against the
project's `capability-map.yaml`, before any tally. The portable validator structurally cannot see
the project's scope files, so this belongs to the owning ticket's QA — not to the gate, and not to
a reviewer reading prose.
