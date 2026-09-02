# `regulatory-prior-art-survey`

Establish which instruments, standards and obligations actually bind a described project — before
the architecture fixes a data model, a retention policy or a transfer route that law will not allow.

**Wave 1 only.** Two kinds: the regulatory scope map, and one search angle's output. Extract and
synthesis are not in it, and nothing here produces advice — it produces a searched, recorded corpus
of citations a later wave and a human lawyer turn into one.

## The organising idea

Every sibling survey can afford a wrong entry in its corpus. This one cannot. A fabricated citation
— an obligation the text does not carry, an identifier nobody resolved, a paraphrase of a clause the
run could not read — is worse than an empty result, because it is confident, checkable-looking, and
wrong in the direction that gets acted on.

So the whole type is shaped around one boundary: **`claim` is what the DOCUMENT says; the
`evidence_quote` is the warrant; and where the two disagree the quote governs.** Nothing in this
survey asserts what a system must do. It records what an instrument states, at an identifier a
reader can re-resolve.

## Two procedures

**Procedure 1 — the regulatory scope map.** Built before any searching, over **nine axes**:
`instrument`, `sector`, `jurisdiction`, `obligation-dimension`, `control-catalog`, `platform-role`,
`transfer-mechanism`, `model-term` and `ui-term`.

It also carries the receipt that makes this type falsifiable: **a verdict for every one of the nine
sector families**, always, each with the evidence it rests on. `applies`, `does-not-apply` or
`undetermined` — and `undetermined` is first-class, because a map that cannot tell whether a sector
regime binds should say so rather than manufacture a clean answer.

**Procedure 2 — one search angle.** Eight angles, three always-on:

| Angle | Trigger | Cap |
| --- | --- | --- |
| a1 primary-law register retrieval | always | 25 |
| a2 regulator guidance and enforcement | always | 20 |
| a3 incorporated control catalogs | always | 12 |
| b1 AI-specific obligations | conditional | 15 |
| b2 accessibility obligations | conditional | 15 |
| b3 platform and intermediary duties | conditional | 15 |
| b4 cross-border transfer mechanisms | conditional | 18 |
| b5 financial and payments regimes | conditional | 18 |

## Authority ranks. It never cuts.

`authority` is how close to the issuing body a text is — `primary-law`, `regulator-guidance`,
`incorporated-standard`, `secondary-compilation`. `binding_force` is whether and how it binds —
`law`, `incorporated-by-reference`, `contractual`, `regulator-guidance`, `voluntary-standard`.

**They are two fields and collapsing them is a defect.** PCI DSS is an incorporated standard whose
binding force is contractual: not law, and it binds anyway. A survey that filtered on authority
would drop it, and the product would ship without the obligation it is most likely to be audited on.

Admission turns on **verifiability**, never on rank: an instrument is carried only where it resolves
at a NAMED issuing body with a stated version or date. Anything else goes to `unadmitted` with a
`reason_class` from a closed set — closed precisely so that "low authority" cannot be written where
"nobody could resolve it" is the truth.

## A text you could not read is a finding, not a gap

Three source classes in this registry cannot be read at all: ISO texts sit behind a challenge, PCI
documents behind a separate host's 403, UK primary law refuses non-JS clients. A record for one of
those carries its NUMBER and **no quote** — `evidence_quote: null` or the field omitted, both legal.

*"ISO/IEC 27001 is incorporated by reference here and its text costs money to read"* is real
information an architect needs. A paraphrase of clauses nobody saw is the fabrication this type
exists to prevent, and the gate refuses it.

## The corpus moves, and the registry records how

**22 sources**, five of them terminals in a fallback forest that is checked for cycles rather than
asserted to have none. Nine rows are excluded on the record, with the reason.

Retrieval here is unusually shape-sensitive, and every trap is written on the row it bites:

- the EU Cellar resolver answers on the `Accept` pair alone — `text/html` and `application/xml`
  each 404 the same URI — and it answers **303** into an object store, so a request issued without
  following the redirect returns zero bytes and reads exactly like a dead channel;
- eCFR serves its structure document to a plain GET and returns **406** on the full XML unless the
  request permits compression, and its `{date}` must be at or before that title's most recent issue
  date or it 404s with an error body naming the real one;
- two rows answer 403 to a default user agent and 200 to a browser one, at identical byte counts.

The lead channel this survey was designed around died during the build: `eur-lex.europa.eu` began
answering HTTP 202 with a JavaScript challenge to every user agent. The replacement is recorded with
its evidence, not silently swapped.

## The coverage grid is 2-D, and its owed set is derived

```
groups = the map's groups whose type is in the angle's applicable_group_types
owed   = {(g, s) for g in groups for s in the angle's OWN sources ∩ the map's ACTIVE sources}
```

Three terms, not two. Dropping the angle's own source list turns the shipped a1 exemplar's 30 owed
cells into 105, and a reviewer applying it finds seventy-five missing cells in a correct artifact.

`returned` counts INSTRUMENTS under a stated frame; `kept` counts rows carried into `candidates`
**plus** `unadmitted`, per cell — the equality that makes a row found and dropped without a record
impossible.

A source is `active` or `skipped`, and `skipped` needs both a cause and a `cause_class`: `refused`
with observable evidence, or `no-holding-angle` because every angle carrying it records
`holds: false`. **A source a holding angle carries stays active even where the scope makes it
unlikely to yield** — its cells are recorded choices, and an omitted pair and a recorded zero are
different facts.

## The deterministic gate

`scripts/validate_regulatory_prior_art.py` checks shape across 77 rules and exits 0 clean, 1 the
artifact has findings, 2 it could not be used at all. The exit-2 class is load-bearing: a malformed
registry, a missing dependency, an unusable `--keyword-map` or an unknown angle are faults in the
invocation or the package, and reporting them as exit 1 sends an author off to edit a file that is
fine.

The JSON Schemas run FIRST and return early. That ordering is not incidental — an earlier draft
loaded them nowhere, and deleting a required field from a search output produced zero findings while
silently disabling eight rules that branch on it. Rules that merely restate a schema enum are
deleted rather than duplicated, because two statements of one enum drift and only one of them runs.

It needs `pyyaml` and `jsonschema`:

```
uv run --no-project --with pyyaml --with jsonschema \
  python scripts/validate_regulatory_prior_art.py keyword-map <your map>
```

Two limitations stated rather than papered over. Wave 1 carries EU acts **as adopted** at their own
CELEX, not consolidated: the id grammar accepts only the as-adopted form, so an angle told to fetch
a consolidated text would have no legal identifier to record it under. And whether a quote is
genuinely verbatim from the division it is attributed to cannot be checked without a fetch — the
gate checks that the identifier, the locator and the citation agree, and the reviewer checks the
rest.

## Companion

[`reviewing-regulatory-prior-art-survey`](reviewing-regulatory-prior-art-survey.md) — the judgement
half of the same gate.
