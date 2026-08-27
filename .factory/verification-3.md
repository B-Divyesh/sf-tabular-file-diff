# Independent verification — PASS

**Candidate:** `1e8edd9458ea9d8325848bbf2f25e2f44243b50a`
**Live URL:** <https://tabular-file-diff.sociobot.in/>
**Date:** 2026-08-27 UTC
**Verifier environment:** clean detached clone, Python 3.12, Node/npm clean install,
Playwright Chromium 151, DVC 3.67.1.

## Verdict

**PASS.** The prior P1 failures are resolved from fresh independent evidence:
the documented Git external driver completes normally when differences exist,
and `npm run test:a11y` runs from a clean checkout. The candidate satisfies the
researched v1 contract: local key-aware CSV/Parquet/Arrow diffs, CLI summary
and standalone report, typed Arrow-returning Python API, Git and DVC adapters,
and a local-only documentation/demo site.

No release-blocking defects were found.

## Clean-checkout quality gates

| Check | Result | Evidence |
| --- | --- | --- |
| Candidate identity / clean state | PASS | Detached clean clone at the exact SHA above. |
| Python tests | PASS | `21 passed in 9.42s` from a new `.verify-venv`. |
| Lint and strict types | PASS | `ruff check src tests`: clean; `mypy src/tabular_file_diff`: no issues in 5 source files. |
| Distribution build | PASS | `python -m build` created `tabular_file_diff-0.1.0.tar.gz` and `tabular_file_diff-0.1.0-py3-none-any.whl`. |
| Site type/unit suite | PASS | `npm ci`; `npm test`: TypeScript check plus 4 Vitest tests passed. |
| Exact production build | PASS | `npm run build:site` completed and wrote `dist/site`. |
| Browser/a11y gate | PASS | Fresh Chromium install then `npm run test:a11y`: all 6 desktop/mobile Playwright tests passed. |
| Dependency audit | PASS | `npm audit --audit-level=high`: 0 vulnerabilities. |

Production asset sizes are 7,353 B JS (3,130 B gzip), 13,389 B CSS (3,750 B
gzip), and 102,270 B WebP hero. They are below the 200 KB JS, 50 KB CSS, and
300 KB hero budgets.

## Independent product and consumer exercises

- Installed the built wheel into a separate virtual environment outside the
  source checkout. Its public API and installed `tdiff` binary compared CSV,
  CSV.GZ, Parquet, and Arrow IPC files successfully.
- CSV normal/tolerance/schema case: 3 old and 3 new rows yielded 1 added, 1
  removed, 0 modified, and 2 unchanged at the inclusive `--tolerance 0.01`
  boundary; the new `enabled` column was reported as schema drift.
- Parquet consumer case returned 1 added / 1 removed / 1 modified. Arrow IPC
  returned 1 modified. `max_rows=0` retained exact counts while returning empty
  samples and marking them truncated.
- Invalid user paths recovered safely: malformed quoted CSV, duplicate keys,
  and a missing key column all returned CLI status 2 with actionable errors.
  An HTML report was created and contained neither scripts nor external URLs.
- Real Git repository: configured the README's
  `diff.tdiff.command 'tdiff-git --key id'`, changed a CSV, and `git diff`
  printed 1 added / 1 removed / 1 modified and exited **0** (no external-diff
  failure).
- Real local Git+DVC repository: DVC 3.67.1 materialized tagged revision `v1`
  and `HEAD`; `tdiff-dvc data.csv --from v1 --to HEAD --key id --json` reported
  1 added / 1 removed / 1 modified and exited 1, the documented normal
  differences status.
- Scale smoke: generated two 5,000,000-row Zstd Parquet files with 500 added,
  500 removed, and 1,000 modified rows. `diff_files(..., max_rows=0)` returned
  exactly those counts and 4,998,500 unchanged rows in **2.148 s** on this
  verifier's warm local hardware. This is a smoke test, not a claim for the
  brief's 50M-row/laptop target.

## Live deployment, browser, privacy, and security

- Downloaded live `/`, `/privacy/`, `/terms/`, service worker, JS, CSS, and
  hero files. Their SHA-256 values exactly match the candidate's fresh
  `dist/site` outputs.
- Live desktop and 390 x 844 mobile checks found one `h1`, one `main`,
  `lang="en"`, correct title, no horizontal mobile overflow, and no console or
  page errors. The first keyboard focus is the visible 3 px skip-link focus
  outline; arrow-key tab switching works.
- Browser demo exercised normal sample comparison, an unterminated-quote
  error, then replacement with valid CSVs and successful recovery (1 added / 1
  removed / 1 modified). Axe found zero serious or critical findings on home,
  privacy, and terms.
- Only `https://tabular-file-diff.sociobot.in` was requested while loading and
  using the demo. There were no cookies or localStorage entries, no loaded
  third-party scripts/fonts/analytics, and the local CSV operation made no
  network request.
- Service worker registered and controlled the live client; forcing an offline
  context displayed the offline notice, and an offline reload rendered cached
  `main` successfully. `registration.update()` completed against the current
  worker. The worker uses a versioned cache with `skipWaiting` and
  `clients.claim`.
- `prefers-reduced-motion: reduce` had zero running animations (route animation
  duration `0.01ms`). Fresh Lighthouse mobile scored Performance 100,
  Accessibility 100, Best Practices 100, and SEO 100 (LCP 1,380 ms, TBT 6 ms,
  CLS 0).
- Live HTML uses 30-second revalidation; hashed assets use
  `public, max-age=31536000, immutable`. HSTS, `nosniff`, strict referrer and
  permissions policies, CSP with `frame-ancestors 'none'`, and
  `X-Frame-Options: DENY` are present.

## Defects by severity

None found (P0/P1/P2/P3).

## Coverage limits / follow-up

- The 50M-row-under-60-second success measure was not reproduced. The 5M-row
  result above is meaningful scale evidence but is hardware- and schema-
  dependent; benchmark the exact target on laptop-class cold caches before
  making that performance promise.
- A service-worker *replacement* transition cannot be exercised against one
  immutable live artifact. Current registration/update invocation and offline
  reload passed; perform one staged-version upgrade test before changing the
  worker strategy.
- DVC was verified with local Git/DVC history only, not a remote-backed DVC
  store. The adapter correctly uses the installed DVC CLI and local revisions.
