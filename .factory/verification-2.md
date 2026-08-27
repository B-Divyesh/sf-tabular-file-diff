# Independent verification 2 — FAIL

**Candidate:** `a4ce405d0ea20285540c3fdad9669176c2849977` (`docs: record static deployment handoff`)

**Live URL:** <https://tabular-file-diff.sociobot.in/>

**Date:** 2026-08-27 UTC

## Verdict

**FAIL.** The candidate and live deployment are otherwise healthy and identical,
but the released CLI/library does not honour its documented absolute-tolerance
boundary and silently accepts malformed CSV. Both produce a normal
"differences found" result for data that should respectively be equal and
rejected, which is unsafe for the data-review job this package exists to do.

## Release-blocking defects

### P1 — exact absolute tolerance boundary is reported as a modification

README states that `--tolerance` is an **absolute** numeric tolerance. In a
fresh consumer environment, I compared these valid CSVs with
`--key id --tolerance 0.01`:

```csv
# old.csv
id,value
1,1.0

# new.csv
id,value
1,1.01
```

The numeric difference is exactly `0.01`, so it is within an absolute
tolerance of `0.01`. `diff_files(...)` instead returned
`modified_count == 1`, and `tdiff` returned exit code `1`. This is a
floating-point boundary error in an area the brief explicitly calls out as
requiring clear tolerance semantics. It can turn an approved threshold change
into a false data-review failure.

### P1 — unterminated quoted CSV is silently diffed instead of rejected

For `bad.csv` containing:

```csv
id,name
1,"unterminated
```

`tdiff bad.csv new.csv --key id --json` exited `1` and emitted a regular JSON
result (`old: 1`, `new: 3`, `added: 2`, `modified: 1`) with no stderr error.
It must exit `2` and explain that the input is malformed, rather than treating
an invalid record as reviewable data. The browser demo correctly says `The CSV
has an unclosed quoted field.`, so the CLI/API and demo currently disagree on
the same input. Replacing the bad file with a valid CSV in the browser recovers
normally, but that does not make the CLI result safe.

## Evidence

All candidate checks below were run from a new detached clone at the exact SHA
above (`git clone --no-local /work/repo`, then detached checkout), with a new
virtual environment and a fresh `npm ci`. No product files were modified.

| Area | Result | Evidence |
| --- | --- | --- |
| Python tests | PASS | `16 passed in 2.56s` with `.verify-venv/bin/pytest` |
| Python lint/types | PASS | `ruff check src tests`; strict `mypy src/tabular_file_diff`: 5 source files, no issues |
| Python distribution | PASS | `python -m build` produced sdist and wheel |
| Package consumer | PASS, except defects above | Installed the built wheel into a brand-new venv outside the clone. Imported `diff_files`; exercised CSV, CSV.GZ, Parquet, Arrow IPC stream, JSON CLI, self-contained HTML report, help/version and conventional 0/1/2 paths. HTML contained no scripts or external URLs. |
| Representative keyed diff | PASS | CSV with one added, removed, modified and unchanged row returned `1/1/1/1`, per-column count, and added/removed schema fields; no-change, duplicate-key and null-key paths behaved as documented. |
| Million-row Parquet smoke | PASS, limited scale coverage | Two 1,000,000-row Parquet snapshots, 1,000 modified / 999,000 unchanged, completed in `0.308s` warm with `max_rows=0`. This is not a 50M-row or laptop benchmark. |
| Git integration | PASS | In a real temporary Git repository, the documented external driver printed 1 added / 1 removed / 1 modified and `git diff` exited `0` without `external diff died`. |
| DVC integration | LIMITED | Adapter unit test passed. No `dvc` executable was installed in this container; `tdiff-dvc` exited `2` with the useful installation error, but live revision materialization was not exercised. |
| Site type/unit tests | PASS | `npm test`: TypeScript check plus 4 Vitest tests passed. |
| Exact production build | PASS | `npm run build:site` wrote `dist/site`. Initial JS: 7,353 B (3,130 B gzip); CSS: 13,389 B (3,750 B gzip); hero WebP: 102,270 B — all inside stated budgets. |
| Browser/a11y gate | PASS | Fresh `npm run test:a11y` passed all 6 desktop/390px Playwright tests; local axe checks had no WCAG A/AA/2.1 AA violations. |
| Live accessibility and interaction | PASS | On desktop, keyboard Enter loaded the sample and compared it (1 added / 1 removed / 2 modified); arrow-left changed the DVC tab to Git. The focused button had a visible `rgb(242, 193, 78) solid 3px` outline with 3px offset. At 390px, `scrollWidth == innerWidth == 390`, with one `h1` and `main`. Live axe serious/critical findings: 0 on `/`, `/privacy/`, and `/terms/`. Reduced-motion context had no running animations. |
| Browser invalid/recovery states | PASS | The live demo rejects an unclosed quote, permits a valid-file recovery to `No differences found`, and reports a duplicate key clearly. |
| Privacy/outbound requests | PASS | Live load and sample comparison requested only `https://tabular-file-diff.sociobot.in`; no cookies or localStorage keys; no third-party scripts, fonts, analytics, or data upload observed. |
| PWA/offline/update | PASS | A controlled live client offline-reloaded successfully. In a temporary copy of the built artifact, a simulated changed `sw.js` plus changed `index.html` caused `controllerchange`; a reload and an offline reload served the updated marker. |
| Security headers/caching | PASS | Live HTTPS response has HSTS, `nosniff`, strict referrer policy, restrictive permissions policy, self-only CSP with `frame-ancestors 'none'`, and `X-Frame-Options: DENY`. Hashed JS/CSS are `public, max-age=31536000, immutable`; HTML is `max-age=30`. |
| Dependency audit | PASS | `npm audit --audit-level=high`: 0 vulnerabilities. |
| Live/candidate parity | PASS | SHA-256 matched candidate build and live `index.html`, privacy/terms pages, service worker, favicon, hero, JS, and CSS. |

## Required follow-up

1. Define and test inclusive absolute-tolerance semantics at the exact
   threshold without binary floating-point false positives (or explicitly
   document a different contract, if that is truly intended).
2. Make CSV parsing reject unclosed quotes and other malformed records in the
   CLI/API, with exit status 2, consistently with the browser demo.
3. Add regression tests for both cases, then rerun independent verification.

## Scope notes

- This environment did not contain DVC, so a real DVC-backed revision fetch
  could not be verified.
- The brief's 50-million-row / under-60-second success measure was not
  reproduced; the million-row smoke only establishes a modest scale check.
