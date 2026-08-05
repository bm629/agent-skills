---
schema_version: 1
meta:
  item_id: frontend-weekly-tabs-post
  as_of: '2026-08-05'
  revision: 1
outcome: extracted
convention:
  id: frontend-weekly-tabs-post
  id_class: aria-pattern
  name: Accessible Tabs — the definitive guide
  corpus:
    name: Frontend Weekly (blog series)
    version: '2026-03 issue 214'
    url: https://frontendweekly.example/issues/214/accessible-tabs
    retrieved_at: '2026-08-05'
  authority: normative-standard
  prescriptivity: normative
  statement: >
    A tab list must place roving tabindex on the selected tab and move focus with the arrow
    keys, and every tab panel must be labelled by its tab.
  governs: tab lists and their panels
  applicability:
    applies: true
    basis: ui.has_ui is true and the archetype ships a tabbed settings surface
  tokens_in_body: false
---

## Statement

A tab list uses roving tabindex; arrow keys move focus; each panel is labelled by its tab.

## Evidence

From Frontend Weekly issue 214: "the pattern everyone should follow is roving tabindex — set
tabindex="0" on the selected tab and tabindex="-1" on the rest, then handle ArrowLeft and
ArrowRight yourself."

## Applicability

Applies. The settings surface ships a tab list.
