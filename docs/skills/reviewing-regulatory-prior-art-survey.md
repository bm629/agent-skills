# `reviewing-regulatory-prior-art-survey`

The judgement half of the regulatory prior-art gate. A second agent reads an artifact that has
already passed the deterministic validator at exit 0, and decides whether it can be built on.

## Why a second half exists

The validator checks shape: that every owed cell is present, that `kept` reconciles against the rows
carried, that an identifier matches its grammar, that a quote is absent where the text could not be
read. All of that can be wrong in a way no script can see.

A candidate can sit in the group its evidence does not serve. A `claim` can assert what the system
must do while its quote says only what an act states. A cell can record `not-attempted` where the
run actually failed. An `authority` value can be honest and the record still be a fabricated
citation. Those are the findings that matter here, and every one of them is a reading.

## The 29 conditions

Each names its evidence, what IS a gap, what is NOT, and — where the boundary is easy to cross —
what is **not yours to report** because the validator already refuses it. That last clause is load-
bearing in both directions: a condition hunting something the gate fails is dead weight, and a
reviewer silent about something nothing checks is a hole.

The two worth the most: **C19**, that nothing is asserted the source does not say, and **C23**, that
`text_retrievable` is the state the fetch actually reached. A finding under either is worth more
than three under anything else, because together they are the two routes to the fabricated citation
this type is built around.

## Six evidence sources, three of them in the producer package

The artifact and the scope map are handed to you. So is **the scope and classification the producer
was handed** — without it, `meta.classification` is a transcription judged only against itself, and
a fabricated value reads exactly like a real one. The schemas, the source registry and the angle
reference are read from the producer package, because an artifact cannot be its own contract: an
angle's source list derived from the artifact would make every omission self-justifying.

Anything you cannot ground in those six is an **observation**, not a finding — said plainly, with no
condition attached. An ungrounded finding costs a revise round on correct work.

## Proportional, on purpose

A thin result honestly recorded is a complete result. A scope with three applicable instruments
yields three, and revising that for being small is how a survey gets padded with instruments nothing
in scope references — obligations put in front of an architect that do not bind.

This is measured rather than asserted. In the pair's cold run, a fresh producer built a fifty-cell
artifact carrying three candidates and one unadmitted row against a scope it had never seen; this
reviewer judged it unseen and returned `approve`, with one upstream finding it explicitly recorded
as not the author's to fix.

## The verdict grammar

Exactly one `VERDICT: approve` or `VERDICT: revise`, with every finding naming its condition. The
producer package's own fixtures calibrate it: clean artifacts that must return `approve`, and
planted ones that each carry a single defect a blind reviewer must find and name correctly.

## Companion

[`regulatory-prior-art-survey`](regulatory-prior-art-survey.md) — the producer half, and where the
schemas, the registry and the angle references live.
