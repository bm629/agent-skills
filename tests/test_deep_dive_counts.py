"""Every count a deep-dive states about a package, checked against the package.

A stated number is a claim, and this repo has now shipped two that drifted: a producer deep-dive
saying "40 rules" against a validator carrying 63, and a reviewer deep-dive saying "twenty-two
conditions" against a file carrying 24 — stale before the fold that found them, because nothing
re-read them when a rule was added.

Derived from the files on disk and over every pair that has a deep-dive, so the seventh type is
covered when its docs land rather than when someone remembers to extend a list.
"""

from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "skills"
SKILLS = ROOT / "skills"

RULE_RE = re.compile(r'_fail\(\s*"([a-z0-9-]+)"')
CONDITION_RE = re.compile(r"^\*\*C\d+[a-z]? — ", re.M)
STATED_RULES_RE = re.compile(r"across (\d+) rules")
STATED_CONDITIONS_RE = re.compile(r"## The (\d+) conditions")


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
    assert stated == len(set(RULE_RE.findall(script.read_text())))


@pytest.mark.parametrize("doc,conditions", _reviewer_pairs(), ids=lambda p: p.stem)
def test_a_stated_condition_count_is_the_real_one(doc, conditions):
    stated = int(STATED_CONDITIONS_RE.search(doc.read_text()).group(1))
    assert stated == len(CONDITION_RE.findall(conditions.read_text()))


def test_the_sweep_actually_found_something_to_check():
    """A derived guard that matches nothing is green and worthless. It found the two stale counts
    it was written for, so it must keep finding at least those two files."""
    assert _producer_pairs(), "no producer deep-dive states a rule count"
    assert _reviewer_pairs(), "no reviewer deep-dive states a condition count"
