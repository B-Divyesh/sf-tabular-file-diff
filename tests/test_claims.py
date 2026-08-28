"""Observable claim checks for the catalog and documentation."""
from __future__ import annotations

import gzip
import json
import socket
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq

from tabular_file_diff import diff_files
from tabular_file_diff.cli import run
from tabular_file_diff.integrations import dvc_run


def test_claim_package_formats(tmp_path: Path, capsys: object) -> None:
    """@claim:package-formats"""
    rows_old = pa.table({"id": [1, 2], "value": ["old", "same"]})
    rows_new = pa.table({"id": [1, 3], "value": ["new", "added"]})
    old_csv, new_csv = tmp_path / "old.csv", tmp_path / "new.csv"
    old_csv.write_text("id,value\n1,old\n2,same\n", encoding="utf-8")
    new_csv.write_text("id,value\n1,new\n3,added\n", encoding="utf-8")
    old_gzip, new_gzip = tmp_path / "old.csv.gz", tmp_path / "new.csv.gz"
    with gzip.open(old_gzip, "wt", encoding="utf-8") as output:
        output.write(old_csv.read_text(encoding="utf-8"))
    with gzip.open(new_gzip, "wt", encoding="utf-8") as output:
        output.write(new_csv.read_text(encoding="utf-8"))
    old_parquet, new_parquet = tmp_path / "old.parquet", tmp_path / "new.parquet"
    pq.write_table(rows_old, old_parquet)
    pq.write_table(rows_new, new_parquet)
    old_arrow, new_arrow = tmp_path / "old.arrow", tmp_path / "new.arrow"
    for path, table in ((old_arrow, rows_old), (new_arrow, rows_new)):
        with path.open("wb") as output, ipc.new_file(output, table.schema) as writer:
            writer.write_table(table)
    for old, new in ((old_csv, new_csv), (old_gzip, new_gzip), (old_parquet, new_parquet), (old_arrow, new_arrow)):
        assert run([str(old), str(new), "--key", "id", "--json"]) == 1
        assert json.loads(capsys.readouterr().out)["counts"]["modified"] == 1


def test_claim_html_report(tmp_path: Path) -> None:
    """@claim:html-report"""
    old, new, report = tmp_path / "old.csv", tmp_path / "new.csv", tmp_path / "report.html"
    old.write_text("id,value\n1,old\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n", encoding="utf-8")
    assert run([str(old), str(new), "--key", "id", "--html", str(report)]) == 1
    html = report.read_text(encoding="utf-8")
    assert "<!doctype html>" in html and "<script" not in html and "https://" not in html


def test_claim_git_wrapper(tmp_path: Path) -> None:
    """@claim:git-wrapper"""
    repository = tmp_path / "repository"
    repository.mkdir()
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repository, check=True, text=True, capture_output=True)
    git("init", "--quiet")
    git("config", "user.email", "claims@example.invalid")
    git("config", "user.name", "claims")
    (repository / ".gitattributes").write_text("*.csv diff=tdiff\n", encoding="utf-8")
    data = repository / "data.csv"
    data.write_text("id,value\n1,old\n", encoding="utf-8")
    git("add", ".")
    git("commit", "--quiet", "-m", "old")
    driver = tmp_path / "tdiff-git"
    driver.write_text("#!/bin/sh\nexec " + sys.executable + " -c 'from tabular_file_diff.integrations import git_main; git_main()' \"$@\"\n", encoding="utf-8")
    driver.chmod(0o755)
    git("config", "diff.tdiff.command", str(driver) + " --key id")
    data.write_text("id,value\n1,new\n", encoding="utf-8")
    completed = subprocess.run(["git", "diff", "--", "data.csv"], cwd=repository, text=True, capture_output=True, check=False)
    assert completed.returncode == 0 and "~ modified" in completed.stdout


def test_claim_dvc_wrapper(tmp_path: Path, monkeypatch: object, capsys: object) -> None:
    """@claim:dvc-wrapper"""
    data = tmp_path / "data.csv"
    data.write_text("id,value\n1,old\n", encoding="utf-8")
    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        output = Path(command[command.index("--out") + 1])
        output.write_text("id,value\n1,new\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")
    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    monkeypatch.setattr(subprocess, "run", fake_run)  # type: ignore[attr-defined]
    assert dvc_run(["data.csv", "--from", "v1", "--to", "workspace", "--key", "id", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["counts"]["modified"] == 1


def test_claim_mit_license() -> None:
    """@claim:mit-license"""
    license_text = Path(__file__).parents[1].joinpath("LICENSE").read_text(encoding="utf-8")
    assert "Permission is hereby granted" in license_text
    assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in license_text


def test_claim_local_no_telemetry(tmp_path: Path, monkeypatch: object) -> None:
    """@claim:local-no-telemetry"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,old\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n", encoding="utf-8")

    def no_socket(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("local comparison attempted network access")

    monkeypatch.setattr(socket, "socket", no_socket)  # type: ignore[attr-defined]
    assert run([str(old), str(new), "--key", "id"]) == 1


def test_claim_cli_contract_and_python_api(tmp_path: Path, capsys: object) -> None:
    """@claim:cli-contract"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,old\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n", encoding="utf-8")
    assert run([str(old), str(new), "--key", "id", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["counts"]["modified"] == 1
    result = diff_files(old, new, key="id")
    assert isinstance(result.modified, pa.Table) and result.modified.num_rows == 1


def test_claim_packaged_demo(capsys: object) -> None:
    """@claim:packaged-demo"""
    assert run(["demo"]) == 1
    output = capsys.readouterr().out
    directory = Path(next(line.split(": ", 1)[1] for line in output.splitlines() if line.startswith("Demo files")))
    assert directory.joinpath("sample-old.csv").is_file()
    assert directory.joinpath("tdiff-demo-report.html").is_file()
