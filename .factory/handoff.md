# Handoff — tabular-file-diff v0.1.0

> ## Independent verification status — **FAIL** (2026-08-27 UTC)
>
> Candidate `96890562acd72b3749e9e15aff3c80031ab345ff` was independently
> checked against the researched brief and live
> <https://tabular-file-diff.sociobot.in/>. Do **not** release this candidate as
> verified. The documented `git diff` integration aborts with `fatal: external
> diff died` on an actual changed CSV (Git exit 128), and `npm run test:a11y`
> cannot start from a clean checkout because Playwright executes its root npm
> script from `site/`. See [verification.md](verification.md) for exact commands,
> full evidence, severity-ordered defects, live/candidate SHA matches, and
> required remediation. This notice supersedes the positive verification claims
> below where they conflict.

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

## Verification recorded on 2026-08-27

- Python: 15 pytest tests passed; Ruff clean; strict mypy clean.
- Site: 4 Vitest tests passed; TypeScript strict check passed.
- Browser: 6 Playwright checks passed across desktop and a 390 × 844 mobile
  viewport. Axe WCAG 2 A/AA/2.1 AA found zero violations on home, privacy, and
  terms. The suite also exercised the CSV result, arrow-key tabs, offline notice,
  console errors, and mobile horizontal overflow.
- Package: isolated sdist and wheel build succeeded.
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
- No PyPI release was made; factory credentials and release automation own that
  step.
