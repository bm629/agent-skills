# Validators (Pydantic v2)

Load when writing field- or model-level validation.

## `@field_validator`

Runs on a single field (or several, or `'*'` for all). **Must** be paired with
`@classmethod`, with the decorator order `@field_validator(...)` on top and
`@classmethod` directly beneath it.

```python
from pydantic import BaseModel, field_validator

class Model(BaseModel):
    number: int

    @field_validator("number", mode="after")
    @classmethod
    def is_even(cls, value: int) -> int:
        if value % 2 == 1:
            raise ValueError(f"{value} is not even")
        return value
```

### Modes

- **`mode="after"`** (default) — runs *after* Pydantic's own parsing/coercion.
  `value` is already the field's type. Use for most business rules.
- **`mode="before"`** — runs *before* parsing. `value` is the raw input; you may
  reshape it (e.g. split a string into a list) before Pydantic validates.
- **`mode="plain"`** — replaces Pydantic's validation entirely; no inner
  validation runs after yours.
- **`mode="wrap"`** — most flexible; you receive a `handler` callable and decide
  whether/when to call the inner validator, running logic before and after it.

### Multiple fields

```python
@field_validator("first", "last", mode="after")
@classmethod
def strip(cls, v: str) -> str:
    return v.strip()

@field_validator("*")          # every field
@classmethod
def not_empty(cls, v): ...
```

### `ValidationInfo`

Add an optional second parameter typed `ValidationInfo` to reach context:

- `info.data` — already-validated fields (those declared *earlier*), field
  validators only.
- `info.field_name` — the field being validated.
- `info.context` — user data passed via `Model.model_validate(obj, context=...)`.

```python
from pydantic import field_validator, ValidationInfo

@field_validator("confirm", mode="after")
@classmethod
def matches(cls, v: str, info: ValidationInfo) -> str:
    if v != info.data.get("password"):
        raise ValueError("does not match password")
    return v
```

(Cross-field checks are usually cleaner as a `@model_validator(mode="after")`,
since `info.data` only holds fields validated *before* the current one.)

## `@model_validator`

Runs across the whole model.

- **`mode="before"`** — receives the **raw input** (often a dict) before any
  field validation. **Must** be `@classmethod`. Return the (possibly reshaped)
  data.
- **`mode="after"`** — runs on the **validated instance** (`self`); returns
  `self`. Does **not** take `@classmethod`. Best place for cross-field rules.

```python
from typing import Any
from typing_extensions import Self
from pydantic import BaseModel, model_validator

class Range(BaseModel):
    low: int
    high: int

    @model_validator(mode="before")
    @classmethod
    def coerce(cls, data: Any) -> Any:
        if isinstance(data, dict) and "high" not in data:
            data["high"] = data.get("low", 0)
        return data

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.high < self.low:
            raise ValueError("high must be >= low")
        return self
```

## Raising errors

Raise `ValueError` (or `AssertionError`) inside a validator — Pydantic wraps it
into a `ValidationError` with the proper `loc`. Do not raise `ValidationError`
directly from inside a validator.
