"""DuckDB-powered, key-aware tabular file comparison."""

from __future__ import annotations

import gzip
import math
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

import duckdb
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.ipc as ipc


class DiffError(ValueError):
    """Raised when inputs cannot be compared safely."""


class _ByteReader(Protocol):
    def read(self, size: int = -1) -> bytes: ...


@dataclass(frozen=True)
class SchemaDiff:
    """Column-level schema changes between the old and new snapshots."""

    added: dict[str, str]
    removed: dict[str, str]
    type_changed: dict[str, tuple[str, str]]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.type_changed)


@dataclass(frozen=True)
class DiffResult:
    """Complete counts and Arrow tables for a keyed file comparison."""

    old_path: str
    new_path: str
    keys: tuple[str, ...]
    old_count: int
    new_count: int
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    column_changes: dict[str, int]
    schema: SchemaDiff
    added: pa.Table
    removed: pa.Table
    modified: pa.Table
    tables_truncated: bool

    @property
    def has_changes(self) -> bool:
        """Whether rows or schema differ."""
        return bool(
            self.added_count
            or self.removed_count
            or self.modified_count
            or self.schema.has_changes
        )

    def to_dict(self, *, include_rows: bool = True) -> dict[str, Any]:
        """Return a JSON-friendly summary (date-like values may need ``default=str``)."""
        data: dict[str, Any] = {
            "old_path": self.old_path,
            "new_path": self.new_path,
            "keys": list(self.keys),
            "counts": {
                "old": self.old_count,
                "new": self.new_count,
                "added": self.added_count,
                "removed": self.removed_count,
                "modified": self.modified_count,
                "unchanged": self.unchanged_count,
            },
            "column_changes": self.column_changes,
            "schema": asdict(self.schema),
            "tables_truncated": self.tables_truncated,
        }
        if include_rows:
            data["rows"] = {
                "added": self.added.to_pylist(),
                "removed": self.removed.to_pylist(),
                "modified": self.modified.to_pylist(),
            }
        return data


_NUMERIC_TYPES = (
    "TINYINT",
    "SMALLINT",
    "INTEGER",
    "BIGINT",
    "HUGEINT",
    "UTINYINT",
    "USMALLINT",
    "UINTEGER",
    "UBIGINT",
    "FLOAT",
    "DOUBLE",
    "DECIMAL",
    "REAL",
)


def _ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _is_numeric(type_name: str) -> bool:
    return type_name.upper().startswith(_NUMERIC_TYPES)


def _read_arrow(path: Path) -> pa.Table:
    if path.suffix.lower() == ".feather":
        return feather.read_table(path)
    try:
        with pa.memory_map(str(path), "r") as source:
            return ipc.open_file(source).read_all()
    except pa.ArrowInvalid:
        with pa.memory_map(str(path), "r") as source:
            return ipc.open_stream(source).read_all()


def _has_unterminated_csv_quote(source: _ByteReader) -> bool:
    """Return whether a streaming CSV source finishes inside a quoted field."""
    quoted = False
    quote_pending = False
    while chunk := source.read(64 * 1024):
        for byte in chunk:
            if quote_pending:
                quote_pending = False
                if byte == ord('"'):
                    # A doubled quote is an escaped literal quote.
                    continue
                quoted = False
            if byte == ord('"'):
                if quoted:
                    # Wait for the next byte to distinguish a closing quote
                    # from a doubled escaped quote.
                    quote_pending = True
                else:
                    quoted = True
    return quoted and not quote_pending


def _validate_csv_quotes(path: Path) -> None:
    """Reject an unclosed quoted field before DuckDB's permissive CSV scan.

    DuckDB intentionally accepts some malformed CSV records as plain text.  A
    dangling quote is unsafe for a diff because it can silently join records,
    so match the browser demo's CSV rule before handing the file to DuckDB.
    The scan is byte-oriented and streaming; it does not materialize the file.
    """
    try:
        if path.name.lower().endswith(".csv.gz"):
            with gzip.open(path, "rb") as source:
                unterminated = _has_unterminated_csv_quote(source)
        else:
            with path.open("rb") as source:
                unterminated = _has_unterminated_csv_quote(source)
    except OSError as error:
        raise DiffError(f"Could not read CSV input {path}: {error}") from error
    if unterminated:
        raise DiffError(f"Malformed CSV input {path}: unterminated quoted field")


def _register_source(connection: duckdb.DuckDBPyConnection, name: str, path: Path) -> None:
    lower = path.name.lower()
    if not path.is_file():
        raise DiffError(f"File not found: {path}")
    if lower.endswith((".parquet", ".pq")):
        reader = f"read_parquet({_literal(str(path))}, union_by_name = true)"
    elif lower.endswith((".csv", ".csv.gz")):
        _validate_csv_quotes(path)
        reader = f"read_csv_auto({_literal(str(path))}, header = true, strict_mode = true)"
    elif lower.endswith((".arrow", ".ipc", ".feather")):
        registered = f"_{name}_arrow"
        try:
            connection.register(registered, _read_arrow(path))
        except (pa.ArrowInvalid, OSError) as error:
            raise DiffError(f"Could not read Arrow input {path}: {error}") from error
        reader = _ident(registered)
    else:
        raise DiffError(
            f"Unsupported input {path}. Use CSV, CSV.GZ, Parquet, Arrow IPC, or Feather."
        )
    connection.execute(f"CREATE TEMP VIEW {_ident(name)} AS SELECT * FROM {reader}")


def _schema(connection: duckdb.DuckDBPyConnection, table: str) -> dict[str, str]:
    rows = connection.execute(f"DESCRIBE SELECT * FROM {_ident(table)}").fetchall()
    return {str(row[0]): str(row[1]) for row in rows}


def _validate_keys(
    connection: duckdb.DuckDBPyConnection,
    table: str,
    path: Path,
    keys: tuple[str, ...],
    schema: dict[str, str],
) -> None:
    missing = [key for key in keys if key not in schema]
    if missing:
        raise DiffError(f"Key column(s) missing from {path}: {', '.join(missing)}")
    null_where = " OR ".join(f"{_ident(key)} IS NULL" for key in keys)
    if connection.execute(
        f"SELECT 1 FROM {_ident(table)} WHERE {null_where} LIMIT 1"
    ).fetchone():
        raise DiffError(f"Null key found in {path}; keys must identify every row")
    grouped = ", ".join(_ident(key) for key in keys)
    if connection.execute(
        f"SELECT 1 FROM {_ident(table)} GROUP BY {grouped} HAVING count(*) > 1 LIMIT 1"
    ).fetchone():
        raise DiffError(f"Duplicate key found in {path}; keys must be unique")


def _change_expression(
    column: str,
    old_type: str,
    new_type: str,
    tolerance: float,
) -> str:
    old = f"o.{_ident(column)}"
    new = f"n.{_ident(column)}"
    distinct = f"{old} IS DISTINCT FROM {new}"
    if tolerance and _is_numeric(old_type) and _is_numeric(new_type):
        # CSV numeric values are commonly IEEE doubles.  An exact decimal
        # boundary such as 1.01 - 1.0 can be a few ULPs larger than 0.01 after
        # binary conversion.  Keep the documented inclusive boundary stable
        # by allowing only that representational noise, not a relative error.
        effective_tolerance = tolerance + 8 * math.ulp(tolerance)
        return (
            f"({distinct} AND ("
            f"{old} IS NULL OR {new} IS NULL OR "
            f"abs(CAST({old} AS DOUBLE) - CAST({new} AS DOUBLE)) "
            f"> {effective_tolerance!r}))"
        )
    if old_type != new_type:
        return f"CAST({old} AS VARCHAR) IS DISTINCT FROM CAST({new} AS VARCHAR)"
    return distinct


def _limited(query: str, max_rows: int | None) -> str:
    return query if max_rows is None else f"{query} LIMIT {max_rows}"


def diff_files(
    old_path: str | Path,
    new_path: str | Path,
    *,
    key: str | Sequence[str],
    tolerance: float = 0.0,
    max_rows: int | None = None,
    threads: int | None = None,
    memory_limit: str | None = None,
) -> DiffResult:
    """Compare two tabular files by a unique, non-null key.

    Aggregate counts always cover the complete inputs. Difference tables contain
    every row unless ``max_rows`` is provided. Numeric tolerance is absolute and
    applies only where both versions of a column have numeric DuckDB types.
    """
    old = Path(old_path).expanduser().resolve()
    new = Path(new_path).expanduser().resolve()
    keys = (key,) if isinstance(key, str) else tuple(key)
    keys = tuple(part.strip() for item in keys for part in item.split(",") if part.strip())
    if not keys:
        raise DiffError("At least one key column is required")
    if len(set(keys)) != len(keys):
        raise DiffError("Key columns must not be repeated")
    if not math.isfinite(tolerance) or tolerance < 0:
        raise DiffError("Tolerance must be a finite number that is zero or greater")
    if max_rows is not None and max_rows < 0:
        raise DiffError("max_rows must be zero or greater")

    connection = duckdb.connect(database=":memory:")
    try:
        if threads is not None:
            if threads < 1:
                raise DiffError("threads must be at least 1")
            connection.execute(f"SET threads = {int(threads)}")
        if memory_limit is not None:
            connection.execute(f"SET memory_limit = {_literal(memory_limit)}")
        _register_source(connection, "old_data", old)
        _register_source(connection, "new_data", new)
        old_schema = _schema(connection, "old_data")
        new_schema = _schema(connection, "new_data")
        _validate_keys(connection, "old_data", old, keys, old_schema)
        _validate_keys(connection, "new_data", new, keys, new_schema)

        schema_diff = SchemaDiff(
            added={name: kind for name, kind in new_schema.items() if name not in old_schema},
            removed={name: kind for name, kind in old_schema.items() if name not in new_schema},
            type_changed={
                name: (old_schema[name], new_schema[name])
                for name in old_schema.keys() & new_schema.keys()
                if old_schema[name] != new_schema[name]
            },
        )
        common_columns = [
            name for name in old_schema if name in new_schema and name not in keys
        ]
        join = " AND ".join(f"o.{_ident(name)} = n.{_ident(name)}" for name in keys)
        changes = {
            name: _change_expression(name, old_schema[name], new_schema[name], tolerance)
            for name in common_columns
        }
        any_change = " OR ".join(f"({value})" for value in changes.values()) or "FALSE"
        old_marker = f"o.{_ident(keys[0])}"
        new_marker = f"n.{_ident(keys[0])}"
        column_sums = "".join(
            f", count(*) FILTER (WHERE {old_marker} IS NOT NULL "
            f"AND {new_marker} IS NOT NULL AND ({expression})) AS {_ident(name)}"
            for name, expression in changes.items()
        )
        aggregates = connection.execute(
            f"""
            SELECT
              count(*) FILTER (WHERE {old_marker} IS NULL) AS added,
              count(*) FILTER (WHERE {new_marker} IS NULL) AS removed,
              count(*) FILTER (WHERE {old_marker} IS NOT NULL AND {new_marker} IS NOT NULL
                               AND ({any_change})) AS modified,
              count(*) FILTER (WHERE {old_marker} IS NOT NULL AND {new_marker} IS NOT NULL
                               AND NOT ({any_change})) AS unchanged
              {column_sums}
            FROM old_data o FULL OUTER JOIN new_data n ON {join}
            """
        ).fetchone()
        assert aggregates is not None
        added_count, removed_count, modified_count, unchanged_count = map(int, aggregates[:4])
        column_changes = {
            name: int(aggregates[index + 4]) for index, name in enumerate(common_columns)
        }
        old_count = int(
            connection.execute("SELECT count(*) FROM old_data").fetchone()[0]  # type: ignore[index]
        )
        new_count = int(
            connection.execute("SELECT count(*) FROM new_data").fetchone()[0]  # type: ignore[index]
        )

        added_query = f"SELECT n.* FROM new_data n ANTI JOIN old_data o ON {join}"
        removed_query = f"SELECT o.* FROM old_data o ANTI JOIN new_data n ON {join}"
        modified_fields = [f"o.{_ident(name)} AS {_ident(name)}" for name in keys] + [
            field
            for name in common_columns
            for field in (
                f"o.{_ident(name)} AS {_ident('old__' + name)}",
                f"n.{_ident(name)} AS {_ident('new__' + name)}",
            )
        ]
        modified_query = (
            f"SELECT {', '.join(modified_fields)} FROM old_data o "
            f"INNER JOIN new_data n ON {join} WHERE {any_change}"
        )
        added = connection.execute(_limited(added_query, max_rows)).to_arrow_table()
        removed = connection.execute(_limited(removed_query, max_rows)).to_arrow_table()
        modified = connection.execute(_limited(modified_query, max_rows)).to_arrow_table()
        truncated = max_rows is not None and any(
            count > max_rows for count in (added_count, removed_count, modified_count)
        )
        return DiffResult(
            old_path=str(old),
            new_path=str(new),
            keys=keys,
            old_count=old_count,
            new_count=new_count,
            added_count=added_count,
            removed_count=removed_count,
            modified_count=modified_count,
            unchanged_count=unchanged_count,
            column_changes=column_changes,
            schema=schema_diff,
            added=added,
            removed=removed,
            modified=modified,
            tables_truncated=truncated,
        )
    except duckdb.Error as error:
        raise DiffError(f"DuckDB could not compare the files: {error}") from error
    finally:
        connection.close()
