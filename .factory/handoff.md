# Review 3 handoff

## Delivered

- Wrote `.factory/review-3.md`; no product source, deployment, or test code was
  modified.
- Ran a cold live review at 390 x 844 and 1440 x 900, direct-demo sandbox and
  storage checks, route/metadata/focus checks, and link crawl.
- Created a fresh clone at `/tmp/tdiff-review3.rOgI9q/repo`, installed new
  Python and npm dependencies, and ran all 20 registered claim commands.
- Ran `tdiff demo` from an unrelated temporary directory.

## Result

**FAIL.** One blocking finding remains: the one-click browser demo uses the
separate `site/src/diff.ts` CSV implementation, not the published Python
library. It cannot exercise the library's Parquet/Arrow/DuckDB/PyArrow/API/
integration behavior. See `F-3-1` in `.factory/review-3.md` for evidence and
the concrete required fix.

All other reviewed first-read, direct-demo mechanics, claim tests, privacy
capture, offline claim coverage, copy, route/metadata, link, responsive, and
historical-regression checks passed.

## Verify

```bash
npm ci
npm test
npm run build
npm run test:a11y
python3 -m pytest tests/test_claims.py
```

Run each exact clean-state claim command from `.factory/claims.json` as well.
The direct browser demo is at `/demo/`; the installed-package demo is `tdiff
demo` from any directory.

## Next step

Implement a local, in-page playground that executes the published package and
add package-parity claims/tests. Then rerun the full adversarial review.
