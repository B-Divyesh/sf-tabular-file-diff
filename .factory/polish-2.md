# Perfection loop 2 — finding closure

Repair implementation: `f977344`  
Review baseline: `360e493`  
Artifact: Python library plus static Vite documentation/sample demo  
Live URL: <https://tabular-file-diff.sociobot.in/>

## Adversarial review 2

| Finding | Change made | Automated evidence | Visual/live evidence |
| --- | --- | --- | --- |
| F1 — results below the first screen | Moved a compact, computed result board before every editor control. It shows 1 added, 1 removed, 2 changed, 0 unchanged, changed columns, added `region`, and an A-101 row change. | `@claim:demo-one-click` asserts the whole board ends inside both 390×844 and desktop viewports. | `.factory/evidence/polish-2-live-demo-mobile.png`; live `/demo/` and `/?demo=1` passed. |
| F2 — 390 px overflow and clipped H1 | Reduced the phone display scale, constrained headings to their content column, simplified phone navigation, and tested the exact 390 CSS-pixel viewport. | `home, routes, keyboard controls, and mobile layout are accessible` asserts document width and H1 bounds. | `.factory/evidence/polish-2-home-mobile.png`; live `/` passed at 390×844. |
| F3 — legal and 404 focus | Loaded the shared route script on Privacy, Terms, and 404. Every route H1 receives `tabindex=-1`, focus without scroll, and an `aria-live` title announcement. | Route loop plus `legal navigation, history, and the 404 route preserve metadata and focus` cover direct navigation, header navigation, back, and unknown routes. | Live `/privacy/`, `/terms/`, and `/does-not-exist` passed in both projects. |
| F4 — incomplete claim registry | Expanded the registry from 13 broad entries to 20 unique claims. Each ID occurs in exactly one `@claim:` test and each command passed separately in the clean clone. | All commands in `.factory/claims.json`; tag audit reports `20` claims, `20` unique IDs, and no missing or duplicate tags. | Claim tests use `/demo/` or temporary package inputs; no manual state. |
| F5 — incomplete 404 metadata | Added canonical, description, Open Graph, Twitter card, favicon, Apple icon, full navigation/footer, live announcer, and shared route code. Added a local preview middleware that returns the designed document with HTTP 404. | `legal navigation, history, and the 404 route preserve metadata and focus` checks status, title, canonical, OG, Twitter, Apple icon, focus, and Axe. | Live `/does-not-exist` returned HTTP 404 and the designed document. |
| F6 — technical/inconsistent copy | Applied every supplied rewrite: row ID explanation, descriptive three-step and local-review labels, plain key explanation, and one “sample demo” term. Updated the README and full word-count audit. | `.factory/copy-audit.md`; banned-word search returns no matches; every prose unit is at most 22 words. | `/` and `/demo/`. |

### Review 2 F4 claim inventory

| Reviewed statement | Registered proof |
| --- | --- |
| Runs locally | `@claim:local-no-telemetry` blocks socket creation during a real comparison. |
| Rows, columns, schema | `@claim:comparison-results` asserts all four row states, column counts, and schema output; `@claim:demo-one-click` asserts visible browser proof. |
| Browser sample compares CSV in this tab | `@claim:browser-csv` supplies two files, compares them, and observes no new request. |
| Sample inputs ship in `examples/` | `@claim:packaged-demo` inspects both source and installed package samples. |
| CSV, gzip CSV, Parquet, and Arrow IPC | `@claim:package-formats` runs every named format through CLI JSON output. |
| Numeric-only inclusive tolerance, null behavior, exact default | `@claim:tolerance-semantics` exercises every rule. |
| CLI statuses 0, 1, and 2 | `@claim:cli-statuses` exercises identical, changed, malformed, and missing inputs. |
| Duplicate and null keys rejected | `@claim:key-validation` checks both errors. |
| Typed `DiffResult` and PyArrow tables | `@claim:python-api` checks the public result and all three difference table types. |
| Python 3.10 or later | `@claim:python-runtime` checks package metadata and classifiers. |
| Package is ready to build | The visitor-facing claim was removed. `python -m build` remains a release gate and produced both artifacts. |

## Adversarial review 1

| Finding | Change made | Evidence |
| --- | --- | --- |
| F1 — audience and first action | The first screen keeps “Compare keyed data snapshots,” names data engineers and Git/DVC, presents one primary sample action, explains its result, and shows three facts. | Home mobile screenshot; `home, routes, keyboard controls, and mobile layout are accessible`. |
| F2 — no direct one-click demo | `/demo/` and `?demo=1` load the completed shipped comparison. The hero action reaches it in one click. | `@claim:demo-one-click`. |
| F3 — no visible sandbox boundary | Persistent banner, Reset demo, Start for real, and the isolated `demo:sample-comparison` namespace remain present. Exit removes only `demo:` keys. | `@claim:demo-isolation`. |
| F4 — CSV preview was presented as the package | Copy now calls it the browser-only sample demo. `tdiff demo` runs the real installed package on bundled data in a fresh temporary directory. | `@claim:browser-csv`, `@claim:packaged-demo`, `.factory/demo.md`. |
| F5 — missing claims and tests | `.factory/claims.json` now has 20 behavior-level claims, including privacy, offline, formats, outputs, tolerance, statuses, Git, DVC, HTML, API, license, package demo, runtime, and read-only inputs. | Every manifest command passed from the clean clone. |
| F6 — fake demo/404 routes | Static MPA routes exist for Demo, Privacy, Terms, and 404. Local preview and deployed hosting return a real 404 for unknown paths. | Route metadata/focus Playwright test. |
| F7 — incomplete titles/metadata/skeleton | Every route has a plain title, canonical, description, OG/Twitter image metadata, icons, consistent header, and legal footer links. Assets are real files. | Per-route Playwright metadata assertions; built artifact inspection. |
| F8 — unclear links/focus | Demo and legal destinations use real URLs, external source labels say GitHub and show an external mark, and route focus/announcement is shared. | Navigation/history Playwright test. |

### Review 1 copy findings

| ID | Change made | Evidence |
| --- | --- | --- |
| C1 | Replaced the line-speed headline with “Compare keyed data snapshots.” | Home screenshot and copy audit. |
| C2 | Replaced the departure-board metaphor with “How keyed comparison works.” | Copy audit. |
| C3 | Removed “conversion detours”; the site now describes choosing and comparing snapshots directly. | Banned/legacy-copy search and copy audit. |
| C4 | Removed “Scale-oriented”; outputs are named concretely. | Copy audit and `@claim:comparison-results`. |
| C5 | Replaced the ambiguous machine fragment with “Runs locally” and a clear privacy page H1. | `@claim:local-no-telemetry`. |
| C6 | Replaced “Fits your workflow” with concrete Git/DVC and local-file headings. | Home copy audit. |
| C7 | Removed “Local station,” “Now boarding,” “signal,” and “Connect your line” from task headings. | Legacy-copy search and copy audit. |
| C8 | Replaced “first-class stops” with “Compare tracked data files.” | Copy audit. |
| C9 | Replaced the schedule metaphor with “Compare local keyed data files.” | Footer on every route. |
| C10 | Removed the competing hero install action; sample data is the sole primary action. | Home screenshot. |
| C11 | Replaced the vague CSV action with “Try it with sample data.” | Home screenshot. |
| C12 | Removed the generic Copy button from the first screen. | Home DOM/browser test. |
| C13 | Reset now immediately recomputes and displays the sample; no second click is needed. | `@claim:demo-isolation` and `@claim:demo-one-click`. |
| C14 | Split the long DuckDB README sentence into short, outcome-focused format and result statements. | README section in copy audit. |
| C15 | Split tolerance scope and boundary behavior into separate sentences. | Copy audit and `@claim:tolerance-semantics`. |
| C16 | Removed the IEEE-754 implementation paragraph from first-read documentation. | README copy audit. |
| C17 | Rewrote the Git sentence as “tdiff-git lets git diff print changes without an external-driver error.” | `@claim:git-wrapper`. |
| C18 | Split DVC behavior and cleanup into two short sentences. | `@claim:dvc-wrapper`. |

## Earlier product-specific regression findings

The pre-review verification findings remain closed: a real temporary Git repo
exits normally on differences (`@claim:git-wrapper`), Playwright starts from a
clean checkout (`22 passed`), malformed CSV exits 2, and deployment headers
declare CSP plus `frame-ancestors 'none'` and `X-Frame-Options: DENY`.

## Verification evidence

- Clean clone: `/tmp/tdiff-polish2.Ex17OJ/repo` at `f977344`.
- All 20 manifest commands: pass; browser claims passed in both projects and
  each package claim passed alone.
- Python: `36 passed`; Ruff clean; mypy clean in five modules; wheel and sdist built.
- Site: 4 Vitest tests; 22 Playwright tests; zero Axe WCAG A/AA violations.
- Browser claims cover request isolation, cookies, local storage, demo reset,
  custom files, route focus, 404, privacy, and offline service-worker reload.
- Build: JS 7.81 KB raw / 3.34 KB gzip; CSS 17.28 KB raw / 4.55 KB gzip;
  hero WebP 102.27 KB.
- Lighthouse desktop local: Performance 100, Accessibility 100, Best Practices
  100, SEO 100; LCP 0.4 s, TBT 0 ms, CLS 0. Evidence:
  `.factory/evidence/lighthouse-local.json`.
- `verify-url.sh` local: title, language, one H1, main, image alts, labels, and
  console checks passed. Evidence: `.factory/evidence/local-verify/`.

Post-deploy cold verification passed all 22 remote Playwright checks. The
worker URL verifier found no console or semantic errors. Live Lighthouse mobile
scored 100 in Performance, Accessibility, Best Practices, and SEO (LCP 1.4 s,
TBT 0 ms, CLS 0). See `.factory/evidence/live-verify/`,
`.factory/evidence/polish-2-live-demo-mobile.png`, and
`.factory/evidence/lighthouse-live-mobile.json`.
