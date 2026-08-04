# Planted defects

Each fixture here **passes the deterministic gate** and is nonetheless wrong. That is the point:
a gate demonstrating only approve-on-good proves nothing about the judgment half. These exist to
prove the reviewing skill's conditions actually bite.

Every one was verified to exit 0 through the validator before being committed. If a change to
the validator ever makes one of these FAIL the gate, re-read rather than re-fix — either the
defect became mechanically detectable (move the check into the gate and retire the fixture) or
the gate grew a false positive.

**No fixture names its own defect.** The bodies carry no marker comments — a fixture that
announces its answer cannot test a blind reviewer.

| Fixture | Passes gate | Must be caught by | The defect |
| --- | --- | --- | --- |
| `search-output.failure-as-zero.yaml` | yes | **C12** | The degraded cell rewritten as `reached, returned: 0`. The arithmetic reconciles perfectly and `degraded_sources` is empty, so nothing mechanical can see it — but the corpus demonstrably carries the queried patterns, so the zero is a failure wearing a receipt. |
| `search-output.corpus-mismatch.yaml` | yes | **C16** | A relevance line asserting a keyboard contract the cited pattern page does not carry — it claims a single tab stop and no roving tabindex where the corpus specifies the opposite. URL resolves, release is plausible, claim is false. |
| `search-output.authority-understated.yaml` | yes | **C19** | A W3C normative pattern recorded as `authority: published-system`, `prescriptivity: descriptive` — a standards-body contract demoted to one organisation's opinion. |

## Why these three

They cover the three ways this artifact fails while looking healthy:

1. **A failure laundered into a zero** — the only defect that actively misleads rather than
   merely omitting, and the one the whole survey exists to prevent.
2. **A citation that resolves but does not say what is claimed** — the shape check can verify a
   URL and a release; only a reader who opens the page can verify the contract.
3. **The authority/prescriptivity distinction collapsed** — which puts a design system's
   preference on the same footing as a normative criterion downstream.

## Blind-run record (2026-08-04)

A reviewer with no knowledge that defects were planted caught all three under exactly the
expected conditions. On an earlier version of the third fixture it additionally found two
defects I had introduced by accident — a candidate attributed to a cell that could not have
produced it (C14), and a design-system record scoped to one component rather than one system
(C18). The fixture was rebuilt to isolate C19; the extra findings were correct and are the
reason it now uses a legitimate same-angle candidate.
