# Amend mode — editing an existing design system as a versioned delta

Depth for Step 7. The first build is greenfield; every later change is a **delta**. Treat the design-system doc like source code: a change is a scoped, reviewed, **versioned** diff — never a regenerate. It must not revamp untouched tokens/components.

## Scope the change + its ripple

Identify the exact token(s)/component(s) the change touches, AND the **ripple** (the blast radius unique to design systems):
- a renamed/removed/retyped **semantic token** orphans every component that references it;
- a renamed **component** is a catalog-API break for every consumer;
- a **primitive** change ripples through every theme alias pointing at it.

The ripple, not just the edit site, is the real scope. The **alias layer contains the blast radius** — re-pointing a semantic alias often turns a breaking change into a non-breaking one.

## Edit-not-redraw

Make the **minimal in-place edit**: add/modify only the scoped token/component spec + the necessary ripple fixes; leave every other token, component, and section **byte-for-byte unchanged**. Don't re-tier, re-name unrelated tokens, or churn the palette "while you're here". Keep the system internally coherent (every component still references a real semantic token).

## Version the delta

Bump the system's **semver** for the change class (rename/remove/retype ⇒ MAJOR; additive ⇒ MINOR; backward-compatible fix ⇒ PATCH) and write a **Keep-a-Changelog** entry naming the exact tokens/components (Added/Changed/Deprecated/Removed/Fixed). An unversioned, unlogged change is invisible to the next iteration.

## Deprecate-then-migrate breaking changes

Never remove/rename abruptly: deprecate in a MINOR (mark + state replacement + removal timeline) → keep through a notice window → remove in the next MAJOR. Ship a migration guide (old→new) + a codemod where feasible (a token rename is near-mechanical).

## Division of responsibility

The skill owns the **amend method** (this) + the reviewer owns the **delta review**. The orchestration that decides it's an iteration, scopes it, and hands the existing doc in is the caller's job — on a change the existing doc arrives as one of the input documents (no input-mechanism change).
