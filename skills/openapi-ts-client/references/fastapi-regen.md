# FastAPI integration + regeneration workflow

Load when integrating with FastAPI or setting up regeneration.

## FastAPI is the recommended pairing

FastAPI's own docs recommend `@hey-api/openapi-ts` as the purpose-built TypeScript client generator. FastAPI ≥ 0.99 emits OpenAPI 3.1 — exactly what hey-api targets. The contract is served at `/openapi.json` on the running app.

```sh
npx @hey-api/openapi-ts -i http://localhost:8000/openapi.json -o src/client
```

## The operationId naming problem (fix at the source)

By default FastAPI builds verbose `operationId`s, so generated methods look like `createItemItemsPost`. Fix it on the FastAPI side so every regenerate is clean — set `generate_unique_id_function`:

```python
from fastapi import FastAPI
from fastapi.routing import APIRoute

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
```

This yields `tag-name` operationIds. FastAPI's docs also show an optional preprocess step that strips the `tag-` prefix from a saved `openapi.json` before generating, for even cleaner names:

```python
import json
from pathlib import Path

p = Path("./openapi.json")
spec = json.loads(p.read_text())
for path_item in spec["paths"].values():
    for op in path_item.values():
        if not isinstance(op, dict) or "tags" not in op:
            continue  # skip non-operation keys (parameters, summary, …)
        tag = op["tags"][0]
        op["operationId"] = op["operationId"][len(f"{tag}-"):]
p.write_text(json.dumps(spec))
```

Requires a tag per route (a common FastAPI convention). Keep this on the backend so the contract — not the frontend — owns naming (consistency-with-shipped-code).

## Regeneration workflow

1. **Script it.** `"gen:api": "openapi-ts"` in `package.json`; never hand-run divergent commands per machine.
2. **Pick the input strategy:**
   - *Live URL* (`http://localhost:8000/openapi.json`) — always current, but needs the server up and changes silently.
   - *Committed snapshot* (`./openapi.json`) — reproducible and reviewable in diffs, but must be refreshed deliberately when the API changes.
3. **CI drift check.** Regenerate in CI and fail if the working tree changed — this catches a stale committed client:
   ```sh
   npm run gen:api && git diff --exit-code src/client   # match your configured output path
   ```

## Commit vs gitignore the generated client (trade-off)

- **Commit it:** the diff shows API changes in review, the build needs no codegen step, and editors get types immediately — but it adds churn and must be kept fresh (the CI drift check enforces this).
- **Gitignore it:** no churn, but every build/CI/editor setup must run codegen first, and the generated output isn't reviewable in diffs.

Either is valid; decide per project. If you commit it, the CI drift check is mandatory.
