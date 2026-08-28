# Adversarial first-read review 1

**Product:** tabular-file-diff  
**Reviewed:** 2026-08-28  
**Verdict:** **FAIL**

This review used a fresh Chromium context against
`https://tabular-file-diff.sociobot.in/` at 390 × 844 and 1440 × 900, then
reviewed the repository at `708b671`. The product has more than three minor
findings and multiple blocking findings.

## Cold first screen

Before scrolling, I understood this as a tool that reviews changes in tabular
data files. I could not identify the intended person from the first screen:
the only explanation is "A key-aware diff for CSV, Parquet, and Arrow. Exact
row and schema changes, streamed through DuckDB, delivered to your terminal or
one portable report." It names technologies and outputs, but not the data
engineer or analyst reviewing snapshots in Git/DVC.

I also could not identify one correct first click. The visually primary action
is **"Install tdiff"** and its peer is **"Compare CSV here"**; neither says
what result it produces. The mandated sample action is absent. On the 390 px
first viewport the headline, technical two-sentence lede, both competing
actions, and install command are visible, but there is no audience statement,
three plain facts, or sample-data action.

### Blocking F1 — First screen does not state the audience or one clear first action

- **Quote:** "Review data changes at line speed." / "Install tdiff" /
  "Compare CSV here".
- **Why this loses a new visitor:** “line speed” is an unmeasurable marketing
  phrase, not the job. A visitor does not know whether the page is for a
  spreadsheet user, an analyst, or a CLI data-review workflow, and has to
  choose between installing and an unexplained CSV path.
- **Concrete fix:** use the headline **"Compare keyed data snapshots"** and
  the one-sentence lede **"For data engineers reviewing CSV, Parquet, or Arrow
  changes in Git or DVC."** Make **"Try it with sample data"** the sole primary
  action and place **"See added, removed, and changed rows immediately"** next
  to it. Put three short facts beneath it: “Runs locally”, “No account”,
  “Free and MIT licensed”.

## Demo and sandbox

### Blocking F2 — There is no one-click, direct, isolated sample demo

- **Evidence:** There is no control named **"Try it with sample data"**. The
  available **"Load sample"** control produces only: "Sample ready. Primary
  key ‘id’ selected; choose Compare rows." The result panel remains hidden.
  A second click on **"Compare rows"** is required before the realistic result
  (1 added, 1 removed, 2 modified, 0 unchanged) appears. `/demo` and
  `/?demo=1` both return the ordinary landing page; neither enters demo mode.
- **Why this misleads:** The required first click must already show the product
  in use. Here it requires finding the lower page, then two actions. A visitor
  cannot link directly to a demonstrable demo.
- **Concrete fix:** make `/demo` and `?demo=1` initialize and display the
  sample comparison result in one navigation. Make the hero button link there.
  Include realistic old/new sample files and show the counts, column changes,
  schema change, and changed rows on the first demo frame.

### Blocking F3 — Demo identity and separation controls are absent

- **Evidence:** No visible text matches **"Demo — sample data, nothing is
  saved"**; no **"Reset demo"** or **"Start for real"** action exists. The
  implementation has no `demo:` storage namespace and no demo URL state.
- **Why this misleads:** There is no persistent indication that a sample is
  being used and no visitor-verifiable reset or exit boundary. The current
  in-memory behavior happens to leave `localStorage` and `sessionStorage`
  empty, but that is not an explicit sandbox contract.
- **Concrete fix:** display the required persistent banner whenever the demo
  is active. Keep all demo state under `demo:` (or in memory clearly tied to
  `/demo`), make Reset restore the shipped sample, and make Start for real
  discard demo state before opening empty file inputs. Document those rules in
  `.factory/demo.md` and add isolated-storage tests.

### Blocking F4 — The supposed library playground is a different, CSV-only implementation

- **Quote:** "The browser demo is for small CSVs; use the CLI for Parquet,
  Arrow, or large files."
- **Why this misleads:** The artifact is a PyPI library whose job includes
  Parquet/Arrow, key-aware diff behavior, reports, Git, and DVC. The page
  presents a hand-written browser CSV comparison instead of a playground using
  the published package, so a visitor cannot try the actual library job.
- **Concrete fix:** provide an in-page playground that invokes the published
  package or an honest supported WebAssembly/browser build, with editable
  inputs and live output. If only the CSV preview can be shipped in browser,
  label it as a limited preview and add a `tdiff demo` command that runs the
  real packaged binary on shipped samples in a temporary directory.

## Claims and proof

### Blocking F5 — Claims registry and claim tests are missing

- **Evidence:** `.factory/claims.json` does not exist. `rg '@claim:'` returns
  no matches. Therefore there are no listed claim commands to run from the
  clean clone and no sandbox evidence for the claims below.
- **Why this misleads:** The landing page and README make behavioral, privacy,
  compatibility, and offline promises a visitor could rely on, but there is no
  machine-verifiable source of truth. Passing unit and accessibility tests do
  not prove those promises.
- **Concrete fix:** add `.factory/claims.json`; give each listed claim one
  `@claim:<id>` test from the direct demo entry point or a clean temporary CLI
  directory; remove any promise that cannot be tested. At minimum test
  same-origin-only requests throughout the demo, offline reload after first
  visit, sample reset/isolation, CSV output, supported format behavior, Git,
  and DVC wrappers.

### Unlisted claim inventory (each is a finding under F5)

The following claim-like statements appear without a claims entry:

| Location | Unlisted statement |
| --- | --- |
| Landing | "A key-aware diff for CSV, Parquet, and Arrow." |
| Landing | "Exact row and schema changes, streamed through DuckDB, delivered to your terminal or one portable report." |
| Landing | "Parquet and CSV are scanned by DuckDB." |
| Landing | "Cap displayed samples without weakening the aggregate counts." |
| Landing | "No account, upload, telemetry, or remote execution." |
| Landing | "HTML reports remain complete and self-contained." |
| Landing | "Use the typed Python API, terminal CLI, or wire the native drivers into Git and DVC review." |
| Landing | "Your files are parsed in this tab and are never uploaded." |
| Landing | "The browser demo is for small CSVs; use the CLI for Parquet, Arrow, or large files." |
| Landing | "Local CSV comparison still works; package links will reconnect later." |
| README | "Key-aware, local-first diffs for CSV, Parquet, and Arrow files." |
| README | "tdiff uses DuckDB to join snapshots without loading Parquet or CSV files into pandas, then reports added, removed, and modified rows, per-column changes, and schema drift." |
| README | "No data leaves your machine and there is no telemetry." |
| README | All tolerance semantics, status-code, supported-format, API-type, Git-driver, DVC temporary-copy, local-file, performance, and scope statements listed in the copy audit below. |

The browser was exercised with request capture during the sample path. It made
only same-origin requests for the document, CSS, JS, and hero image. That is a
useful observation, not a privacy proof without an intercepted assertion in a
claim test. Offline reload after service-worker activation did render the
landing page from cache, but that observation likewise has no registered test.

## Structure, routes, and metadata

### Blocking F6 — `/demo` is not a real route and unknown URLs masquerade as valid pages

- **Evidence:** Direct navigation to `/demo`, `/?demo=1`, and `/missing-route`
  all returned HTTP 200 with title `tabular-file-diff — Review data changes at
  line speed` and the landing H1. No designed 404 exists.
- **Why this loses visitors:** A linked demo cannot open the promised state,
  and a mistyped deep link silently shows unrelated content rather than a clear
  recovery page.
- **Concrete fix:** implement a real `/demo` route and a designed 404 route
  returning a 404 response where hosting permits. Preserve browser history,
  move focus to the route H1, and announce route changes.

### Major F7 — Required route metadata and consistent skeleton are incomplete

- **Evidence:** The home title is `tabular-file-diff — Review data changes at
  line speed`, which uses the slug and does not say what it does in plain
  words. Privacy/Terms use `Privacy · tabular-file-diff` and
  `Terms · tabular-file-diff`, not the required title pattern. Privacy and
  Terms have no canonical or Open Graph/Twitter metadata. The homepage has no
  OG/Twitter tags; `/og-image.png` and `/apple-touch-icon.png` return the HTML
  landing page (`content-type: text/html`), not image assets. The legal-page
  header omits Demo/Privacy navigation and the footer omits Privacy and Terms.
- **Why this matters:** Shared previews, saved links, route identity, and the
  stated site skeleton are broken or inconsistent.
- **Concrete fix:** set route-specific plain-language titles such as
  `tdiff — Compare keyed data files`, add canonical/OG/Twitter/favicons and
  real image files, and reuse the full header/footer on every route.

### Minor F8 — Link language and navigation do not expose destinations clearly

- **Evidence:** Header actions **"Try CSV"** and **"Install"** are hash links;
  **"GitHub"** and footer **"Source"** are external links with no external
  indication. The app uses hash jumps rather than real product URLs and has no
  focus/announcement code on navigation.
- **Concrete fix:** use `/demo` and a real install/docs URL; label external
  links as “Source on GitHub (opens GitHub)”; add route-focus and `aria-live`
  handling.

### Confirmed, not a finding

The live page has one H1, `lang="en"`, main/header/footer landmarks, visible
skip link, a responsive 390 px layout without horizontal overflow, valid
internal landing/privacy/terms links, and no console errors during the tested
flows. The art-deco rail treatment is distinct and agrees with
`.factory/design.md`; it does not read as a generic SaaS template. The local
axe suite passed for home, Privacy, and Terms. These checks do not cure the
route/demo failures above.

## Copy audit

Word counts use whitespace-normalized visible text; commands and code examples
are excluded because they are not sentences. Labels, headings, and status text
are included so their first-read meaning can be checked.

### Landing page — every visible copy unit

| Words | Copy |
| ---: | --- |
| 3 | Skip to content |
| 1 | tdiff |
| 2 | Try CSV |
| 1 | Install |
| 1 | GitHub |
| 2 | You’re offline. |
| 10 | Local CSV comparison still works; package links will reconnect later. |
| 3 | File-native data review |
| 6 | Review data changes at line speed. |
| 8 | A key-aware diff for CSV, Parquet, and Arrow. |
| 16 | Exact row and schema changes, streamed through DuckDB, delivered to your terminal or one portable report. |
| 2 | Install tdiff |
| 3 | Compare CSV here |
| 3 | pip install tabular-file-diff |
| 1 | Copy |
| 2 | Two snapshots. |
| 3 | One key junction. |
| 3 | Every change routed. |
| 4 | One full outer join |
| 6 | A departure board for your data. |
| 2 | Old snapshot |
| 3 | CSV / Parquet / Arrow |
| 2 | Primary key |
| 3 | Unique and explicit |
| 2 | New snapshot |
| 3 | Scanned by DuckDB |
| 2 | Change set |
| 3 | Rows, columns, schema |
| 4 | Built for real snapshots |
| 3 | No conversion detours. |
| 1 | Scale-oriented |
| 7 | Parquet and CSV are scanned by DuckDB. |
| 8 | Cap displayed samples without weakening the aggregate counts. |
| 3 | Leaves your machine |
| 7 | No account, upload, telemetry, or remote execution. |
| 6 | HTML reports remain complete and self-contained. |
| 3 | Fits your workflow |
| 17 | Use the typed Python API, terminal CLI, or wire the native drivers into Git and DVC review. |
| 2 | Local station |
| 4 | Try a CSV diff. |
| 11 | Your files are parsed in this tab and are never uploaded. |
| 16 | The browser demo is for small CSVs; use the CLI for Parquet, Arrow, or large files. |
| 2 | Old CSV |
| 3 | No file selected |
| 1 | KEY |
| 2 | New CSV |
| 2 | Primary key |
| 5 | Select two CSV files first |
| 2 | Load sample |
| 2 | Compare rows |
| 3 | No comparison yet. |
| 8 | Load the sample or choose two CSV files. |
| 1 | Added |
| 1 | Removed |
| 1 | Modified |
| 1 | Unchanged |
| 3 | Changes by column |
| 1 | Schema |
| 2 | Changed-row sample |
| 2 | Now boarding |
| 7 | From install to signal in one command. |
| 3 | Connect your line |
| 6 | Git and DVC are first-class stops. |
| 1 | Git |
| 1 | DVC |
| 5 | Local data review, on schedule. |
| 1 | Privacy |
| 1 | Terms |
| 1 | Source |
| 5 | MIT licensed · Param Factory · 2026 |

### README — every prose sentence/headline

| Words | Copy |
| ---: | --- |
| 1 | tabular-file-diff |
| 9 | Key-aware, local-first diffs for CSV, Parquet, and Arrow files. |
| 26 | tdiff uses DuckDB to join snapshots without loading Parquet or CSV files into pandas, then reports added, removed, and modified rows, per-column changes, and schema drift. |
| 14 | It is for data engineers and analysts reviewing versioned datasets in Git or DVC. |
| 10 | No data leaves your machine and there is no telemetry. |
| 11 | The documentation and browser-only CSV demo live at tabular-file-diff.sociobot.in. |
| 1 | Usage |
| 10 | Use one or more columns as the stable row key: |
| 29 | `--tolerance` is an absolute, inclusive tolerance applied only when both versions of a column are numeric: a row is unchanged when `abs(old - new) <= tolerance`, including the exact boundary. |
| 7 | Null versus non-null is always a change. |
| 9 | It defaults to `0`, so floating-point comparison is exact. |
| 33 | The comparison absorbs only a few IEEE-754 rounding units at a nonzero boundary, preventing decimal CSV values such as `1.0` and `1.01` from being falsely reported as outside `--tolerance 0.01`. |
| 9 | Write a standalone, offline HTML report or machine-readable JSON: |
| 20 | The CLI returns `0` when snapshots are identical, `1` when differences exist, and `2` for invalid input or operational errors. |
| 12 | Duplicate or null keys are rejected because they make row identity ambiguous. |
| 17 | `--sample` controls rows shown in terminal, JSON, and HTML output; aggregate counts still cover the full files. |
| 2 | Python API |
| 6 | `diff_files` returns a typed `DiffResult`. |
| 9 | Its `added`, `removed`, and `modified` values are PyArrow tables. |
| 19 | The API materializes every difference by default; pass `max_rows` to cap those tables while retaining exact aggregate counts. |
| 9 | Composite keys and explicit tolerance work the same way: |
| 12 | Supported inputs are `.csv`, `.csv.gz`, `.parquet`, `.pq`, `.arrow`, `.ipc`, and `.feather`. |
| 16 | Arrow IPC inputs are registered as Arrow tables; Parquet and CSV are scanned directly by DuckDB. |
| 13 | CSV input with an unterminated quoted field is rejected rather than silently compared. |
| 1 | Git |
| 15 | Install the external diff driver once in a repository, choosing the key for that dataset: |
| 8 | `tdiff-git` accepts Git's seven-argument external diff protocol. |
| 26 | It translates `tdiff`'s normal “differences found” status into a successful external-driver status, so `git diff` prints the tabular summary and exits normally for changed files. |
| 4 | Operational errors remain non-zero. |
| 19 | For repositories with different keys per dataset, define named drivers such as `tdiff_accounts` and assign them in `.gitattributes`. |
| 1 | DVC |
| 10 | Compare any DVC-tracked file across revisions without checking it out: |
| 24 | The wrapper calls the installed `dvc` executable to materialize revisions in a temporary directory, invokes the same comparison engine, then removes the temporary copies. |
| 7 | Use `workspace` for the current local file. |
| 3 | Install and develop |
| 5 | Python 3.10+ is required. |
| 7 | Build and test the static documentation site: |
| 12 | For the browser accessibility suite, install its Chromium build once and run: |
| 19 | The package is ready to publish with `python -m build`; registry credentials are intentionally not part of this repository. |
| 2 | Performance notes |
| 11 | DuckDB scans Parquet/CSV and performs a keyed full outer join. |
| 12 | Runtime and working memory depend on key cardinality and available DuckDB memory. |
| 15 | Set `--threads` and `--memory-limit` (for example `8GB`) when the defaults do not fit your environment. |
| 20 | The 50-million-row target should be benchmarked on the actual schema and hardware; this repository does not claim a universal timing. |
| 1 | Scope |
| 16 | Version 0.1 deliberately does not connect to databases, guess unkeyed row alignment, or apply patches. |
| 6 | It compares local, keyed tabular files. |
| 1 | License |
| 5 | MIT © 2026 Sociobot (Param Factory). |

### Copy findings and rewrites

Each item below is a finding; all use plain words and retain the intended
meaning.

| ID | Flagged copy | Why | Proposed rewrite |
| --- | --- | --- | --- |
| C1 | "Review data changes at line speed." | Marketing adjective/metaphor; does not name data files or a key. | "Compare keyed data snapshots" |
| C2 | "A departure board for your data." | Heading makes no sense out of context. | "How keyed comparison works" |
| C3 | "No conversion detours." | Metaphor; does not explain the benefit. | "Compare files without converting them" |
| C4 | "Scale-oriented" | Jargon and a non-claim-like adjective. | "Shows full change counts" |
| C5 | "Leaves your machine" | Fragment with an ambiguous subject. | "Your files stay on this machine" |
| C6 | "Fits your workflow" | Generic marketing phrase. | "Use it from Python, Git, or DVC" |
| C7 | "Local station", "Now boarding", "From install to signal in one command.", and "Connect your line" | Transit metaphors obscure section purpose when headings are read out of context. | "Try the CSV preview", "Install the CLI", and "Use it with Git or DVC" |
| C8 | "Git and DVC are first-class stops." | Jargon/metaphor; does not say what works. | "Compare tracked files from Git or DVC" |
| C9 | "Local data review, on schedule." | Marketing/metaphor, unclear footer one-liner. | "Compare local keyed data files" |
| C10 | Button "Install tdiff" | It names an action but not a visitor result; it competes with the preview. | "Try sample comparison" (primary), "Install the CLI" (secondary) |
| C11 | Button "Compare CSV here" | Vague result and only describes a constrained input. | "Show sample CSV changes" |
| C12 | Button "Copy" | Not a result-naming verb. | "Copy install command" |
| C13 | Button "Load sample" | Does not tell the visitor it will show a diff; requires another action. | "Show sample comparison" |
| C14 | README sentence beginning "tdiff uses DuckDB..." (26 words) | Over 22 words; combines implementation, exclusion, and four output types. | "tdiff joins two snapshots with DuckDB. It reports added, removed, changed, and schema-drift rows." |
| C15 | README `--tolerance` sentence (29 words) | Over 22 words and mixes definition, condition, and boundary rule. | "`--tolerance` applies only to numeric values. A row is unchanged when the absolute difference is at most the tolerance." |
| C16 | README IEEE-754 sentence (33 words) | Over 22 words and too implementation-specific for first read. | "At a tolerance boundary, tdiff allows normal floating-point rounding. `1.0` and `1.01` match with `--tolerance 0.01`." |
| C17 | README Git external-driver sentence (26 words) | Over 22 words and needs prior knowledge of exit codes. | "`tdiff-git` lets `git diff` show changed tables. Differences do not make Git report an error." |
| C18 | README DVC wrapper sentence (24 words) | Over 22 words and hides the user outcome. | "The DVC wrapper compares two revisions in a temporary directory. It removes those temporary files when it finishes." |

Terminology is mostly consistent on “key”/“primary key,” but the page alternates
between “snapshot,” “file,” “CSV,” “data,” “comparison,” and the metaphorical
“line/station/route.” Use **data snapshot** for the compared inputs, **primary
key** for row identity, and **comparison** for the output.

## Verification record

| Check | Result | Evidence |
| --- | --- | --- |
| Fresh live 390/desktop first read | Fail | No audience statement, no `Try it with sample data`, competing CTA labels. |
| Demo interaction | Fail | Sample click leaves results hidden; second click needed; no banner/reset/start-for-real. |
| Direct demo and 404 routes | Fail | `/demo`, `?demo=1`, and missing route all render home with HTTP 200. |
| Claim registry/tests | Fail | `.factory/claims.json` and `@claim:` tests absent. |
| Network/offline observation | Partial only | Sample flow requested same-origin assets only; after SW activation, offline reload rendered home. No registered assertion. |
| `npm test` | Pass | 1 Vitest file, 4 tests. |
| `npm run build` | Pass | `dist/site/` produced; JS gzip 3.13 kB. |
| `npm run test:a11y` | Pass | 6 Playwright/Axe tests, desktop and mobile. |
| Clean-clone package tests | Pass | `python3 -m venv .venv && .venv/bin/pip install -e '.[dev]' && .venv/bin/pytest`: 21 passed. |
| Documented `python -m pytest` in current sandbox | Fail to invoke | `python` is not installed; `python3 -m pytest` initially lacked pytest. Clean-clone documented venv procedure succeeds. |
| Crawl | Partial | Home, Privacy, Terms, source repository, and issue tracker responded; fake OG/apple asset URLs return HTML. |

## Final verdict

**FAIL.** Do not pass this product until a direct, one-click, isolated sample
demo shows the real product output; the first screen plainly names the user and
first action; claims have isolated tests; and `/demo`/404/metadata routes are
real. The product’s local tests and distinct visual identity are positive, but
they do not make the site clear, tryable, or provably honest in 30 seconds.
