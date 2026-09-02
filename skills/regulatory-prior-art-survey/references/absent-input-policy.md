# When the input is missing, thin, or not what the contract promised

## The map is missing a field you need

Read the field's absence as a FACT about the scope, not as permission to invent one. A predicate
leg whose field is absent is FALSE — every atom is false on absent except the one that tests for
absence. That is deliberate: an angle that fired on a missing field would fire for every scope that
omitted it.

**Decide on the legs you have.** A disjunctive precondition with one leg absent and one leg true
still holds; a conditional angle whose every leg is absent does not.

## The classification names a value the enum does not have

Record it verbatim in `meta.classification` and say so in `assumptions`. Do NOT round it to the
nearest legal value: a verdict citing a value nobody handed you is unfalsifiable, and the whole
point of recording the classification is that a reader can check the verdict against it.

## A sector verdict you cannot determine

`undetermined` is FIRST-CLASS and it is the right answer more often than it looks. The map cannot
always know whether a sector regime binds — a scope that books consultations may or may not take
payment itself — and recording a guess as `applies` or `does-not-apply` manufactures a clean result
out of an unresolved question.

What `undetermined` owes is the same as the other two: evidence for why it could not be settled.

## A source refuses at wave 0

It goes in `sources.skipped` with OBSERVABLE evidence — an HTTP status, a redirect target, a
challenge body, an auth wall. "Could not access" is not a cause.

A skipped source is one **no angle can query**, because every angle's source set is intersected
with the active list. That is what makes "active" a map STATUS rather than each angle's private
opinion.

## A source answered last month and refuses now

Distinguish the three. **They are wave-1 CELL statuses**: a wave-0 map records `active` rows with
an `access_status` from its own smaller enum (`open | rate-limited | throttled | polite-pool |
registration-required`) and `skipped` rows with a prose `cause`, so at wave 0 this three-way
distinction goes IN THAT CAUSE, in these words. `rate-limited` is the one member both enums carry,
and it means the same thing in each.

- **`gated`** — it completed the fetch and refused it. A source that answered and now demands a key
  is gated, not unreachable.
- **`rate-limited`** — a normal operating condition on a shared pool, not a searched zero.
- **`unreachable`** — the request did not complete at all.

A channel that MOVED is none of these: record the redirect target, because a 301 to a different
page that answers 200 is how a run records the wrong corpus and sees no error.

## The angle you were handed does not hold

Write `outcome: not_run` with the map's verdict quoted, no cells and no candidates. Searching
anyway inflates the survey with an angle the scope ruled out.

If you STARTED and there was nothing to search, that is `vacated`: cells, their causes, a
`vacated.cause` naming why there was nothing, and a `retrieval_summary` are all owed — candidates
are not. A vacated angle and one that searched and found nothing are different facts, and
`vacated.cause` is the only thing that separates them.

## The corpus is thin

A scope with three applicable instruments yields three. **A thin result honestly recorded is
complete**, and padding it with instruments nothing in scope references is worse than the thinness
— it puts obligations in front of an architect that do not bind.
