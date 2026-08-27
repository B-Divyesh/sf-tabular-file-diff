# Independent verification — FAIL

**Candidate:** `96890562acd72b3749e9e15aff3c80031ab345ff` (`test: verify accessibility scale and release workflow`)

**Live URL:** <https://tabular-file-diff.sociobot.in/>

**Date:** 2026-08-27 UTC

## Verdict

**FAIL.** The advertised Git integration fails for the ordinary case where a
tabular file has differences. The repository's documented browser accessibility
test command also fails before executing any tests. These defects mean the
candidate does not meet the work order's end-to-end and local-quality-gate
requirements, despite the underlying diff engine, package build, and deployed
site otherwise behaving substantially as described.

## Severity-ordered defects

### P1 — documented Git diff workflow aborts on changed files

The README instructs users to configure:

```sh
git config diff.tdiff.command 'tdiff-git --key id'
printf '*.parquet diff=tdiff\n' >> .gitattributes
git diff -- data/snapshot.parquet
```

In a new Git repository I configured that driver (using an absolute path to the
candidate's `tdiff-git`), committed `snapshot.csv` with `id,v` rows `1,old` and
`2,stay`, then changed it to `1,new` and `3,add`. `tdiff-git` printed the
correct one-added / one-removed / one-modified summary, but returned `1` for
differences. Git treats that non-zero external-diff result as an execution
failure:

```text
fatal: external diff died, stopping at snapshot.csv
```

`git diff` exited `128`. Setting both `diff.tdiff.trustExitCode=true` and
`diff.trustExitCode=true` did not change that result with Git 2.43.0. Thus the
README recipe is not usable to review a changed file. `tdiff-git` must adapt
the `tdiff` difference exit code to Git's external-diff expectations (or the
documented integration must use a supported, actually tested invocation).

### P1 — declared browser accessibility command does not run from a clean checkout

After `npm ci` and `npx playwright install chromium`, the documented command
`npm run test:a11y` failed before it discovered a test:

```text
[WebServer] npm error path /tmp/tdiff-verify.Z7VnDz/site/package.json
[WebServer] npm error enoent Could not read package.json
Error: Process from config.webServer was not able to start. Exit code: 254
```

`site/playwright.config.ts` resolves the configuration directory as its working
directory, but its `webServer.command` calls `npm run build:site`, a script that
exists only in the repository-root `package.json`. Starting a production preview
at the root first allows the six Playwright tests to pass, but that is a manual
workaround, not the required clean-clone quality gate.

### P2 — production site has no CSP or clickjacking protection

The live home page and static assets send HSTS, `X-Content-Type-Options`,
`Referrer-Policy`, and a restrictive `Permissions-Policy`, but neither
`Content-Security-Policy` nor `X-Frame-Options` / `frame-ancestors` is present.
This is not the reason for the FAIL, but should be addressed on the deployment
configuration for a public site that runs client-side code.

### P3 — malformed CLI CSV is silently accepted

For `id,v\n1,"unterminated\n`, `tdiff bad.csv good.csv --key id` did not reject
the unclosed quote. DuckDB treated the old field as the literal string
`"unterminated` and reported a modification. The browser demo correctly says
`The CSV has an unclosed quoted field.` The CLI should either use strict CSV
parsing or document its deliberately permissive parsing; silent reinterpretation
is unsafe for a data-review tool.

## Evidence and checks performed

All commands below were run in a separate clean detached clone at exactly the
candidate SHA, with a fresh `.verify-venv` and a fresh `npm ci`.

| Area | Result | Evidence |
| --- | --- | --- |
| Python unit tests | PASS | `15 passed in 0.69s` (`.verify-venv/bin/pytest`) |
| Lint / strict types | PASS | `ruff check src tests`; `mypy src/tabular_file_diff`: `Success: no issues found in 5 source files` |
| Package build | PASS | `python -m build` created `tabular_file_diff-0.1.0.tar.gz` and `tabular_file_diff-0.1.0-py3-none-any.whl` |
| Site unit/type tests | PASS | `npm test`: TypeScript check and 4 Vitest tests passed |
| Exact production build | PASS | `npm run build:site` wrote `dist/site`; JS 7,353 B (3,130 B gzip), CSS 13,389 B (3,750 B gzip), hero 102,270 B — within 200 KB / 50 KB / 300 KB budgets |
| Declared a11y browser gate | **FAIL** | `npm run test:a11y` fails with missing `site/package.json`, as above |
| Browser suite with manual root preview workaround | PASS | All 6 desktop + 390×844 mobile Playwright tests passed; they covered sample comparison, tabs, offline notice, privacy, terms, and axe WCAG tags |
| Independent live browser smoke | PASS | Desktop keyboard-only sample/load/compare and tab arrows worked; brass 3 px focus ring was visible on the skip link; 390 px document width equalled viewport; reduced-motion context had no active CSS animations; no console/page errors |
| Independent browser demo inputs | PASS | Normal CSV: 1 added / 1 removed / 1 modified. Unclosed quote: clear error. Duplicate key: clear error. Replacing it with valid input recovered and completed comparison. |
| Axe serious/critical | PASS | Zero serious/critical violations on live `/`, `/privacy/`, and `/terms/` |
| Privacy / outbound requests | PASS | During live load and demo use the only request origin was `https://tabular-file-diff.sociobot.in`; no cookies or localStorage keys were present; no third-party font/script/analytics request observed. GitHub is an explicit outbound link, not fetched on load. |
| PWA/offline | PASS, limited | After a normal online load activated the service worker, an offline reload rendered the home page. `sw.js` uses a versioned cache and `skipWaiting`; no update migration scenario could be exercised without changing a deployed artifact. |
| Consumer installation / public API | PASS | Installed the built wheel into a brand-new venv outside the source tree; imported `diff_files`, compared CSVs (1/1/1), exercised `tdiff --json` and `tdiff --html` (exit 1 and non-empty standalone report). |
| Inputs | Mixed | API successfully exercised CSV normal/no-change/tolerance boundary/empty/composite-key, Parquet, Arrow IPC file + stream, duplicate/null-key rejection, and missing-file error. The malformed-CSV issue above failed. |
| Git integration | **FAIL** | Real temporary Git repo reproducer above. |
| DVC integration | LIMITED | No `dvc` executable was installed. `tdiff-dvc` handled the absence with exit 2 and a useful error, but no live DVC revision materialization was possible. |
| Dependency audit | PASS | `npm audit --audit-level=high`: `found 0 vulnerabilities` |
| Live/candidate match | PASS | SHA-256 matched for `index.html`, `privacy/index.html`, `terms/index.html`, `sw.js`, JS, CSS, and hero image. |
| Live transport/cache headers | MIXED | HTTPS/HSTS, nosniff, referrer, permissions policy present; hashed assets are `public, max-age=31536000, immutable`; HTML and SW are `max-age=30`; CSP and anti-framing headers absent. |

## Scope notes

- The original success target of two 50M-row Parquet files in under 60 seconds
  was not reproduced in this disposable verifier environment. The candidate
  itself makes no universal runtime claim; its small representative Parquet
  exercise passed.
- The service-worker update path is not proven merely by the offline smoke;
  deploy an updated cache/version and test an existing controlled client before
  representing update behavior as verified.

## Required next steps

1. Make the Git driver/recommended Git configuration complete successfully for
   changed files, then add an integration test using a real temporary Git repo.
2. Fix the Playwright web-server working directory/command so `npm run
   test:a11y` is self-contained from a clean checkout.
3. Add a CSP with an appropriate `frame-ancestors` policy in deployment config.
4. Decide and test strict malformed-CSV semantics for the CLI.
5. Re-run this verification; do not mark the release PASS until the P1 defects
   are resolved.
