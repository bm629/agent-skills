"""The CALL-SITE kill sweep. Run it; it is not part of the suite.

For each `_fail` call site, suppress that ONE site and run the package suite. A site no test
notices is a branch that can be deleted with everything green — five such sites, when they were
found, turned a real exit-1 finding into exit 0.

    uv run --group dev python3 skills/scale-prior-art-survey/scripts/kill_site_sweep.py

IT VALIDATES ITSELF BEFORE IT REPORTS, and that is the whole design. Three separate defects made
earlier versions print `SURVIVORS: 0` from any codebase, each introduced by the fix for the last:

- a pytest flag no installed plugin provides, so every run exited non-zero;
- line numbers derived from the UNPATCHED source, so no suppression ever matched a site;
- a copy at the wrong DEPTH — the suite derives the repo root from the package's own location, so
  a package copied to `<tmp>/pkg` made `ROOT` become `<tmp>` and fifty tests failed on every run.

Each `0` was quoted into a commit message and a plan before anyone checked it. Patching the third
would only invite a fourth, so the tool now refuses to report at all unless BOTH controls hold:

- BASELINE — with nothing suppressed, the suite in the copy must be GREEN. That catches every
  "the runs were failing for an unrelated reason" defect, which is two of the three above.
- POSITIVE CONTROL — suppression must actually change something. If EVERY site is a survivor,
  that is a broken instrument, not a clean codebase.

It sweeps a copy of the WHOLE REPO at its real depth. In-place patching left an env-var backdoor
in the shipped validator when a run was killed before its `finally`; no `finally` survives a
SIGKILL, and a copy needs none.
"""

import ast
import os
import pathlib
import subprocess
import sys
import shutil
import tempfile

PKG_NAME = "scale-prior-art-survey"
PKG = pathlib.Path(__file__).resolve().parents[1]
REPO = PKG.parents[1]

#: Inserted at the top of `_fail`. Its own line count is what the second defect got wrong.
PATCH = (
    "def _fail(rule: str, message: str, f: Findings) -> None:\n"
    "    import inspect\n"
    "    import os\n"
    "\n"
    "    _k = os.environ.get('KILL_SITE')\n"
    "    if _k and inspect.currentframe().f_back.f_lineno == int(_k):\n"
    "        return\n"
)
ANCHOR = "def _fail(rule: str, message: str, f: Findings) -> None:\n"


def call_sites(source: str) -> list[tuple[int, str]]:
    """Every `_fail` call site as (lineno, rule id), derived from the source that will RUN."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.Call)
            and getattr(node.func, "id", "") == "_fail"
            and node.args
        ):
            first = node.args[0]
            rule = first.value if isinstance(first, ast.Constant) else "<computed>"
            out.append((node.lineno, rule))
    return sorted(out)


#: Guards that read the validator's SOURCE SHAPE. The sweep deliberately modifies that source,
#: so running them against it is a category error — and one of them exists precisely to forbid
#: the env-var read this tool injects. Deselected BY NAME and stated here rather than silently,
#: because everything else passing is what makes the patched baseline mean anything.
SOURCE_SHAPE_GUARDS = (
    "not reads_NO_environment_variable and not DISPLACED_by_inserted_code"
)


def _run(scripts: pathlib.Path, kill: str | None) -> int:
    env = dict(os.environ)
    env.pop("KILL_SITE", None)
    if kill is not None:
        env["KILL_SITE"] = kill
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(scripts),
            "-q",
            "--no-header",
            "-x",
            "-p",
            "no:cacheprovider",
            "-k",
            SOURCE_SHAPE_GUARDS,
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    ).returncode


def sweep() -> tuple[list[tuple[int, str]], int]:
    """Sweep a copy of the whole repo. Raises rather than reporting a number it cannot trust."""
    validator = PKG / "scripts" / "validate_scale_prior_art.py"
    patched = validator.read_text().replace(ANCHOR, PATCH, 1)
    sites = call_sites(patched)
    with tempfile.TemporaryDirectory() as td:
        work = pathlib.Path(td) / "repo"
        # DEPTH MATTERS, and no VCS is involved. The suite derives the repo root from the
        # package's own location, so a package copied to `<tmp>/pkg` makes `ROOT` become `<tmp>`
        # and fifty tests fail on every run — the third way this tool became unable to report a
        # survivor, introduced by the fix for the second. Copying only what the suite reads keeps
        # it fast; copying it at the SAME DEPTH keeps it correct. `git archive` was tried and
        # rejected: it fails wherever the package is not a git checkout, which is everywhere it
        # ships.
        # THE WHOLE TREE, minus what cannot matter. An earlier version listed the four paths
        # the suite reads — and the list was written from memory and wrong: the suite also reads
        # a THIRD package's `capability-map.schema.json`, so the baseline was red and the sweep
        # (correctly) refused to report. Enumerating a population from memory is the mistake this
        # tool exists to catch; deriving it is not worth it here when copying everything costs
        # ~30 MB once per run.
        shutil.copytree(
            REPO,
            work,
            ignore=shutil.ignore_patterns(
                ".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", "*.pyc"
            ),
        )
        scripts = work / "skills" / PKG_NAME / "scripts"
        (scripts / "validate_scale_prior_art.py").write_text(patched)

        if _run(scripts, None) != 0:
            raise SystemExit(
                "BASELINE IS RED in the copy with nothing suppressed, so no run can ever return "
                "0 and every site would look like a survivor. The sweep refuses to report. This "
                "is the shape of three of its four historical defects."
            )
        survivors = [(ln, rule) for ln, rule in sites if _run(scripts, str(ln)) == 0]
        if survivors and len(survivors) == len(sites):
            raise SystemExit(
                f"EVERY one of {len(sites)} sites 'survived', which means suppression never took "
                "effect — a broken instrument, not a clean codebase."
            )
    return survivors, len(sites)


def main() -> int:
    found, total = sweep()
    print(f"call sites: {total}")
    print(f"SURVIVORS: {len(found)}")
    for lineno, rule in found:
        print(f"   L{lineno}  {rule}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
