"""ONE guard over every prior-art registry's fallback graph, derived from what is on disk.

A `fallback` promises a SECOND CHANNEL: when this source fails, go there. A cycle breaks that
promise while satisfying every rule written about it — `ml`'s registry says "every one names a
DIFFERENT row — checked, not assumed", and every one does, and five of its chains still return to
where they started. Checking rows one at a time cannot see this; only walking can.

TWO IDIOMS BOTH MEAN TERMINAL, and the guard honours both:

  * `fallback: null` — this is `regulatory`'s, paired with a `fallback_rationale`.
  * a SELF-fallback — this is `platform-ecosystem`'s, and its own registry documents it: "Ten rows
    name THEMSELVES, which is a record, not an oversight: no distinct second channel exists for
    that material. Read a self-fallback as 'there is no fallback'."

Treating a self-fallback as a cycle would report ten false defects in a package that made a
deliberate, written choice. The DEFECT is a cycle through two or more DISTINCT rows.

ROOT CAUSE, worth stating where the next author will meet it: `ml` has zero terminals. Its preamble
requires every row to name a fallback AND every fallback to name a different row. In a finite graph
with no terminal that guarantees a cycle by pigeonhole — the rule written as a virtue produced the
defect it was meant to prevent.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Cycles in packages that are already SHIPPED and installed. Repairing them means re-deciding which
# channel actually substitutes for which, with evidence — that is its own task with its own review,
# the same call taken on `security`'s `kept`. Recorded deterministically here rather than in prose
# so no NEW cycle can be added anywhere.
#
# EQUALITY is asserted, not a ceiling: a new cycle fails, and so does a repair nobody records.
KNOWN_CYCLES = {
    "ml": 5,
    "platform-ecosystem": 8,
}


def _registries() -> list[pathlib.Path]:
    """DERIVED by glob. A hand-listed set is how the ninth type ships unchecked."""
    out = sorted(
        (ROOT / "skills").glob("*-prior-art-survey/references/source-registry.yaml")
    )
    assert len(out) >= 8, (
        f"only {len(out)} registries found — the glob is wrong, not the repo"
    )
    return out


def _rows(path: pathlib.Path) -> dict[str, dict]:
    raw = (yaml.safe_load(path.read_text()) or {}).get("sources") or []
    if isinstance(raw, dict):
        return {k: (v if isinstance(v, dict) else {}) for k, v in raw.items()}
    return {s["id"]: s for s in raw if isinstance(s, dict) and "id" in s}


def _edges(rows: dict[str, dict]) -> dict[str, str | None]:
    """`None` for a terminal — both idioms collapse to it here."""
    out: dict[str, str | None] = {}
    for rid, row in rows.items():
        f = row.get("fallback")
        out[rid] = None if (not isinstance(f, str) or f == rid) else f
    return out


def _cycles(edges: dict[str, str | None]) -> set[tuple[str, ...]]:
    found: set[tuple[str, ...]] = set()
    done: set[str] = set()

    def walk(node: str, stack: list[str]) -> None:
        if node in stack:
            found.add(tuple(stack[stack.index(node) :] + [node]))
            return
        if node in done:
            return
        nxt = edges.get(node)
        if nxt:
            walk(nxt, stack + [node])
        done.add(node)

    for rid in edges:
        walk(rid, [])
    return found


def _slug(path: pathlib.Path) -> str:
    return path.parent.parent.name.removesuffix("-prior-art-survey")


@pytest.mark.parametrize("path", _registries(), ids=_slug)
def test_no_fallback_cycle(path: pathlib.Path) -> None:
    slug = _slug(path)
    cycles = _cycles(_edges(_rows(path)))
    expected = KNOWN_CYCLES.get(slug, 0)
    detail = "\n".join("  " + " -> ".join(c) for c in sorted(cycles))
    assert len(cycles) == expected, (
        f"{slug}: {len(cycles)} fallback cycles, recorded {expected}.\n{detail}\n"
        "A cycle promises a second channel and returns to the first. If you FIXED one, "
        "update KNOWN_CYCLES — equality is asserted so a repair cannot go unrecorded."
    )


@pytest.mark.parametrize("path", _registries(), ids=_slug)
def test_every_fallback_resolves(path: pathlib.Path) -> None:
    """A fallback naming a row that does not exist is worse than none: it reads as a route."""
    rows = _rows(path)
    dangling = {
        i: f for i, f in _edges(rows).items() if f is not None and f not in rows
    }
    assert not dangling, (
        f"{_slug(path)}: fallback edges into a non-existent row: {dangling}"
    )


@pytest.mark.parametrize("path", _registries(), ids=_slug)
def test_a_null_terminal_says_why(path: pathlib.Path) -> None:
    """The `fallback: null` idiom carries a rationale. A self-fallback does not need one — the
    self-reference IS the statement, and its registry's preamble explains it once."""
    rows = _rows(path)
    bare = [
        i
        for i, r in rows.items()
        if "fallback" in r
        and r.get("fallback") is None
        and not str(r.get("fallback_rationale") or "").strip()
    ]
    assert not bare, (
        f"{_slug(path)}: rows declaring `fallback: null` with no `fallback_rationale`: {bare}. "
        "A terminal is a claim that no second channel exists; say why."
    )


def test_the_exemption_names_only_real_packages() -> None:
    """An exemption for a package that no longer exists silently protects nothing."""
    slugs = {_slug(p) for p in _registries()}
    assert not (set(KNOWN_CYCLES) - slugs), (
        f"exemption names unknown packages: {set(KNOWN_CYCLES) - slugs}"
    )


def test_a_self_fallback_is_read_as_a_terminal_not_a_cycle() -> None:
    """Both directions, on a synthetic graph. Reading platform-ecosystem's documented idiom as a
    cycle would report ten false defects; reading a real two-row loop as a terminal would report
    none of the thirteen that exist."""
    assert _cycles(_edges({"a": {"fallback": "a"}})) == set()
    assert _cycles(_edges({"a": {"fallback": None}})) == set()
    assert _cycles(_edges({"a": {"fallback": "b"}, "b": {"fallback": "a"}})) == {
        ("a", "b", "a")
    }
