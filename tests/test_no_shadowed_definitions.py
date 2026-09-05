"""No module-level name may be bound twice in a prior-art skill module.

Origin: two live defects, one authoring error. `validate_market_competitive_prior_art.py` defined
`REQUIRED_CAPABILITY_FIELDS` twice — the corrected 14-entry tuple, then a stale 5-entry one that
shadowed it and made the validator reject 9 of 14 genuinely-required anchor fields. Its own test
module then did the same thing with `class TestTriggerAnchors`, so three tests never ran and one of
them was wrong.

Both are "a correction applied by ADDING the fixed version and leaving the stale one in place".
Python binds the last silently, and no ruff rule flags either — F811 included, verified.

Scoped to the prior-art skills rather than proposed repo-wide: the evidence is two instances in one
file, and a rule enters this suite only with a recorded defect behind it.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _modules() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for pkg in sorted(SKILLS.glob("*-prior-art-survey")):
        if pkg.name.startswith("reviewing-"):
            continue
        out.extend(sorted((pkg / "scripts").glob("*.py")))
    return out


def _duplicate_bindings(source: str) -> dict[str, list[int]]:
    """Module-level names bound more than once, mapped to every line that binds them.

    Only top-level statements are walked — a name rebound inside a function or a class body is
    ordinary code, not the shadowing this guards.
    """
    seen: dict[str, list[int]] = {}
    for node in ast.parse(source).body:
        names: list[str] = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        for n in names:
            seen.setdefault(n, []).append(node.lineno)
    return {n: ls for n, ls in seen.items() if len(ls) > 1}


@pytest.mark.parametrize(
    "path", _modules(), ids=lambda p: f"{p.parent.parent.name}/{p.name}"
)
def test_no_module_level_name_is_bound_twice(path: pathlib.Path) -> None:
    dupes = _duplicate_bindings(path.read_text())
    assert not dupes, "\n".join(
        f"{path.relative_to(ROOT)}: {name!r} bound at lines {lines} — the later binding "
        f"silently wins and the earlier one is dead code"
        for name, lines in sorted(dupes.items())
    )


class TestTheDetectorItself:
    """A detector that has never seen its own defect is an assumption."""

    def test_it_catches_a_duplicated_constant(self) -> None:
        src = "A = (1,)\nB = 2\nA = (1, 2, 3)\n"
        assert _duplicate_bindings(src) == {"A": [1, 3]}

    def test_it_catches_a_duplicated_class(self) -> None:
        src = "class T:\n    pass\n\n\nclass T:\n    pass\n"
        assert _duplicate_bindings(src) == {"T": [1, 5]}

    def test_it_ignores_rebinding_inside_a_function(self) -> None:
        src = "def f():\n    x = 1\n    x = 2\n    return x\n"
        assert _duplicate_bindings(src) == {}

    def test_a_clean_module_is_clean(self) -> None:
        assert (
            _duplicate_bindings("A = 1\ndef f():\n    pass\n\n\nclass C:\n    pass\n")
            == {}
        )
