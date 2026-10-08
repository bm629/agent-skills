#!/usr/bin/env python3
"""Capture one live site for angle b6: read its robots.txt and terms, then shoot it.

Standard library only, plus the installed Google Chrome, driven over the DevTools protocol on a
pipe (file descriptors 3 and 4): no websocket library, and no network port.

Usage:
    capture_live_site.py terms <url> --user-agent UA --out DIR
    capture_live_site.py shoot <url> --user-agent UA --out DIR --terms-basis TEXT

DIR is <evidence>/captures/<record_filename(item_id)>/. Read the terms that `terms` prints before
running `shoot`. Exit 0 done; 1 with REFUSED (robots, terms or the survey's own rules say no) or
UNREACHABLE (a 403, a challenge or an error page), each recorded and never retried; 2 with FAILED
(the run itself failed, a timeout, or a 406 or 429), which is not a refusal: references/angles/b6.md
lists the only retries the owner's rulings allow.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parent / "references" / "source-registry.yaml"
_SHOT = json.loads((HERE.parent / "schemas" / "extract-output.schema.json").read_text())["$defs"][
    "shot"
]["properties"]
MAX_BYTES = _SHOT["bytes"]["maximum"]
MAX_HEIGHT = _SHOT["height_px"]["maximum"]
MAX_FONTS = _SHOT["fonts_loaded"]["maxItems"]

#: An explicit path wins; otherwise the first of these names found on PATH.
CHROME_ENV = "CAPTURE_CHROME"
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
UA_SHAPE = re.compile(r"^\S+/\S+ \(.+\)$")
#: The owner's rule names these as Claude agents; a group naming one binds every run.
CLAUDE_AGENTS = ("claude", "anthropic-ai")
VIEWPORTS = {1280: 800, 320: 640}
ELEMENTS = ("html", "body", "h1", "h2", "h3", "p", "a", "button")
PROPS = ("font-family", "font-size", "font-weight", "line-height", "color", "background-color")
CUT = 200
TIMEOUT = 30
MIN_WAIT = 5
TERMS_LINK = re.compile(r"\b(terms|legal|conditions)", re.IGNORECASE)

STYLES_JS = """(() => {
  const out = {};
  for (const sel of ELEMENTS) {
    const el = document.querySelector(sel);
    if (!el) continue;
    const cs = getComputedStyle(el);
    out[sel] = {};
    for (const p of PROPS) out[sel][p] = cs.getPropertyValue(p);
  }
  const fonts = [];
  for (const f of document.fonts) if (f.status === "loaded") fonts.push(`${f.family} ${f.weight} ${f.style}`);
  return {styles: out, fonts: [...new Set(fonts)]};
})()""".replace("ELEMENTS", json.dumps(ELEMENTS)).replace("PROPS", json.dumps(PROPS))


class Refused(Exception):
    """Robots, terms or the survey's own rules say no: a `forbidden-by-terms` skip, never retried."""


class Unreachable(Exception):
    """A 403, a challenge or an error page: a `corpus-unreachable` skip, never retried."""


def _answered(url: str, status: int) -> Exception:
    """A 406 or 429 is not a refusal (FAILED; b6.md says when one retry is allowed); any other error is unreachable."""
    if status in (406, 429):
        return RuntimeError(f"{url} answered {status}")
    return Unreachable(f"{url} answered {status}; a challenge or error page is not the site")


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def chrome_binary() -> str:
    """$CAPTURE_CHROME if set, else the first Chrome or Chromium on PATH; none is a run failure."""
    if path := os.environ.get(CHROME_ENV):
        return path
    for name in CHROME_NAMES:
        if found := shutil.which(name):
            return found
    raise FileNotFoundError(f"no Chrome found: set {CHROME_ENV} or put {CHROME_NAMES[0]} on PATH")


def host(url: str) -> str:
    """The host, without `www.`, for the excluded-host comparison."""
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def excluded_hosts(registry_text: str) -> set[str]:
    """The registry's excluded hosts, read from its own `excluded:` block so the two cannot drift."""
    block = registry_text.split("\nexcluded:", 1)[1]
    return {host(u) for u in re.findall(r"^\s+url:\s*(\S+)", block, re.MULTILINE)}


def check_url(url: str, excluded: set[str]) -> None:
    """HTTPS only, and never a host the registry excludes or a subdomain of one."""
    if urlparse(url).scheme != "https":
        raise Refused(f"{url}: HTTPS only")
    h = host(url)
    if not h or any(h == x or h.endswith(f".{x}") for x in excluded):
        raise Refused(f"{url}: the registry excludes this host")


def robots_verdict(text: str, user_agent: str, url: str) -> dict:
    """Whether robots.txt lets this run fetch ``url``, and the longest delay it asks for.

    The run's product token, `*` and every Claude-named group all bind; a disallow in any of them
    is a refusal, and the largest Crawl-delay among them is the one honoured.
    """
    token = user_agent.split("/", 1)[0]
    parser = RobotFileParser()
    parser.parse(text.splitlines())
    named = re.findall(r"^\s*user-agent\s*:\s*(\S+)", text, re.IGNORECASE | re.MULTILINE)
    claude = [a for a in named if any(c in a.lower() for c in CLAUDE_AGENTS)]
    groups = sorted({a for a in named if a == "*" or a.lower() in token.lower() or a in claude})
    binding = [token, "*", *claude]
    return {
        "allowed": all(parser.can_fetch(a, url) for a in binding),
        "groups": groups,
        "crawl_delay_s": max((parser.crawl_delay(a) or 0 for a in binding), default=0),
        "refused_by": [a for a in binding if not parser.can_fetch(a, url)],
    }


class _Links(HTMLParser):
    """Every <a href> with its text, plus the page's visible text."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.text: list[str] = []
        self._href: str | None = None
        self._label: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "a":
            self._href, self._label = dict(attrs).get("href"), []

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._label)))
            self._href = None

    def handle_data(self, data):
        if self._skip:
            return
        self.text.append(data)
        if self._href is not None:
            self._label.append(data)


def terms_link(html: str, base: str) -> str | None:
    """The page's first terms or legal link, by its path or a short label.

    A long label is a card or a teaser: one tagged "Legal" is a case study, not the terms.
    """
    links = _Links()
    links.feed(html)
    for href, label in links.links:
        url = urljoin(base, href)
        if urlparse(url).scheme != "https":
            continue
        short = len(label.split()) <= 5
        if (short and TERMS_LINK.search(label)) or TERMS_LINK.search(urlparse(href).path):
            return url
    return None


class _Redirects(urllib.request.HTTPRedirectHandler):
    max_redirections = 5  # RFC 9309 follows robots.txt through at most five

    def __init__(self, same_host: bool) -> None:
        self.same_host = same_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlparse(req.full_url), urlparse(newurl)
        if self.same_host and (new.scheme != "https" or new.hostname != old.hostname):
            raise Refused(
                f"{req.full_url} redirects to {newurl}; that host's robots.txt was never read"
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_last = 0.0


def _pace(delay: float) -> None:
    """Wait max(Crawl-delay, 5 s), whole seconds, since the previous request to the site."""
    time.sleep(max(0.0, _last + math.ceil(max(delay, MIN_WAIT)) - time.time()))


def _get(url: str, user_agent: str, accept: str, same_host: bool = True) -> tuple[bytes, str]:
    global _last
    opener = urllib.request.build_opener(_Redirects(same_host))
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": accept})
    try:
        with opener.open(req, timeout=TIMEOUT) as resp:
            return resp.read(), resp.geturl()
    finally:
        _last = time.time()


def read_robots(url: str, user_agent: str) -> tuple[str, str]:
    """robots.txt for the URL's host. A 404 is no file; anything unreadable means disallow."""
    robots_url = f"https://{urlparse(url).hostname}/robots.txt"
    try:
        body, _ = _get(robots_url, user_agent, "text/plain", same_host=False)
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return robots_url, ""
        if exc.code in (406, 429):
            raise
        raise Refused(f"{robots_url} answered {exc.code}; an unreadable robots.txt means disallow")
    text = body.decode("utf-8", "replace")
    if re.search(r"<(!doctype|html)", text[:2048], re.IGNORECASE):
        raise Refused(
            f"{robots_url} came back as an HTML page; an unreadable robots.txt means disallow"
        )
    return robots_url, text


def _allowed(url: str, user_agent: str) -> tuple[dict, str]:
    robots_url, text = read_robots(url, user_agent)
    verdict = robots_verdict(text, user_agent, url)
    if not verdict["allowed"]:
        raise Refused(f"{robots_url} disallows {url} for {', '.join(verdict['refused_by'])}")
    return verdict, robots_url


def terms(url: str, user_agent: str, out: Path, excluded: set[str]) -> None:
    """Step 1: robots.txt, then the home page's first terms or legal link, printed for reading."""
    check_url(url, excluded)
    verdict, robots_url = _allowed(url, user_agent)
    print(
        f"{robots_url}: allowed; groups {verdict['groups']}, crawl delay {verdict['crawl_delay_s']}s"
    )
    _pace(verdict["crawl_delay_s"])
    page, final = _get(url, user_agent, "text/html")
    link = terms_link(page.decode("utf-8", "replace"), final)
    record = {"url": None, "read_at": now(), "sha256": None}
    if link is None:
        print("No terms or legal link on the home page.")
    else:
        check_url(link, excluded)
        delay = verdict["crawl_delay_s"]
        if urlparse(link).hostname != urlparse(url).hostname:
            delay = max(delay, _allowed(link, user_agent)[0]["crawl_delay_s"])
        _pace(delay)
        body, _ = _get(link, user_agent, "text/html")
        record = {"url": link, "read_at": now(), "sha256": hashlib.sha256(body).hexdigest()}
        text = _Links()
        text.feed(body.decode("utf-8", "replace"))
        print(f"Terms at {link}:\n")
        print(re.sub(r"\n\s*\n+", "\n\n", "".join(text.text)).strip())
    out.mkdir(parents=True, exist_ok=True)
    (out / "terms.json").write_text(json.dumps(record, indent=2) + "\n")


class Chrome:
    """Headless Chrome on a pipe: sandbox on, throwaway profile, no input events, killed on exit."""

    def __init__(self, user_agent: str, site: str) -> None:
        self.site = urlparse(site).hostname
        self.page: str | None = None
        self.blocked: str | None = None
        self.final_url: str | None = None
        self.status = 0
        self.profile = tempfile.mkdtemp(prefix="b6-profile-")
        self.log = os.path.join(self.profile, "chrome-stderr.log")
        try:
            self._launch(user_agent)
        except BaseException:
            self._remove_profile()
            raise
        self._id, self._buf, self.events = 0, b"", []

    def _launch(self, user_agent: str) -> None:
        err = os.open(self.log, os.O_WRONLY | os.O_CREAT, 0o600)
        to_chrome, self._to = os.pipe()
        self._from, from_chrome = os.pipe()

        def fds() -> None:
            r, w = os.dup(to_chrome), os.dup(from_chrome)
            os.dup2(r, 3)
            os.dup2(w, 4)

        try:
            self.proc = subprocess.Popen(
                [
                    chrome_binary(),
                    "--headless",
                    "--remote-debugging-pipe",
                    f"--user-data-dir={self.profile}",
                    f"--user-agent={user_agent}",
                    "--disable-extensions",
                    "--block-new-web-contents",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-networking",
                    "--disable-component-update",
                    "--disable-sync",
                    "--hide-scrollbars",
                    "--mute-audio",
                    "about:blank",
                ],
                preexec_fn=fds,
                close_fds=False,
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=err,
            )
        except BaseException:
            for fd in (self._to, self._from):
                os.close(fd)
            raise
        finally:
            for fd in (err, to_chrome, from_chrome):
                os.close(fd)

    def close(self) -> None:
        try:
            os.killpg(self.proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        self.proc.wait()
        os.close(self._to)
        os.close(self._from)
        self._remove_profile()

    def _remove_profile(self) -> None:
        try:
            shutil.rmtree(self.profile)
        except OSError as exc:
            print(f"WARN throwaway profile {self.profile} not removed: {exc}", file=sys.stderr)

    def _send(self, method: str, params: dict | None = None, session: str | None = None) -> int:
        self._id += 1
        msg = {"id": self._id, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        data = json.dumps(msg).encode() + b"\0"
        while data:
            data = data[os.write(self._to, data) :]
        return self._id

    def _next(self, deadline: float) -> dict:
        while b"\0" not in self._buf:
            left = deadline - time.time()
            if left <= 0 or not select.select([self._from], [], [], left)[0]:
                raise TimeoutError(f"Chrome gave no answer within {TIMEOUT}s")
            chunk = os.read(self._from, 1 << 20)
            if not chunk:
                with open(self.log, "rb") as log:
                    tail = log.read()[-800:].decode("utf-8", "replace")
                raise RuntimeError(f"Chrome exited; its stderr ends: {tail}")
            self._buf += chunk
        raw, self._buf = self._buf.split(b"\0", 1)
        msg = json.loads(raw)
        if msg.get("method") == "Fetch.requestPaused":
            self._gate(msg)
        return msg

    def _gate(self, msg: dict) -> None:
        """A main-frame navigation off the site's host is refused, never followed, and the main
        document's status is kept, so an error or challenge page is never shot as the site."""
        p, session = msg["params"], msg.get("sessionId")
        target = urlparse(p["request"]["url"])
        main = p.get("frameId") == self.page
        if main and "responseStatusCode" in p:
            self.status = max(self.status, p["responseStatusCode"])
            # The document's own URL, which pushState cannot move.
            self.final_url = p["request"]["url"][:CUT]
        elif main and (target.scheme != "https" or target.hostname != self.site):
            self.blocked = p["request"]["url"]
            self._send(
                "Fetch.failRequest",
                {"requestId": p["requestId"], "errorReason": "BlockedByClient"},
                session,
            )
            return
        self._send("Fetch.continueRequest", {"requestId": p["requestId"]}, session)

    def call(self, method: str, params: dict | None = None, session: str | None = None) -> dict:
        mid = self._send(method, params, session)
        deadline = time.time() + TIMEOUT
        while True:
            msg = self._next(deadline)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg)

    def wait(self, method: str) -> None:
        deadline = time.time() + TIMEOUT
        while not any(e["method"] == method for e in self.events):
            msg = self._next(deadline)
            if "method" in msg:
                self.events.append(msg)
        self.events.clear()

    def settle(self, seconds: float) -> None:
        """Let the page settle, still answering its paused requests."""
        deadline = time.time() + seconds
        try:
            while True:
                self._next(deadline)
        except TimeoutError:
            pass

    def open(self) -> str:
        self.page = self.call("Target.createTarget", {"url": "about:blank"})["targetId"]
        s = self.call("Target.attachToTarget", {"targetId": self.page, "flatten": True})[
            "sessionId"
        ]
        self.call("Page.enable", session=s)
        self.call(
            "Fetch.enable",
            {
                "patterns": [
                    {"resourceType": "Document", "requestStage": "Request"},
                    {"resourceType": "Document", "requestStage": "Response"},
                ]
            },
            session=s,
        )
        return s


def _styles(raw: dict) -> tuple[dict, list[str]]:
    """Computed values are page-controlled data: only the expected keys, each cut at 200."""
    raw_styles = raw.get("styles") if isinstance(raw.get("styles"), dict) else {}
    styles = {
        el: {p: str(raw_styles[el].get(p, ""))[:CUT] for p in PROPS}
        for el in ELEMENTS
        if isinstance(raw_styles.get(el), dict)
    }
    return styles, [str(f)[:CUT] for f in (raw.get("fonts") or [])[:MAX_FONTS]]


def _colours(styles: dict) -> dict:
    return {(el, p): v[p] for el, v in styles.items() for p in ("color", "background-color")}


def shoot(url: str, user_agent: str, out: Path, basis: str, excluded: set[str]) -> None:
    """Step 2: re-read robots.txt, then capture 1280 and 320 px, light and (if offered) dark."""
    global _last
    check_url(url, excluded)
    if out.parent.name != "captures":
        raise ValueError(f"--out must be <evidence>/captures/<record_filename(item_id)>, not {out}")
    terms_file = out / "terms.json"
    if not terms_file.is_file():
        raise ValueError(f"no {terms_file}: run `terms` and read the terms first")
    verdict, robots_url = _allowed(url, user_agent)
    robots = {
        "url": robots_url,
        "fetched_at": now(),
        "groups": verdict["groups"],
        "crawl_delay_s": verdict["crawl_delay_s"],
        "allowed": True,
    }
    shots, images, final_url = [], {}, None
    chrome = Chrome(user_agent, url)
    try:
        renderer = chrome.call("Browser.getVersion")["product"]
        chrome.call("Browser.setDownloadBehavior", {"behavior": "deny"})
        s = chrome.open()
        for viewport, height in VIEWPORTS.items():
            chrome.call(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": viewport,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": viewport == 320,
                },
                session=s,
            )
            schemes = {}
            for scheme in ("light", "dark"):
                chrome.call(
                    "Emulation.setEmulatedMedia",
                    {"features": [{"name": "prefers-color-scheme", "value": scheme}]},
                    session=s,
                )
                if scheme == "light":
                    _pace(verdict["crawl_delay_s"])
                    chrome.events.clear()
                    nav = chrome.call("Page.navigate", {"url": url}, session=s)
                    if nav.get("errorText") and not chrome.blocked:
                        raise RuntimeError(f"{url} did not load: {nav['errorText']}")
                    if not chrome.blocked:
                        chrome.wait("Page.loadEventFired")
                        chrome.settle(2)
                    final_url = final_url or chrome.final_url
                else:
                    chrome.settle(1)
                if chrome.blocked:
                    raise Refused(
                        f"{url} navigated to {chrome.blocked}; that host's robots.txt was never read"
                    )
                if chrome.status >= 400:
                    raise _answered(url, chrome.status)
                world = chrome.call(
                    "Page.createIsolatedWorld",
                    {"frameId": chrome.page, "worldName": "b6"},
                    session=s,
                )
                raw = (
                    chrome.call(
                        "Runtime.evaluate",
                        {
                            "expression": STYLES_JS,
                            "contextId": world["executionContextId"],
                            "returnByValue": True,
                        },
                        session=s,
                    )["result"].get("value")
                    or {}
                )
                styles, fonts = _styles(raw)
                schemes[scheme] = styles
                if scheme == "dark" and _colours(styles) == _colours(schemes["light"]):
                    continue
                full = math.ceil(
                    chrome.call("Page.getLayoutMetrics", session=s)["cssContentSize"]["height"]
                )
                clip = min(full, MAX_HEIGHT)
                while True:
                    data = base64.b64decode(
                        chrome.call(
                            "Page.captureScreenshot",
                            {
                                "format": "webp",
                                "quality": 80,
                                "captureBeyondViewport": True,
                                "clip": {
                                    "x": 0,
                                    "y": 0,
                                    "width": viewport,
                                    "height": clip,
                                    "scale": 1,
                                },
                            },
                            session=s,
                        )["data"]
                    )
                    if len(data) <= MAX_BYTES or clip < 2:
                        break
                    clip //= 2  # ponytail: halve the height until it fits; truncated says so
                name = f"{viewport}-{scheme}.webp"
                images[name] = data
                shots.append(
                    {
                        "viewport": viewport,
                        "scheme": scheme,
                        "path": f"captures/{out.name}/{name}",
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data),
                        "height_px": clip,
                        "truncated": clip < full,
                        "captured_at": now(),
                        "styles": styles,
                        "fonts_loaded": fonts,
                    }
                )
            _last = time.time()
    finally:
        chrome.close()
    if any(len(d) > MAX_BYTES for d in images.values()):
        raise RuntimeError(f"an image stayed above {MAX_BYTES} bytes; nothing written")
    for name, data in images.items():
        (out / name).write_bytes(data)
    capture = {
        "url": url,
        "final_url": final_url,
        "user_agent": user_agent,
        "renderer": renderer,
        "robots": robots,
        "terms": {**json.loads(terms_file.read_text()), "basis": basis},
        "dark_scheme": "offered" if any(s["scheme"] == "dark" for s in shots) else "not-offered",
        "shots": shots,
    }
    (out / "capture.json").write_text(json.dumps(capture, indent=2) + "\n")
    terms_file.unlink()
    print(json.dumps({"shots": [s["path"] for s in shots], "bytes": [s["bytes"] for s in shots]}))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("terms", "shoot"):
        sp = sub.add_parser(name)
        sp.add_argument("url")
        sp.add_argument("--user-agent", required=True)
        sp.add_argument("--out", type=Path, required=True)
        if name == "shoot":
            sp.add_argument("--terms-basis", required=True)
    args = p.parse_args(argv)
    if not UA_SHAPE.match(args.user_agent):
        print("FAILED: --user-agent must read product/version (contact)")
        return 2
    excluded = excluded_hosts(REGISTRY.read_text())
    try:
        if args.cmd == "terms":
            terms(args.url, args.user_agent, args.out, excluded)
        else:
            shoot(args.url, args.user_agent, args.out, args.terms_basis, excluded)
    except urllib.error.HTTPError as exc:
        return _report(_answered(exc.url, exc.code))
    except (Refused, Unreachable, OSError, ValueError, RuntimeError) as exc:
        return _report(exc)
    return 0


def _report(exc: Exception) -> int:
    """REFUSED reads as `forbidden-by-terms`, UNREACHABLE as `corpus-unreachable`."""
    prefix, code = {Refused: ("REFUSED", 1), Unreachable: ("UNREACHABLE", 1)}.get(
        type(exc), ("FAILED", 2)
    )
    print(f"{prefix}: {exc}")
    return code


if __name__ == "__main__":
    sys.exit(main())
