"""Public API for :mod:`tabular_file_diff`."""

from .core import DiffError, DiffResult, SchemaDiff, diff_files

__all__ = ["DiffError", "DiffResult", "SchemaDiff", "diff_files"]
__version__ = "0.1.0"
