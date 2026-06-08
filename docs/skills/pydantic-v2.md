# pydantic-v2

> Write correct, idiomatic, **current** Pydantic v2 — `BaseModel` with typed +
> constrained fields, `@field_validator` / `@model_validator`, `model_dump*`
> serialization, `model_config = ConfigDict(...)`, `pydantic-settings`,
> `TypeAdapter`, enums / `Literal` / discriminated unions — and modernize any
> v1-era idiom (`class Config`, `.dict()`/`.json()`, `@validator`,
> `@root_validator`, `.parse_obj()`) it meets. It is the standalone-Pydantic
> knowledge delta; framework request/response wiring belongs to `fastapi`.

**Skill file:** [`skills/pydantic-v2/SKILL.md`](../../skills/pydantic-v2/SKILL.md)
**Version:** 1.0.0

## Purpose

Gives an agent the post-v1 Pydantic API plus the pitfalls that bite when v1
muscle memory leaks in, so the data models it writes are current and correct
rather than a working-but-deprecated mix. It is scoped to **standalone
Pydantic** — models, fields, validators, serialization, config,
`pydantic-settings`, `TypeAdapter`, and structured/union types — and it
deliberately does not re-teach framework mechanics: when those models back an
HTTP API, the `fastapi` skill governs `response_model` and the wiring.

## When to activate

- ✅ Defining a data model, config object, or DTO with typed fields + constraints.
- ✅ Writing field- or model-level validation, custom serialization, or computed fields.
- ✅ Loading app configuration from env vars / `.env` with `pydantic-settings`.
- ✅ Validating non-model shapes in bulk (`list[Model]`, dicts, primitives) with `TypeAdapter`.
- ✅ Modernizing v1-era code (`class Config`, `.dict()`, `@validator`) to v2.

### When NOT to activate

- FastAPI request/response wiring or `response_model` — use the `fastapi` skill.
- Pydantic-AI agents or Logfire instrumentation — different products, out of scope.

## Workflow

The skill walks an 8-step path, each step stating the current-v2 idiom:

| Step | Does |
|---|---|
| 1 Define | fields as type hints; `Optional[x]` is **not** a default; mutable defaults via `default_factory`; validate untrusted input with the `model_validate*` classmethods |
| 2 Constrain | `Annotated[T, Field(...)]` for `gt`/`ge`/`min_length`/`pattern`/… |
| 3 Validate | `@field_validator` (with `@classmethod` beneath) + `@model_validator(mode="after")` on `self` |
| 4 Serialize | `model_dump()` / `model_dump_json()` with `include`/`exclude`/`exclude_unset`/`by_alias`; `@field_serializer`, `@computed_field` |
| 5 Configure | `model_config = ConfigDict(...)` — never a nested `class Config` |
| 6 Settings | `BaseSettings` from the separate `pydantic-settings` package + `SettingsConfigDict` |
| 7 Structure | enums / `Literal`, discriminated unions via `Field(discriminator=...)`, `TypeAdapter` for non-model shapes |
| 8 Errors | `ValidationError.errors()` (`type`/`loc`/`msg`/`input`/`url`) |

## Hard rules it enforces

- **v2 API only** — `ConfigDict`, `model_dump*`, `model_validate*`,
  `@field_validator`/`@model_validator`, `model_json_schema()`; never
  `class Config`, `.dict()`/`.json()`, `@validator`/`@root_validator`,
  `.parse_obj()`/`.parse_raw()`, or `.schema()`.
- `@field_validator` carries `@classmethod` directly beneath it; the after-mode
  `@model_validator` operates on `self` and does not.
- `Optional[x]` only marks nullable — supply a default explicitly if optional.
- Mutable defaults via `default_factory`, never a literal `[]`/`{}`.
- `BaseSettings` imports from `pydantic_settings`, not `pydantic`.

## Progressive disclosure (`references/`)

- `references/validators.md` — all validator modes (`before`/`after`/`plain`/`wrap`), `ValidationInfo`, the `@classmethod` rule.
- `references/serialization.md` — every `model_dump*` kwarg, `@field_serializer`/`@model_serializer`/`@computed_field`, alias kinds.
- `references/settings.md` — `pydantic-settings` depth: nested settings, `env_nested_delimiter`, source precedence, `secrets_dir`.
- `references/migration-v1-to-v2.md` — the full v1→v2 rename table + behavior changes.
- `references/sources.md` — research provenance.

## Limitations

- **Standalone Pydantic only** — framework request/response handling is the `fastapi` skill's job; this skill defines the models, the framework consumes them.
- **Current-2.x idioms** — notes 2.11+ shifts (e.g. `validate_by_name`/`validate_by_alias` over `populate_by_name`); refresh as Pydantic evolves toward v3.

## License

MIT — part of the [`agent-skills`](https://github.com/bm629/agent-skills) collection.
