# Perfection loop 3 handoff

## Delivered

- Replaced the separate TypeScript CSV comparator with the built
  `tabular-file-diff` Python wheel running in a self-hosted Pyodide worker.
- The in-page package playground now handles editable CSV plus selected CSV,
  gzip CSV, Parquet, Arrow IPC, and Feather files through `diff_files`.
- Added numeric tolerance, package JSON output, self-contained HTML report
  download, a working fresh-project snippet, exact engine versions, loading and
  recovery states, and offline package caching.
- Preserved the direct `?demo=1` and `/demo/` path, first-screen result,
  persistent sandbox banner, Reset demo, Start for real, and isolated `demo:`
  session state.
- Removed `site/src/diff.ts` and its look-alike implementation entirely.
- Fixed DuckDB 1.1 compatibility for CSV options and Arrow-table extraction.
- Expanded `.factory/claims.json` to 21 claims and added real wheel/fixture
  parity tests.
- Updated the catalog line, README, demo documentation, copy audit, design
  rationale, changelog, and cumulative finding ledger.

Implementation commit: `631a2a822e299f0d3bb538860776ad9d985153e5`.

## Verification

Fresh clone: `/tmp/tdiff-polish3.pDwQzV/repo` at `631a2a8`.

```bash
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build
npm test
npm run build
.venv/bin/python -m pytest
.venv/bin/ruff check src tests scripts
.venv/bin/mypy src/tabular_file_diff
.venv/bin/python -m build
npm run test:a11y
```

Results:

- Every exact command in `.factory/claims.json`: 21/21 passed individually.
- Python: 41 passed.
- Site unit tests: 2 passed.
- Desktop/mobile Playwright and Axe: 24 passed locally and 24 passed live.
- Ruff: clean. Mypy: clean across five source modules.
- Python wheel and sdist: built successfully.
- Vite output: `dist/site`, 45 MB total. Initial JS is 10.29 KB raw and
  initial CSS is 18.95 KB raw. The Python runtime is deferred to the demo.
- Local Lighthouse: 100 Performance, 100 Accessibility, 100 Best Practices,
  100 SEO; LCP 1.5 s, TBT 0 ms, CLS 0.
- Live Lighthouse: 100 Performance, 100 Accessibility, 100 Best Practices,
  100 SEO; LCP 1.4 s, TBT 0 ms, CLS 0.
- URL verifier: home and demo passed locally and live with no console errors,
  one H1, `lang`, `main`, image alternatives, and labeled buttons.
- Live unknown route: HTTP 404 with the designed recovery document.

Evidence is under `.factory/evidence/polish-3-*` and
`.factory/evidence/lighthouse-polish-3-*.json`. The finding-by-finding ledger is
`.factory/polish-3.md`.

## Deployment

- Production URL: <https://tabular-file-diff.sociobot.in/>
- Direct demo: <https://tabular-file-diff.sociobot.in/?demo=1>
- Azure Static Web Apps deployment: `d51f5f08-fa68-426d-ba1e-888a1387bd47`
- The deployed artifact was built from implementation commit `631a2a8`.
- A cold post-deploy run passed all 24 live Playwright checks, including the
  real wheel, every browser fixture, privacy interception, offline reload,
  metadata, focus, 404, mobile width, and Axe.

## Known gaps

None. All findings from reviews 1–3 and polish records are closed. The browser
runtime is intentionally deferred and self-hosted; it does not affect the
landing-page performance budget.

Registry publishing was not performed. The release artifacts are ready for the
factory-owned PyPI publishing step.
