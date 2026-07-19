# Extraction template guide (Procedure 3 output)

One extraction is a Markdown file per candidate repo — a **YAML frontmatter** machine
block above a **10-section markdown body**. The frontmatter is defined + validated by
`schemas/extract-output.schema.json` (see `extract-output-guide.md`); this guide covers
the 10 body sections.

The 10 section headings are FIXED (the validator's `EXTRACT_HEADINGS` constant in
`scripts/validate_prior_art.py` checks each `## <heading>` is present — guide and
validator share one list, so they cannot drift):

1. **## Core abstractions** — the load-bearing types/modules, with file references.
2. **## Architectural pattern** — the overall shape (event loop, pipeline, plugin
   registry, …), grounded in a cited file.
3. **## Solved well** — the hard problems this repo solves cleanly.
4. **## Solved poorly** — where it struggles; cite the file/issue.
5. **## Trusted dependencies** — the key deps and why they're sound (mirrors the
   `key_deps` purl list in the frontmatter).
6. **## Patterns to borrow** — reusable patterns worth adopting — PATTERNS + file
   references only, never verbatim code (license risk).
7. **## Anti-patterns** — what NOT to copy.
8. **## Testing approach** — how the repo tests itself.
9. **## Production setup** — deploy/ops maturity.
10. **## Verdict** — restate the frontmatter `verdict` enum
    (`borrow-architecture | borrow-patterns | reference-failure-modes | discard`) with
    a one-paragraph justification.

Each claim must trace to a file/path actually read (condition 13, deep-read fidelity) —
no README paraphrase. Depth over skim (condition 14): follow the read protocol
(structure → entities → entry → config → tests → issues → changelog → deps).

Worked example: `scripts/fixtures/extract-output.valid.md` (a synthetic full extraction
that passes `validate_prior_art.py extract`).

**Bail (no deep read).** When a repo confidently touches none of the caller's scope, or
its clone fails / it's gone, emit a frontmatter-only skip record (no body) — see
`extract-output-guide.md`.
