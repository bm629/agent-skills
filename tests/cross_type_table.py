"""Derive the cross-type contract comparison from the shipped schemas.

Every prior-art spec states how its pair sits against its siblings on a handful of contracts, and
three spec revisions in a row have shipped a WRONG cardinality doing it — "5j is the outlier on all
four" (false once its `kept` was fixed), "THREE readings of `found_by`" (there are four). A third
example used to sit here -- "all six shipped maps require `groups`" annotated "(five do)" -- and it
has been WITHDRAWN: that annotation was produced by this module's own broken `_map_schema`, which
resolved `borrow-index` for `code` and `evidence-register` for `user-research`. Re-run against the
right schemas on 2026-09-03, SEVEN of the eight require `groups` and the sole exception is
`platform-ecosystem`, which declares `platforms` and `mechanisms` by design.

The withdrawn example is the sharpest lesson in this file: the tool built to stop a wrong
cardinality shipped one, in its own docstring, computed by its own bug. A derived number is only as
trustworthy as the derivation -- check the extractor, not just the output.

Playbook #62 says a count stated in prose drifts; this is that rule applied to the comparison
itself.

Run it and paste the output. Do not retype it.

    uv run python tests/cross_type_table.py
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _find(node: object, key: str) -> object:
    """First value under `key`, anywhere in the schema tree."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                return v
            got = _find(v, key)
            if got is not None:
                return got
    elif isinstance(node, list):
        for v in node:
            got = _find(v, key)
            if got is not None:
                return got
    return None


def _types() -> list[str]:
    """DERIVED by glob. A hand-listed set is how a seventh type goes uncompared."""
    out = []
    for p in sorted(SKILLS.glob("*-prior-art-survey")):
        if p.name.startswith("reviewing-"):
            continue
        if (p / "schemas").is_dir():
            out.append(p.name.removesuffix("-prior-art-survey"))
    return out


def _search_schema(t: str) -> dict:
    p = SKILLS / f"{t}-prior-art-survey" / "schemas" / "search-output.schema.json"
    return json.loads(p.read_text())


def _map_schema(t: str) -> dict:
    """The MAP schema, resolved by the `-map` stem every package uses.

    This used to return the first `*.schema.json` that was not `search-output`, in sorted order.
    That silently compared `borrow-index` for `code` and `evidence-register` for `user-research`,
    and the "required top-level keys" row was wrong for every package shipping a register or an
    index -- the exact class of error this module exists to prevent, in the module itself.
    """
    d = SKILLS / f"{t}-prior-art-survey" / "schemas"
    hits = [
        p
        for p in sorted(d.glob("*.schema.json"))
        if p.name.removesuffix(".schema.json").endswith("-map")
    ]
    assert len(hits) == 1, (
        f"{t}: expected exactly one `*-map.schema.json`, found {[h.name for h in hits]}. "
        "A package that names its map differently must be resolved explicitly -- do not let the "
        "comparison fall back to a neighbouring schema."
    )
    return json.loads(hits[0].read_text())


def _resolve(schema: dict, node: object) -> object:
    """Follow a local `$ref` one hop. Without this the cell row returned None for six of seven
    packages — a derived table that silently reports nothing is worse than a prose claim, because
    it looks measured."""
    seen = 0
    while isinstance(node, dict) and "$ref" in node and seen < 8:
        ref = node["$ref"]
        if not ref.startswith("#/"):
            return node
        cur: object = schema
        for part in ref[2:].split("/"):
            if not isinstance(cur, dict) or part not in cur:
                return node
            cur = cur[part]
        node, seen = cur, seen + 1
    return node


def _cell_required(schema: dict) -> object:
    """The coverage cell's required keys — the grid's dimensionality."""
    cov = _find(schema, "coverage")
    if not isinstance(cov, dict):
        return None
    items = _resolve(schema, cov.get("items"))
    if isinstance(items, dict) and items.get("required"):
        return items["required"]
    return None


def _shape(node: object) -> str:
    if node is None:
        return "ABSENT"
    if not isinstance(node, dict):
        return "?"
    t = node.get("type")
    if t == "object":
        return "object{" + ", ".join(sorted(node.get("properties") or {})) + "}"
    if t == "array":
        item = node.get("items") or {}
        return (
            "array[" + _shape(item) + "]"
            if item.get("type") != "string"
            else "array[string]"
        )
    return str(t)


def main() -> int:
    types = _types()
    print(f"# Cross-type contract table — derived from {len(types)} shipped packages")
    print(f"# {', '.join(types)}\n")

    print("## `found_by` — the shape, per package")
    groups: dict[str, list[str]] = {}
    for t in types:
        s = _shape(_find(_search_schema(t), "found_by"))
        groups.setdefault(s, []).append(t)
    for s, ts in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"  {len(ts)}x  {s}\n        {', '.join(ts)}")
    print(f"  => {len(groups)} distinct SHAPES")
    print(
        "     NOTE: shape is not meaning. Within `string`, platform-ecosystem stores a bare"
    )
    print(
        "     SOURCE ID where the rest store a `group/source` CELL key, so the semantic split"
    )
    print("     is one finer than the shape split. This tool measures shape; read the")
    print("     descriptions for meaning.")
    print(
        "     (No count in that sentence on purpose: this file exists because counts stated"
    )
    print(
        "      in prose go stale, and one in its own output would be the same defect.)\n"
    )

    print("## `kept` — present, and its stated meaning")
    for t in types:
        k = _find(_search_schema(t), "kept")
        desc = (k or {}).get("description", "") if isinstance(k, dict) else ""
        print(f"  {t:<20} {'ABSENT' if k is None else desc[:88]}")
    print()

    print("## `count_frame` — which packages require a frame on the count")
    has = [t for t in types if _find(_search_schema(t), "count_frame") is not None]
    print(f"  present: {', '.join(has) or '(none)'}")
    print(f"  absent : {', '.join(t for t in types if t not in has)}\n")

    print("## coverage cell — required keys (the grid's dimensionality)")
    for t in types:
        sch = _search_schema(t)
        req = _cell_required(sch)
        assert req, (
            f"{t}: cell required keys not resolved -- fix the extractor, do not ship a None"
        )
        print(f"  {t:<20} {req}")
    print()

    print("## vocabulary map — required top-level keys")
    for t in types:
        m = _map_schema(t)
        print(f"  {t:<20} {m.get('required')}")
    print()

    print("## `lineage` on the map — declared, required, and READ by a rule")
    print(
        "   (three states, and the third is the one prose keeps getting wrong: a block the"
    )
    print(
        "    root field guard passes on `instructed OR read` is declared but checked by nothing)"
    )
    for t in types:
        m = _map_schema(t)
        if "lineage" not in m.get("properties", {}):
            print(f"  {t:<20} absent")
            continue
        req = "lineage" in m.get("required", [])
        src = next(SKILLS.glob(f"{t}-prior-art-survey/scripts/validate_*.py"), None)
        assert src is not None, (
            f"{t}: no validator found -- fix the glob, do not report False"
        )
        read = "lineage" in src.read_text()
        print(f"  {t:<20} declared | required={str(req):<5} | read_by_a_rule={read}")
    print()

    print("## reviewer conditions — condition NUMBERS are NOT stable across packages")
    print("   (cite a sibling condition by its TEXT and package, never by its number)")
    import re

    for t in types:
        c = SKILLS / f"reviewing-{t}-prior-art-survey" / "references" / "conditions.md"
        if not c.exists():
            print(f"  {t:<20} (no conditions.md)")
            continue
        m = re.search(r"^\*\*C17 — (.{0,66})", c.read_text(), re.M)
        print(f"  {t:<20} C17 = {m.group(1) if m else '(no C17)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
