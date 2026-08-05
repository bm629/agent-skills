---
schema_version: 1
meta:
  item_id: acme-design-system
  as_of: '2026-08-05'
  revision: 1
outcome: extracted
convention:
  id: acme-design-system
  id_class: design-system
  name: ACME Design System
  corpus:
    name: ACME Design System documentation
    version: '4.2'
    url: https://design.acme.example/tokens
    retrieved_at: '2026-08-05'
  authority: published-system
  prescriptivity: descriptive
  statement: >
    The system publishes a governed token set covering colour, spacing and type scale.
  governs: the system's colour, spacing and type primitives
  applicability:
    applies: true
    basis: ui.has_ui is true and the project needs a token foundation
  tokens_in_body: true
---

## Statement

ACME publishes a governed DTCG token set.

## Evidence

From the ACME token reference (4.2): the palette is published as DTCG with `color.*` groups.

## Applicability

Applies; the project needs a token foundation.

```dtcg
{
  "brand-primary": { "$type": "color", "$value": "#0055ff" },
  "gap-small": { "$type": "dimension", "$value": "4px" }
}
```
