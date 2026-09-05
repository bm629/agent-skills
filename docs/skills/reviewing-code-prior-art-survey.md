# reviewing-code-prior-art-survey

The acceptance gate over the search wave of an open-source code prior-art
survey — the reviewing half of the `code-prior-art-survey` pair.

## Purpose

Judges the three artifacts the producer emits — a keyword map (typed search
vocabulary), a per-angle search output (coverage cells + candidate
repositories), and a per-repository extraction — and answers one question: is
this artifact sound enough for the survey's later stages to build on? It
applies a fixed twenty-two-condition
bar and emits exactly one verdict — a terminal `VERDICT: approve|revise` line
by default, or the caller's named equivalent where its brief replaces that
line — with condition-named, actionable findings. Review-only: it never
authors or fixes; the producer revises.

## The twenty-two-condition bar (single-sourced with the producer)

Keyword map (1–6): typed coverage · expansion quality · disambiguation ·
scope honesty · source contract · self-description. Search output (7–11):
coverage proven · candidate integrity · boundary honesty · failure
transparency · schema-valid (11 applies to maps too). Judge-side (12):
proportionality — a thin-but-honest result in a thin domain meets the bar;
revise only on a named gap. Extraction (13–18): deep-read fidelity · depth,
not skim · bail integrity · verdict groundedness · score defensibility ·
safety honesty. Conditions 11 and 12 generalize across artifact kinds, and
1–12 keep their numbers. The producer produces TO this bar; this skill
asserts it independently — same numbered list, no drift by construction.

Two defect classes only judgment can catch: a `verdict` its own findings do not
support (16), and an `irrelevant` bail whose rationale reads as uncertainty
rather than a confident out-of-scope call (15) — both pass the deterministic
validator, which is exactly why the gate exists.

## How it judges

- The deterministic pair (conditions 7 + 11) is discharged by ONE run of the
  co-installed producer's validator (`validate_prior_art.py`), which
  recomputes coverage completeness from the map × its own source registry —
  never re-implemented, never waved through on FAIL lines.
- The judgment conditions (1–6, 8–10) are walked from
  `references/conditions.md`, each with an explicit gap-vs-not calibration
  (the no-false-revise discipline made concrete).
- A delta lens judges inheriting keyword maps as scoped deltas: new/changed
  groups only; findings against untouched inherited groups are themselves
  defects.

## Precondition

`code-prior-art-survey` must be co-installed — it supplies the artifacts, the
schemas, the source registry, and the validator (which needs `pyyaml` +
`jsonschema` on the invoking interpreter).

## Package layout

- `SKILL.md` — the review method (Orient / Judge / Decide+emit) + the verdict
  contract.
- `references/conditions.md` — the twenty-two conditions expanded with
  what-to-check + IS-a-gap / NOT-a-gap calibration, per artifact type, plus
  the delta lens.
- Ships no `schemas/` and no `scripts/` by design — the contracts and the
  validator belong to the producer package.

## License

MIT (see repository root).
