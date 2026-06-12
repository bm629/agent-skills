#!/usr/bin/env python3
"""Resolve one Penpot RPC command from the bundled OpenAPI spec.

Usage: python3 endpoint.py <command-name>

Penpot's API is an RPC: every command is POST to
`<base_url>/api/rpc/command/<command-name>` with a JSON body. This finds the
command in the bundled spec, $ref-resolves its request-body schema (bounded
depth + cycle guard), and prints a readable field list + a curl skeleton.
Python stdlib only; no pip dependency. The spec declares request bodies only
(no response/error schemas) — those are documented in references/patterns.md.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "penpot-openapi.json")
MAXDEPTH = 6


def load():
    with open(SPEC) as f:
        return json.load(f)


def resolve_ref(spec, ref):
    node = spec
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def prop_type(ps, spec):
    if "$ref" in ps:
        return ps["$ref"].split("/")[-1]
    t = ps.get("type")
    if t == "array":
        it = ps.get("items", {}) or {}
        inner = it["$ref"].split("/")[-1] if "$ref" in it else it.get("type", "?")
        return f"array<{inner}>"
    if ps.get("enum"):
        return f"{t or 'enum'} {ps['enum']}"
    return t or "object"


def schema_lines(schema, spec, seen, depth, indent):
    pad = "  " * indent
    if depth <= 0:
        yield pad + "… (max depth — re-run on the referenced schema name)"
        return
    if not isinstance(schema, dict):
        return
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            yield pad + f"→ {ref.split('/')[-1]} (recursive)"
            return
        yield from schema_lines(resolve_ref(spec, ref), spec, seen | {ref}, depth, indent)
        return
    for comb in ("allOf", "oneOf", "anyOf"):
        if comb in schema:
            yield pad + f"({comb}, {len(schema[comb])} variants):"
            for sub in schema[comb][:8]:
                yield from schema_lines(sub, spec, seen, depth - 1, indent + 1)
            if len(schema[comb]) > 8:
                yield pad + f"  … ({len(schema[comb]) - 8} more variants)"
            return
    t = schema.get("type")
    if t == "object" or "properties" in schema:
        req = set(schema.get("required", []))
        props = schema.get("properties", {}) or {}
        if not props:
            yield pad + "{ free-form object }"
            return
        for name, ps in props.items():
            mark = " *" if name in req else ""
            yield pad + f"- {name}{mark}: {prop_type(ps, spec)}"
            yield from schema_lines(ps, spec, seen, depth - 1, indent + 1)
    elif t == "array":
        yield pad + "[array of]:"
        yield from schema_lines(schema.get("items", {}), spec, seen, depth - 1, indent + 1)


def main():
    if len(sys.argv) != 2:
        print("usage: python3 endpoint.py <command-name>", file=sys.stderr)
        sys.exit(2)
    cmd = sys.argv[1]
    spec = load()
    item = spec.get("paths", {}).get(cmd)
    if not item or "post" not in item:
        print(f"command '{cmd}' not found — scan assets/endpoint-index.md.", file=sys.stderr)
        sys.exit(1)
    op = item["post"]

    print(f"command: {cmd}")
    print(f"POST <base_url>/api/rpc/command/{cmd}")
    if op.get("deprecated"):
        print("DEPRECATED — prefer a current command.")
    print('auth: -H "Authorization: Token $<token_env>"  (NOT Bearer)')

    rb = op.get("requestBody", {}) or {}
    content = (rb.get("content", {}) or {}).get("application/json", {}) or {}
    schema = content.get("schema", {}) or {}
    required = " (required body)" if rb.get("required") else ""
    print(f"\nREQUEST BODY (application/json){required}  (* = required field):")
    body_lines = list(schema_lines(schema, spec, set(), MAXDEPTH, 1))
    if body_lines:
        print("\n".join(body_lines))
    else:
        print("  {} (no fields — POST an empty object)")

    ex = content.get("example")
    if ex:
        print(f"\nSPEC EXAMPLE (auto-generated — values are noise, shape is the signal):\n  {ex}")

    print("\nRESPONSE / ERRORS: not declared in the spec — see references/patterns.md")
    print("  (reads return the resource JSON; errors are a non-2xx {type, code, hint} envelope).")
    print("\nCURL SKELETON:")
    print(f'  curl -sS -X POST "$base_url/api/rpc/command/{cmd}" \\')
    print('    -H "Authorization: Token $<token_env>" \\')
    print('    -H "Content-Type: application/json" -H "Accept: application/json" \\')
    print("    -d '<json body>'")


if __name__ == "__main__":
    main()
