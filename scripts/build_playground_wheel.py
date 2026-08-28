"""Build the exact source package as a small, deterministic browser wheel.

The regular release still uses ``python -m build``. This standard-library-only
builder lets the static-site build embed the same Python package without
requiring a second build environment during an npm-only deployment.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "src" / "tabular_file_diff"
OUTPUT = ROOT / "site" / "public" / "playground" / "tabular_file_diff-0.1.0-py3-none-any.whl"
DIST_INFO = "tabular_file_diff-0.1.0.dist-info"


def digest(data: bytes) -> str:
    value = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
    return f"sha256={value}"


def metadata() -> bytes:
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE)
    if not version or version.group(1) != "0.1.0":
        raise RuntimeError("Update the playground wheel filename when the package version changes")
    return (
        "Metadata-Version: 2.3\n"
        "Name: tabular-file-diff\n"
        f"Version: {version.group(1)}\n"
        "Summary: Key-aware local diffs for tabular files\n"
        "Requires-Python: >=3.10\n"
        "Requires-Dist: duckdb>=1.1,<2\n"
        "Requires-Dist: pyarrow>=15,<22\n\n"
    ).encode()


def main() -> None:
    files: dict[str, bytes] = {}
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file() and path.suffix not in {".pyc"}:
            files[path.relative_to(ROOT / "src").as_posix()] = path.read_bytes()
    files[f"{DIST_INFO}/METADATA"] = metadata()
    files[f"{DIST_INFO}/WHEEL"] = (
        b"Wheel-Version: 1.0\nGenerator: tabular-file-diff browser builder\n"
        b"Root-Is-Purelib: true\nTag: py3-none-any\n"
    )
    files[f"{DIST_INFO}/entry_points.txt"] = (
        b"[console_scripts]\n"
        b"tdiff = tabular_file_diff.cli:main\n"
        b"tdiff-dvc = tabular_file_diff.integrations:dvc_main\n"
        b"tdiff-git = tabular_file_diff.integrations:git_main\n"
    )
    files[f"{DIST_INFO}/licenses/LICENSE"] = (ROOT / "LICENSE").read_bytes()
    record_path = f"{DIST_INFO}/RECORD"
    rows = [[name, digest(data), str(len(data))] for name, data in files.items()]
    rows.append([record_path, "", ""])
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(rows)
    files[record_path] = output.getvalue().encode()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED, compresslevel=9) as wheel:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            wheel.writestr(info, data)
    print(OUTPUT)
if __name__ == "__main__":
    main()
