# Serialization (Pydantic v2)

Load when customizing model output.

## `model_dump()` / `model_dump_json()`

`model_dump()` returns a dict; `model_dump_json()` returns a JSON string
(`model_dump_json` also takes `indent`). Shared keyword args:

| kwarg | effect |
|---|---|
| `mode` | `"python"` (default, native types) or `"json"` (JSON-safe types in a dict) |
| `include` / `exclude` | field name set (or nested dict) to keep / drop |
| `exclude_unset` | omit fields the caller never explicitly set — PATCH-style payloads |
| `exclude_defaults` | omit fields still equal to their default |
| `exclude_none` | omit fields whose value is `None` |
| `by_alias` | emit field aliases instead of Python names |
| `round_trip` | keep data able to re-validate back into the model |
| `warnings` | control serialization warnings |

```python
m.model_dump()                                   # {'a': 1, 'b': None}
m.model_dump(mode="json")                         # datetimes -> ISO strings, etc.
m.model_dump(exclude={"secret"})
m.model_dump(exclude_unset=True)                  # only what was set
m.model_dump_json(by_alias=True, exclude_none=True, indent=2)
```

Field-level `exclude=True` on `Field(...)` always wins over call-time options.

## `@field_serializer`

Customize one (or several) field's output. `mode="plain"` (default) replaces the
field's serialization; `mode="wrap"` wraps the default with a handler.

```python
from datetime import datetime
from pydantic import BaseModel, field_serializer

class Event(BaseModel):
    when: datetime

    @field_serializer("when")
    def ser_when(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d")
```

An optional `info` parameter gives serialization context (`info.context`,
`info.by_alias`, etc.).

## `@model_serializer`

Replace serialization for the **whole** model (return the dict yourself). Use
sparingly — prefer field serializers and dump options first.

## `@computed_field`

Expose a derived value in the output. Stack it **above** `@property`.

```python
from pydantic import BaseModel, computed_field

class Box(BaseModel):
    w: float
    h: float

    @computed_field
    @property
    def area(self) -> float:
        return self.w * self.h

# Box(w=2, h=3).model_dump() -> {'w': 2.0, 'h': 3.0, 'area': 6.0}
```

## Aliases

- `alias` — one name used for both validation input and serialization output.
- `validation_alias` — accepted on input only.
- `serialization_alias` — emitted on output only (with `by_alias=True`).
- `AliasChoices("a", "b")` — accept any of several input names for one field.

```python
from typing import Annotated
from pydantic import BaseModel, Field, AliasChoices

class P(BaseModel):
    user_id: Annotated[int, Field(validation_alias=AliasChoices("userId", "uid"),
                                  serialization_alias="userId")]
```

To accept BOTH the field name and its alias on input, set
`ConfigDict(validate_by_name=True, validate_by_alias=True)` (2.11+; the older
`populate_by_name=True` still works in 2.x).
