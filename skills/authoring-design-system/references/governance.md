# Lifecycle & Governance (as documented policy)

Depth for the Lifecycle & governance method. The doc **documents the policy**; operationally running governance (staffing a team, running the backlog/cadence, tracking adoption metrics) is out of scope.

## Omit-below-threshold rule

**Fully omittable** when the system is single-maintainer AND single-consumer AND not a versioned external release (the thin internal archetype) — omit the whole section, not a gap. **Required** once there is >1 consumer or team, or a versioned external release. Above the threshold, document all of the below. No mandatory lightweight middle tier.

## Versioning

Semantic versioning adapted to the system: **MAJOR** for a breaking token/component change (rename/remove/retype/changed contract), **MINOR** for an additive token/component, **PATCH** for a backward-compatible fix. **Library-level** versioning (whole system versions together) is the simpler default; component-level is higher complexity.

## Changelog

Keep a Changelog: grouped by version, typed entries — **Added / Changed / Deprecated / Removed / Fixed** — capturing the noteworthy user-facing diff, not commit noise. Collect in an `[Unreleased]` section between releases.

## Deprecation & migration

Three phases: **warn** (mark `@deprecated`, announce what/why/impact + timeline), **wait** (a support window where old + new coexist), **remove** (drop at the next major). Every deprecation ships a **migration guide** (before/after) + a **codemod** where feasible. State a version support policy.

## Contribution model

Who can propose, the review process, and the criteria for entering the core system vs a team-level pattern library.

## Ownership / governance

Treat the system as a product: a named owner / core team, how decisions are made. Name the model; don't run it.

## Adoption / getting started

A getting-started / how-to-consume path so a new consumer can begin.

## Audience (owner decision)

The target audience(s) + their domain-literacy is an **owner decision**, recorded in the doc's Decisions — never an agent assumption driving the visual language. Surface an assumed audience as an Open Question for sign-off.
