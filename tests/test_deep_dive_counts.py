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


#: TWO heading shapes. `**C12 — …**` is what nine twins use; `### 12.` is what `code` uses, and
#: reading only the first scored that package ZERO while its deep-dive stated a count.
CONDITION_RE = re.compile(r"^(?:\*\*C\d+[a-z]? — |### \d+\. )", re.M)

#: Spelled-out counts, because SIX of the ten reviewer deep-dives write theirs in English and a
#: digits-only pattern could not see any of them. Two were drifted when this was added.
_UNITS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60}
_WORD = "|".join(sorted(list(_UNITS) + list(_TENS), key=len, reverse=True))


def _to_int(text: str) -> int:
    """A count written in digits or in English. `forty-three` and `43` are one claim."""
    if text.isdigit():
        return int(text)
    parts = re.split(r"[-\s]+", text.lower())
    if len(parts) == 2 and parts[0] in _TENS and parts[1] in _UNITS:
        return _TENS[parts[0]] + _UNITS[parts[1]]
    word = parts[0]
    return _TENS.get(word) or _UNITS[word]


#: ANY phrasing, not one sentence. The first version matched `across N rules` and
#: `## The N conditions` exactly, so of sixteen deep-dives it could see THREE — and the thirteen it
#: could not see included three whose rule counts had drifted by fifteen, eighteen and eighteen.
#: A guard that inspects part of a population certifies that part and licenses the rest.
#:
#: `(?<![-\w])` keeps a hyphenated ordinal out: "the wave-2 conditions were appended" is prose about
#: a wave, not a claim about a count, and matching it made a correct file look like a drifted one.
STATED_RULES_RE = re.compile(
    rf"(?<![-\w])(?:\*\*)?(\d+|(?:{_WORD})(?:[-\s](?:{_WORD}))?)(?:\*\*)?\s+(?:validator\s+)?rules\b",
    re.I,
)
STATED_CONDITIONS_RE = re.compile(
    rf"(?<![-\w])(?:\*\*)?(\d+|(?:{_WORD})(?:[-\s](?:{_WORD}))?)(?:\*\*)?"
    r"[-\s]+(?:numbered\s+)?conditions?\b",
    re.I,
)


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
    stated = _to_int(STATED_RULES_RE.search(doc.read_text()).group(1))
    assert stated == len(_emitted_rule_ids(script.read_text()))


@pytest.mark.parametrize("doc,conditions", _reviewer_pairs(), ids=lambda p: p.stem)
def test_a_stated_condition_count_is_the_real_one(doc, conditions):
    stated = _to_int(STATED_CONDITIONS_RE.search(doc.read_text()).group(1))
    assert stated == len(CONDITION_RE.findall(conditions.read_text()))


def test_the_sweep_actually_found_something_to_check():
    """A derived guard that matches nothing is green and worthless. It found the two stale counts
    it was written for, so it must keep finding at least those two files."""
    assert _producer_pairs(), "no producer deep-dive states a rule count"
    assert _reviewer_pairs(), "no reviewer deep-dive states a condition count"


def test_the_sweep_reaches_EVERY_pair_that_has_a_deep_dive():
    """The docstring's claim, asserted instead of stated.

    It said "over every pair that has a deep-dive" and collected 8 producers of 10 and 4 reviewers
    of 10: pair collection required DIGITS, and six reviewer deep-dives write their count in
    English. Two of those six were drifted at the moment this was added — exactly the defect the
    module exists to catch, sitting inside the part it certified without inspecting.
    """
    reviewers = [
        d
        for d in sorted(DOCS.glob("reviewing-*.md"))
        if (SKILLS / d.stem / "references" / "conditions.md").exists()
    ]
    reached = {d.name for d, _ in _reviewer_pairs()}
    missing = [d.name for d in reviewers if d.name not in reached]
    assert not missing, (
        f"a reviewer deep-dive states no count this guard can read: {missing}"
    )


#: Producer deep-dives that state NO rule count, so no pair is formed for them. Declared, because
#: "unreached" and "states nothing to check" are indistinguishable from outside — and the reviewer
#: half of this sweep was asserted while the producer half was left to be assumed.
PRODUCERS_STATING_NO_RULE_COUNT = {
    "code-prior-art-survey.md",
    "security-prior-art-survey.md",
}


def test_the_sweep_reaches_every_PRODUCER_that_states_a_count():
    """The other half. A producer doc whose phrasing this guard cannot read is skipped silently,
    which is the shape that hid six reviewer docs and five stale counts."""
    producers = [
        d
        for d in sorted(DOCS.glob("*-prior-art-survey.md"))
        if not d.name.startswith("reviewing-")
        and len(
            [
                s
                for s in (SKILLS / d.stem / "scripts").glob("validate_*.py")
                if not s.name.startswith("test_")
            ]
        )
        == 1
    ]
    reached = {d.name for d, _ in _producer_pairs()}
    missing = {d.name for d in producers if d.name not in reached}
    assert missing == PRODUCERS_STATING_NO_RULE_COUNT, {
        "unreached": sorted(missing),
        "declared as stating no count": sorted(PRODUCERS_STATING_NO_RULE_COUNT),
    }
