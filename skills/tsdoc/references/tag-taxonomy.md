# TSDoc tag taxonomy

TSDoc distinguishes **three kinds** of tags, each with distinct syntax. A tag name is an at-sign followed by camelCase ASCII letters. Categorizing a tag correctly matters because the parser treats the kinds differently.

- **Block tag** — introduces a section. It must be the first element on its line; all text after it (up to the next block or modifier tag) is its content, and may contain Markdown and inline tags.
- **Modifier tag** — a standalone flag whose mere presence marks an aspect of the API item. Carries no content; conventionally collected on a line at the bottom of the comment.
- **Inline tag** — appears within running text, always delimited by `{` and `}`.

## Block tags

| Tag | Purpose | Syntax notes |
|---|---|---|
| `@param` | Document a function/method parameter | `@param name - description` — the **hyphen** separator is required |
| `@typeParam` | Document a generic type parameter | `@typeParam T - description` — same hyphen rule as `@param` |
| `@returns` | Document the return value | `@returns description` (no `{type}`). Standard spelling is `@returns`, **not** `@return` |
| `@remarks` | Detailed discussion beyond the summary | Ends the summary section and begins the remarks section; should not restate the summary |
| `@example` | A usage example | First line on the `@example` line is treated as the example's title; index numerically otherwise |
| `@defaultValue` | Default for a field/property | Only valid on a class/interface member field or property |
| `@see` | A cross-reference list item | Each `@see` block becomes one item in a references list |
| `@throws` | An exception the caller should know about | Use a **separate** `@throws` block per exception type |
| `@deprecated` | Mark as deprecated | A **block** tag (not a modifier) — followed by a sentence naming the recommended alternative |

`@privateRemarks` (a block tag) holds notes stripped from the public docs; use when you need internal commentary that should not ship.

## Inline tags

| Tag | Purpose |
|---|---|
| `{@link Target}` or `{@link Target | label}` | An explicit hyperlink/cross-reference to another API item (TSDoc requires this tag to make a link) |
| `{@inheritDoc Target}` | Inherit the summary/`@remarks`/params from a base member. When used, the comment must **not** also declare its own summary or `@remarks` |
| `{@label}` | Label a declaration so it can be referenced by a selector in declaration-reference notation |

## Modifier tags

| Tag | Marks |
|---|---|
| `@public` | API item is public (part of the supported surface) |
| `@internal` | Not intended for third-party use; tooling may trim it from a public release |
| `@beta` | Released experimentally for feedback; contract may change, not for production |
| `@alpha` | Earlier-stage than beta; intended for eventual third-party use but not yet released; may be trimmed |
| `@experimental` | Synonym alias for `@beta` in the standard set |
| `@readonly` | Documented as read-only even if the type system would allow writes |
| `@override` | Member overrides a base member (prefer TS's `override` keyword in source; reserve the tag for docs generated from `.d.ts`) |
| `@sealed` | Class must not be subclassed / member must not be overridden |
| `@virtual` | Member may be overridden by subclasses |
| `@eventProperty` | Property returns an event object handlers can attach to |

## Document structure

- **Summary** — everything before the first block tag is the summary section. Keep it brief; doc sites list it in API indexes.
- **`@remarks`** — the detailed section after the summary; may be lengthy.
- **Release tags** (`@public`/`@beta`/`@alpha`/`@internal`) are typically driven by an API-extraction tool (e.g. API Extractor) to control what a published package exposes.

## Custom tags

A project may define additional tags via `tsdoc.json` (the `@microsoft/tsdoc-config` package), declaring each new tag's kind. Without such a declaration, an unrecognized `@tag` produces a parser warning — do not invent ad-hoc tags in a project that hasn't declared them.
