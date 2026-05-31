#!/usr/bin/env python3
"""Resolve one OpenAPI operation from the bundled GitHub REST spec.

Usage: python3 endpoint.py <operationId>   (e.g. repos/get, issues/create)

Finds the operation by operationId in assets/github-openapi.json, $ref-resolves
its parameters / request body / response (bounded depth + cycle guard), and prints
a readable summary plus a `gh api` skeleton. Python stdlib only; no pip dependency.

This resolver only reads the spec; it never authenticates or calls the API. The
actual call is made by `gh api` (see references/gh-api.md), authenticated per-call
with GH_TOKEN.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "assets", "github-openapi.json")
MAXDEPTH = 5


def load():
    with open(SPEC) as f:
        return json.load(f)


def resolve_ref(spec, ref):
    node = spec
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def find_op(spec, opid):
    for path, item in spec.get("paths", {}).items():
        for method, op in (item or {}).items():
            if isinstance(op, dict) and op.get("operationId") == opid:
                return method.upper(), path, op
    return None


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
        yield pad + "… (max depth)"
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
            yield pad + f"({comb}):"
            for sub in schema[comb]:
                yield "  " * (indent + 1) + f"- option: {prop_type(sub, spec)}"
                yield from schema_lines(sub, spec, seen, depth - 1, indent + 2)
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
        print("usage: python3 endpoint.py <operationId>  (e.g. repos/get)", file=sys.stderr)
        sys.exit(2)
    opid = sys.argv[1]
    spec = load()
    found = find_op(spec, opid)
    if not found:
        print(f"operationId '{opid}' not found — scan assets/endpoint-index.md", file=sys.stderr)
        sys.exit(1)
    method, path, op = found

    print(f"operation: {opid}")
    print(f"{method} {path}")
    if op.get("summary"):
        print(f"summary: {op['summary'].strip()}")

    params = []
    for pr in (op.get("parameters") or []):
        if "$ref" in pr:
            pr = resolve_ref(spec, pr["$ref"])
        params.append(pr)
    if params:
        print("\nPARAMS (* = required):")
        for pr in params:
            mark = " *" if pr.get("required") else ""
            sch = pr.get("schema", {}) or {}
            print(f"  - {pr.get('name')} ({pr.get('in')}){mark}: {prop_type(sch, spec)}")

    rb = op.get("requestBody", {})
    if "$ref" in rb:
        rb = resolve_ref(spec, rb["$ref"])
    content = rb.get("content", {}) or {}
    if content:
        ct = next(iter(content))
        print(f"\nREQUEST BODY ({ct})  (* = required):")
        for line in schema_lines(content[ct].get("schema", {}), spec, set(), MAXDEPTH, 1):
            print(line)

    resp = op.get("responses", {}) or {}
    code = next((c for c in ("200", "201", "202", "204") if c in resp), None)
    if code and code != "204":
        r = resp[code]
        if "$ref" in r:
            r = resolve_ref(spec, r["$ref"])
        rc = r.get("content", {}) or {}
        if rc:
            ct = next(iter(rc))
            print(f"\nRESPONSE {code} ({ct}):")
            for line in schema_lines(rc[ct].get("schema", {}), spec, set(), 3, 1):
                print(line)

    print("\nERRORS / SCOPES: see references/gh-api.md (4xx is usually a missing token scope).")
    print("\ngh api SKELETON  (per-call GH_TOKEN; {owner}/{repo} fill from repo/GH_REPO):")
    gpath = path.lstrip("/")
    if content:
        print(f'  GH_TOKEN="$<token_env>" gh api -X {method} {gpath} \\')
        print("    -f key=value   # string; -F for typed/@file; or --input body.json")
    elif method == "GET":
        print(f'  GH_TOKEN="$<token_env>" gh api {gpath}')
    else:
        print(f'  GH_TOKEN="$<token_env>" gh api -X {method} {gpath}')


if __name__ == "__main__":
    main()
