# Review handoff — review 1

Completed the requested adversarial first-read review without modifying product
code. The review is in `.factory/review-1.md`; the verdict is **FAIL**.

Verified live behavior at 390 × 844 and 1440 × 900 against
`https://tabular-file-diff.sociobot.in/`. The main blockers are the absent
one-click isolated demo, no `.factory/claims.json`/claim tests, unclear
first-screen audience/action, inert `/demo`, and no designed 404.

Verification performed:

- `npm test` — pass (4 tests)
- `npm run build` — pass (`dist/site/` produced)
- `npm run test:a11y` — pass (6 tests)
- fresh local clone: `.venv/bin/pytest` after `pip install -e '.[dev]'` — pass
  (21 tests)

No product code, dependencies, or deployment assets were changed. `npm ci` and
Playwright browser installation were used only as local review prerequisites;
their generated directories remain untracked/ignored.
