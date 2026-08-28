# Perfection loop 3 — cumulative finding closure

Implementation commit: `631a2a822e299f0d3bb538860776ad9d985153e5`
Review baseline: `1e66e2e53eddea34ade819e8f0486b5755b92864`
Deployment: `d51f5f08-fa68-426d-ba1e-888a1387bd47`
Live URL: <https://tabular-file-diff.sociobot.in/>

No review finding remains open.

## Adversarial review 3

| Finding | Change made | Automated evidence | Screenshot and live evidence |
| --- | --- | --- | --- |
| F-3-1 — browser demo did not run the library | Deleted `site/src/diff.ts`. The demo now loads a deterministic wheel built from `src/tabular_file_diff`, imports `diff_files` in a self-hosted Pyodide worker, and runs DuckDB plus PyArrow locally. It accepts editable CSV and uploaded CSV, gzip CSV, Parquet, Arrow IPC, and Feather files. It exposes package JSON, an HTML report download, numeric tolerance, and a fresh-project Python snippet. | `@claim:library-playground`; `test_playground_fixtures_match_diff_files`; `test_playground_wheel_contains_current_package`; the browser asserts the imported module is under `site-packages` and that no `site/src/diff` implementation exists. | `.factory/evidence/polish-3-live-demo-mobile.png`; live `/demo/` and `/?demo=1`; full live Playwright run: 24 passed. |

The real browser path found and fixed two package compatibility defects: the
declared DuckDB 1.1 range did not support `strict_mode` or `to_arrow_table`.
CSV uses compatible error handling, and Arrow conversion supports both DuckDB
1.x method names. The browser runs DuckDB 1.1.2, proving the lower bound.

## Adversarial review 2

| Finding | Change made | Evidence |
| --- | --- | --- |
| F1 — result below the first screen | Kept the compact result board directly below package identity. At 390×844 it spans y=466–674; at 1440×900 it spans y=601–751. | `@claim:demo-one-click`; `.factory/evidence/polish-3-demo-mobile.png`; `.factory/evidence/polish-3-demo-desktop.png`; live mobile screenshot. |
| F2 — 390 px overflow | The package heading, proof board, banner, editor, and tables all stay within 390 CSS pixels. | `expectDemo` and the mobile layout test assert `scrollWidth <= innerWidth`; live measured 390=390. |
| F3 — route focus | Home, Demo, Privacy, Terms, and 404 keep shared H1 focus and polite announcement behavior. | `legal navigation, history, and the 404 route preserve metadata and focus`; all live route tests passed. |
| F4 — incomplete claims | Expanded the registry to 21 entries with one unique `@claim:<id>` test each. Added the package-playground claim without dropping any earlier claim. | All 21 exact manifest commands passed individually from clean clone `/tmp/tdiff-polish3.pDwQzV/repo`; tag audit is 21/21 unique. |
| F5 — incomplete 404 metadata | Retained the designed HTTP 404 with canonical, description, Open Graph, Twitter, icons, full header/footer, and focused H1. | Live `/does-not-exist` returned 404; route metadata/focus test and Axe passed. |
| F6 — technical or inconsistent copy | Kept the prior plain-language rewrites and renamed the browser path consistently to “package playground.” | `.factory/copy-audit.md`; banned-word search is empty; every prose sentence is at most 22 words. |

## Adversarial review 1

| Finding | Change made | Evidence |
| --- | --- | --- |
| F1 — audience and first action | Retained “Compare keyed data snapshots,” the data-engineer/Git/DVC audience sentence, one sample action, its outcome, and three facts. | Live cold home screenshot at `.factory/evidence/polish-3-live-home-mobile.png`; home/mobile Playwright test. |
| F2 — no direct one-click demo | `/demo/` and `?demo=1` load the sample and automatically run the packaged wheel. | `@claim:demo-one-click`; live `/demo/` and `/?demo=1`. |
| F3 — no sandbox boundary | Retained the persistent banner, Reset demo, Start for real, and `demo:` session namespace. Runtime caches contain immutable code only, never selected files or results. | `@claim:demo-isolation`; `@claim:browser-private`; live demo. |
| F4 — look-alike CSV preview | Replaced the look-alike implementation with the real built wheel and removed both TypeScript comparator files. | `@claim:library-playground`; wheel-source parity test; live engine ticket shows wheel 0.1.0, DuckDB 1.1.2, PyArrow 18.1.0. |
| F5 — missing claims | Registry now covers demo behavior, privacy, offline execution, all formats, comparison semantics, CLI, API, reports, wrappers, licensing, and runtime support. | Every one of 21 claim commands passed separately from the clean clone. |
| F6 — fake demo and 404 routes | Retained real MPA routes and the deployed 404 response. | Live full Playwright route suite; `curl /does-not-exist` returned HTTP 404. |
| F7 — incomplete metadata/skeleton | Every route retains its own title, canonical, description, OG/Twitter data, icons, shared header, and legal footer. | Live metadata tests and `.factory/evidence/polish-3-live-home/verify.json`. |
| F8 — unclear links/focus | Demo/legal links use real URLs, external links name GitHub, and every route focuses and announces its H1. | Live route navigation/history/focus test. |

### Review 1 copy findings

| ID | Change retained or completed | Evidence |
| --- | --- | --- |
| C1 | Uses “Compare keyed data snapshots.” | Copy audit; live home. |
| C2 | Uses “How keyed comparison works.” | Copy audit. |
| C3 | Removed “conversion detours.” | Legacy-copy search. |
| C4 | Removed “Scale-oriented.” | Legacy-copy search. |
| C5 | Uses “Runs locally” with a precise privacy page. | `@claim:local-no-telemetry`; `@claim:browser-private`. |
| C6 | Uses concrete local-file and Git/DVC headings. | Copy audit. |
| C7 | Removed task-obscuring station and boarding headings. | Copy audit. |
| C8 | Uses “Compare tracked data files.” | Copy audit. |
| C9 | Uses “Compare local keyed data files.” | Footer on every route. |
| C10 | Keeps the sample action as the only primary hero action. | Live home screenshot. |
| C11 | Uses the mandated “Try it with sample data.” | Live home screenshot. |
| C12 | No generic Copy button appears on the first screen. | Home DOM test. |
| C13 | Reset immediately reruns the packaged sample. | `@claim:demo-isolation`. |
| C14 | README uses short format and result sentences. | Copy audit. |
| C15 | README separates tolerance scope and boundary behavior. | `@claim:tolerance-semantics`; copy audit. |
| C16 | Removed the long IEEE-754 first-read paragraph. | Copy audit. |
| C17 | Keeps the short Git external-driver explanation. | `@claim:git-wrapper`. |
| C18 | Keeps separate DVC materialization and cleanup sentences. | `@claim:dvc-wrapper`. |

## Earlier product and polish regressions

| Area | Evidence |
| --- | --- |
| Git/DVC adapters | `@claim:git-wrapper` and `@claim:dvc-wrapper` passed from clean temporary repositories. |
| Invalid CSV and CLI status | `@claim:cli-statuses` and package consumer tests passed. |
| Tolerance semantics | `@claim:tolerance-semantics` passed at the inclusive boundary. |
| Formats and API types | `@claim:package-formats` and `@claim:python-api` passed. |
| Local privacy | Package socket blocking and full browser request interception passed. |
| Offline | The packaged wheel recomputed the sample after a cold offline reload in both browser projects. |
| Visual identity | The art-deco transit-poster palette, type, geometry, and enamel-sign controls remain intact. |

## Verification evidence

- Clean clone: `/tmp/tdiff-polish3.pDwQzV/repo` at `631a2a8`.
- All 21 exact `.factory/claims.json` commands: pass.
- Python: 41 passed; Ruff clean; mypy clean across five modules; sdist and wheel built.
- Site: 2 Vitest tests; 24 Playwright tests; zero Axe WCAG A/AA violations.
- Build: 10.29 KB initial JS raw, 18.95 KB CSS raw; deferred self-hosted runtime; 45 MB total site artifact.
- Local Lighthouse: Performance 100, Accessibility 100, Best Practices 100, SEO 100; LCP 1.5 s, TBT 0 ms, CLS 0.
- Live Lighthouse: Performance 100, Accessibility 100, Best Practices 100, SEO 100; LCP 1.4 s, TBT 0 ms, CLS 0.
- Local URL evidence: `.factory/evidence/polish-3-local-home/` and `.factory/evidence/polish-3-local-demo/`.
- Live URL evidence: `.factory/evidence/polish-3-live-home/` and `.factory/evidence/polish-3-live-demo/`.
- Live deployment headers include CSP with WASM permission, HSTS, `nosniff`, strict referrer policy, permissions policy, and frame denial.
- Live unknown paths return the designed document with HTTP 404.

## Final live cold check

A new browser context opened the home page and `/?demo=1` at 390×844 with no
stored state. Home wording, the first action, route title, mobile width, and
console were correct. The demo redirected to `/demo/`, loaded the wheel from
the product origin, showed its engine versions and result in the first screen,
and produced no console error. Reset, Start for real, CSV edits, gzip CSV,
Parquet, Arrow IPC, report download, offline recomputation, legal routes,
focus, metadata, and 404 were rechecked by the 24-test live suite.
