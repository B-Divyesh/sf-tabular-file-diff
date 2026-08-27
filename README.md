# tabular-file-diff

Key-aware, local-first diffs for CSV, Parquet, and Arrow files. `tdiff` uses
DuckDB to join snapshots without loading Parquet or CSV files into pandas, then
reports added, removed, and modified rows, per-column changes, and schema drift.

It is for data engineers and analysts reviewing versioned datasets in Git or
DVC. No data leaves your machine and there is no telemetry.

```console
$ pip install tabular-file-diff
$ tdiff snapshots/old.parquet snapshots/new.parquet --key account_id

TABULAR FILE DIFF
old.parquet → new.parquet

  + added          12
  - removed         3
  ~ modified       41
  Σ unchanged  2,184,009
```

The documentation and browser-only CSV demo live at
[tabular-file-diff.sociobot.in](https://tabular-file-diff.sociobot.in).

## Usage

Use one or more columns as the stable row key:

```bash
tdiff old.parquet new.parquet --key id
tdiff old.csv new.csv --key tenant_id,event_id
tdiff old.arrow new.arrow --key id --tolerance 0.001
```

`--tolerance` is an **absolute, inclusive** tolerance applied only when both
versions of a column are numeric: a row is unchanged when
`abs(old - new) <= tolerance`, including the exact boundary. Null versus
non-null is always a change. It defaults to `0`, so floating-point comparison
is exact. The comparison absorbs only a few IEEE-754 rounding units at a
nonzero boundary, preventing decimal CSV values such as `1.0` and `1.01` from
being falsely reported as outside `--tolerance 0.01`.

Write a standalone, offline HTML report or machine-readable JSON:

```bash
tdiff old.parquet new.parquet --key id --html report.html
tdiff old.parquet new.parquet --key id --json > result.json
```

The CLI returns `0` when snapshots are identical, `1` when differences exist,
and `2` for invalid input or operational errors. Duplicate or null keys are
rejected because they make row identity ambiguous. `--sample` controls rows
shown in terminal, JSON, and HTML output; aggregate counts still cover the full
files.

### Python API

`diff_files` returns a typed `DiffResult`. Its `added`, `removed`, and
`modified` values are PyArrow tables. The API materializes every difference by
default; pass `max_rows` to cap those tables while retaining exact aggregate
counts.

```python
from tabular_file_diff import diff_files

result = diff_files("old.parquet", "new.parquet", key="id")

assert result.added_count == result.added.num_rows
print(result.column_changes)
print(result.modified.to_pylist())
```

Composite keys and explicit tolerance work the same way:

```python
result = diff_files(
    "old.csv",
    "new.csv",
    key=["tenant_id", "event_id"],
    tolerance=1e-6,
    max_rows=100,
)
```

Supported inputs are `.csv`, `.csv.gz`, `.parquet`, `.pq`, `.arrow`, `.ipc`,
and `.feather`. Arrow IPC inputs are registered as Arrow tables; Parquet and CSV
are scanned directly by DuckDB. CSV input with an unterminated quoted field is
rejected rather than silently compared.

### Git

Install the external diff driver once in a repository, choosing the key for
that dataset:

```bash
git config diff.tdiff.command 'tdiff-git --key id'
printf '*.parquet diff=tdiff\n*.csv diff=tdiff\n' >> .gitattributes
git diff -- data/snapshot.parquet
```

`tdiff-git` accepts Git's seven-argument external diff protocol. It translates
`tdiff`'s normal “differences found” status into a successful external-driver
status, so `git diff` prints the tabular summary and exits normally for changed
files. Operational errors remain non-zero. For repositories with different
keys per dataset, define named drivers such as `tdiff_accounts` and assign them
in `.gitattributes`.

### DVC

Compare any DVC-tracked file across revisions without checking it out:

```bash
tdiff-dvc data/snapshot.parquet --from v1.4.0 --to HEAD --key id
tdiff-dvc data/snapshot.parquet --from HEAD~1 --to workspace --key id --html report.html
```

The wrapper calls the installed `dvc` executable to materialize revisions in a
temporary directory, invokes the same comparison engine, then removes the
temporary copies. Use `workspace` for the current local file.

## Install and develop

Python 3.10+ is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
python -m build
```

Build and test the static documentation site:

```bash
npm ci
npm test
npm run build:site       # writes dist/site/index.html
npm run dev
```

For the browser accessibility suite, install its Chromium build once and run:

```bash
npx playwright install chromium
npm run test:a11y
```

The package is ready to publish with `python -m build`; registry credentials
are intentionally not part of this repository.

## Performance notes

DuckDB scans Parquet/CSV and performs a keyed full outer join. Runtime and
working memory depend on key cardinality and available DuckDB memory. Set
`--threads` and `--memory-limit` (for example `8GB`) when the defaults do not
fit your environment. The 50-million-row target should be benchmarked on the
actual schema and hardware; this repository does not claim a universal timing.

## Scope

Version 0.1 deliberately does not connect to databases, guess unkeyed row
alignment, or apply patches. It compares local, keyed tabular files.

## License

MIT © 2026 Sociobot (Param Factory). See [LICENSE](LICENSE).
