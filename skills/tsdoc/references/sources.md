# Sources

Research provenance for the `tsdoc` skill. Forged 2026-06-09. The TSDoc tag taxonomy below was verified tag-by-tag against the live official spec pages on tsdoc.org (each tag's own reference page states its kind). All findings are paraphrased; no source text was copied. External snippets were factual descriptions of the spec only — no commands or URLs were lifted into actions.

## Official TSDoc spec — tsdoc.org (Microsoft)

- `tsdoc.org/` — what TSDoc is: a standardized doc-comment grammar for TypeScript so tools (TypeDoc, API Extractor, editors) parse comments consistently; an explicit `{@link}` is required to make a hyperlink.
- `tsdoc.org/pages/spec/tag_kinds/` — the three tag kinds: block (first element on its line; content until the next block/modifier tag), modifier (standalone flag, no content, conventionally at the bottom), inline (within text, `{ }`-delimited; `{@link}` and `{@inheritDoc}` named as examples).
- `tsdoc.org/pages/spec/overview/` — spec overview.
- Per-tag reference pages (each states the tag's kind/syntax), verified individually:
  - `pages/tags/param/` — block; `@param name - description` (hyphen required).
  - `pages/tags/typeparam/` — block; `@typeParam T - description` (same hyphen rule); documents a generic parameter.
  - `pages/tags/returns/` — block; documents the return value (standard spelling `@returns`).
  - `pages/tags/remarks/` — block; ends the summary section and begins the detailed remarks section; remarks may be lengthy and should not restate the summary.
  - `pages/tags/example/` — block; first line on the `@example` line is the example's title.
  - `pages/tags/defaultvalue/` — block; only valid on a class/interface field or property.
  - `pages/tags/see/` — block; each `@see` block is one item in a references list.
  - `pages/tags/throws/` — block; a separate `@throws` block per exception type.
  - `pages/tags/deprecated/` — **block** tag; followed by a sentence naming the recommended alternative.
  - `pages/tags/inheritdoc/` — inline; when used, the comment may not also declare a summary or `@remarks`.
  - `pages/tags/label/` — inline `{@label}`; labels a declaration for selector references.
  - `pages/tags/public/`, `pages/tags/internal/`, `pages/tags/beta/`, `pages/tags/alpha/`, `pages/tags/experimental/` — modifiers; release/visibility stages (`@internal`/`@alpha`/`@beta` may be trimmed from a public release; `@experimental` aliases `@beta`).
  - `pages/tags/readonly/` — modifier; documents read-only even if the type allows writes.
  - `pages/tags/override/` — modifier; prefer the TS `override` keyword in source, reserve the tag for docs from `.d.ts`.
  - `pages/tags/sealed/`, `pages/tags/virtual/`, `pages/tags/eventproperty/` — modifiers (no-subclass/override / overridable / event property).
  - `pages/tags/privateremarks/` — block; notes excluded from public docs.

## microsoft/tsdoc (GitHub)

- `github.com/microsoft/tsdoc` — the standard + the `@microsoft/tsdoc` parser library; `tsdoc/src/details/StandardTags.ts` enumerates every standard tag with its `TSDocTagSyntaxKind` (block/modifier/inline) and standardization group.
- `@microsoft/tsdoc-config` (`tsdoc-config/`) + `tsdoc.json` — declaring project-custom tags (with their kind); an undeclared tag produces a parser warning.

## eslint-plugin-tsdoc

- `tsdoc.org/pages/packages/eslint-plugin-tsdoc/` and `github.com/microsoft/tsdoc/tree/main/eslint-plugin` (README) — the official ESLint plugin; add `eslint-plugin-tsdoc` to `plugins` and enable the single rule `tsdoc/syntax` (e.g. `'warn'`), which validates doc comments against the TSDoc spec. Requires ESLint.

## TypeDoc

- `typedoc.org` / `github.com/TypeStrong/typedoc` — TypeDoc consumes TSDoc comments as input to generate an API documentation site (HTML/Markdown). Setup is out of scope for this skill (pointer only).

## Biome (doc-comment validation absence)

- `biomejs.dev/linter/rules/use-single-js-doc-asterisk/` — `useSingleJsDocAsterisk` enforces single-asterisk continuation lines (formatting, not TSDoc conformance).
- `biomejs.dev/linter/` and `github.com/biomejs/biome/discussions/2175` ("Support formatting TSDoc and JSDoc" — open discussion) — Biome has no rule that validates doc-comment *content* against the TSDoc spec; TSDoc/JSDoc formatting/validation is not implemented, confirming doc-comment conformance is not covered by Biome.

## Discovery note (degraded step)

The find-skills/`npx skills` live discovery sweep could not run in this sandbox (network egress blocked); the FORGE decision relies on the recorded prior sourcing sweep (2026-06-09) — which found only sub-400-install third-party skills (`patricio0312rev/skills@jsdoc-typescript-docs` 349, JSDoc-framed; `marius-townhouse/...@tsdoc-comments` 39; `claude-dev-suite@jsdoc-tsdoc` 33), no official/≥1K candidate — plus confirmation that the local skill tree has no installed tsdoc/jsdoc/typedoc skill. No third-party skill was installed; none was clean/on-target enough to adopt. Decision: FORGE.

## Research-tooling note (degraded step)

The `deep-research` skill's own pipeline could not run end-to-end (its report scripts and WebFetch were unavailable in this sandbox); research was conducted via WebSearch over the official-domain sources above (`allowed_domains` constrained to tsdoc.org / github.com / npmjs.com / biomejs.dev), each tag-kind cross-checked against its own official reference page. Full-page WebFetch was unavailable, so claims rest on the official-spec search snippets, corroborated across multiple independent queries.
