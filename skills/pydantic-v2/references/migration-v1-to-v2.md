# Migrating v1 idioms to v2

Load when modernizing Pydantic v1 code. Every left-column form is v1 and should
be replaced by the right-column v2 form. Many v1 forms still "work" with
deprecation warnings — they are still wrong style and lose v2 features.

## Method / attribute renames

| v1 | v2 |
|---|---|
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj(obj)` | `.model_validate(obj)` |
| `.parse_raw(data)` | `.model_validate_json(data)` |
| `.schema()` | `.model_json_schema()` |
| `.construct(...)` | `.model_construct(...)` |
| `.copy(...)` | `.model_copy(...)` |
| `.update_forward_refs()` | `.model_rebuild()` |
| `__fields__` | `model_fields` |
| `.parse_file(path)` | read the file yourself, then `.model_validate_json(...)` |

## Validators

| v1 | v2 |
|---|---|
| `@validator("x")` | `@field_validator("x")` (+ `@classmethod` beneath) |
| `@root_validator` | `@model_validator(mode="before" \| "after")` |
| `@validate_arguments` | `@validate_call` |
| validator `pre=True` | `mode="before"` |
| validator `pre=False` | `mode="after"` (default) |

## Config

Replace the nested `class Config` with the class attribute
`model_config = ConfigDict(...)`.

| v1 `Config` option | v2 `ConfigDict` option |
|---|---|
| `orm_mode = True` | `from_attributes=True` |
| `allow_population_by_field_name = True` | `populate_by_name=True` (2.11+: `validate_by_name=True`) |
| `allow_mutation = False` | `frozen=True` (inverted sense) |
| `anystr_strip_whitespace = True` | `str_strip_whitespace=True` |
| `min_anystr_length` / `max_anystr_length` | `str_min_length` / `str_max_length` |
| `schema_extra` | `json_schema_extra` |
| `validate_all` | `validate_default` |

```python
# v1
class User(BaseModel):
    name: str
    class Config:
        orm_mode = True
        allow_mutation = False

# v2
from pydantic import BaseModel, ConfigDict
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    name: str
```

## Moved packages

| v1 import | v2 import |
|---|---|
| `from pydantic import BaseSettings` | `from pydantic_settings import BaseSettings` |
| `pydantic.color.Color` | `pydantic_extra_types.color.Color` |
| `pydantic.types.PaymentCardNumber` | `pydantic_extra_types.PaymentCardNumber` |

## Behavior changes that bite

- **`Optional[x]` is no longer an implicit `None` default.** In v1 a field typed
  `Optional[int]` defaulted to `None`; in v2 it is still **required** unless you
  write `int | None = None`. This is the most common silent v1→v2 break.
- **Constrained types removed.** `conint`, `constr`, `ConstrainedInt`, etc. give
  way to `Annotated[int, Field(gt=0)]` / `Annotated[str, Field(max_length=10)]`.
- **`GenericModel` gone.** Subclass `BaseModel, Generic[T]` directly.
- **Default coercion is lax.** `"123"` → `123`. Opt into strictness with
  `ConfigDict(strict=True)` or `Field(strict=True)`.
