# pydantic-settings (Pydantic v2)

Load when loading application configuration from the environment.

## Install + import

`BaseSettings` is **not** in core `pydantic` in v2 — it moved to the separate
`pydantic-settings` package.

```bash
pip install pydantic-settings   # or: uv add pydantic-settings
```

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
```

A `BaseSettings` subclass reads each field from the environment when no value is
passed to the initializer; a field with no default becomes a required env var.

## `SettingsConfigDict` options

| option | effect |
|---|---|
| `env_prefix` | prefix on env var names (`env_prefix="APP_"` → field `api_key` reads `APP_API_KEY`) |
| `env_file` | path (or tuple of paths) to a dotenv file |
| `env_file_encoding` | encoding for the dotenv file (e.g. `"utf-8"`) |
| `case_sensitive` | match env var case exactly (default `False`) |
| `extra` | `"ignore"` (default for settings) / `"allow"` / `"forbid"` |
| `env_nested_delimiter` | delimiter for populating nested-model fields from flat env vars |
| `secrets_dir` | directory of secret files (one file per field) |

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", env_file_encoding="utf-8",
    )
    api_key: str           # required → APP_API_KEY
    host: str = "127.0.0.1"
    port: int = 8000       # "8000" from the env is coerced to int

settings = Settings()
```

## Source precedence

Highest priority wins, in this order:

1. Arguments passed to the initializer (`Settings(port=9000)`)
2. Environment variables
3. Values from the dotenv (`.env`) file
4. Files in the `secrets_dir`

So an explicit env var always overrides a `.env` entry.

## Nested settings

Nest a model and populate it from flat env vars with `env_nested_delimiter`:

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class DbConfig(BaseModel):
    host: str
    port: int

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    db: DbConfig

# reads DB__HOST and DB__PORT from the environment
```

To override which sources are consulted and in what order, override the
`settings_customise_sources` classmethod (advanced — consult the official docs).
