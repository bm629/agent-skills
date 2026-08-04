# Absent-input policy

**Proceed on what you have, and record what you assumed — never fabricate, and never stop.**

## Why inference rather than a default or a halt

**Halting** turns a survey into a support ticket; most missing inputs are recoverable from
signals already present.

**A silent default** is the dangerous one. If an absent conformance level quietly becomes AA, a
later reader cannot tell an inferred value from a stated one, and every conclusion resting on it
inherits a confidence nobody granted.

**A recorded inference** keeps the run moving and the seam visible: the value is used, and used
*as an assumption*, with the signal it came from, where a reviewer can challenge it.

## The record

```yaml
assumptions:
  - input: ui.accessibility.required_level
    assumed: AA
    inferred_from: >
      No level was declared. The downstream design-system consumer requires WCAG 2.2 AA
      unconditionally, so AA is the floor this survey must cover regardless.
```

Three fields, all required. `inferred_from` names a **signal**, not a rationale. One hop only —
an inferred level does not license a further inference built on it.

## Per-input fallbacks

| Missing | Do this | Never |
| --- | --- | --- |
| Conformance level | Default to AA and record it; the downstream consumer requires AA regardless | Skip the accessibility angle |
| Platform context | Derive from the archetype; if none, declare the type absent | Assume a platform |
| Design systems to walk | Select by archetype and audience fit, and record the selection basis | Guess a system the scope never implies |
| Component list | Derive from the screen archetypes the scope names | Enumerate a general widget catalog |
| An angle's precondition input | Treat the disjunct as false — absent means not-in-set | Assume it holds |

The conformance-level row is the one that differs from a naive reading: absent does **not** mean
skip. The default exists because the consumer's own bar is unconditional, so a survey that
skipped accessibility on silence would hand its consumer an unmeetable requirement.

## When there is no capability map at all

The registry's preconditions are written in capability-map paths, and the map guide asks each
angle verdict to be grounded in that map's actual values — but a caller may hand you prose
instead. That is not a blocker: ground each verdict in what the prose actually says, quote the
phrase you relied on, and record in `meta.note` that the scope arrived as prose. A verdict
grounded in a quoted sentence is checkable; one grounded in an imagined field value is not.

## Absent inputs versus empty results

These look alike downstream and are not:

- **Absent input** — never given. Goes in `assumptions`.
- **Declared-absent group type** — genuinely has no members. Goes in `scope_guard.absent_types`
  with a reason. Neither present nor declared is a silent omission, and it empties every angle
  depending on it.
- **Empty result** — you searched and found nothing. A zero-hit coverage cell, and a *finding*,
  recorded with the query that produced it.
- **Unreachable source** — you could not search. A typed cell failure with a cause.
- **Forbidden source** — you chose not to fetch. A decision, not an outage.

Collapsing any into any other is the failure this survey is built to prevent.

## When there is genuinely not enough

If the scope is too thin to produce a map — no components, no screen archetypes, nothing to
derive a platform from — say so in `meta` and produce what you can rather than padding. A
thin-but-honest map is correct output for a thin scope, and a reviewer must not revise it for
thinness alone.
