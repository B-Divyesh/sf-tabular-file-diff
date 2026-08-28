# Demo sandbox

Open [`/demo/`](https://tabular-file-diff.sociobot.in/demo/) or
[`/?demo=1`](https://tabular-file-diff.sociobot.in/?demo=1).

The direct sample demo loads two shipped CSV snapshots and immediately displays
one added row, one removed row, two changed rows, column counts, a schema
change, and changed-row details. A self-hosted Python/WASM worker then runs the
built `tabular-file-diff` wheel with DuckDB and PyArrow to verify that result.

The workbench accepts CSV, gzip CSV, Parquet, Arrow IPC, and Feather files. Its
format picker includes shipped CSV, gzip CSV, Parquet, and Arrow IPC pairs. CSV
sample text is editable. Each comparison exposes the package JSON and a
self-contained HTML report for download.

The persistent banner says **Demo — sample data, nothing is saved**. **Reset
demo** restores those shipped inputs. **Start for real** removes the
`demo:sample-comparison` session-storage key and returns to the empty landing
page. Demo code does not read or write any non-`demo:` storage key.

Python, DuckDB, PyArrow, and their required packages are served from the same
origin. The browser caches immutable runtime code for later offline use; no
selected file or comparison result is added to that cache.

For the actual Python package demo, run:

```bash
tdiff demo
```

It copies bundled sample CSVs into a fresh temporary directory, runs the real
comparison engine, writes a self-contained report there, and prints the path.
The matching inspectable samples are in `examples/`.
