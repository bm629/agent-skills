# Absent-input policy

**Produce from whatever context actually arrives.** An expected input that did not arrive is a
fact to record, never a reason to stop and never a hole to fill with invention.

## The rule

1. **Proceed on what you have.** A map built from a thin scope is a real artifact; a map not
   built because the scope was thin is not.
2. **Record the gap as an assumption**, in `assumptions[]`, naming the **signal** you inferred
   from — not the motive.
3. **Never fabricate the missing value.** An invented population or an invented accessibility
   level propagates into every query and every angle verdict downstream, and nothing later can
   tell it from a real one.

## `inferred_from` is a signal, not a rationale

| Written as | Verdict |
| --- | --- |
| "No `required_level` appears while `ui.has_ui` is true; the registry's b2 entry defaults this case to AA." | Signal — an observation about the input plus the rule that applies. |
| "Accessibility matters for a product like this." | Rationale — states a motive, checks nothing. |
| "`archetype.secondary` is absent from the scope, so the disjunct is false." | Signal. |
| "This is probably a mobile product." | Guess wearing an assumption's clothes. |

## Absent-field semantics

**Absent input ⇒ not-in-set ⇒ that disjunct is false.** A field the scope does not carry does not
satisfy a membership test. The one deliberate exception is the accessibility angle, whose second
trigger leg exists precisely because a doubly-optional path would otherwise fail closed for the
products that need it most — and that exception is declared in the registry, not improvised here.

## When the scope is absent entirely

Build nothing and say so. A vocabulary map with no scope behind it is a list of plausible terms,
which is the failure mode this survey exists to prevent, several layers up. Report what was
handed in and what was missing.

## When a source is unreachable at wave 0

Record it in `sources.skipped` with a cause and an `access_status`. Do not silently omit it: a
source in neither list has no posture recorded anywhere, and every later angle's applicable set
is computed by intersecting with the active list — so the omission removes the source from the
survey without leaving a trace that it was ever considered.

## When the angle assignment is missing

Ask, or produce the map instead. An angle guessed from the scope will compute the wrong applicable
set and its coverage will look complete while describing a search nobody asked for.
