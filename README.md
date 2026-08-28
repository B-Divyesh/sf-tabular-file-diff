# tabular-file-diff

Compare keyed CSV, Parquet, and Arrow data snapshots.

tdiff is for data engineers and analysts reviewing versioned data in Git or DVC.
It runs locally and has no telemetry.

Try the shipped browser sample at [tabular-file-diff.sociobot.in/demo/](https://tabular-file-diff.sociobot.in/demo/).
The browser preview compares CSV only.
Run `tdiff demo` to run the installed package on its bundled sample.

## Install

```bash
python3 -m pip install tabular-file-diff
tdiff demo
```

The demo prints its temporary directory and writes an HTML report there.
Its sample inputs also ship in [examples/](examples/).

## Compare files

Use one or more columns as the primary key.

```bash
tdiff old.parquet new.parquet --key account_id
tdiff old.csv new.csv --key tenant_id,event_id
tdiff old.arrow new.arrow --key id --tolerance 0.001
```

tdiff reports added, removed, changed, and unchanged rows.
It also reports changed columns and schema changes.
Supported files are CSV, gzip CSV, Parquet, and Arrow IPC.

`--tolerance` applies only to numeric values.
A row is unchanged when the absolute difference is at most the tolerance.
Null versus non-null is always a change.
It defaults to `0`, so comparisons are exact.

Write JSON or a self-contained HTML report:

```bash
tdiff old.parquet new.parquet --key account_id --json
tdiff old.parquet new.parquet --key account_id --html report.html
```

The CLI returns `0` for no differences and `1` for differences.
It returns `2` for invalid input or operational errors.
Duplicate or null key values are rejected.

## Python API

`diff_files` returns a typed `DiffResult`.
Its added, removed, and modified values are PyArrow tables.

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

`tdiff-dvc` materializes the requested revision in a temporary directory.

## Develop and verify

Python 3.10 or later is required.

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
python3 -m pytest
ruff check src tests
mypy src/tabular_file_diff
python3 -m build
```

Build and test the static docs and sample preview:

```bash
npm ci
npm test
npm run build:site
npm run test:a11y
```

Run every visitor claim from [`.factory/claims.json`](.factory/claims.json):

```bash
npm run test:claims -- --grep @claim:demo-one-click
python3 -m pytest tests/test_claims.py
```

Deploy the static site by pushing `main`; the factory deploys `dist/site`.
The package is ready for `python3 -m build`.
Registry credentials are not kept in this repository.

## License

tdiff is free software under the [MIT License](LICENSE).

