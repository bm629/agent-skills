"""Tests for the b6 capture script's pure decisions. No network and no browser.

The decisions that refuse a site are the ones worth pinning: a wrong answer there either reaches a
site that asked to be left alone, or reaches a host nobody checked.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

import capture_live_site as C
import pytest
import yaml

REGISTRY = Path(__file__).resolve().parent.parent / "references" / "source-registry.yaml"
UA = "Sample-research/1.0 (research@example.org)"
HOME = "https://example.org/"


def test_a_claude_group_disallow_wins_over_a_star_allow():
    verdict = C.robots_verdict(
        "User-agent: *\nAllow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n", UA, HOME
    )
    assert verdict["allowed"] is False
    assert verdict["refused_by"] == ["ClaudeBot"]
    assert set(verdict["groups"]) == {"*", "ClaudeBot"}


def test_an_anthropic_ai_group_binds_too():
    """The owner's rule names anthropic-ai among the Claude agents; its name holds no 'claude'."""
    verdict = C.robots_verdict("User-agent: anthropic-ai\nDisallow: /\n", UA, HOME)
    assert verdict["allowed"] is False


def test_the_largest_crawl_delay_wins():
    text = (
        "User-agent: *\nCrawl-delay: 2\nAllow: /\n\n"
        "User-agent: Claude-User\nCrawl-delay: 30\nAllow: /\n\n"
        "User-agent: Sample-research\nCrawl-delay: 7\nAllow: /\n"
    )
    verdict = C.robots_verdict(text, UA, HOME)
    assert verdict["allowed"] is True
    assert verdict["crawl_delay_s"] == 30


def test_no_robots_file_allows_with_no_delay():
    assert C.robots_verdict("", UA, HOME) == {
        "allowed": True,
        "groups": [],
        "crawl_delay_s": 0,
        "refused_by": [],
    }


def test_every_registry_excluded_host_is_refused():
    excluded = yaml.safe_load(REGISTRY.read_text())["excluded"]
    hosts = C.excluded_hosts(REGISTRY.read_text())
    assert hosts == {C.host(e["url"]) for e in excluded.values()}
    for entry in excluded.values():
        with pytest.raises(C.Refused):
            C.check_url(entry["url"].rstrip("/") + "/shots/1", hosts)
    with pytest.raises(C.Refused):
        C.check_url("https://cdn.dribbble.com/x.png", hosts)


def test_plain_http_is_refused():
    with pytest.raises(C.Refused):
        C.check_url("http://example.org/", set())
    C.check_url(HOME, set())


def test_the_first_terms_or_legal_link_is_followed_and_privacy_is_not():
    html = (
        '<a href="/about">About</a><a href="/privacy">Privacy</a>'
        '<a href="/legal/terms">Terms of use</a><a href="/conditions">Conditions</a>'
    )
    assert C.terms_link(html, HOME) == "https://example.org/legal/terms"
    assert C.terms_link('<a href="/privacy">Privacy</a>', HOME) is None


def test_a_card_that_mentions_legal_is_not_the_terms_link():
    """Found in calibration: a case-study card tagged "Legal" came before the real terms link."""
    html = (
        '<a href="/case-study/notion-sync-for-a-law-firm/">Automation Legal No more re-keying'
        " between two systems</a>"
        '<a href="/terms-and-conditions/">Terms</a>'
    )
    assert C.terms_link(html, HOME) == "https://example.org/terms-and-conditions/"


def test_a_redirect_to_another_host_or_to_http_is_refused():
    handler = C._Redirects(same_host=True)
    req = urllib.request.Request(HOME)
    for target in ("https://other.example/", "http://example.org/"):
        with pytest.raises(C.Refused):
            handler.redirect_request(req, None, 301, "Moved", {}, target)
    assert handler.redirect_request(req, None, 301, "Moved", {}, "https://example.org/a")


def test_computed_values_are_cut_and_only_expected_keys_kept():
    raw = {
        "styles": {"body": {"color": "x" * 500, "evil": "y"}, "script": {"color": "z"}},
        "fonts": ["f" * 500] * 500,
    }
    styles, fonts = C._styles(raw)
    assert set(styles) == {"body"} and set(styles["body"]) == set(C.PROPS)
    assert styles["body"]["color"] == "x" * 200
    assert len(fonts) == C.MAX_FONTS and all(len(f) == 200 for f in fonts)


def test_a_non_https_terms_link_is_passed_over_for_the_next():
    html = (
        '<a href="mailto:legal@example.org">Legal</a>'
        '<a href="http://example.org/terms">Terms</a>'
        '<a href="/terms-of-use">Terms of use</a>'
    )
    assert C.terms_link(html, HOME) == "https://example.org/terms-of-use"


@pytest.mark.parametrize(
    "raised,prefix,code",
    [
        (C.Refused("robots.txt disallows /"), "REFUSED:", 1),
        (urllib.error.HTTPError(HOME, 403, "Forbidden", {}, None), "UNREACHABLE:", 1),
        (urllib.error.HTTPError(HOME, 503, "Unavailable", {}, None), "UNREACHABLE:", 1),
        (urllib.error.HTTPError(HOME, 429, "Too Many", {}, None), "FAILED:", 2),
        (TimeoutError("no answer"), "FAILED:", 2),
    ],
)
def test_each_outcome_prints_the_prefix_its_skip_cause_reads(
    monkeypatch, capsys, tmp_path, raised, prefix, code
):
    """REFUSED is a robots or terms refusal; UNREACHABLE is a 403, a challenge or an error page."""

    def boom(*a, **k):
        raise raised

    monkeypatch.setattr(C, "terms", boom)
    assert C.main(["terms", HOME, "--user-agent", UA, "--out", str(tmp_path)]) == code
    assert capsys.readouterr().out.startswith(prefix)


def test_shoot_without_terms_json_is_a_caller_fault_not_a_refusal(tmp_path):
    out = tmp_path / "captures" / "SITE-example.org"
    out.mkdir(parents=True)
    with pytest.raises(ValueError):
        C.shoot(HOME, UA, out, "basis", set())


def _bare_chrome(site: str = HOME):
    chrome = object.__new__(C.Chrome)
    chrome.site, chrome.page, chrome.status, chrome.blocked, chrome.final_url = (
        "example.org",
        "MAIN",
        0,
        None,
        None,
    )
    chrome.sent = []
    chrome._send = lambda *a, **k: chrome.sent.append(a)
    return chrome


def test_final_url_is_the_main_documents_response_and_is_cut():
    chrome = _bare_chrome()
    long_url = HOME + "a" * 400
    for frame, url in (("MAIN", long_url), ("SUB", "https://example.org/frame")):
        chrome._gate(
            {
                "params": {
                    "requestId": "1",
                    "frameId": frame,
                    "request": {"url": url},
                    "responseStatusCode": 200,
                }
            }
        )
    assert chrome.final_url == long_url[:200]


def test_an_explicit_chrome_path_wins(monkeypatch):
    monkeypatch.setenv(C.CHROME_ENV, "/opt/chrome/chrome")
    monkeypatch.setattr(C.shutil, "which", lambda name: "/usr/bin/" + name)
    assert C.chrome_binary() == "/opt/chrome/chrome"


def test_chrome_is_found_on_the_path_by_any_known_name(monkeypatch):
    monkeypatch.delenv(C.CHROME_ENV, raising=False)
    monkeypatch.setattr(C.shutil, "which", lambda name: "/snap/bin/chromium" if name == "chromium" else None)
    assert C.chrome_binary() == "/snap/bin/chromium"


def test_no_chrome_anywhere_is_a_run_failure_not_a_refusal(monkeypatch):
    monkeypatch.delenv(C.CHROME_ENV, raising=False)
    monkeypatch.setattr(C.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError, match=C.CHROME_ENV):
        C.chrome_binary()


def test_a_failed_launch_still_removes_the_throwaway_profile(monkeypatch, tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    monkeypatch.setenv(C.CHROME_ENV, str(tmp_path / "no-such-chrome"))
    monkeypatch.setattr(C.tempfile, "mkdtemp", lambda **k: str(profile))
    with pytest.raises(OSError):
        C.Chrome(UA, HOME)
    assert not profile.exists()


@pytest.mark.parametrize("status", [406, 429])
def test_a_robots_406_or_429_is_a_failure_to_retry_not_a_refusal(monkeypatch, status):
    """Neither is a refusal, so neither may read as forbidden-by-terms; b6.md says when one retry is allowed."""

    def answer(*a, **k):
        raise urllib.error.HTTPError(HOME + "robots.txt", status, "", {}, None)

    monkeypatch.setattr(C, "_get", answer)
    with pytest.raises(urllib.error.HTTPError):
        C.read_robots(HOME, UA)
