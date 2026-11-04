# QA for the live page (2026-11-04)

Served from docs/ with python -m http.server, loaded in headless Chromium (software WebGL, so render timing is not representative).

## Lighthouse (desktop preset)

Performance 100, Accessibility 100, Best Practices 100, SEO 100

| Metric | Value |
|---|---|
| First Contentful Paint | 0.3 s |
| Largest Contentful Paint | 0.5 s |
| Speed Index | 0.9 s |
| Total Blocking Time | 40 ms |
| Cumulative Layout Shift | 0 |
| Time to Interactive | 0.5 s |
| Avoids enormous network payloads | Total size was 905 KiB |

Report: lighthouse.report.html, lighthouse.report.json.

## Headless-browser check

| View | Load (ms) | Transfer (bytes) | Images loaded | Canvases | Failed requests | Console errors |
|---|---|---|---|---|---|---|
| desktop | 1326 | 2,664,277 | 3/3 | heroCanvas 1440x900, xtalCanvas 512x538 | 0 | 0 |
| mobile | 1329 | 2,664,277 | 3/3 | heroCanvas 375x812, xtalCanvas 341x355 | 0 | 0 |

Screenshots: 2026-11-04-desktop-hero.png, 2026-11-04-desktop-dark-flythrough.png, 2026-11-04-desktop-end.png, 2026-11-04-desktop-full.png, 2026-11-04-mobile-375-hero.png, 2026-11-04-mobile-375-full.png.
