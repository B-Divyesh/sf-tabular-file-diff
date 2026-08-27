from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

from tabular_file_diff.cli import run
from tabular_file_diff.integrations import dvc_run, git_run


def write_pair(tmp_path: Path) -> tuple[Path, Path]:
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,name\n1,Ada\n2,Lin\n", encoding="utf-8")
    new.write_text("id,name\n1,Ada\n2,Mae\n", encoding="utf-8")
    return old, new


def test_json_cli_and_diff_exit_code(tmp_path: Path, capsys: object) -> None:
    old, new = write_pair(tmp_path)
    assert run([str(old), str(new), "--key", "id", "--json"]) == 1
    output = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert output["counts"]["modified"] == 1
    assert output["rows"]["modified"][0]["id"] == 2


def test_html_report_is_self_contained_and_escaped(tmp_path: Path) -> None:
    old, new = write_pair(tmp_path)
    report = tmp_path / "report.html"
    run([str(old), str(new), "--key", "id", "--html", str(report)])
    html = report.read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "<script" not in html
    assert "Modified rows" in html
    assert "https://" not in html


def test_cli_error_is_exit_two(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "missing.csv"
    assert run([str(path), str(path), "--key", "id"]) == 2
    assert "File not found" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_cli_exact_tolerance_boundary_is_unchanged(tmp_path: Path, capsys: object) -> None:
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    old.write_text("id,value\n1,1.0\n", encoding="utf-8")
    new.write_text("id,value\n1,1.01\n", encoding="utf-8")

    assert run([str(old), str(new), "--key", "id", "--tolerance", "0.01", "--json"]) == 0
    output = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert output["counts"] == {
        "old": 1,
        "new": 1,
        "added": 0,
        "removed": 0,
        "modified": 0,
        "unchanged": 1,
    }


def test_cli_unterminated_quoted_csv_is_exit_two(tmp_path: Path, capsys: object) -> None:
    malformed = tmp_path / "malformed.csv"
    valid = tmp_path / "valid.csv"
    malformed.write_text('id,name\n1,"unterminated\n', encoding="utf-8")
    valid.write_text("id,name\n1,Ada\n", encoding="utf-8")

    assert run([str(malformed), str(valid), "--key", "id", "--json"]) == 2
    error = capsys.readouterr().err  # type: ignore[attr-defined]
    assert "Malformed CSV input" in error
    assert "unterminated quoted field" in error


def test_git_driver_handles_file_level_addition(capsys: object) -> None:
    code = git_run(
        [
            "--key",
            "id",
            "data/file.parquet",
            "/dev/null",
            "." * 40,
            "000000",
            "/tmp/new.parquet",
            "a" * 40,
            "100644",
        ]
    )
    assert code == 0
    assert "file added" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_git_external_diff_handles_changed_csv(tmp_path: Path) -> None:
    """The documented Git driver must not make ``git diff`` fail on changes."""
    repository = tmp_path / "repository"
    repository.mkdir()

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repository,
            check=True,
            text=True,
            capture_output=True,
        )

    git("init", "--quiet")
    git("config", "user.email", "tests@example.invalid")
    git("config", "user.name", "tdiff tests")
    (repository / ".gitattributes").write_text("*.csv diff=tdiff\n", encoding="utf-8")
    snapshot = repository / "snapshot.csv"
    snapshot.write_text("id,value\n1,old\n2,stay\n", encoding="utf-8")
    git("add", ".gitattributes", "snapshot.csv")
    git("commit", "--quiet", "-m", "initial snapshot")

    driver = tmp_path / "tdiff-git"
    driver.write_text(
        "#!/bin/sh\n"
        f"exec {shlex.quote(sys.executable)} -c "
        f"{shlex.quote('from tabular_file_diff.integrations import git_main; git_main()')} \"$@\"\n",
        encoding="utf-8",
    )
    driver.chmod(0o755)
    git("config", "diff.tdiff.command", f"{driver} --key id")

    snapshot.write_text("id,value\n1,new\n3,added\n", encoding="utf-8")
    result = subprocess.run(
        ["git", "diff", "--", "snapshot.csv"],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "fatal: external diff died" not in result.stderr
    assert "+ added                 1" in result.stdout
    assert "- removed               1" in result.stdout
    assert "~ modified              1" in result.stdout


def test_dvc_driver_materializes_a_revision(
    tmp_path: Path, capsys: object, monkeypatch: object
) -> None:
    workspace = tmp_path / "data.csv"
    workspace.write_text("id,name\n1,Ada\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        output = Path(command[command.index("--out") + 1])
        output.write_text("id,name\n1,Ada\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    monkeypatch.setattr(subprocess, "run", fake_run)  # type: ignore[attr-defined]
    code = dvc_run(["data.csv", "--from", "v1", "--to", "workspace", "--key", "id", "--json"])
    assert code == 0
    assert calls[0][:5] == ["dvc", "get", ".", "data.csv", "--rev"]
    assert json.loads(capsys.readouterr().out)["counts"]["unchanged"] == 1  # type: ignore[attr-defined]
