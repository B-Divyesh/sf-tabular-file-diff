from __future__ import annotations

import json
import subprocess
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
    assert code == 1
    assert "file added" in capsys.readouterr().out  # type: ignore[attr-defined]


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
