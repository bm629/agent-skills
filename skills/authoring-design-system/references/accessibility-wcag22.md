# Accessibility — WCAG 2.2 AA (numeric)

Depth for the Accessibility method. State **WCAG 2.2 Level AA** as the target and make every threshold a number. Bake a11y into the token specs (contrast, focus) and every component's accessibility part — not a later pass.

## Contrast (SC 1.4.3 / 1.4.11)

- Normal text ≥ **4.5:1** against its background.
- Large text (≥24px, or ≥18.66px bold) ≥ **3:1**.
- Non-text / UI components + graphical objects (icons, input borders, focus, chart keys) ≥ **3:1**.
- Record a contrast ratio for **every** text + UI color pairing in the token set.

## Focus (visible + not-obscured = AA; Focus Appearance = AAA)

- **AA baseline:** every interactive element has a **visible** focus indicator (SC 2.4.7 Focus Visible, AA) that is **not obscured** by author content (sticky headers/footers, modals) when focused (SC 2.4.11 Focus Not Obscured (Minimum), AA).
- **House rule (adopts the AAA bar):** the indicator is at least **2 CSS px** thick (or equivalent area) and ≥ **3:1** contrast against the element's unfocused state **and** adjacent colors. This numeric bar is **SC 2.4.13 Focus Appearance, which is AAA** — adopted here as a stronger-than-AA house rule, not an AA requirement.

Define a `color.focus.ring` token meeting this; spec focus per interactive component.

## Target size (SC 2.5.8)

Interactive targets ≥ **24×24 CSS px**, OR meet the **spacing exception** (a smaller target with enough surrounding gap that a 24px circle doesn't overlap the next). (AAA 2.5.5 is the stricter 44px; AA is 24px.)

## Keyboard (SC 2.1.x)

Every interactive element operable by keyboard alone; logical tab order; no keyboard trap; documented shortcuts. Per-component keyboard model (Tab/Shift-Tab/Enter/Space/Arrow/Esc as applicable) in its accessibility part.

## Reduced motion (SC 2.3.3)

Honor `prefers-reduced-motion`; provide a reduced/none alternative for non-essential motion; no content flashing >3×/sec.

## Color independence (SC 1.4.1)

Information conveyed by color also has a non-color cue (icon, text, pattern). Error = red **and** an icon/label.

## Semantics & screen-reader support

Correct roles/semantics (native elements first; ARIA only to fill gaps), accessible names for all controls, dynamic-state conveyance (`aria-expanded`, `aria-invalid`, live regions for async). System-level landmark/heading structure.

## Per-component a11y part

Each component spec states: role + accessible name + keyboard model + focus + contrast + state conveyance. An unlabeled control or a custom widget with no keyboard/ARIA model is a gap.
