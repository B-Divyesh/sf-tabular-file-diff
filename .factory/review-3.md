# Adversarial first-read review 3

**Product:** tabular-file-diff  
**Reviewed:** 2026-08-28  
**Live URL:** <https://tabular-file-diff.sociobot.in/>  
**Repository reviewed:** clean clone of `971ee26cc43f5bd79d6c6a67332bf888b51296a5`  
**Verdict:** **FAIL**

## Cold read

Fresh Chromium contexts opened the live home page without stored state at 390 x
844 and 1440 x 900, before scrolling.

- **What it does:** compares two versions of tabular data using a row key and
  shows changed rows, columns, and schema.
- **For whom:** data engineers reviewing CSV, Parquet, or Arrow changes in Git
  or DVC.
- **What to click first:** **“Try it with sample data.”**

Those answers are visible in the first viewport from **“Compare keyed data
snapshots”**, **“For data engineers reviewing CSV, Parquet, or Arrow changes
in Git or DVC.”**, and **“Try it with sample data.”** The 390 px document width
was 390 px, with no horizontal overflow or console error. The first-read test
does not produce a finding.

## Findings

### BLOCKING F-3-1 — The advertised browser demo is not a playground for the shipped library

This is the unresolved substance of review-1 **F4**, despite the prior closure
record.

- **Exact quote/location:** `/demo/` says **“Compare sample CSV changes”** and
  **“Use `tdiff demo` to compare the same files with the package.”** Its editor
  accepts only `accept=".csv,text/csv"`.
- **Evidence:** `site/src/main.ts` imports `parseCsv` and `diffCsv` from
  `site/src/diff.ts`. That TypeScript file implements a separate string/Map CSV
  comparator. It neither loads nor invokes `tabular_file_diff`, DuckDB, or
  PyArrow. The actual package engine in `src/tabular_file_diff/core.py` imports
  DuckDB and PyArrow and supports CSV, gzip CSV, Parquet, and Arrow IPC.
- **Why this is blocking:** this product is a PyPI library. The direct demo
  proves only a look-alike, CSV-only subset. A visitor cannot try the package's
  supported formats, tolerance behavior, Arrow-table API, HTML-report output,
  Git integration, or DVC integration in the required library playground. A
  separate terminal command after installation is useful, but it is not the
  one-click in-page playground required for this artifact class.
- **Concrete fix:** replace the hand-written browser comparator with a
  sandboxed playground that executes the published package (for example, a
  self-hosted Python/WASM worker running the built wheel) and accepts the
  package's supported fixtures. Show editable inputs, live package output, and
  a copy-paste fresh-project snippet. Keep the existing `tdiff demo` command
  as the installed-package path. Add a `@claim:library-playground` test that
  supplies CSV, Parquet, and Arrow fixtures to the playground and proves the
  same observable results as `diff_files`; add a test that the playground
  imports the packaged artifact rather than `site/src/diff.ts`.

## Demo and sandbox checks

The direct-demo mechanics themselves pass. On fresh `/demo/` at 390 x 844, the
banner **“Demo — sample data, nothing is saved”** was visible at 72–162 px and
the completed result was visible at 420–628 px. It displayed 1 added, 1
removed, 2 changed, 0 unchanged, two changed columns, `region` added, and the
`A-101` changed-row example. Reset restored the sample. During demo use, the
only session key was `demo:sample-comparison`; local storage and cookies were
empty. **Start for real** returned to `/` and removed that key. Request capture
observed only `https://tabular-file-diff.sociobot.in`.

The installed package demo also ran from an unrelated temporary directory. It
created a new `/tmp/tdiff-demo-*` directory, printed its location, and reported
the shipped sample's 1/1/2 row result plus the `region` schema change. This
confirms the CLI demo but does not cure F-3-1's in-page-library requirement.

## Claims audit

I created a fresh clone at `/tmp/tdiff-review3.rOgI9q/repo`, made a new Python
environment, installed the project and test dependencies, and ran every command
listed in `.factory/claims.json`. All 20 passed. The 14 package claims also
passed together as `14 passed` in `tests/test_claims.py`; the six browser claims
passed in both desktop and 390 px Playwright projects.

| Claim IDs checked | Result |
| --- | --- |
| `demo-one-click`, `demo-isolation`, `browser-private`, `browser-csv`, `no-account`, `offline-demo` | PASS |
| `package-formats`, `comparison-results`, `tolerance-semantics`, `cli-statuses`, `key-validation` | PASS |
| `html-report`, `git-wrapper`, `dvc-wrapper`, `mit-license`, `local-no-telemetry` | PASS |
| `python-api`, `packaged-demo`, `input-read-only`, `python-runtime` | PASS |

The tag audit found exactly one `@claim:<id>` occurrence for each of those 20
manifest IDs. The browser privacy test intercepts requests, the offline test
reloads the saved demo offline, and the package demo test runs the command in a
temporary directory.

I reread the live landing page and README against the registry. The behavioral
copy maps to registered claims: local/no telemetry (`local-no-telemetry`), no
account (`no-account`), MIT/free (`mit-license`), browser CSV comparison
(`browser-csv`), package demo (`packaged-demo`), self-contained report
(`html-report`), formats (`package-formats`), results
(`comparison-results`), tolerance (`tolerance-semantics`), statuses
(`cli-statuses`), key validation (`key-validation`), Git/DVC wrappers
(`git-wrapper`, `dvc-wrapper`), API (`python-api`), input safety
(`input-read-only`), and Python version (`python-runtime`). No additional
unlisted visitor claim was found. F-3-1 is a product-scope failure, not a
failing registered claim.

## Copy audit

Word counts treat commands, filenames, and sample output as executable input or
output rather than prose. The tables list every visible landing-page and README
copy unit. No prose unit exceeds 22 words; no banned marketing adjective is
present. Domain terms such as CSV, Parquet, Arrow, DVC, schema, and primary key
are appropriate for the named data-engineer audience and are grounded by the
first-screen “row ID” explanation. Navigation labels are links, not action
buttons; the actual controls name their outcome or are the mandated sample
action. No copy finding is added.

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
| 4 | Try the sample demo |
| 10 | The sample demo compares two shipped CSV files in this tab. |
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
| 4 | Try the sample demo. |
| 10 | It compares shipped or selected CSV files in your browser tab. |
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

## Earlier-review and structure regression check

| Earlier finding | Live and code check | Status |
| --- | --- | --- |
| Review 1 F1–F3 | First screen is clear; `/demo/` is direct; banner, reset, and isolated `demo:` state work. | Fixed |
| Review 1 F4 | Browser uses `site/src/diff.ts`, not the package. | **Unfixed — F-3-1** |
| Review 1 F5 | 20 registered claims have unique tags and clean-clone passing commands. | Fixed |
| Review 1 F6–F8 | Real demo/privacy/terms routes, a 404 response, route focus/announcement, and complete shared header/footer exist. | Fixed |
| Review 1 C1–C18 | Current copy audit above confirms the supplied short, concrete replacements. | Fixed |
| Review 2 F1 | Direct demo result board is fully in the 390 px viewport. | Fixed |
| Review 2 F2 | 390 px scroll width equals client width. | Fixed |
| Review 2 F3–F5 | Legal and 404 H1s receive focus; the 404 has metadata and returns HTTP 404. | Fixed |
| Review 2 F6 | No flagged unclear, overlong, or inconsistent copy remains. | Fixed |

All five routes (`/`, `/demo/`, `/privacy/`, `/terms/`, and an unknown path)
have one H1, a description, canonical URL, OG/Twitter image, favicon, and a
route-specific title. Unknown paths return the designed 404 with an H1 and a
way home. Direct-load focus landed on each route H1. The internal routes,
assets, repository, issue tracker, and license link returned HTTP 200; the
unknown path returned HTTP 404 as intended. Header and footer are consistent,
including Privacy and Terms. The art-deco transit-poster treatment is distinct
from a generic SaaS template and matches `.factory/design.md`.

The brief does not imply an AI action: the job is deterministic file
comparison. No decorative AI feature, provider key, or undeclared external AI
request was found. No additional AI, sync, or import/export leverage finding is
added beyond the missing real library playground in F-3-1.

## What would make this perfect

Provide a one-click, local sandboxed playground that runs the actual published
library and makes its real format/API/report behavior inspectable. Then add
observable package-parity claims and rerun this review from a clean clone. With
that change, the first-read, copy, privacy, route, accessibility, and claim
checks recorded here have no remaining finding.
