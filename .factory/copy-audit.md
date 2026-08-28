# Copy audit — perfection loop 3

Audited 28 August 2026. Commands, filenames, and sample output are treated as
data. Sentences are counted separately when one paragraph contains more than
one sentence. No prose sentence exceeds 22 words. No banned marketing word is
present.

## First-screen read-aloud check

“Compare keyed data snapshots. For data engineers reviewing CSV, Parquet, or
Arrow changes in Git or DVC. Try it with sample data.” This states the job,
audience, context, and first action in one breath.

## Landing page

| Words | Visible copy unit |
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
| 5 | Compare local keyed data files. |
| 7 | MIT licensed · Built by Param Factory · 0.1.0 |

## Package playground

| Words | Visible copy unit |
| ---: | --- |
| 7 | Demo — sample data, nothing is saved |
| 2 | Reset demo |
| 3 | Start for real |
| 2 | Package playground |
| 6 | Run the package in your browser |
| 9 | The shipped Python wheel runs here with DuckDB and PyArrow. |
| 6 | Your files stay in this tab. |
| 5 | Loading the local Python package… |
| 2 | Package result |
| 1 | Added |
| 1 | Removed |
| 1 | Changed |
| 1 | Unchanged |
| 3 | region added |
| 6 | A-101 · status: open → closed |
| 8 | Running the packaged comparison locally… |
| 2 | Your files |
| 3 | Compare supported files |
| 13 | Edit CSV text or choose CSV, gzip CSV, Parquet, Arrow IPC, or Feather files. |
| 3 | Shipped sample format |
| 3 | Load format sample |
| 3 | Old data snapshot |
| 3 | New data snapshot |
| 3 | Old CSV text |
| 3 | New CSV text |
| 2 | Primary key |
| 2 | Numeric tolerance |
| 3 | Compare with package |
| 3 | Changes by column |
| 2 | Schema changes |
| 2 | Changed-row sample |
| 3 | Package JSON output |
| 5 | Waiting for the packaged comparison. |
| 3 | Download HTML report |
| 2 | Fresh project |
| 5 | Use the same Python API |
| 3 | Copy Python snippet |

Dynamic progress, success, empty, and error messages are each at most 18
words. Errors state what failed and tell the visitor to check the inputs or
reload while online.

## README prose

| Words | Sentence or heading |
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

## Terminology

| Concept | Approved term |
| --- | --- |
| Compared inputs | data snapshots |
| Row identity | primary key; row ID only in the first explanation |
| In-browser path | package playground |
| Installed path | package demo |
| Output | comparison |
| Difference state | changed |

The package API and terminal keep `modified` as their stable technical field.
Visible instructional copy uses the plainer word “changed.”
