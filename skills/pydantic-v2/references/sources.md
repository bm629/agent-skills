# Sources — pydantic-v2

Research provenance for this skill. Synthesized via skill-forge v2: a broad
discovery sweep, comprehensive deep-research against the official docs, and a
fact-check pass. All code paraphrased — no source text copied verbatim.

## Discovery sweep (skill-forge Step 2.1)

Searched the published-skill ecosystem (`npx skills find`) across six distinct
query angles: `pydantic`; `data validation python`; `pydantic v2`;
`pydantic settings serialization`; `python models schema`; `luxor pydantic`.

Install-count pre-filter (<1K = not deep-read) applied:

- The only candidate clearing 1K installs was `pydantic/skills@building-pydantic-ai-agents`
  (~1.5K) — but it is Pydantic-AI, which is out of scope for a general v2 skill.
- All general-Pydantic candidates were under 1K (`jiatastic/open-python-skills@pydantic`
  ~131, `sickn33/...@pydantic-models-py` ~128, `midudev/autoskills@pydantic` ~31)
  and none is official/maintainer-authored for general v2.
- Forge-vs-install gate: no on-target survivor cleared the bar to recommend-and-return,
  so the decision was to forge a clean general skill.

## Source material (consumed, then generalized)

- `manutej/luxor-claude-marketplace@pydantic` — comprehensive + current-v2 but
  customer-support-framed. Consumed as source material (sanitized via
  `external-content-sanitizer`; no injection found), then fully generalized:
  all customer-support persona/framing/examples stripped; only general Pydantic
  v2 knowledge retained. Its dict-style `model_config = {...}` examples were
  standardized to `ConfigDict(...)` here.

## Official docs (primary, citation-grounded)

Deep-research (the `deep-research` skill, NOT a WebSearch-only shortcut) verified
every API name against the official Pydantic docs. The docs are served from the
`pydantic.dev/docs/validation/latest/...` host (the older `docs.pydantic.dev/latest/...`
paths 301-redirect there). Pages consulted:

- Migration guide (`.../get-started/migration/`) — the full v1→v2 rename table,
  the `Optional[x]` behavior change, moved packages.
- Models (`.../concepts/models/`) — `model_validate` / `model_validate_json` /
  `model_construct` classmethods, `model_fields`, `model_copy`, required-vs-default.
- Fields (`.../concepts/fields/`) — `Field` constraints, the `Annotated` idiom,
  alias kinds, `default_factory`.
- Validators (`.../concepts/validators/`) — `@field_validator` modes
  (before/after/plain/wrap) + the `@classmethod` rule, `@model_validator`,
  `ValidationInfo`.
- Serialization (`.../concepts/serialization/`) — `model_dump*` kwargs,
  `@field_serializer`, `@model_serializer`, `@computed_field`.
- Config (`.../concepts/config/`) — `model_config = ConfigDict(...)` is current;
  `class Config` deprecated.
- pydantic-settings (`.../concepts/pydantic_settings/`) — `BaseSettings` +
  `SettingsConfigDict`, env sources, precedence, `env_nested_delimiter`.
- Unions (`.../concepts/unions/`) — discriminated unions via
  `Field(discriminator=...)` with `Literal` tags.
- TypeAdapter (`.../concepts/type_adapter/`) — `validate_python` / `validate_json`
  / `dump_python` / `dump_json`; not usable as a field annotation.

## Verified current-vs-early-2.x note

- Pydantic **2.11** introduced `validate_by_name` + `validate_by_alias` on
  `ConfigDict`; `populate_by_name` is pending deprecation in v3 but still works in
  2.x. Triangulated via the official 2.11 release announcement and the upstream
  alias-config PR. The skill teaches the current pair while noting `populate_by_name`
  remains valid on current 2.x.

## Out of scope (excluded by design)

Pydantic-AI, Logfire, and FastAPI framework internals — the `fastapi` skill owns
framework request/response and `response_model` mechanics; this skill references
it rather than duplicating it.
