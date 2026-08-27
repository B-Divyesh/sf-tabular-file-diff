"""Command-line interface for tabular-file-diff."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .core import DiffError, DiffResult, diff_files
from .report import write_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tdiff",
        description="Key-aware diff for CSV, Parquet, and Arrow files.",
        epilog="Exit 0: identical; 1: differences; 2: invalid input or operational error.",
    )
    parser.add_argument("old", help="old snapshot (.csv, .parquet, .arrow, .ipc, .feather)")
    parser.add_argument("new", help="new snapshot")
    parser.add_argument(
        "--key",
        required=True,
        action="append",
        help="key column; comma-separate or repeat for composite keys",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.0,
        help="absolute tolerance for numeric values (default: exact)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=10,
        help="maximum rows per change group in output (default: 10)",
    )
    parser.add_argument(
        "--html",
        nargs="?",
        const="tdiff-report.html",
        metavar="PATH",
        help="write a self-contained HTML report",
    )
    parser.add_argument(
        "--json", action="store_true", help="write machine-readable JSON to stdout"
    )
    parser.add_argument("--threads", type=int, help="DuckDB worker threads")
    parser.add_argument(
        "--memory-limit", metavar="SIZE", help="DuckDB memory limit, for example 8GB"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _schema_lines(result: DiffResult) -> list[str]:
    lines: list[str] = []
    lines.extend(f"  + {name}: {kind}" for name, kind in result.schema.added.items())
    lines.extend(f"  - {name}: {kind}" for name, kind in result.schema.removed.items())
    lines.extend(
        f"  ~ {name}: {old} → {new}" for name, (old, new) in result.schema.type_changed.items()
    )
    return lines


def _terminal(result: DiffResult) -> str:
    lines = [
        "TABULAR FILE DIFF",
        f"{Path(result.old_path).name} → {Path(result.new_path).name}",
        f"key: {', '.join(result.keys)}",
        "",
        f"  + added      {result.added_count:>12,}",
        f"  - removed    {result.removed_count:>12,}",
        f"  ~ modified   {result.modified_count:>12,}",
        f"  = unchanged  {result.unchanged_count:>12,}",
        "",
        "CHANGES BY COLUMN",
    ]
    changed_columns = [(name, count) for name, count in result.column_changes.items() if count]
    lines.extend(f"  {name:<24} {count:>12,}" for name, count in changed_columns)
    if not changed_columns:
        lines.append("  none")
    lines.extend(["", "SCHEMA"])
    lines.extend(_schema_lines(result) or ["  unchanged"])
    for label, table in (
        ("ADDED SAMPLE", result.added),
        ("REMOVED SAMPLE", result.removed),
        ("MODIFIED SAMPLE", result.modified),
    ):
        if table.num_rows:
            lines.extend(["", label, json.dumps(table.to_pylist(), indent=2, default=str)])
    if result.tables_truncated:
        lines.extend(["", "Samples are truncated; aggregate counts cover all rows."])
    return "\n".join(lines)


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = diff_files(
            args.old,
            args.new,
            key=args.key,
            tolerance=args.tolerance,
            max_rows=args.sample,
            threads=args.threads,
            memory_limit=args.memory_limit,
        )
        if args.html:
            output = write_html(result, args.html)
            if not args.json:
                print(f"Report: {output}", file=sys.stderr)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, default=str))
        else:
            print(_terminal(result))
        return 1 if result.has_changes else 0
    except (DiffError, OSError) as error:
        print(f"tdiff: {error}", file=sys.stderr)
        return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
