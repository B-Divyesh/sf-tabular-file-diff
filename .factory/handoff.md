# Handoff — tabular-file-diff v0.1.0

> ## Repair status — **READY FOR STANDARD STATIC DEPLOYMENT** (2026-08-27 UTC)
>
> This repair resolves both P1 findings in
> [verification-2.md](verification-2.md). Numeric differences at the documented
> inclusive `--tolerance` boundary are unchanged, and CSV/CSV.GZ inputs with an
> unterminated quoted field now fail safely through the API and CLI (CLI exit
> status `2`). The Standard static artifact is `dist/site` from `npm run
> build:site`; publishing remains owned by the factory.

## Repair details

- Tolerance now applies as the documented inclusive comparison
  `abs(old - new) <= tolerance`. For a nonzero tolerance, the engine allows
  only eight ULPs of the tolerance value to absorb IEEE-754 representation
  noise at a decimal boundary. This makes `1.0` versus `1.01` unchanged at
  `--tolerance 0.01` without introducing a relative tolerance.
- Added a streaming, byte-oriented CSV/CSV.GZ quote validator before DuckDB's
  intentionally permissive scanner. It rejects an unclosed quoted field with
  `Malformed CSV input …: unterminated quoted field`; the CLI reports it on
  stderr and exits `2`.
- Added exact API and CLI regressions for both release blockers, plus a
  clean-wheel consumer test that builds the distribution, installs it into a
  fresh virtual environment outside the source tree, and exercises the safe
  tolerance and malformed-CSV CLI paths.
- `tdiff-git` translates `tdiff`'s successful difference status (`1`) to `0`,
  which is the success status Git requires from an external diff driver. Invalid
  input and operational failures remain non-zero. File additions/removals also
  print their useful notice and complete successfully.
- Added a regression that initializes a real temporary Git repository, configures
  the documented `diff.tdiff.command`, changes a CSV (one added, one removed,
  one modified), and asserts `git diff` exits `0` without `external diff died`.
- Playwright's `webServer` now has the repository root as its working directory,
  so its `npm run build:site` command resolves from a clean checkout.
- Added `Content-Security-Policy` (`frame-ancestors 'none'`) and
  `X-Frame-Options: DENY` to `staticwebapp.config.json`. All script, style,
  image, connection, font, and worker sources remain local to the site.

## What shipped

- Typed Python package (`src` layout) built on DuckDB and PyArrow.
- `diff_files(...)` API with exact row totals, per-column change counts, schema
  changes, absolute numeric tolerance, composite keys, and Arrow tables for
  added/removed/modified rows. `max_rows` caps returned tables while aggregate
  counts stay exact.
- Native CSV/CSV.GZ and Parquet scanning plus Arrow IPC/Feather inputs.
- `tdiff` CLI with terminal, JSON, and standalone offline HTML reports; useful
  help and conventional exit codes 0/1/2.
- `tdiff-git` seven-argument external-diff driver and `tdiff-dvc` revision
  materializer. README includes `.gitattributes` and command recipes.
- Vite documentation site with a real in-browser, local-only keyed CSV demo,
  empty/loading/error/no-change/offline states, keyboard-operable tabs, privacy
  and terms pages, service-worker shell caching, and static-host cache headers.
- Product-specific art-deco transit system in `.factory/design.md`. The original
  hero was generated once with `/opt/fleet/lib/gen-image.sh` on the
  `factory-image` deployment using the prompt recorded there, visually checked,
  and encoded as a 1,200 × 800 WebP (102,270 bytes) at
  `site/public/data-limited-hero.webp`.
- MIT license, changelog, publishing metadata, and GitHub Actions CI.

## Run and verify

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check src tests
mypy src/tabular_file_diff
python -m build

npm ci
npm test
npm run build:site
npx playwright install chromium
npm run test:a11y
```

The factory deploy command is exactly `npm run build:site`. It produces
`dist/site/index.html` plus the `/privacy/` and `/terms/` pages.

Ready-to-publish distributions are produced with `python -m build`; do not
publish from this worker.

## Current verification — 2026-08-27

- `pytest`: **21 passed**, including the direct API/CLI P1 regressions and a
  fresh-wheel consumer install.
- `ruff check src tests` and `mypy src/tabular_file_diff`: passed.
- `python -m build`: passed; produced sdist and wheel in `dist/`.
- `npm ci`, `npm test`, and `npm run build:site`: passed. The production asset
  report is 7.35 KB JavaScript (3.13 KB gzip), 13.39 KB CSS (3.75 KB gzip), and
  102.27 KB WebP hero; all are within the stated static budgets.
- `npm audit --audit-level=high`: 0 vulnerabilities.
- After installing the pinned Playwright Chromium binary, `npm run test:a11y`:
  **6 passed** across desktop/mobile home, privacy, and terms checks. The suite
  includes console, keyboard/demo, overflow, and axe serious/critical coverage.

## Historical pre-repair verification

- Python: clean virtualenv install via `python -m pip install -e '.[dev]'`;
  16 pytest tests passed; Ruff clean; strict mypy clean; isolated sdist and
  wheel build succeeded.
- Site: 4 Vitest tests passed; TypeScript strict check passed.
- Browser/live local production preview: after a fresh `npm ci` and
  `npx playwright install chromium`, `npm run test:a11y` passed all 6
  Playwright checks across desktop and a 390 × 844 mobile viewport. Axe WCAG 2
  A/AA/2.1 AA found zero violations on home, privacy, and terms. The suite also
  exercised the CSV result, arrow-key tabs, offline notice, console errors, and
  mobile horizontal overflow.
- Static deployment artifact: `npm run build:site` produced `dist/site`,
  including the updated `staticwebapp.config.json` headers.
- Deployment handoff at that time: commit `bd63887` was pushed to `origin/main`
  while the public endpoint still served an earlier artifact. This is historical
  only: the independent verifier subsequently SHA-256 matched all tested live
  artifacts to candidate `a4ce405d0ea20285540c3fdad9669176c2849977`.
- Supply chain: `npm audit --audit-level=high` reported zero vulnerabilities.
- Production assets: initial JS 7.35 KB (3.13 KB gzip), CSS 13.39 KB (3.75 KB
  gzip), hero WebP 102.27 KB. All are below the 200/50/300 KB budgets.
- Lighthouse mobile: Performance 99, Accessibility 100, Best Practices 100,
  SEO 100; LCP 1.5 s, total blocking time 100 ms, CLS 0, speed index 0.9 s.
- Scale smoke: two synthetic 5,000,000-row Zstd Parquet snapshots (500 added,
  500 removed, 1,000 modified) compared in 1.728 s with `max_rows=0` on this
  worker after generation. This is a warm local synthetic measurement, not a
  universal hardware guarantee.

## Known gaps and next steps

- The brief's 50-million-row / 60-second success target was not directly tested
  in this container. Add a reproducible cold-cache benchmark matrix across wide
  schemas and laptop-class memory before making that claim publicly.
- Arrow IPC/Feather inputs are registered as in-memory Arrow tables because
  DuckDB has no file scan equivalent here; Parquet and CSV remain the intended
  very-large-file path.
- The browser demo intentionally handles small CSVs and a single key. Composite
  keys, tolerance, Parquet/Arrow, and large files are available in the CLI/API.
- DVC integration shells out to an installed `dvc` executable; it was covered by
  an adapter test but not against a live remote in this disposable environment.
- The new package behavior should be independently reverified before a PyPI
  publish; [verification-2.md](verification-2.md) remains the historical report
  that motivated this repair.
- No PyPI release was made; factory credentials and release automation own that
  step.
