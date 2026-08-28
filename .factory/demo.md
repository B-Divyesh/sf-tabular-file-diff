# Demo sandbox

Open [`/demo/`](https://tabular-file-diff.sociobot.in/demo/) or
[`/?demo=1`](https://tabular-file-diff.sociobot.in/?demo=1).

The direct sample demo loads two shipped CSV snapshots and immediately displays one
added row, one removed row, two changed rows, column counts, schema change, and
changed-row details. It is a browser-only CSV comparison, labeled separately
from the package demo.

The persistent banner says **Demo — sample data, nothing is saved**. **Reset
demo** restores those shipped inputs. **Start for real** removes the
`demo:sample-comparison` session-storage key and returns to the empty landing
page. Demo code does not read or write any non-`demo:` storage key.

For the actual Python package demo, run:

```bash
tdiff demo
```

It copies bundled sample CSVs into a fresh temporary directory, runs the real
comparison engine, writes a self-contained report there, and prints the path.
The matching inspectable samples are in `examples/`.
