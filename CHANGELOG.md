# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- Made nonzero numeric tolerances inclusive at their decimal boundary, without
  IEEE-754 round-off falsely reporting a change.
- Reject CSV and CSV.GZ inputs with an unterminated quoted field before they
  can be silently compared by the CSV scanner.

## [0.1.0] - 2026-08-27

### Added

- Key-aware CSV, Parquet, Arrow IPC, and Feather comparisons powered by DuckDB.
- Terminal, JSON, and self-contained HTML reports.
- Typed Python API returning PyArrow difference tables.
- Git external-diff and DVC revision wrappers.
- Local-first documentation site and in-browser CSV demo.
