# Perfection loop 2 handoff

## Release

- Work order: `tabular-file-diff-polish-2`
- Review baseline: `360e4934f8ff26fa04fc6266545a52181451dc15`
- Repair implementation: `f977344`
- Evidence and release record: `32fcb76`
- Branch: `main`, pushed to `origin/main`
- Artifact class: Python library plus static Vite site; unchanged
- Deployment: Azure Static Web Apps via the work-order static deploy helper
- Deployment IDs: `93e62aa3-81b9-4c8f-ba0b-7e317191b368`, then final
  exact-artifact deployment `aeec77ed-ba8e-4fad-a548-298a45be3ecb`
- Live URL: <https://tabular-file-diff.sociobot.in/>

## Delivered

- Reordered the sample demo so its computed counts, changed columns, schema
  change, and one changed row are all visible inside the first 390×844 screen.
- Kept one-click `/demo/` and `?demo=1` entry, the persistent demo banner,
  Reset demo, and Start for real. Exiting deletes only `demo:` session keys.
- Fixed the 390 px headline and navigation overflow without changing the Data
  Limited art-deco transit-poster identity.
- Added shared H1 focus and route announcements to Privacy, Terms, and 404.
- Completed 404 metadata, the consistent header/footer, and an actual local
  preview 404 response.
- Rewrote every copy item named by review 2 and every C1–C18 item from review
  1. The full word-count and terminology record is `.factory/copy-audit.md`.
- Expanded `.factory/claims.json` to 20 unique behavioral claims. Every claim
  has exactly one tagged test and a clean-state command.
- Strengthened browser tests for exact first-viewport visibility, real selected
  CSV files, no extra request, storage isolation, route history/focus, complete
  route metadata, 404 status, mobile width, Axe, and offline reload.
- Bumped the service-worker cache to v3 and made document navigations
  network-first with a cached offline fallback, so deployed fixes replace the
  old shell for returning visitors.
- Updated the catalog description to a 63-character verb-first sentence.
- Added `.factory/polish-2.md`, screenshots, live verification output, and
  Lighthouse JSON evidence.

## Clean-clone verification

Verified the exact repair commit in a separate clone at
`/tmp/tdiff-polish2.Ex17OJ/repo` with a new Python virtual environment and a
new `npm ci` install.

- Every one of the 20 commands in `.factory/claims.json`: pass. The six browser
  commands each passed desktop and 390×844; the 14 package commands each ran
  their one selected tagged test.
- `pytest`: 36 passed, including a built-wheel consumer in a separate venv.
- `ruff check src tests`: pass.
- `mypy src/tabular_file_diff`: success in five source files.
- `python -m build`: produced the 0.1.0 wheel and source distribution.
- `npm test`: TypeScript passed; 4 Vitest tests passed.
- `npm run build`: pass; wrote `dist/site`.
- `npm run test:a11y`: 22 Playwright tests passed in desktop and true 390×844
  projects, with no Axe WCAG A/AA violations.
- `npm audit --audit-level=high`: 0 vulnerabilities.
- Claim tag audit: 20 IDs, 20 unique IDs, zero missing or duplicate tags.

Production build sizes are 7.81 KB raw / 3.34 KB gzip JavaScript, 17.28 KB
raw / 4.55 KB gzip CSS, and 102.27 KB for the hero WebP. They are below the
200 KB, 50 KB, and 300 KB budgets.

## Live verification after deployment

Cold checks ran against the custom domain on 28 August 2026 after deployment.

- The worker `verify-url.sh` returned HTTP 200, title
  `tdiff — Compare keyed data files`, `lang=en`, one H1, one main landmark,
  zero missing alt attributes, zero unlabeled buttons, and zero console errors.
- The full remote Playwright suite ran with
  `PLAYWRIGHT_BASE_URL=https://tabular-file-diff.sociobot.in` and passed 22/22.
  This includes the direct demo, viewport proof, reset/exit isolation, selected
  local files, same-origin-only requests, no cookies/local storage, offline
  reload, route focus/history, 404, mobile width, and Axe.
- Final cold checks matched SHA-256 for home HTML, demo HTML, 404 HTML, hashed
  JavaScript, hashed CSS, and `sw.js` between `dist/site` and the live domain.
- Route checks: `/`, `/demo/`, `/privacy/`, and `/terms/` return 200 with their
  route titles. `/does-not-exist` returns 404 with `Route not found — tdiff`.
- Live response headers include CSP with `frame-ancestors 'none'`,
  `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, strict referrer
  policy, and a restrictive permissions policy.
- Lighthouse mobile: Performance 100, Accessibility 100, Best Practices 100,
  SEO 100; LCP 1.4 s, TBT 0 ms, CLS 0.
- Evidence: `.factory/evidence/polish-2-live-demo-mobile.png`,
  `.factory/evidence/live-verify/`, and
  `.factory/evidence/lighthouse-live-mobile.json`.

## Run and verify

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
pytest
ruff check src tests
mypy src/tabular_file_diff
python -m build
npm ci
npm test
npm run build
npm run test:a11y
```

Run a specific claim using its exact command in `.factory/claims.json`. Run the
browser suite against production with:

```bash
PLAYWRIGHT_BASE_URL=https://tabular-file-diff.sociobot.in npm run test:a11y
```

## Known gaps and next steps

No review-1 or review-2 finding remains open. The package was built and checked
as an external wheel consumer, but was not published to PyPI because registry
credentials and publication belong to the factory release process.
