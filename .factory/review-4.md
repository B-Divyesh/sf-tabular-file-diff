# Adversarial first-read review 4

**Product:** tabular-file-diff (tdiff)  
**Reviewed:** 2026-08-28  
**Live URL:** https://tabular-file-diff.sociobot.in/  
**Repository:** clean clone of f02d6d8e6ee57a227d1873abfda2f1521a8fe720  
**Verdict:** **PASS**

No finding of any severity, unlisted claim, or untested claim remains. This was a
full re-review, not a review of prior closure notes.

## Cold first screen

Fresh Chromium contexts, with no cookies or site storage, opened the live home
page at 390 × 844 and 1440 × 900 before scrolling.

- **What it does:** Compare two versions of tabular data by a row key and show row, column, and schema differences.
- **For whom:** Data engineers reviewing CSV, Parquet, or Arrow changes in Git or DVC.
- **What to click first:** **“Try it with sample data.”**

All three answers are present in the first screen's exact text:

> “Compare keyed data snapshots”

> “For data engineers reviewing CSV, Parquet, or Arrow changes in Git or DVC.”

> “Try it with sample data”

At 390 px the H1 is x=16–374, the action is x=16–374, and document width equals
viewport width (390 px). The desktop view presents the same job, audience,
action, outcome, and three facts before scrolling. Neither view emitted a
console error. The documented art-deco train-and-key visual system is distinct
and does not read as a generic SaaS template.

## Copy audit

Counts use whitespace-normalized visible copy. Commands, sample data, and code
blocks are executable input or output, not prose. No unit exceeds 22 words. No
banned marketing adjective appears. The first-screen “row ID” and later “A
column that identifies each row” explain the necessary domain term, primary
key. No copy finding is raised.

### Landing page

| Words | Copy |
| ---: | --- |
| 3 | Skip to content |
| 1 | tdiff |
| 1 | Demo |
| 1 | Install |
| 1 | Privacy |
| 3 | Source on GitHub |
| 6 | Compare files by a row ID |
| 4 | Compare keyed data snapshots |
| 13 | For data engineers reviewing CSV, Parquet, or Arrow changes in Git or DVC. |
| 6 | Try it with sample data |
| 7 | See added, removed, and changed rows immediately. |
| 2 | Runs locally |
| 2 | No account |
| 5 | Free and MIT licensed |
| 8 | Two data snapshots meet at one primary key. |
| 5 | Compare files in three steps |
| 4 | How keyed comparison works |
| 2 | Choose snapshots |
| 4 | Old and new files |
| 3 | Name the key |
| 6 | A column that identifies each row |
| 2 | Compare changes |
| 4 | Rows, columns, and schema |
| 6 | Review data files on your machine |
| 8 | Use the comparison where your files live |
| 4 | Try the package playground |
| 16 | The playground runs the shipped Python wheel on CSV, Parquet, and Arrow files in this tab. |
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
| 1 | Terms |
| 7 | MIT licensed · Built by Param Factory · 0.1.0 |

### README

| Words | Copy |
| ---: | --- |
| 1 | tabular-file-diff |
| 8 | Compare keyed CSV, Parquet, and Arrow data snapshots. |
| 14 | tdiff is for data engineers and analysts reviewing versioned data in Git or DVC. |
| 8 | Package and CLI comparisons run locally without telemetry. |
| 4 | Try the package playground. |
| 19 | It runs the shipped Python wheel on CSV, gzip CSV, Parquet, and Arrow IPC files in your browser tab. |
| 12 | Run tdiff demo to compare the bundled files with the installed package. |
| 1 | Install |
| 7 | tabular-file-diff supports Python 3.10 and later. |
| 13 | The package demo creates a temporary directory and writes a self-contained HTML report there. |
| 7 | The bundled inputs are also in examples. |
| 2 | Compare files |
| 9 | Use one or more columns as the primary key. |
| 10 | tdiff compares CSV, gzip CSV, Parquet, and Arrow IPC files. |
| 8 | It reports added, removed, changed, and unchanged rows. |
| 8 | It also reports changed columns and schema changes. |
| 6 | --tolerance applies only to numeric values. |
| 5 | The numeric boundary is inclusive. |
| 5 | Null versus non-null remains a change. |
| 9 | The default is 0, which makes numeric comparisons exact. |
| 8 | Write JSON or a self-contained HTML report. |
| 11 | The CLI returns 0 for no changes and 1 for differences. |
| 9 | It returns 2 for invalid input or operational errors. |
| 7 | Duplicate or null primary keys are rejected. |
| 2 | Python API |
| 5 | diff_files returns a typed DiffResult. |
| 10 | Its added, removed, and modified results are PyArrow tables. |
| 3 | Git and DVC |
| 8 | Use the Git wrapper for changed keyed files. |
| 10 | tdiff-git lets git diff print changes without an external-driver error. |
| 7 | Compare a DVC revision with the workspace. |
| 8 | tdiff-dvc materializes the revision in a temporary directory. |
| 9 | It removes the temporary files when the comparison finishes. |
| 3 | Develop and verify |
| 8 | Build and test the static docs and sample demo. |
| 8 | Run every visitor claim listed in .factory/claims.json. |
| 7 | Each entry contains its exact clean-state command. |
| 8 | The factory deploys dist/site when main is pushed. |
| 8 | Registry credentials are not kept in this repository. |
| 1 | License |
| 9 | tdiff is free software under the MIT License. |

Terms are consistent: data snapshots are inputs, primary key is row identity,
package playground is the browser path, package demo is the installed path, and
visible results use changed (the API keeps modified).

## Demo and sandbox

The home action reaches /demo/ in one click; /?demo=1 redirects there. A fresh
390 × 844 direct demo loaded the real package wheel and displayed its completed
result board at y=466–674, fully in the initial viewport. It showed 1 added, 1
removed, 2 changed, 0 unchanged, status and amount changes, region added, and
the A-101 status change.

The persistent banner exactly says **“Demo — sample data, nothing is saved”**.
It contains **Reset demo** and **Start for real**. Reset restores the completed
sample. A fresh context held only demo:sample-comparison in session storage,
with no local-storage keys or cookies. Start for real removed only demo: state
and returned home; the isolation test also verifies that a seeded non-demo key
is untouched.

The library playground is genuine: site/public/playground/worker.js loads the
built tabular_file_diff-0.1.0-py3-none-any.whl, imports diff_files, and runs it
with self-hosted DuckDB and PyArrow. The live engine ticket reported Wheel
0.1.0, DuckDB 1.1.2, and PyArrow 18.1.0. The playground accepts editable CSV
and selected CSV, gzip CSV, Parquet, Arrow IPC, and Feather files; it exposes
package JSON, a self-contained report, and a fresh-project snippet. The former
TypeScript look-alike comparator is absent.

Request capture across the demo found GET requests only to the product origin;
selected-file comparison created no new request. The full browser claim suite
independently verifies that behavior, cookies/local storage, and offline reload
after the first visit. From an unrelated temporary directory, tdiff demo created
a new /tmp/tdiff-demo-* directory, wrote its report there, and printed the
expected 1/1/2 result.

## Claims and verification

A clean clone was created at /tmp/tabular-file-diff-review4.yCnQ5r/repo; npm ci
and a new Python virtual environment were used. All 21 manifest IDs have
exactly one @claim: test. The 24-test live Playwright run passed in desktop and
390 px projects, covering all browser claims plus accessibility, metadata,
routing, history/focus, and 404. The 14 package claim commands were run
separately, exactly as listed in .factory/claims.json.

| Claim IDs | Result |
| --- | --- |
| demo-one-click, demo-isolation, browser-private, browser-csv, library-playground, no-account, offline-demo | PASS — live browser suite |
| package-formats, comparison-results, tolerance-semantics, cli-statuses, key-validation | PASS — individual commands |
| html-report, git-wrapper, dvc-wrapper, mit-license, local-no-telemetry | PASS — individual commands |
| python-api, packaged-demo, input-read-only, python-runtime | PASS — individual commands |

Also from that clone: npm test passed, npm run build produced dist/site (initial
JS 4.32 KB gzip), and the complete Python suite passed (41 tests). The live
browser suite found no console errors or Axe A/AA violations.

The landing page and README were reread against the registry. Their
visitor-relevant behavioral and privacy statements map to the listed claims:
local/no telemetry, no account, MIT licensing, browser wheel/formats, package
demo, report, results, tolerance, statuses, key validation, API, Git/DVC,
input safety, and Python support. No unlisted claim was found.

## Earlier finding regression check

Every earlier review, polish record, and handoff was read. The following were
confirmed on the live product and current code, rather than accepted by their
prior status.

| Earlier finding group | Current confirmation | Status |
| --- | --- | --- |
| Review 1 F1–F3 | Clear audience/action; direct demo; banner, reset, exit, and demo: isolation. | Fixed |
| Review 1 F4; Review 3 F-3-1 | Playground imports and executes the shipped package wheel with DuckDB/PyArrow; format fixtures pass. | Fixed |
| Review 1 F5; Review 2 F4 | 21 manifest claims have unique tags and passing clean-state tests. | Fixed |
| Review 1 F6–F8 | Real routes, designed 404, metadata, external labels, focus, and shared header/footer work. | Fixed |
| Review 1 C1–C18; Review 2 F6 | The complete audit above confirms plain, short, consistent replacements. | Fixed |
| Review 2 F1–F2 | Result is in the direct 390 px demo viewport; home width is 390 px. | Fixed |
| Review 2 F3 and F5 | Privacy, Terms, and 404 focus their H1 and contain full metadata. | Fixed |
| Earlier Git/CSV defects | Git maps differences to success; claim test uses real Git; malformed CSV exits 2. | Fixed |

## Structure, links, and leverage

Home, Demo, Privacy, Terms, and the designed unknown-route page each have one
H1, lang=en, main, description, canonical URL, OG/Twitter metadata, favicon,
and Apple touch icon. Their titles follow the route pattern: tdiff — Compare
keyed data files, Demo — tdiff, Privacy — tdiff, Terms — tdiff, and Route not
found — tdiff. Direct unknown navigation returns HTTP 404. The route suite
verifies direct H1 focus, navigation, Back, and the polite route announcer.

All discoverable user links on those pages were crawled: home, Demo, Privacy,
Terms, assets, GitHub repository, issue tracker, and license returned 200. The
unknown route correctly returns 404 rather than home. Header and footer are
consistent and include Privacy and Terms.

The brief implies deterministic local comparison, report output, Python API,
Git, and DVC; each is present. It does not imply that an AI step benefits the
core deterministic task. No decorative AI, provider key, or external AI request
exists, so no missed-leverage finding is raised.

## What would make this perfect

Nothing additional is required for this review's first-read, copy, demo,
privacy, claims, history, routing, accessibility, and product-scope checks.
Preserve the self-hosted wheel/runtime and direct-demo regression tests when the
playground changes.

