---
name: pydantic-v2
description: >
  Use when defining, validating, serializing, or configuring data with
  Pydantic v2 in Python — BaseModel, Field constraints, field/model
  validators, model_dump serialization, pydantic-settings, TypeAdapter,
  enums, Literal, and discriminated unions — or when fixing code that
  still uses v1-era idioms (class Config, .dict()/.json(), @validator).
  Produces correct, idiomatic, current Pydantic v2 code. Keywords:
  pydantic, BaseModel, ConfigDict, model_validate, validator, settings.
extensions:
  claude:
    when_to_use: "Writing or fixing Pydantic v2 models, validators, serialization, or settings."
  copilot: {}
  cursor: {}
  gemini: {}
  codex: {}
version: "1.0.0"
forge:
  status: reviewed
  forged: 2026-06-08
  reviewed: 2026-06-08
---

# Pydantic v2

## Overview

Pydantic v2 validates and serializes data from Python type hints. A `BaseModel`
subclass declares fields as annotations; constructing it validates and coerces
the input, and the instance round-trips to dicts/JSON via `model_dump*`. This
skill is the knowledge delta for writing **current** v2 — the post-v1 API
(`model_config = ConfigDict(...)`, `model_dump()`, `@field_validator`) plus the
pitfalls that bite when v1 muscle memory leaks in. It covers standalone Pydantic:
models, fields, validators, serialization, config, `pydantic-settings`,
`TypeAdapter`, and structured/union types. For framework-level request/response
modeling and `response_model`, see the `fastapi` skill — this skill does not
duplicate framework mechanics.

## When to activate

- ✅ Defining a data model, config object, or DTO with typed fields + constraints.
- ✅ Writing field- or model-level validation, custom serialization, or computed fields.
- ✅ Loading app configuration from env vars / `.env` with `pydantic-settings`.
- ✅ Validating non-model shapes in bulk (`list[Model]`, dicts, primitives) with `TypeAdapter`.
- ✅ Modernizing v1-era code (`class Config`, `.dict()`, `@validator`) to v2.

**Do NOT activate when:**

- The task is FastAPI request/response wiring or `response_model` — use the `fastapi` skill.
- The topic is Pydantic-AI agents or Logfire instrumentation — different products, out of scope.

## Workflow

### Step 1: Define the model with type hints

A field is `name: Type`. With **no default it is required**; a default makes it
optional. Critically in v2, `Optional[int]` (i.e. `int | None`) **only marks the
field nullable — it does NOT supply a default**; omit the default and the field
is still required. Use `default_factory` for mutable defaults (never a literal
`[]`/`{}`, which is shared across instances).

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int                                   # required
    name: str = "anon"                        # optional, has default
    nickname: str | None = None               # nullable AND optional (explicit default)
    tags: list[str] = Field(default_factory=list)  # safe mutable default
```

Construct from trusted kwargs (`User(id=1)`) or validate untrusted input with
the **classmethods** `User.model_validate(obj)` (dict / object) and
`User.model_validate_json(data)` (JSON str/bytes). `model_construct(**data)`
skips validation — trusted data only.

### Step 2: Constrain fields with `Annotated[..., Field(...)]`

Prefer the `Annotated` style; it keeps the type honest and composes cleanly.
`Field` supplies `gt`/`ge`/`lt`/`le`/`multiple_of` (numeric),
`min_length`/`max_length`/`pattern` (string), plus `default`, `default_factory`,
`description`, `alias`, and `exclude`.

```python
from typing import Annotated
from pydantic import BaseModel, Field

class Account(BaseModel):
    balance: Annotated[int, Field(ge=0)]
    handle: Annotated[str, Field(min_length=3, max_length=32, pattern=r"^[a-z0-9_]+$")]
    score: Annotated[float, Field(default=0.0, le=100.0)]
```

### Step 3: Validate with `@field_validator` / `@model_validator`

Field validators run per-field; model validators run across fields. See
[`references/validators.md`](references/validators.md) for `before`/`after`/
`plain`/`wrap` modes, `ValidationInfo`, and the `@classmethod` rule.

```python
from typing_extensions import Self
from pydantic import BaseModel, field_validator, model_validator

class Signup(BaseModel):
    email: str
    password: str
    password_repeat: str

    @field_validator("email", mode="after")
    @classmethod
    def lowercase(cls, v: str) -> str:
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("passwords do not match")
        return self
```

### Step 4: Serialize with `model_dump*`

`model_dump()` → dict, `model_dump_json()` → JSON string. Shape with
`include` / `exclude` / `exclude_unset` / `exclude_defaults` / `exclude_none` /
`by_alias` / `mode`. Customize with `@field_serializer` and add derived output
with `@computed_field`. See [`references/serialization.md`](references/serialization.md).

```python
user.model_dump()                              # dict, python types
user.model_dump(exclude={"password"})          # drop a field
user.model_dump(exclude_unset=True)            # only explicitly-set fields (PATCH-style)
user.model_dump_json(by_alias=True, exclude_none=True, indent=2)
```

### Step 5: Configure with `model_config = ConfigDict(...)`

The class attribute `model_config` (NOT a nested `class Config`) holds a
`ConfigDict`. Common options: `strict`, `from_attributes` (read ORM objects),
`validate_assignment`, `use_enum_values`, `extra` (`"ignore"`/`"allow"`/
`"forbid"`), `frozen`, `str_strip_whitespace`. For alias-by-name, current 2.11+
prefers `validate_by_name=True` (with `validate_by_alias=True`) — see Gotchas.

```python
from pydantic import BaseModel, ConfigDict

class Row(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True)
    id: int
    label: str

obj = Row.model_validate(orm_row)   # from_attributes reads attributes off an ORM object
```

### Step 6: Load config with `pydantic-settings`

`BaseSettings` lives in the **separate `pydantic-settings` package** (not core
`pydantic`). It reads fields from environment variables and `.env`. Configure
via `SettingsConfigDict`. See [`references/settings.md`](references/settings.md)
for nested settings and source precedence.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env",
                                      env_file_encoding="utf-8")
    api_key: str                  # required → from APP_API_KEY
    host: str = "127.0.0.1"
    port: int = 8000              # coerced from the string env value

settings = Settings()             # reads env / .env at construction
```

### Step 7: Structure — enums, Literal, unions, `TypeAdapter`

Nest models by using one as another's field type. Use `Enum` (subclass
`str, Enum` for JSON-friendly values) or `Literal` for fixed choices.
**Discriminated unions** dispatch on a tag field via `Field(discriminator=...)`.
Validate non-model shapes (lists, dicts, primitives) with `TypeAdapter` — it is
the v2-idiomatic choice over `RootModel` for bulk/standalone validation.

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter

class Cat(BaseModel):
    kind: Literal["cat"]
    lives: int

class Dog(BaseModel):
    kind: Literal["dog"]
    good_boy: bool = True

class Owner(BaseModel):
    pet: Annotated[Cat | Dog, Field(discriminator="kind")]

cats = TypeAdapter(list[Cat]).validate_python([{"kind": "cat", "lives": 9}])
```

### Step 8: Handle `ValidationError`

`model_validate*` and construction raise `ValidationError` on bad input.
`.errors()` returns a list of dicts (`type`, `loc`, `msg`, `input`, `url`);
`.error_count()` returns the count; `.json()` serializes them.

```python
from pydantic import ValidationError

try:
    User.model_validate({"id": "not-an-int"})
except ValidationError as e:
    for err in e.errors():
        print(".".join(map(str, err["loc"])), err["type"], err["msg"])
```

## Rules

**Hard rules (never violate):**

- **v2 API only.** `model_config = ConfigDict(...)`, `model_dump()` /
  `model_dump_json()`, `model_validate()` / `model_validate_json()`,
  `@field_validator` / `@model_validator`, `model_json_schema()`.
  Never `class Config`, `.dict()` / `.json()`, `@validator` / `@root_validator`,
  `.parse_obj()` / `.parse_raw()`, or `.schema()`.
- **`@field_validator` must have `@classmethod` directly beneath it.**
  `@model_validator(mode="after")` operates on `self` and does NOT.
- **`Optional[x]` is not a default.** Provide one explicitly (`x | None = None`)
  if the field should be optional.
- **Mutable defaults via `default_factory`,** never a literal `[]` / `{}` / `dict()`.
- **`BaseSettings` imports from `pydantic_settings`,** not `pydantic`.
- **Don't use `TypeAdapter` as a field annotation** inside a `BaseModel`; use it
  standalone for validating non-model types.

**Preferences (override-able):**

- Prefer `Annotated[T, Field(...)]` over assigning `Field(...)` as the default value.
- Separate request and response models rather than reusing one model for both.
- Reuse a `TypeAdapter` instance (build once, validate many) for hot paths.

## Gotchas

- **`populate_by_name` is on the way out.** In Pydantic **2.11+**, prefer
  `ConfigDict(validate_by_name=True, validate_by_alias=True)`. `populate_by_name`
  still works in 2.x (pending deprecation in v3) — fine on older 2.x, but write
  the new pair on current versions.
- **`class Config` silently still works but is deprecated** — it won't error, so
  v1 code "looks fine" yet is wrong style and loses v2 options. Convert to
  `model_config = ConfigDict(...)`.
- **Forgetting `@classmethod` on a `@field_validator`** raises at class-definition
  time or misbehaves — the decorator order is `@field_validator(...)` on top,
  `@classmethod` directly under it.
- **`model_config` as a plain `dict` works but loses type-checker help** — use the
  `ConfigDict(...)` constructor so IDEs and `ty`/mypy validate the keys.
- **Lax coercion surprises.** By default `"123"` coerces to `123`. If you need
  exactness, set `ConfigDict(strict=True)` (or `Field(strict=True)` per field).
- **`exclude_unset` vs `exclude_defaults`.** `exclude_unset` drops fields the
  caller never set (ideal for PATCH bodies); `exclude_defaults` drops fields equal
  to their default even if set. They are not interchangeable.

## Anti-patterns

- **"It's just a small model, I'll use the old `.dict()`."** No — `.dict()` is
  removed-in-spirit/deprecated; use `model_dump()`. Mixed v1/v2 idioms are the
  top source of broken Pydantic code.
- **Reaching for `@root_validator`** because you "remember it" — it does not exist
  in v2; use `@model_validator(mode="before"|"after")`.
- **Wrapping a bare type in a one-field `RootModel`** to validate a list/dict —
  use `TypeAdapter(list[T])` instead.
- **Re-implementing FastAPI request/response handling here** — that belongs to the
  `fastapi` skill; this skill defines the models, the framework consumes them.

## Output

Correct, current Pydantic v2 source: model classes with `ConfigDict`, typed +
constrained fields, `@field_validator`/`@model_validator` validation,
`model_dump*` serialization, `pydantic-settings` config classes, and
`TypeAdapter`/discriminated-union structures — free of any v1-era idiom. The
consumer is whatever code or workflow phase needs validated, serializable data
models; when those models back an HTTP API, the `fastapi` skill governs the
framework wiring.

## Related

- `fastapi` — framework specifics: request/response models, `response_model`,
  dependency-injected validation. This skill defines the models; `fastapi`
  consumes them. Do not duplicate framework mechanics here.
- Official docs (provenance): see [`references/sources.md`](references/sources.md).

## Progressive disclosure

Heavy detail lives in `references/`, loaded on demand:

- [`references/validators.md`](references/validators.md) — load when writing
  validators: all `@field_validator`/`@model_validator` modes, `ValidationInfo`,
  the `@classmethod` rule, before/after ordering.
- [`references/serialization.md`](references/serialization.md) — load when
  customizing output: every `model_dump*` kwarg, `@field_serializer`,
  `@model_serializer`, `@computed_field`, alias kinds (`validation_alias` /
  `serialization_alias` / `AliasChoices`).
- [`references/settings.md`](references/settings.md) — load for `pydantic-settings`
  depth: nested settings, `env_nested_delimiter`, source precedence, `secrets_dir`.
- [`references/migration-v1-to-v2.md`](references/migration-v1-to-v2.md) — load
  when modernizing v1 code: the full rename table and behavior changes.
- [`references/sources.md`](references/sources.md) — research provenance.

## Body budget

- `description` ≤ 1,024 chars (respected).
- Body ~290 lines / well under the 5,000-token soft target.
- Reference files each well under the 10k-token warn threshold.
