---
schema_version: 1
meta:
  item_id: aria-apg-disclosure
  as_of: '2026-08-05'
  revision: 1
outcome: extracted
convention:
  id: aria-apg-disclosure
  id_class: aria-pattern
  name: Disclosure (Show/Hide)
  corpus:
    name: WAI-ARIA Authoring Practices Guide
    version: '2026-04'
    url: https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/
    retrieved_at: '2026-08-05'
  authority: normative-standard
  prescriptivity: normative
  statement: >
    A disclosure is a button that controls the visibility of a section of content. The
    button carries aria-expanded reflecting the section's state, and aria-controls
    referencing the element whose visibility it toggles.
  governs: collapsible section headers and their toggle controls
  applicability:
    applies: true
    basis: ui.has_ui is true and the archetype ships progressive-disclosure sections
  tokens_in_body: false
notes:
  - The APG's keyboard interaction table also covers Enter and Space; carried in the body.
---

## Statement

A disclosure is a button controlling the visibility of a content section. `aria-expanded`
reflects state on the button itself, and `aria-controls` references the toggled element.

## Evidence

The APG page describes the disclosure pattern and is widely used across design systems.

## Applicability

Applies. The project's archetype ships collapsible sections, so the pattern binds directly to
its disclosure controls.
