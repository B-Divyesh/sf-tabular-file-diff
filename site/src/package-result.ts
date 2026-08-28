export type PackageResult = {
  keys: string[];
  counts: { old: number; new: number; added: number; removed: number; modified: number; unchanged: number };
  column_changes: Record<string, number>;
  schema: {
    added: Record<string, string>;
    removed: Record<string, string>;
    type_changed: Record<string, [string, string]>;
  };
  rows: {
    added: Record<string, unknown>[];
    removed: Record<string, unknown>[];
    modified: Record<string, unknown>[];
  };
};

export type DisplayRow = { status: "added" | "removed" | "modified"; key: string; changes: string };

function value(value: unknown): string {
  return value === null || value === undefined ? "null" : String(value);
}

export function displayRows(result: PackageResult): DisplayRow[] {
  const keyOf = (row: Record<string, unknown>) => result.keys.map((key) => value(row[key])).join(" / ");
  const added = result.rows.added.map((row) => ({ status: "added" as const, key: keyOf(row), changes: "New row" }));
  const removed = result.rows.removed.map((row) => ({ status: "removed" as const, key: keyOf(row), changes: "Row removed" }));
  const modified = result.rows.modified.map((row) => {
    const changes = Object.keys(result.column_changes)
      .filter((name) => value(row[`old__${name}`]) !== value(row[`new__${name}`]))
      .map((name) => `${name}: ${value(row[`old__${name}`])} → ${value(row[`new__${name}`])}`);
    return { status: "modified" as const, key: keyOf(row), changes: changes.join("; ") || "Value changed" };
  });
  return [...added, ...removed, ...modified];
}

export function schemaLines(result: PackageResult): string[] {
  return [
    ...Object.keys(result.schema.added).map((name) => `Added: ${name}`),
    ...Object.keys(result.schema.removed).map((name) => `Removed: ${name}`),
    ...Object.entries(result.schema.type_changed).map(([name, types]) => `Changed: ${name} (${types[0]} → ${types[1]})`)
  ];
}
