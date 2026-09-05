# `reviewing-scale-prior-art-survey`

The reviewing twin. It judges what a deterministic gate structurally cannot, on an artifact that
has already passed one.

**41 numbered conditions**, contiguous, grouped per kind — plus one group headed `## Every kind`,
because the proportionality duty belongs to all four and the twin tells a reviewer to read their
own group and only that group. Placed inside a kind's section it would have been invisible to
three reviewers out of four, which is how it shipped the first time.

The count is DERIVED from the file and stated nowhere in prose. It lands ONE above the sibling
range of 20-40, and the spec says so and why: merging two conditions to fit inside a measured
range would be picking a number over a duty.

## What it judges that the gate cannot

- **The declared band is a faithful transcription of the handed SCOPE.** A fabricated band reads
  exactly like a real one, and every lens leans on it.
- **The number is the SOURCE's number.** A converted, rounded or recomputed figure is a finding
  even when the arithmetic is right.
- **`configuration_stated: true` means the configuration is actually stated.** A benchmark number
  with no disclosed configuration is not a comparable measurement, however authoritative its host.
- **`primary_dimension` is the dimension the episode actually MEASURED** — judged from `signal`
  and `metric_name` against the source. This duty was DEMOTED from the validator, because no
  signal-to-dimension mapping exists to decide it deterministically.
- **`transferability` is weighable and INDEPENDENT of `confidence`.** A reason that restates the
  level is not a reason.
- **The band for an UNSOURCED dimension is the reviewer's alone.** No published boundary exists,
  so the gate skips the re-derivation entirely — `concurrency: extreme` on an episode measuring
  300 requests per second is caught by nothing upstream.
- **An absence is phrased with its receipt.** What was looked for, and where.

## The calibration set

Four clean artifacts, the SOURCE one was extracted from, and the extracts directory the index
resolves against — all gating at exit 0, all byte-identical to the producer package's copies with
a test asserting it.

Staging the source is not decoration. Five conditions name "the SOURCE itself" as their first
evidence, and without it they can only ever record "unjudgeable" — a reviewer calibrating on the
set would never see them run. A blind review found exactly that: six of the conditions could not
be exercised against the reference set at all.

## Install

```
npx skills add bm629/agent-skills@reviewing-scale-prior-art-survey
npx skills add bm629/agent-skills@scale-prior-art-survey
```
