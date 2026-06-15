# Stateful-change safety & rollback levers (depth)

Depth for the SKILL.md Step-5 stateful-change + rollback method. Load when the release changes a schema/data or uses progressive delivery. Established SRE/operational practice; the roll-forward-as-default for live schema is widely advised but scenario-dependent (state the chosen path, don't dogmatically prescribe one).

## Expand-and-contract (parallel-change) migration

A schema/data migration is the forward change most likely to be *irreversible* — and the dominant rollback concern. Make a breaking change in backward-compatible steps so the running code works AND a rollback is clean at every point:

1. **Expand** — add the new schema element *alongside* the old (add a column/table; never drop or rename in place). Backward-compatible: old code still works.
2. **Migrate / transition** — deploy code that writes/reads the new structure; old and new coexist; backfill existing data if needed.
3. **Contract** — once nothing uses the old element, remove it in a *later, separate* release.

Each step is independently deployable and **independently rollbackable** — the property that makes a clean rollback possible. This **decouples the schema migration from the code deploy**: the DB and the app can sit at different release stages without a synchronized cut-over. **Backward-compatible-first** is the rule — any change touching schema the production app already uses must be backward-compatible so a rollback never loses data.

A runbook that ships a breaking schema change in one big-bang step has, by construction, no clean rollback. Either sequence the expand/migrate/contract phases across releases (each phase its own runbook run with its own rollback) or call the change irreversible and carry the roll-forward path below.

## Roll-forward vs rollback (the irreversible-change decision)

Not every forward change can be cleanly reverted:

- A `DROP TABLE`/`DROP COLUMN` or a destructive transform cannot be un-done by a down-migration — the data is gone; recovery needs a **restore from backup**.
- A committed data mutation, or a rollback after new transactions have landed, can itself cause data loss.

So the rollback section makes an explicit decision per forward change:

- **Rollback** (revert to the prior state) — the default for reversible/backward-compatible changes; fast, but risks data loss if the change wasn't backward-compatible.
- **Roll-forward / fix-forward** — keep the deploy active and ship a correction or disable the feature (often via a flag). The general recommendation for *live schema* changes; it also preserves the deploy audit trail. (Prefer rollback when the change left the DB in a dangerous state.)
- **Containment / compensating transactions + restore-from-backup** — when a data mutation is irreversible, contain it and compensate rather than naively rolling back.

The runbook must *state* the chosen recovery path per irreversible change (the reviewer's cond-10 checks that a recovery path exists, not which one).

## Measurable triggers — SLO error-budget burn-rate

A raw "error rate > 0.5%" threshold fires late/noisily. The Google-SRE-standard basis is the **error-budget burn rate** — how fast you consume the monthly budget relative to steady state:

- **Multi-window, multi-burn-rate**: a long window detects a sustained problem; a short window confirms it is current.
- Reference tiers (a *reference*, not a runbook demand): page at burn-rate > 14.4 over 1h; ticket at > 6 over 6h; review at > 1 over 3 days.

A verification check or a rollback trigger may be expressed as a burn-rate OR a raw threshold — the bar is *measurable*, not *which metric*. "Feels fine"/"looks healthy" fails.

## Rollback levers — progressive delivery & feature flags

- **Canary analysis + automated rollback.** A canary serves a small % of traffic, bakes on metrics, and ramps; impact is proportional to exposed traffic. Automated rollback on SLO deviation is standard at scale.
- **Decouple DEPLOY from RELEASE (feature flags / dark launch).** A flag enables/disables a feature at runtime; a dark launch deploys hidden behind an off flag. The flag is also a **near-instant, localized rollback lever** — flip it off, faster and lower-blast-radius than a redeploy.

When the system uses flags, a legitimate rollback path is "flip flag X off" rather than a redeploy. The canary/flag *mechanics* are aids — the bar is a complete, measurable-triggered rollback (cond-4), however realized.

## Proportionality

A stateless deploy or a purely additive/backward-compatible single migration does not exercise this depth — no expand/contract phasing, no roll-forward decision, no canary/flag. That is correct sizing, not a gap.

## Sources

- Expand-and-contract / parallel-change / backward-compatible migration: Pete Hodgson "expand/contract: making a breaking change without a big bang" (blog.thepete.net); Tim Wellhausen "Expand and Contract" (tim-wellhausen.de); PlanetScale "backward-compatible database changes".
- Roll-forward vs rollback / irreversible migration: Redgate Flyway "roll back or fix forward"; Hokstad "rollback vs rollforward"; SQLServerCentral "rollback vs roll forward".
- SLO burn-rate / canary / automated rollback: Google SRE workbook "Alerting on SLOs" + "Canarying Releases"; OneUptime "burn-rate alerts".
- Decouple deploy from release / feature flags / dark launch: LaunchDarkly "why decouple deployments from releases"; Unleash "progressive delivery with feature flags"; AB Tasty "dark launch".
</content>
