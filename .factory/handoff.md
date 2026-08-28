# Review 2 handoff

## Current review result

Adversarial review 2 was performed read-only against the live site and a clean
clone of `16f3288`. The detailed report is `.factory/review-2.md`.

**Verdict: FAIL.** The blocking finding is that the one-click sample demo loads
data but places all actual comparison results below the first 390 px and desktop
viewport. The review also records 390 px horizontal overflow, missing H1 focus
on Privacy/Terms/404, unlisted claims, and incomplete 404 metadata.

## How this review was verified

- All 13 commands in `.factory/claims.json` passed from a fresh clone.
- `npm test`, `npm run build`, `npm run test:a11y`, Python pytest, Ruff, and
  mypy all passed in that clone.
- Fresh live Chromium contexts checked 390 px and desktop cold reads, CTA/demo
  storage/reset/exit, same-origin requests, offline reload, metadata, routing,
  focus, and link crawl.
- Installed `tdiff demo` was run from an unrelated temporary directory and
  wrote its output under a separate `/tmp/tdiff-demo-*` directory.

## Next step

Address F1 in `.factory/review-2.md` first, then add a true-390-px viewport
test requiring the sample result to be visible without scrolling and rerun the
claim/quality commands.

---

# Historical repair handoff — perfection loop 1

## Delivered

Repair commit: 7a98c432ccb0ce3ffba5b97e2f576a97bdc22493.

- Rewrote the first screen around the reviewed headline, audience, sample CTA,
  outcome note, and three plain facts.
- Added direct /demo/ and ?demo=1 entry. The shipped sample is rendered as a
  completed comparison on first load.
- Added a persistent demo boundary, Reset demo, Start for real, and the
  demo:sample-comparison session-storage namespace.
- Added tdiff demo. It runs bundled CSVs through the installed package in a
  temporary directory and writes a self-contained report.
- Added claims registry, tagged browser/package claim tests, demo documentation,
  copy audit, sample inputs, and a verb-first catalog description.
- Added real static /demo/, privacy, terms, and 404 artifacts; route-specific
  titles, canonical/OG/Twitter metadata, favicon, 180px touch icon, social
  image, sitemap, and static-host 404 override.
- Preserved the Data Limited transit-poster identity while tightening mobile
  stacking, banner controls, focus treatment, link labels, and legal skeletons.

## Verification

A separate clean clone at /tmp/tdiff-clean.Z92cC5/repo was made from repair
commit 7a98c432ccb0ce3ffba5b97e2f576a97bdc22493.

- npm ci — pass, 0 high vulnerabilities.
- .verify-venv/bin/pytest — **30 passed**.
- .verify-venv/bin/ruff check src tests — pass.
- .verify-venv/bin/mypy src/tabular_file_diff — pass.
- .verify-venv/bin/python -m build — pass; wheel and sdist produced.
- npm test — **4 passed**.
- npm run build:site — pass; writes dist/site.
- npm run test:a11y -- --reporter=dot — **18 passed** across desktop and
  390px mobile, including Axe WCAG A/AA checks, keyboard tabs, offline reload,
  direct demo, reset/exit isolation, and same-origin-only request assertions.
- Every package claim test in tests/test_claims.py — **8 passed**.
  The full browser suite executes every browser @claim: test; the direct
  npm run test:claims -- --grep @claim:demo-one-click command also passed in
  2 browser projects.
- Static route smoke: /demo/ returns 200 and an unknown route returns 404
  under the Vite MPA preview. Built social images are non-empty.
- Produced assets: JS 7,228 B, CSS 14,690 B, and hero WebP 102,270 B.

## Deploy

The site remains a static Vite artifact. Push main to invoke the factory
work-order deployment for dist/site; no infrastructure configuration was
changed outside the repository.

## Historical known gaps

This section predates review 2 and is superseded by the findings above and in
`.factory/review-2.md`.
