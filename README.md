# tabular-file-diff

Compare keyed CSV, Parquet, and Arrow data snapshots.

tdiff is for data engineers and analysts reviewing versioned data in Git or DVC.
Package and CLI comparisons run locally without telemetry.

Try the [package playground](https://tabular-file-diff.sociobot.in/demo/).
It runs the shipped Python wheel on CSV, gzip CSV, Parquet, and Arrow IPC files in your browser tab.
Run `tdiff demo` to compare the bundled files with the installed package.

## Install

tabular-file-diff supports Python 3.10 and later.

```bash
python3 -m pip install tabular-file-diff
tdiff demo
```

The package demo creates a temporary directory and writes a self-contained HTML report there.
The bundled inputs are also in [examples/](examples/).

## Compare files

Use one or more columns as the primary key.

```bash
tdiff old.parquet new.parquet --key account_id
tdiff old.csv new.csv --key tenant_id,event_id
tdiff old.arrow new.arrow --key id --tolerance 0.001
```

tdiff compares CSV, gzip CSV, Parquet, and Arrow IPC files.
It reports added, removed, changed, and unchanged rows.
It also reports changed columns and schema changes.

`--tolerance` applies only to numeric values.
The numeric boundary is inclusive.
Null versus non-null remains a change.
The default is `0`, which makes numeric comparisons exact.

Write JSON or a self-contained HTML report:

```bash
tdiff old.parquet new.parquet --key account_id --json
tdiff old.parquet new.parquet --key account_id --html report.html
```

The CLI returns `0` for no changes and `1` for differences.
It returns `2` for invalid input or operational errors.
Duplicate or null primary keys are rejected.

## Python API

`diff_files` returns a typed `DiffResult`.
Its added, removed, and modified results are PyArrow tables.

```python
from tabular_file_diff import diff_files

result = diff_files("old.parquet", "new.parquet", key="account_id")
print(result.column_changes)
```

## Git and DVC

Use the Git wrapper for changed keyed files:

```bash
git config diff.tdiff.command 'tdiff-git --key id'
printf '*.parquet diff=tdiff\n*.csv diff=tdiff\n' >> .gitattributes
git diff -- data/snapshot.parquet
```

`tdiff-git` lets `git diff` print changes without an external-driver error.

Compare a DVC revision with the workspace:

```bash
tdiff-dvc data/snapshot.parquet --from v1 --to workspace --key id
```

`tdiff-dvc` materializes the revision in a temporary directory.
It removes the temporary files when the comparison finishes.

## Develop and verify

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest
ruff check src tests
mypy src/tabular_file_diff
python3 -m build
```

Build and test the static docs and sample demo:

```bash
npm ci
npm test
npm run build:site
npm run test:a11y
```

Run every visitor claim listed in [`.factory/claims.json`](.factory/claims.json).
Each entry contains its exact clean-state command.

The factory deploys `dist/site` when `main` is pushed.
Registry credentials are not kept in this repository.

## License

tdiff is free software under the [MIT License](LICENSE).
