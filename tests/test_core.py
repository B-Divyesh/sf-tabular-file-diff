from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as parquet
import pytest

from tabular_file_diff import DiffError, diff_files


def write_csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_documented_diff_returns_arrow_tables(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,name,score\n1,Ada,10\n2,Lin,20\n3,Sam,30\n")
    new = write_csv(tmp_path / "new.csv", "id,name,score\n1,Ada,10\n2,Lin,21\n4,Mae,40\n")

    result = diff_files(old, new, key="id")

    assert isinstance(result.added, pa.Table)
    assert (result.added_count, result.removed_count, result.modified_count) == (1, 1, 1)
    assert result.unchanged_count == 1
    assert result.added_count == result.added.num_rows
    assert result.added.to_pylist() == [{"id": 4, "name": "Mae", "score": 40}]
    assert result.removed.to_pylist() == [{"id": 3, "name": "Sam", "score": 30}]
    assert result.modified.to_pylist() == [
        {"id": 2, "old__name": "Lin", "new__name": "Lin", "old__score": 20, "new__score": 21}
    ]
    assert result.column_changes == {"name": 0, "score": 1}
    assert result.has_changes


def test_composite_key_and_absolute_numeric_tolerance(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "tenant,id,value\na,1,1.0\na,2,2.0\n")
    new = write_csv(tmp_path / "new.csv", "tenant,id,value\na,1,1.005\na,2,2.02\n")

    result = diff_files(old, new, key=["tenant", "id"], tolerance=0.01)

    assert result.modified_count == 1
    assert result.column_changes["value"] == 1
    assert result.modified.column_names[:2] == ["tenant", "id"]


def test_exact_numeric_tolerance_boundary_is_inclusive(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,value\n1,1.0\n")
    new = write_csv(tmp_path / "new.csv", "id,value\n1,1.01\n")

    result = diff_files(old, new, key="id", tolerance=0.01)

    assert result.modified_count == 0
    assert result.unchanged_count == 1
    assert result.column_changes == {"value": 0}


def test_unterminated_quoted_csv_is_rejected(tmp_path: Path) -> None:
    malformed = write_csv(tmp_path / "malformed.csv", 'id,name\n1,"unterminated\n')
    valid = write_csv(tmp_path / "valid.csv", "id,name\n1,Ada\n")

    with pytest.raises(DiffError, match="Malformed CSV input .*unterminated quoted field"):
        diff_files(malformed, valid, key="id")


def test_schema_changes_are_reported_without_false_row_modifications(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,name\n1,Ada\n")
    new = write_csv(tmp_path / "new.csv", "id,name,active\n1,Ada,true\n")

    result = diff_files(old, new, key="id")

    assert result.modified_count == 0
    assert result.schema.added == {"active": "BOOLEAN"}
    assert result.has_changes


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        ("id,name\n1,Ada\n1,Lin\n", "Duplicate key"),
        ("id,name\n,Ada\n", "Null key"),
    ],
)
def test_ambiguous_keys_are_rejected(tmp_path: Path, contents: str, message: str) -> None:
    old = write_csv(tmp_path / "old.csv", contents)
    new = write_csv(tmp_path / "new.csv", "id,name\n1,Ada\n")

    with pytest.raises(DiffError, match=message):
        diff_files(old, new, key="id")


def test_missing_key_and_invalid_options_are_clear(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,name\n1,Ada\n")
    new = write_csv(tmp_path / "new.csv", "id,name\n1,Ada\n")

    with pytest.raises(DiffError, match="missing"):
        diff_files(old, new, key="account_id")
    with pytest.raises(DiffError, match="Tolerance"):
        diff_files(old, new, key="id", tolerance=-1)


def test_max_rows_caps_tables_but_not_counts(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,value\n1,a\n2,b\n3,c\n")
    new = write_csv(tmp_path / "new.csv", "id,value\n4,d\n5,e\n6,f\n")

    result = diff_files(old, new, key="id", max_rows=1)

    assert result.added_count == 3
    assert result.removed_count == 3
    assert result.added.num_rows == result.removed.num_rows == 1
    assert result.tables_truncated


def test_parquet_and_feather_inputs(tmp_path: Path) -> None:
    old_table = pa.table({"id": [1, 2], "value": ["a", "b"]})
    new_table = pa.table({"id": [1, 2], "value": ["a", "c"]})
    old_parquet, new_parquet = tmp_path / "old.parquet", tmp_path / "new.parquet"
    parquet.write_table(old_table, old_parquet)
    parquet.write_table(new_table, new_parquet)
    assert diff_files(old_parquet, new_parquet, key="id").modified_count == 1

    old_feather, new_feather = tmp_path / "old.feather", tmp_path / "new.feather"
    feather.write_feather(old_table, old_feather)
    feather.write_feather(new_table, new_feather)
    assert diff_files(old_feather, new_feather, key="id").modified_count == 1


def test_no_changes(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,name\n1,Ada\n")
    new = write_csv(tmp_path / "new.csv", "id,name\n1,Ada\n")
    result = diff_files(old, new, key="id")
    assert not result.has_changes
    assert result.unchanged_count == 1


def test_header_only_csvs_are_a_valid_empty_comparison(tmp_path: Path) -> None:
    old = write_csv(tmp_path / "old.csv", "id,name\n")
    new = write_csv(tmp_path / "new.csv", "id,name\n")
    result = diff_files(old, new, key="id")
    assert not result.has_changes
    assert result.old_count == result.new_count == 0
    assert result.added.schema.names == ["id", "name"]
