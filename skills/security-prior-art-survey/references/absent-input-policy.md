# Absent-input policy

Scope context arrives from the caller, and parts of it are routinely missing — a caller may
describe a product without ever stating its verification level or its supply-chain posture. The
survey must still run, and must never let a missing input quietly become a finding.

**The governing rule:** an absent input reduces **coverage**, and reduced coverage is reported.
It never silently becomes "nothing there".

**Precedence.** An angle's own brief states its precondition authoritatively. This file states
what to assume about *scope* when an input is missing, and which angles therefore cannot fire.
Where the two appear to disagree about whether an angle runs, the angle brief wins.

## Per-input fallbacks

| Missing input | What to do |
|---|---|
| **Verification level** (how rigorous the product's security bar is meant to be) | Infer it from what *is* present — the sensitivity of the data described, the domain, and the complexity of the authentication and authorization the product needs — with the baseline level as the floor when nothing points higher. Record the inferred level **and the signal it was inferred from**. Never infer below the baseline. |
| **Supply-chain risk posture** | Treat as medium, so build-path attack-pattern enumeration still runs. A product with named third-party services and an unstated posture is not evidence of low risk, and this survey's asymmetry favours over-inclusion. |
| **Data sensitivity, authentication or authorization complexity, external attack surface** | Derive the surface from the product's described capabilities alone, and record that coverage was reduced — not that the surface is absent. |
| **Named third-party services, platforms or hosted dependencies** | The vendor-advisory angle does not fire. Report that the vendor-advisory surface was **not covered and why** — never "no vendor advisories found". |
| **A named package or dependency set** | The package-advisory angle does not fire; record it as not-run with cause. This is common early, before a product has chosen its stack. |
| **Whether the product ships a mobile client** | Run the mobile control-standard angle. The over-inclusion asymmetry applies: surveying mobile controls for a product that turns out to be web-only costs some extra low-evidence findings the ranking sinks, while skipping them for a product that does ship a client omits an entire control family invisibly. Record the assumption. |

## Why inference rather than a default or a stop

Three options exist when a level is missing: assume the baseline, infer from the surrounding
signals, or stop and ask.

Assuming the baseline takes the under-coverage direction by default, and under-coverage is the
invisible failure in security work — an over-surveyed product yields some extra low-evidence
findings that ranking pushes to the bottom, whereas an under-surveyed one produces a report that
looks complete and quietly omits the controls that mattered, leaving no trace that anything is
missing.

Stopping to ask turns a missing optional input into a human gate on an otherwise automatic
process, which does not scale and blocks callers who genuinely do not know yet.

Inference uses information the caller already supplied, costs nothing at run time, and stays
honest because the inference and its basis are both written into the artifact where a reader can
disagree with them.

## Recording assumptions

Every assumption this policy forces is recorded in the artifact as an assumption — **with the
signal it was inferred from**, for every row in the table above and not only the verification
level — not folded into the scope as though the caller had stated it. A downstream reader must be able to tell the
difference between "the caller said the product handles payment data" and "no level was given,
so one was inferred from the mention of payouts".
