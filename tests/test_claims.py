"""Observable claim checks for the catalog and documentation."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import socket
import subprocess
import sys
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.ipc as ipc
import pyarrow.parquet as pq
import pytest

from tabular_file_diff import DiffError, DiffResult, diff_files
from tabular_file_diff.cli import run
from tabular_file_diff.integrations import dvc_run


@pytest.mark.parametrize("suffix", ["csv", "csv-gzip.bin", "parquet", "arrow"])
def test_playground_fixtures_match_diff_files(tmp_path: Path, suffix: str) -> None:
    """The browser fixtures produce the same result through the package API."""
    fixtures = Path(__file__).parents[1] / "site" / "public" / "samples"
    package_suffix = "csv.gz" if suffix == "csv-gzip.bin" else suffix
    old = tmp_path / f"old.{package_suffix}"
    new = tmp_path / f"new.{package_suffix}"
    old.write_bytes(fixtures.joinpath(f"sample-old.{suffix}").read_bytes())
    new.write_bytes(fixtures.joinpath(f"sample-new.{suffix}").read_bytes())
    result = diff_files(old, new, key="id")
    assert (result.added_count, result.removed_count, result.modified_count, result.unchanged_count) == (1, 1, 2, 0)
    assert result.column_changes == {"name": 0, "status": 1, "amount": 1}
    assert result.schema.added == {"region": "VARCHAR"}


def test_playground_wheel_contains_current_package(tmp_path: Path) -> None:
    """The self-hosted wheel is rebuilt from, and contains, the package source."""
    repository = Path(__file__).parents[1]
    subprocess.run([sys.executable, "scripts/build_playground_wheel.py"], cwd=repository, check=True)
    wheel = repository / "site/public/playground/tabular_file_diff-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel) as archive:
        for source in (repository / "src/tabular_file_diff").rglob("*"):
            if source.is_file() and source.suffix != ".pyc":
                packaged = archive.read(source.relative_to(repository / "src").as_posix())
                assert packaged == source.read_bytes()
    worker = repository.joinpath("site/public/playground/worker.js").read_text(encoding="utf-8")
    assert "from tabular_file_diff import diff_files" in worker
    assert "site/src/diff" not in worker


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


def test_claim_comparison_results(tmp_path: Path) -> None:
    """@claim:comparison-results"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,same\n2,old\n3,removed\n5,also-same\n", encoding="utf-8")
    new.write_text("id,value,region\n1,same,north\n2,new,south\n4,added,west\n5,also-same,east\n", encoding="utf-8")
    result = diff_files(old, new, key="id")
    assert (result.added_count, result.removed_count, result.modified_count, result.unchanged_count) == (1, 1, 1, 2)
    assert result.column_changes["value"] == 1
    assert result.schema.added == {"region": "VARCHAR"}


def test_claim_tolerance_semantics(tmp_path: Path) -> None:
    """@claim:tolerance-semantics"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,number,text,nullable\n1,1.0,old,value\n", encoding="utf-8")
    new.write_text("id,number,text,nullable\n1,1.01,new,\n", encoding="utf-8")
    tolerant = diff_files(old, new, key="id", tolerance=0.01)
    assert tolerant.column_changes == {"number": 0, "text": 1, "nullable": 1}
    assert tolerant.modified_count == 1
    exact = diff_files(old, new, key="id")
    assert exact.column_changes["number"] == 1


def test_claim_cli_statuses(tmp_path: Path) -> None:
    """@claim:cli-statuses"""
    same_a, same_b = tmp_path / "same-a.csv", tmp_path / "same-b.csv"
    changed = tmp_path / "changed.csv"
    malformed = tmp_path / "malformed.csv"
    same_a.write_text("id,value\n1,same\n", encoding="utf-8")
    same_b.write_text("id,value\n1,same\n", encoding="utf-8")
    changed.write_text("id,value\n1,new\n", encoding="utf-8")
    malformed.write_text('id,value\n1,"open\n', encoding="utf-8")
    assert run([str(same_a), str(same_b), "--key", "id"]) == 0
    assert run([str(same_a), str(changed), "--key", "id"]) == 1
    assert run([str(malformed), str(same_b), "--key", "id"]) == 2
    assert run([str(tmp_path / "missing.csv"), str(same_b), "--key", "id"]) == 2


def test_claim_key_validation(tmp_path: Path) -> None:
    """@claim:key-validation"""
    valid = tmp_path / "valid.csv"
    duplicate = tmp_path / "duplicate.csv"
    null = tmp_path / "null.csv"
    valid.write_text("id,value\n1,a\n", encoding="utf-8")
    duplicate.write_text("id,value\n1,a\n1,b\n", encoding="utf-8")
    null.write_text("id,value\n,a\n", encoding="utf-8")
    with pytest.raises(DiffError, match="Duplicate key"):
        diff_files(duplicate, valid, key="id")
    with pytest.raises(DiffError, match="Null key"):
        diff_files(null, valid, key="id")


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
    materialized: list[Path] = []
    def fake_run(command: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        output = Path(command[command.index("--out") + 1])
        materialized.append(output)
        output.write_text("id,value\n1,new\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")
    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    monkeypatch.setattr(subprocess, "run", fake_run)  # type: ignore[attr-defined]
    assert dvc_run(["data.csv", "--from", "v1", "--to", "workspace", "--key", "id", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["counts"]["modified"] == 1
    assert materialized and not materialized[0].exists()


def test_claim_mit_license() -> None:
    """@claim:mit-license"""
    license_text = Path(__file__).parents[1].joinpath("LICENSE").read_text(encoding="utf-8")
    assert "Permission is hereby granted" in license_text
    assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in license_text
    metadata = Path(__file__).parents[1].joinpath("pyproject.toml").read_text(encoding="utf-8")
    assert 'license = { file = "LICENSE" }' in metadata


def test_claim_local_no_telemetry(tmp_path: Path, monkeypatch: object) -> None:
    """@claim:local-no-telemetry"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,old\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n", encoding="utf-8")

    def no_socket(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("local comparison attempted network access")

    monkeypatch.setattr(socket, "socket", no_socket)  # type: ignore[attr-defined]
    assert run([str(old), str(new), "--key", "id"]) == 1


def test_claim_python_api(tmp_path: Path) -> None:
    """@claim:python-api"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,old\n2,removed\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n3,added\n", encoding="utf-8")
    result = diff_files(old, new, key="id")
    assert isinstance(result, DiffResult)
    assert all(isinstance(table, pa.Table) for table in (result.added, result.removed, result.modified))
    assert (result.added.num_rows, result.removed.num_rows, result.modified.num_rows) == (1, 1, 1)


def test_claim_packaged_demo(tmp_path: Path, capsys: object, monkeypatch: object) -> None:
    """@claim:packaged-demo"""
    monkeypatch.chdir(tmp_path)  # type: ignore[attr-defined]
    assert run(["demo"]) == 1
    output = capsys.readouterr().out
    directory = Path(next(line.split(": ", 1)[1] for line in output.splitlines() if line.startswith("Demo files")))
    assert directory.parent == Path("/tmp")
    assert directory != tmp_path
    assert directory.joinpath("sample-old.csv").is_file()
    report = directory.joinpath("tdiff-demo-report.html")
    assert report.is_file()
    html = report.read_text(encoding="utf-8")
    assert "<script" not in html and "https://" not in html
    repository = Path(__file__).parents[1]
    assert repository.joinpath("examples/sample-old.csv").is_file()
    assert repository.joinpath("src/tabular_file_diff/samples/sample-old.csv").is_file()


def test_claim_python_runtime() -> None:
    """@claim:python-runtime"""
    metadata = Path(__file__).parents[1].joinpath("pyproject.toml").read_text(encoding="utf-8")
    assert re.search(r'^requires-python = ">=3\.10"$', metadata, re.MULTILINE)
    assert all(f'"Programming Language :: Python :: {minor}"' in metadata for minor in ("3.10", "3.11", "3.12"))


def test_claim_input_read_only(tmp_path: Path) -> None:
    """@claim:input-read-only"""
    old, new = tmp_path / "old.csv", tmp_path / "new.csv"
    old.write_text("id,value\n1,old\n", encoding="utf-8")
    new.write_text("id,value\n1,new\n", encoding="utf-8")
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (old, new)}
    assert run([str(old), str(new), "--key", "id", "--html", str(tmp_path / "report.html")]) == 1
    assert diff_files(old, new, key="id").modified_count == 1
    for path, digest in before.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
