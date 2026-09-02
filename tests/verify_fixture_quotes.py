"""Hold every fixture quote against the instrument its record CITES.

AUTHOR-TIME, not CI. It fetches, so it is a maintainer tool like the registry re-probe, and it
lives here rather than in the shipped package -- a skill that must run without a network should not
carry a network dependency.

    uv run python tests/verify_fixture_quotes.py

WHY IT EXISTS. A blind reviewer found a fabricated citation in the regulatory pair's CLEAN
calibration fixture: `CFR-45-160` carried "Implement policies and procedures to prevent, detect,
contain, and correct security violations", which is 45 CFR 164.308(a)(1)(i) and appears nowhere in
part 160. Four mechanical guards missed it, and so did the author -- who had fetched part 164,
found the sentence, and reported both fixture quotes "verified verbatim against the primary
sources". They were: the STRINGS existed. The quote was then attached to a part-160 record without
part 160 ever being fetched.

**Verifying that a sentence exists somewhere is not verifying a citation.** The check has to be
"does THIS instrument carry this text", and that is a different request. This script makes the
difference mechanical.

A second, quieter defect it also catches: the same fixture reproduced an act's title with a
straight apostrophe where the act carries a curly one. `evidence_quote`'s whole contract is
verbatim, and "close enough" is not it.
"""

from __future__ import annotations

import html
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CELLAR = "http://publications.europa.eu/resource/celex/{}"
ECFR = "https://www.ecfr.gov/api/versioner/v1/full/2026-01-01/title-{title}.xml?part={part}"


def _get(url: str, headers: dict[str, str]) -> str:
    """Fetch, permitting compression.

    The first version forced `Accept-Encoding: identity` and every eCFR request came back 406 --
    which the pair's own registry already records: that endpoint "returns HTTP 406 with
    supportCode: 11 unless the request permits compression". A checker that cannot reach the
    source reports a clean run, so this is not a detail.
    """
    req = urllib.request.Request(url, headers={**headers, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310 — fixed, author-supplied
        raw = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", errors="replace")


def _flatten(markup: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", markup)))


def _fetch_for(candidate: dict) -> str | None:
    """The cited division, fetched by the record's OWN citation -- never by its locator.

    Using the locator would defeat the point: a record whose locator and citation disagree is
    exactly what this checks for.
    """
    prov = candidate.get("provenance") or {}
    if prov.get("celex"):
        return _flatten(_get(CELLAR.format(prov["celex"]),
                             {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}))
    if prov.get("cfr_citation"):
        m = re.match(r"(\d+)\s+CFR\s+(\d+)", str(prov["cfr_citation"]))
        if m:
            return _flatten(_get(ECFR.format(title=m.group(1), part=m.group(2)), {}))
    return None


def main() -> int:
    import yaml

    bad: list[str] = []
    checked = 0
    for path in sorted((ROOT / "skills").glob("*-prior-art-survey/scripts/fixtures/*.valid.yaml")):
        doc = yaml.safe_load(path.read_text())
        for cand in (doc.get("candidates") or []):
            quote = (cand.get("evidence_quote") or "").strip().strip('"')
            quote = " ".join(quote.split())
            if not quote or ":" in quote[:40]:      # a field-value warrant, not prose
                continue
            try:
                body = _fetch_for(cand)
            except Exception as exc:                # noqa: BLE001 — reported, not raised
                bad.append(f"{path.name} {cand['item_id']}: fetch failed: {exc}")
                continue
            if body is None:
                continue
            checked += 1
            if quote not in body:
                bad.append(
                    f"{path.name} {cand['item_id']}: the cited instrument does NOT carry this "
                    f"quote.\n    cited: {(cand.get('provenance') or {})}\n    quote: {quote[:110]}…")

    print(f"checked {checked} prose quotes against the instrument each record cites")
    if checked == 0 and not bad:
        print("FAIL nothing was checked -- a checker that reaches no source reports a clean run")
        return 1
    for line in bad:
        print("FAIL " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
