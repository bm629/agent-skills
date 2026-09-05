"""Every count a deep-dive states about a package, checked against the package.

A stated number is a claim, and this repo has now shipped two that drifted: a producer deep-dive
saying "40 rules" against a validator carrying 63, and a reviewer deep-dive saying "twenty-two
conditions" against a file carrying 24 — stale before the fold that found them, because nothing
re-read them when a rule was added.

Derived from the files on disk and over every pair that has a deep-dive, so the seventh type is
covered when its docs land rather than when someone remembers to extend a list.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "skills"
SKILLS = ROOT / "skills"

def _emitted_rule_ids(source: str) -> set[str]:
    """Every rule id a validator can emit — an AST walk, not a regex over the call text.

    TWO shapes. A positional `_fail("id", ...)`, and a `rule="id"` keyword threaded through a
    helper that calls `_fail` itself. The regex this replaces read only the first, so a package
    that filed its own registry read under the rule that carries the parse error measured 103
    against a validator emitting 104 — and the deep-dive it was checking was right.

    Measured over all ten producer validators before adoption: the count changes for exactly the
    one package that uses the keyword shape, and is byte-identical for the other nine.
    """
    out: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", "") == "_fail" and node.args:
            if isinstance(node.args[0], ast.Constant):
                out.add(node.args[0].value)
        for kw in node.keywords:
            if kw.arg == "rule" and isinstance(kw.value, ast.Constant):
                out.add(kw.value.value)
    return out

CONDITION_RE = re.compile(r"^\*\*C\d+[a-z]? — ", re.M)
#: ANY phrasing, not one sentence. The first version matched `across N rules` and
#: `## The N conditions` exactly, so of sixteen deep-dives it could see THREE — and the thirteen it
#: could not see included three whose rule counts had drifted by fifteen, eighteen and eighteen.
#: A guard that inspects part of a population certifies that part and licenses the rest.
#:
#: `(?<![-\w])` keeps a hyphenated ordinal out: "the wave-2 conditions were appended" is prose about
#: a wave, not a claim about a count, and matching it made a correct file look like a drifted one.
STATED_RULES_RE = re.compile(r"(?<![-\w])(?:\*\*)?(\d+)(?:\*\*)?\s+(?:validator\s+)?rules\b")
STATED_CONDITIONS_RE = re.compile(r"(?<![-\w])(?:\*\*)?(\d+)(?:\*\*)?\s+(?:numbered\s+)?conditions\b")


def _producer_pairs() -> list[tuple[pathlib.Path, pathlib.Path]]:
    """(deep-dive, validator) for every producer package whose deep-dive states a rule count."""
    out = []
    for doc in sorted(DOCS.glob("*-prior-art-survey.md")):
        if doc.name.startswith("reviewing-"):
            continue
        scripts = list((SKILLS / doc.stem / "scripts").glob("validate_*.py"))
        scripts = [s for s in scripts if not s.name.startswith("test_")]
        if len(scripts) == 1 and STATED_RULES_RE.search(doc.read_text()):
            out.append((doc, scripts[0]))
    return out


def _reviewer_pairs() -> list[tuple[pathlib.Path, pathlib.Path]]:
    """(deep-dive, conditions.md) for every reviewer whose deep-dive states a condition count."""
    out = []
    for doc in sorted(DOCS.glob("reviewing-*.md")):
        conditions = SKILLS / doc.stem / "references" / "conditions.md"
        if conditions.exists() and STATED_CONDITIONS_RE.search(doc.read_text()):
            out.append((doc, conditions))
    return out


@pytest.mark.parametrize("doc,script", _producer_pairs(), ids=lambda p: p.stem)
def test_a_stated_rule_count_is_the_real_one(doc, script):
    stated = int(STATED_RULES_RE.search(doc.read_text()).group(1))
    assert stated == len(_emitted_rule_ids(script.read_text()))


@pytest.mark.parametrize("doc,conditions", _reviewer_pairs(), ids=lambda p: p.stem)
def test_a_stated_condition_count_is_the_real_one(doc, conditions):
    stated = int(STATED_CONDITIONS_RE.search(doc.read_text()).group(1))
    assert stated == len(CONDITION_RE.findall(conditions.read_text()))


def test_the_sweep_actually_found_something_to_check():
    """A derived guard that matches nothing is green and worthless. It found the two stale counts
    it was written for, so it must keep finding at least those two files."""
    assert _producer_pairs(), "no producer deep-dive states a rule count"
    assert _reviewer_pairs(), "no reviewer deep-dive states a condition count"
