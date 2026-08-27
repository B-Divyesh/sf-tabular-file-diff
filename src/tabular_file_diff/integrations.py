"""Git external-diff and DVC revision adapters."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from .cli import run


def _common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--key", required=True, action="append", help="key column; comma-separate or repeat"
    )
    parser.add_argument(
        "--tolerance", type=float, default=0.0, help="absolute numeric tolerance"
    )
    parser.add_argument("--sample", type=int, default=10, help="sample rows per change group")
    parser.add_argument("--html", nargs="?", const="tdiff-report.html", metavar="PATH")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--threads", type=int)
    parser.add_argument("--memory-limit")


def _forward(args: argparse.Namespace, old: str, new: str) -> int:
    forwarded = [old, new]
    for key in args.key:
        forwarded.extend(["--key", key])
    forwarded.extend(["--tolerance", str(args.tolerance), "--sample", str(args.sample)])
    if args.html:
        forwarded.extend(["--html", args.html])
    if args.json:
        forwarded.append("--json")
    if args.threads:
        forwarded.extend(["--threads", str(args.threads)])
    if args.memory_limit:
        forwarded.extend(["--memory-limit", args.memory_limit])
    return run(forwarded)


def git_run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tdiff-git",
        description="Git external diff driver for keyed tabular files.",
    )
    _common_options(parser)
    parser.add_argument("path", help="logical repository path supplied by Git")
    parser.add_argument("old_file")
    parser.add_argument("old_hex")
    parser.add_argument("old_mode")
    parser.add_argument("new_file")
    parser.add_argument("new_hex")
    parser.add_argument("new_mode")
    args = parser.parse_args(argv)
    if args.old_file == "/dev/null" or args.new_file == "/dev/null":
        side = "added" if args.old_file == "/dev/null" else "removed"
        print(f"TABULAR FILE DIFF\n{args.path}\n\n  file {side} (no two schemas to compare)")
        return 0

    # Git treats any non-zero external-diff exit status as a driver failure.
    # `tdiff`, like conventional diff tools, returns 1 when it finds changes,
    # so translate its successful comparison statuses for Git while preserving
    # operational errors (normally 2).
    status = _forward(args, args.old_file, args.new_file)
    return 0 if status in (0, 1) else status


def git_main() -> None:
    raise SystemExit(git_run())


def _dvc_get(path: str, revision: str, destination: Path) -> None:
    command = ["dvc", "get", ".", path, "--rev", revision, "--out", str(destination)]
    try:
        completed = subprocess.run(command, check=False, text=True, capture_output=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            "DVC is not installed; install it or use local file paths with tdiff"
        ) from error
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown DVC error"
        raise RuntimeError(f"Could not fetch {path}@{revision}: {detail}")


def dvc_run(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tdiff-dvc",
        description="Compare a DVC-tracked tabular file across two revisions.",
    )
    parser.add_argument("path", help="repository-relative path to the tracked file")
    parser.add_argument(
        "--from", dest="from_revision", required=True, help="old Git/DVC revision"
    )
    parser.add_argument(
        "--to", dest="to_revision", default="workspace", help="new revision or workspace"
    )
    _common_options(parser)
    args = parser.parse_args(argv)
    source = Path(args.path)
    suffix = "".join(source.suffixes)
    with tempfile.TemporaryDirectory(prefix="tdiff-dvc-") as temporary:
        root = Path(temporary)

        def resolve(revision: str, name: str) -> Path:
            if revision == "workspace":
                if not source.is_file():
                    raise RuntimeError(f"Workspace file not found: {source}")
                return source
            output = root / f"{name}{suffix}"
            _dvc_get(args.path, revision, output)
            return output

        try:
            old = resolve(args.from_revision, "old")
            new = resolve(args.to_revision, "new")
            return _forward(args, str(old), str(new))
        except RuntimeError as error:
            print(f"tdiff-dvc: {error}", file=sys.stderr)
            return 2


def dvc_main() -> None:
    raise SystemExit(dvc_run())
