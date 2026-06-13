# Amending a user-flows document — depth

> Loaded for Workflow Step 11. The first build is greenfield; every change after is an
> **edit**. Treat the user-flows doc like versioned source code: scope the change, edit
> in place, version + changelog, review only the delta. Never regenerate — a careless
> re-draw corrupts the cross-flow graph and the screens index nobody asked you to touch.
> Scope unit = a **flow / branch / path**. "Regression" = a hand-off pointing at a
> renamed/removed flow, a removed screen still in the index, a previously-reachable path
> newly stranded, or a diagram⇄narrative drift introduced by the edit.

## The amend procedure

### 1. Scope the change & analyze the ripple

Identify exactly which flow(s)/branch(es)/path(s) the change touches, then trace the
**ripple** — the change's true scope is the edited flow PLUS:

- every **cross-flow transition** that hands off *to* a changed/removed flow;
- every screen in the **screens index** referenced by an edited/removed path;
- every **branch** whose target moved.

The blast radius of a flow change shows up at the **seams** (cross-flow transitions +
the screens index) — that is where to look, not the whole document.

### 2. Edit, don't redraw

Apply the **minimal in-place edit** to the affected flow/branch. Untouched flows — their
diagrams, narratives, branch lists, and screens-index rows — stay **byte-for-byte
unchanged**. No gratuitous re-numbering, re-drawing, or re-wording of flows the change
didn't touch. Preserve stable screen names (a rename is itself a scoped change with its
own ripple — propagate it to all four places: diagram, narrative, per-flow list, index).

### 3. Version the document + changelog

Bump the **document's own** version by change class:

- **MAJOR** — a removed or renamed flow, or a removed previously-reachable path (breaks
  the downstream wireframe contract / cross-flow integrity).
- **MINOR** — an added flow / branch / path / entry-point.
- **PATCH** — a wording / notation / diagram fix with no path change.

Add a **Keep-a-Changelog** entry (Added / Changed / Deprecated / Removed / Fixed) at the
**flow/path grain** — no silent change, no MAJOR dressed as a PATCH.

### 4. Deprecate / remove safely

Don't yank a flow/path out from under its consumers. **Deprecate first** (mark the
flow/path + name its replacement) in a MINOR, then **remove** in the next MAJOR. When a
screen leaves with a removed path, confirm **no remaining path references it** and prune
it from the screens index. A removed entry-point or cross-flow hand-off is **announced**
(changelog + deprecation), not silently dropped.

## What the delta review checks (single-sourced, for the reviewer)

The review gate reviews the **diff**, not the whole document, applying the greenfield bar
(no dead-ends, notation-sync, branch resolution, screens enumerable) **scoped to the
delta + its ripple**, plus: scope-confinement (untouched flows unchanged), ripple/
regression (no hand-off left pointing at a removed/renamed flow; no orphaned/missing
screens-index entry; no newly-stranded path; diagram⇄narrative still synced on the
edit), correct version for the change class, and deprecation-safety. An unscoped
regenerate (churn outside the delta) is itself a `revise`.

## Sources

- Keep-a-Changelog (Added/Changed/Deprecated/Removed/Fixed) + SemVer (MAJOR/MINOR/PATCH),
  applied to a design document.
- Docs-as-code / diagrams-as-code versioning practice — design docs versioned in source
  control, each change a reviewable commit, a changelog for traceability.
- The "treat a design doc like source code; amend, don't regenerate" discipline — edit
  the affected flow, never re-draw the untouched ones.
