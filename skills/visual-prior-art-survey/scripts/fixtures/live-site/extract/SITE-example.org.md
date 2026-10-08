---
# A clean live-site record: one capture, observed and never prescribed. Its `capture` block is
# capture.json copied verbatim, and the images are placeholder bytes the gate hashes, never decodes.
schema_version: 1
meta:
  item_id: SITE-example.org
  as_of: '2026-10-08T10:00:14Z'
  revision: 1
outcome: extracted
convention:
  id: SITE-example.org
  id_class: live-site
  name: Example Domain home page
  corpus:
    name: example.org home page, as rendered
    version: Chrome/155.0.8059.39 render of 2026-10-08
    url: https://example.org/
    retrieved_at: '2026-10-08T10:00:14Z'
  authority: observed-site
  prescriptivity: observed
  statement: >
    The home page sets one centred column of system sans-serif text at 16px on a light grey
    background, with a 32px bold heading and one text link, at both 1280 and 320 px. No dark
    scheme is offered.
  governs: a single-page informational home page
  applicability:
    applies: false
    basis: 'observed, not prescribed: a capture binds nothing'
  tokens_in_body: false
  capture:
    url: https://example.org/
    final_url: https://example.org/
    user_agent: Sample-research/1.0 (research@example.org)
    renderer: Chrome/155.0.8059.39
    robots:
      url: https://example.org/robots.txt
      fetched_at: '2026-10-08T10:00:00Z'
      groups: []
      crawl_delay_s: 0
      allowed: true
    terms: {url: null, read_at: '2026-10-08T09:58:10Z', sha256: null, basis: no terms link on the home page}
    dark_scheme: not-offered
    shots:
    - viewport: 1280
      scheme: light
      path: captures/SITE-example.org/1280-light.webp
      sha256: 5a98f9a13022d6fa4222b1260a4860698f8232f2a46636e77c2cf12d67aa5349
      bytes: 75
      height_px: 800
      truncated: false
      captured_at: '2026-10-08T10:00:07Z'
      styles:
        html: {font-family: Times New Roman, font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        body: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgb(240, 240, 242)'}
        h1: {font-family: 'system-ui, sans-serif', font-size: 32px, font-weight: '700', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        p: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        a: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(56, 72, 143)', background-color: 'rgba(0, 0, 0, 0)'}
      fonts_loaded: []
    - viewport: 320
      scheme: light
      path: captures/SITE-example.org/320-light.webp
      sha256: 83f9d74ce143cdbb14030fccaf324c35739e5f12a57c9bb39b4b79827d9f55c5
      bytes: 74
      height_px: 640
      truncated: false
      captured_at: '2026-10-08T10:00:14Z'
      styles:
        html: {font-family: Times New Roman, font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        body: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgb(240, 240, 242)'}
        h1: {font-family: 'system-ui, sans-serif', font-size: 32px, font-weight: '700', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        p: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(0, 0, 0)', background-color: 'rgba(0, 0, 0, 0)'}
        a: {font-family: 'system-ui, sans-serif', font-size: 16px, font-weight: '400', line-height: normal, color: 'rgb(56, 72, 143)', background-color: 'rgba(0, 0, 0, 0)'}
      fonts_loaded: []
---

## Statement

One firm's home page, as Chrome rendered it on 2026-10-08: a single centred column, body text in
the system sans-serif at 16px on `rgb(240, 240, 242)`, an `h1` at 32px weight 700, and one link in
`rgb(56, 72, 143)`. The same layout at 1280 and 320 px. No dark scheme is offered. Observed, not
prescribed.

## Evidence

`captures/SITE-example.org/1280-light.webp` and `captures/SITE-example.org/320-light.webp`, with
the computed styles recorded beside each shot in `capture.shots[].styles`.

## Applicability

Does not apply: observed, not prescribed. `ui.complexity` is `consumer-grade`, so b6 ran; the
capture shows what one site shipped and binds nothing.
