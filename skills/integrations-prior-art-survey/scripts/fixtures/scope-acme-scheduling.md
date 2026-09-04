# Acme Scheduling — integration scope (calibration fixture)

The scope excerpt the calibration map's `meta.classification` is a TRANSCRIPTION of. It ships so
that C19 can be exercised: judged only against itself, a fabricated classification reads exactly
like a real one, and a blind packet that stages no scope can only record C19 unjudgeable.

**It is deliberately NOT a mirror of the classification.** The six deciding values are stated the
way a product scope states them — in prose, with the business reason — so a reviewer has to derive
them rather than diff two copies of the same YAML.

## The product

Acme Scheduling sells appointment booking to mid-sized B2B teams: sales demos, client sessions,
recurring service visits. Around 400 paying organisations, self-serve plus a small enterprise tier.

## What it integrates with, and why that is not optional

Booking is worthless if it cannot write to the calendar the customer already lives in, so
**calendar sync is table stakes** — today that means **Google Calendar**. (Microsoft 365 is wanted
and is deferred to a later phase; it is deliberately NOT in the set this survey covers, and a
transcription that added it would be recording a plan rather than the scope.) Paid booking needs a
payment processor; today that is **Stripe**. Enterprise buyers ask for their CRM to see the
booking as an activity, which in practice means **Salesforce**. Video sessions are created and
torn down against **Zoom**.

Those four are the named starting set. The surface is **complex** rather than incidental: each is a
different auth model, several push events back, and a customer expects a broken sync to be visible
rather than silent.

## How fast it has to be

A booking confirmed in Acme must appear on the customer's calendar **within a few seconds** — the
customer is often still on the phone with the person who booked. It is not a hard real-time system:
a few seconds of lag is acceptable, a scheduled nightly reconciliation is not.

## What it is, architecturally

A hosted **API-first service**. The web app is one consumer of the same public API partners build
against; there is no separate private backend, and third-party developers are an audience.

## Regulatory position

Bookings carry names, contact details and, for the healthcare vertical, appointment reasons that
are health information. **GDPR applies** to the EU customer base and the healthcare tier brings
**HIPAA obligations** in the US. Both are live constraints on which vendors can be integrated at
all, not aspirations.

## Machine learning

**None.** There is no model in the product. Suggested-time ranking is a deterministic heuristic over
the customer's own availability, and no third-party ML service is called.
