# Adversarial first-read review 2

**Product:** tabular-file-diff  
**Reviewed:** 2026-08-28  
**Live URL:** https://tabular-file-diff.sociobot.in/  
**Repository:** clean clone of `16f3288`  
**Verdict:** **FAIL**

The direct sample demo fails the required first-screen test: it loads the
sample, but its actual result is below the initial viewport on phone and
desktop. There are also mobile overflow, route-focus, claims-registry, and 404
metadata findings.

## Cold first screen

Fresh Chromium contexts, with no prior storage, opened the live home page at
390 × 844 and 1440 × 900 before scrolling.

- **What it does:** compares two tabular-data versions by a row key and reports
  changes.
- **For whom:** data engineers reviewing CSV, Parquet, or Arrow changes in Git
  or DVC.
- **First click:** **“Try it with sample data.”**

Those answers are available above the fold from **“Compare keyed data
snapshots”**, **“For data engineers reviewing CSV, Parquet, or Arrow changes in
Git or DVC.”**, and **“Try it with sample data.”** The cold landing read is not
blocking.

## Findings

### BLOCKING F1 — Direct demo results are not visible in the first screen

- **Quote:** **“See keyed CSV changes”** and **“Sample comparison loaded. It
  has 1 added, 1 removed, and 2 changed rows.”**
- **Check:** the home CTA does reach `/demo/` in one click. The shipped sample,
  banner, and results load correctly. At 390 × 844, however, `#demo-result`
  starts at **1,437 px** and its first added count at **1,480 px**. At
  1440 × 900, the result starts at **1,107 px**. The first screen therefore
  contains the banner, title, copy, and setup controls, but no added/removed/
  changed result, schema result, or changed row.
- **Why a visitor is lost:** a phone visitor must scroll substantially before
  seeing proof that the sample works. This violates the one-click-demo rule
  that the first screen after the action already show the product in use with
  realistic data.
- **Concrete fix:** show a compact result directly below the banner, for
  example: **“Sample result: 1 added · 1 removed · 2 changed · column `region`
  added.”** Include one changed-row example there, and move/collapse editable
  controls below it. Extend `@claim:demo-one-click` to assert that the result
  intersects a 390 × 844 viewport after direct `/demo/` navigation.

### Major F2 — The 390 px homepage overflows horizontally and clips the H1

- **Quote:** **“Compare keyed data snapshots”**.
- **Check:** with a true `viewport: { width: 390, height: 844 }`, the live page
  reports `clientWidth: 390` and `scrollWidth: 408`. The H1 is 391.69 px wide,
  begins at 16 px, and ends at 407.69 px. Its final line is clipped in the
  first viewport.
- **Why a visitor is lost:** the job statement appears broken on the stated
  phone size before the visitor reaches the sample action.
- **Concrete fix:** reduce the mobile H1 maximum size or ensure the final word
  wraps within the content column. Add a true-390-px assertion that
  `scrollWidth <= clientWidth`; the current mobile emulation checks a 408 CSS
  px layout and misses this fault.

### Major F3 — Legal and 404 routes do not move focus to their H1

- **Quote:** **“Your data stays on your machine”** and **“Use the tool with
  checked results”**.
- **Check:** Home and Demo focus their H1. On direct `/privacy/`, `/terms/`, or
  `/does-not-exist`, `document.activeElement` is `BODY`. Clicking the header
  Privacy link has the same result. Back returns to home and focuses its H1,
  but that does not repair the legal/404 routes.
- **Why a visitor is lost:** keyboard and screen-reader users do not receive a
  reliable route location after navigation.
- **Concrete fix:** load the shared focus/`aria-live` route code on Privacy,
  Terms, and 404; give each H1 `tabindex="-1"` and focus it on load. Test direct
  loads and header navigation for every route.

### Major F4 — Claim-like copy is not fully registered or tested

- **Quote:** **“Runs locally”**, **“Rows, columns, schema”**, and **“The browser
  preview compares the shipped CSV sample in this tab.”**
- **Why a visitor is misled:** all 13 declared claims pass, but those statements
  and the README statements in the inventory below have no exact claims entry.
  The registry is therefore not the required complete source of truth.
- **Concrete fix:** remove/soften each statement or add one named claim and an
  observable sandbox assertion for it. Add specific coverage for visible demo
  results, tolerance semantics, statuses, and gzip support.

### Minor F5 — The designed 404 page lacks standard route metadata

- **Quote:** **“Route not found — tdiff”**.
- **Check:** an unknown live route returns HTTP 404 and shows a product-specific
  recovery page. Its document has no canonical URL, Open Graph/Twitter tags,
  or Apple touch icon, unlike the main routes.
- **Concrete fix:** add the canonical, OG/Twitter title/description/image, and
  Apple icon; test the 404 document metadata.

### Minor F6 — Several copy units are technical or inconsistent

Each flagged item has a concrete rewrite:

| Quote | Why it fails first read | Rewrite |
| --- | --- | --- |
| “Key-aware file comparison” | “key-aware” is unexplained jargon. | “Compare files by a row ID.” |
| “Stable row identity” | Names a database concept rather than the action. | “A column that identifies each row.” |
| “Three steps” | Does not state its subject in a heading list. | “Compare files in three steps.” |
| “Local review” | Does not state its subject in a heading list. | “Review data files on your machine.” |
| “Try it with sample data” / “browser preview” / “browser sample” | Names one path three ways. | Use “sample demo” consistently. |

No audited prose unit exceeds 22 words. The primary CTA is a clear,
result-naming action; no prohibited marketing adjective was found.

## Demo and sandbox checks

The following passed in a fresh live 390 px context:

- The CTA reaches `/demo/` in one click; `/?demo=1` redirects there.
- The sample contains 1 added, 1 removed, 2 modified, 0 unchanged, and added
  `region` schema data.
- The persistent banner says **“Demo — sample data, nothing is saved”**.
- **Reset demo** restores the sample. Demo session storage has only
  `demo:sample-comparison`; local storage is empty. **Start for real** returns
  home and removes the demo key.
- Intercepted home → demo requests were same-origin `GET`s only. After service
  worker activation and one online reload, offline demo reload retained its
  banner and result with no console errors.
- The installed `tdiff demo` command was run from an unrelated temporary
  directory. It wrote its sample/report under a distinct `/tmp/tdiff-demo-*`
  directory and printed the expected 1/1/2 summary.

These pass results do not cure F1: the result must be visible without scroll.

## Claim-test ledger

Every command in `.factory/claims.json` was run from the clean clone. All
passed.

| Claim | Result |
| --- | --- |
| `demo-one-click` | PASS — 2 Playwright projects |
| `demo-isolation` | PASS — 2 Playwright projects |
| `browser-private` | PASS — 2 Playwright projects |
| `no-account` | PASS — 2 Playwright projects |
| `offline-demo` | PASS — 2 Playwright projects |
| `package-formats` | PASS |
| `html-report` | PASS |
| `git-wrapper` | PASS |
| `dvc-wrapper` | PASS |
| `mit-license` | PASS |
| `local-no-telemetry` | PASS |
| `cli-contract` | PASS |
| `packaged-demo` | PASS |

The browser test currently checks that results exist in the DOM, not that they
are in the initial viewport. That omission explains the passing claim command
and observed F1.

## Structure and visual checks

Confirmed: Home, Demo, Privacy, and Terms each have one H1, route-specific
titles, description, canonical, OG/Twitter tags, favicon, and Apple icon.
`/demo/`, `/privacy/`, and `/terms/` deep-link directly; the missing route
returns HTTP 404 and is designed in the product style. Header/footer include
Privacy and Terms. The crawl of site links and linked GitHub project/issues/
license URLs returned 200. No console errors appeared in the live home/demo
flow. The clean-clone axe suite passed. The original art-deco rail system,
enamel palette, and custom hero are distinctive and match `.factory/design.md`;
they do not read as a generic SaaS template. F3 and F5 are the exceptions.

## Copy audit

Word counts cover all visible prose, headings, labels, buttons, captions, and
footer text. Code blocks and sample terminal output are excluded as commands/
data rather than sentences.

### Landing page

| Words | Copy |
| ---: | --- |
| 3 | Skip to content |
| 1 | tdiff |
| 1 | Demo |
| 1 | Install |
| 1 | Privacy |
| 3 | Source on GitHub |
| 3 | Key-aware file comparison |
| 4 | Compare keyed data snapshots |
| 13 | For data engineers reviewing CSV, Parquet, or Arrow changes in Git or DVC. |
| 6 | Try it with sample data |
| 7 | See added, removed, and changed rows immediately. |
| 2 | Runs locally |
| 2 | No account |
| 5 | Free and MIT licensed |
| 8 | Two data snapshots meet at one primary key. |
| 3 | Three steps |
| 4 | How keyed comparison works |
| 2 | Choose snapshots |
| 4 | Old and new files |
| 3 | Name the key |
| 3 | Stable row identity |
| 2 | Compare changes |
| 3 | Rows, columns, schema |
| 2 | Local review |
| 6 | Use the comparison where your files live |
| 3 | Preview a sample |
| 11 | The browser preview compares the shipped CSV sample in this tab. |
| 4 | Run the package demo |
| 10 | tdiff demo runs the packaged sample in a temporary directory. |
| 3 | Write a report |
| 11 | The CLI can write a self-contained HTML report beside your work. |
| 3 | Install the CLI |
| 4 | Compare your first files |
| 12 | Use a primary key that identifies each row in both data snapshots. |
| 2 | Snapshot review |
| 3 | Git and DVC |
| 4 | Compare tracked data files |
| 1 | Git |
| 1 | DVC |
| 5 | Compare local keyed data files. |
| 1 | Privacy |
| 1 | Terms |
| 3 | Source on GitHub |
| 7 | MIT licensed · Built by Param Factory · 0.1.0 |

### README

| Words | Copy |
| ---: | --- |
| 1 | tabular-file-diff |
| 8 | Compare keyed CSV, Parquet, and Arrow data snapshots. |
| 14 | tdiff is for data engineers and analysts reviewing versioned data in Git or DVC. |
| 7 | It runs locally and has no telemetry. |
| 7 | Try the shipped browser sample at tabular-file-diff.sociobot.in/demo/. |
| 6 | The browser preview compares CSV only. |
| 12 | Run tdiff demo to run the installed package on its bundled sample. |
| 1 | Install |
| 12 | The demo prints its temporary directory and writes an HTML report there. |
| 7 | Its sample inputs also ship in examples/. |
| 2 | Compare files |
| 9 | Use one or more columns as the primary key. |
| 8 | tdiff reports added, removed, changed, and unchanged rows. |
| 8 | It also reports changed columns and schema changes. |
| 10 | Supported files are CSV, gzip CSV, Parquet, and Arrow IPC. |
| 6 | --tolerance applies only to numeric values. |
| 13 | A row is unchanged when the absolute difference is at most the tolerance. |
| 7 | Null versus non-null is always a change. |
| 8 | It defaults to 0, so comparisons are exact. |
| 7 | Write JSON or a self-contained HTML report: |
| 11 | The CLI returns 0 for no differences and 1 for differences. |
| 9 | It returns 2 for invalid input or operational errors. |
| 7 | Duplicate or null key values are rejected. |
| 2 | Python API |
| 5 | diff_files returns a typed DiffResult. |
| 9 | Its added, removed, and modified values are PyArrow tables. |
| 3 | Git and DVC |
| 8 | Use the Git wrapper for changed keyed files: |
| 10 | tdiff-git lets git diff print changes without an external-driver error. |
| 7 | Compare a DVC revision with the workspace: |
| 9 | tdiff-dvc materializes the requested revision in a temporary directory. |
| 3 | Develop and verify |
| 6 | Python 3.10 or later is required. |
| 9 | Build and test the static docs and sample preview: |
| 6 | Run every visitor claim from .factory/claims.json: |
| 11 | Deploy the static site by pushing main; the factory deploys dist/site. |
| 8 | The package is ready for python3 -m build. |
| 8 | Registry credentials are not kept in this repository. |
| 1 | License |
| 8 | tdiff is free software under the MIT License. |

### Unlisted claim inventory

These claim-like statements have no exact registry entry. Add a named claim and
observable test, or remove/rewrite them.

| Location | Statement | Needed proof |
| --- | --- | --- |
| Landing | Runs locally | Named local-execution claim covering the landing fact. |
| Landing | Rows, columns, schema | Test all three result categories, including schema. |
| Landing | The browser preview compares the shipped CSV sample in this tab. | Browser CSV-only/in-tab computation assertion. |
| README | The browser preview compares CSV only. | Browser format-boundary test. |
| README | Its sample inputs also ship in examples/. | Packaged/source artifact assertion. |
| README | tdiff reports added, removed, changed, and unchanged rows. | All-four-category assertion. |
| README | It also reports changed columns and schema changes. | Column and schema assertion. |
| README | Supported files are CSV, gzip CSV, Parquet, and Arrow IPC. | Explicit gzip CSV/Arrow IPC claim and test. |
| README | --tolerance applies only to numeric values. | Numeric/non-numeric tolerance test. |
| README | A row is unchanged when the absolute difference is at most the tolerance. | Boundary-value tolerance test. |
| README | Null versus non-null is always a change. | Null-comparison test. |
| README | It defaults to 0, so comparisons are exact. | Default-tolerance test. |
| README | The CLI returns 0 for no differences and 1 for differences. | Exit-status test. |
| README | It returns 2 for invalid input or operational errors. | Invalid-input/operational-error test. |
| README | Duplicate or null key values are rejected. | Duplicate/null-key rejection test. |
| README | diff_files returns a typed DiffResult. | Named API type assertion. |
| README | Python 3.10 or later is required. | Runtime policy test or remove. |
| README | The package is ready for python3 -m build. | Clean-build artifact assertion. |

## Verification record

From the clean clone: all 13 declared claim commands passed; `npm test` passed
(4 tests); `npm run build` produced `dist/site`; `npm run test:a11y` passed
(18 Playwright/axe tests); Python pytest passed (30 tests); Ruff and mypy
passed. No product code was changed for this review.
