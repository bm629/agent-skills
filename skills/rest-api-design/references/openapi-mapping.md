# Design → OpenAPI 3.1 contract mapping

Load when expressing a finished REST design as a contract. This is the **mapping + one worked contract**, not an OpenAPI authoring tutorial — deep authoring, linting, mock servers, and SDK codegen are a separate concern to hand off.

## Why 3.1 (not 3.0)

- **OpenAPI 3.1 aligns fully with JSON Schema 2020-12.** 3.0 used a modified JSON-Schema subset; 3.1 is the real thing.
- **Nullability:** the 3.0 `nullable: true` keyword is **gone** in 3.1. Express it as a type union: `type: ["string", "null"]`. A stray `nullable: true` in a 3.1 doc is silently ignored.
- A 3.1 document needs at least one of `paths`, `components`, or `webhooks`. The new top-level `webhooks` object describes callbacks the API *sends* (out of scope here, but the reason a contract can exist without `paths`).
- Default to 3.1 for new contracts. Use 3.0 only when a required tool in the chain hasn't caught up.

## The mapping

| Design decision | OpenAPI element |
|---|---|
| Resource collection / item | a `paths` entry (`/orders`, `/orders/{orderId}`) |
| HTTP method on a resource | an operation under the path (`get`, `post`, `patch`, `delete`) |
| Status code per outcome | keys under the operation's `responses` (`"201"`, `"422"`, `"429"`) |
| Entity / envelope / problem shape | `components.schemas` (referenced by `$ref`) |
| Reused error/success responses | `components.responses` (`$ref` from each operation) |
| Reused query/path params (page, limit, id) | `components.parameters` |
| Auth scheme | `components.securitySchemes` + a `security` requirement |
| problem+json error body | a response with `content: application/problem+json` → a `Problem` schema |
| Create returns Location | a `headers` entry on the `"201"` response |

Reuse aggressively with `$ref` — define `Problem`, `Pagination`, and each error response once and reference them everywhere. Add `examples` so consumers see real payloads.

## One worked contract

A minimal but complete `orders` surface: list (cursor-paginated), create (201 + Location), get, with problem+json errors and bearer auth.

```yaml
openapi: 3.1.0
info:
  title: Orders API
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
security:
  - bearerAuth: []
paths:
  /orders:
    get:
      operationId: listOrders
      summary: List orders (cursor-paginated)
      parameters:
        - $ref: "#/components/parameters/Cursor"
        - $ref: "#/components/parameters/Limit"
      responses:
        "200":
          description: A page of orders
          content:
            application/json:
              schema: { $ref: "#/components/schemas/OrderList" }
        "401": { $ref: "#/components/responses/Unauthorized" }
        "429": { $ref: "#/components/responses/TooManyRequests" }
    post:
      operationId: createOrder
      summary: Create an order
      parameters:
        - name: Idempotency-Key
          in: header
          schema: { type: string }
          description: Opaque key making a retried create safe.
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/OrderCreate" }
      responses:
        "201":
          description: Order created
          headers:
            Location:
              description: URL of the created order
              schema: { type: string, format: uri }
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Order" }
        "401": { $ref: "#/components/responses/Unauthorized" }
        "422": { $ref: "#/components/responses/ValidationProblem" }
  /orders/{orderId}:
    parameters:
      - name: orderId
        in: path
        required: true
        schema: { type: string }
    get:
      operationId: getOrder
      summary: Get one order
      responses:
        "200":
          description: The order
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Order" }
        "401": { $ref: "#/components/responses/Unauthorized" }
        "404": { $ref: "#/components/responses/NotFound" }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  parameters:
    Cursor:
      name: cursor
      in: query
      schema: { type: string }
      description: Opaque pagination cursor.
    Limit:
      name: limit
      in: query
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
  schemas:
    Order:
      type: object
      required: [id, total_cents, status, created_at]
      properties:
        id: { type: string, readOnly: true }
        total_cents: { type: integer, minimum: 0 }
        status: { type: string, enum: [pending, paid, shipped, cancelled] }
        note: { type: ["string", "null"] }      # 3.1 nullability — NOT nullable:true
        created_at: { type: string, format: date-time, readOnly: true }
    OrderCreate:
      type: object
      required: [total_cents]
      properties:
        total_cents: { type: integer, minimum: 1 }
        note: { type: ["string", "null"] }
    OrderList:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items: { $ref: "#/components/schemas/Order" }
        pagination:
          type: object
          required: [has_more]
          properties:
            next_cursor: { type: ["string", "null"] }
            has_more: { type: boolean }
    Problem:                                     # RFC 9457 problem detail
      type: object
      required: [title, status]
      properties:
        type: { type: string, format: uri, default: "about:blank" }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
        instance: { type: string }
        errors:
          type: array
          items:
            type: object
            properties:
              detail: { type: string }
              pointer: { type: string }
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    ValidationProblem:
      description: Request failed validation
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After: { schema: { type: integer } }
      content:
        application/problem+json:
          schema: { $ref: "#/components/schemas/Problem" }
```

## Code-first note (FastAPI)

FastAPI generates an OpenAPI document from the Pydantic v2 models + route signatures (`response_model`, `status_code`, `responses=`), and recent FastAPI emits OpenAPI 3.1. That makes "code-first" viable: design the contract here, then let the framework produce and serve it — see the `fastapi` skill for the route/model wiring and the `pydantic-v2` skill for the schemas. Hand off to dedicated OpenAPI tooling for linting (e.g. a spec linter), mock servers, and client/SDK generation.
