"""Release checks from the perspective of a clean wheel consumer."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


def test_built_wheel_consumer_gets_safe_tolerance_and_csv_errors(tmp_path: Path) -> None:
    """The built package, not the source tree, retains the P1 fixes."""
    distribution = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(distribution)],
        check=True,
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
    )
    wheel = next(distribution.glob("*.whl"))
    environment = tmp_path / "consumer-venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    executable = environment / "bin" / "python"
    pip = environment / "bin" / "pip"
    subprocess.run(
        [str(pip), "install", str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )

    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    malformed = tmp_path / "malformed.csv"
    old.write_text("id,value\n1,1.0\n", encoding="utf-8")
    new.write_text("id,value\n1,1.01\n", encoding="utf-8")
    malformed.write_text('id,value\n1,"unterminated\n', encoding="utf-8")
    environment_variables = os.environ.copy()
    environment_variables.pop("PYTHONPATH", None)

    api = subprocess.run(
        [
            str(executable),
            "-c",
            (
                "from tabular_file_diff import diff_files; "
                f"result = diff_files({str(old)!r}, {str(new)!r}, key='id', tolerance=0.01); "
                "assert result.modified_count == 0; "
                "assert result.unchanged_count == 1"
            ),
        ],
        check=True,
        cwd=tmp_path,
        env=environment_variables,
        capture_output=True,
        text=True,
    )
    assert api.stderr == ""

    cli = subprocess.run(
        [
            str(environment / "bin" / "tdiff"),
            str(malformed),
            str(new),
            "--key",
            "id",
            "--json",
        ],
        check=False,
        cwd=tmp_path,
        env=environment_variables,
        capture_output=True,
        text=True,
    )
    assert cli.returncode == 2
    assert "Malformed CSV input" in cli.stderr
    assert "unterminated quoted field" in cli.stderr

    demo = subprocess.run(
        [str(environment / "bin" / "tdiff"), "demo"],
        check=False,
        cwd=tmp_path,
        env=environment_variables,
        capture_output=True,
        text=True,
    )
    assert demo.returncode == 1
    demo_directory = Path(
        next(line.split(": ", 1)[1] for line in demo.stdout.splitlines() if line.startswith("Demo files"))
    )
    assert demo_directory.joinpath("sample-old.csv").is_file()
    assert demo_directory.joinpath("tdiff-demo-report.html").is_file()
