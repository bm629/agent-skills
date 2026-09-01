# Writing the platform-and-mechanism vocabulary map

The map is a **search protocol**, not a glossary. It records what you will look for, where, and
how — before you look — so a reader can re-run the PROTOCOL and see exactly what changed — not get the same corpus, which channel death makes impossible.

## It mints the platform slugs, once

The record id downstream is `<platform_slug>__<angle_id>`. If two angles each invent a slug for
the same platform, they produce two rows for one platform and the dedupe never fires. **The map is
the only place a slug is minted**; every angle adopts them verbatim. Lowercase kebab-case.

## Every angle gets a verdict, including the ones that do not apply

An angle that never ran and an angle that ran and found nothing are different facts, and only a
recorded verdict distinguishes them — before the search wave starts. A missing verdict hides an
unexamined angle; a wrong positive runs an angle the scope ruled out. Both directions are
checked, so write all seven.

## `why_comparable` is not decoration

A slug with no stated comparability is a platform someone recognised, not one they justified. The
downstream reader is deciding whether this evidence applies to their product; give them the reason.

## Worked example

```yaml
schema_version: 1
meta:
  retrieved_at: "2026-09-01"
  revision: 1
platforms:
  - slug: vscode
    name: Visual Studio Code
    platform_type: dev-platform
    why_comparable: >
      The reference implementation of a declarative contribution model, and the scope's own
      extension surface is declarative.
mechanisms:
  - term: contribution point
    kind: declarative-contract
    expansions: [extension point, manifest contribution]
angle_applicability:
  - angle_id: a1
    precondition: "always applicable"
    holds: true
    reason: "Always-on."
  - angle_id: a2
    precondition: "always applicable"
    holds: true
    reason: "Always-on."
  - angle_id: a3
    precondition: "always applicable"
    holds: true
    reason: "Always-on."
  - angle_id: a4
    precondition: "always applicable"
    holds: true
    reason: "Always-on."
  - angle_id: b1
    precondition: "platform.type in {app-store, dev-platform}"
    holds: true
    reason: "The scope is a dev-platform."
  - angle_id: b2
    precondition: "platform.type in {marketplace, app-store, payments-network} OR regulatory.applies"
    holds: false
    reason: "Not in the set, and regulatory.applies is false."
  - angle_id: b3
    precondition: "platform.type in {marketplace, app-store, dev-platform}"
    holds: true
    reason: "The scope is a dev-platform."
scope_guard:
  excluded:
    - item: Stripe Connect
      reason: A payments-network; its commercial model answers none of the scope's questions.
sources: [vscode-api]
```
