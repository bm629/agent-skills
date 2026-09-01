# Absent input

The governing convention: **absent input implies not-in-set implies false.**

A field the capability map omits does not make a predicate true, and does not make it undefined —
it makes that disjunct false. This is why a conditional angle needs at least one REQUIRED-rooted
leg: a predicate resting only on optional fields is false for every map that omitted them, so the
angle looks configured and never runs, which is indistinguishable from an angle nobody set up.

## What to do when the scope omits something you need

Record the absence and proceed. Do not infer a value, and do not treat silence as permission:

- **A scope field is missing** — the angle whose predicate needs it does not fire, and its
  `angle_applicability` verdict says so with that reason.
- **A source states no date** — `as_of` is `null` with the reason recorded. Never the fetch date.
- **A source states no number** — that is a FINDING. Three platforms here publish no commission
  rate anywhere; "the guidelines state no rate" is evidence, an empty field is a hole.
- **A source's terms do not address automated access** — record "not addressed". Do not read it as
  permission and do not read it as prohibition.
