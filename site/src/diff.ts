export type CsvTable = {
  headers: string[];
  rows: Record<string, string>[];
};

export type BrowserDiff = {
  counts: { added: number; removed: number; modified: number; unchanged: number };
  columnChanges: Record<string, number>;
  schema: { added: string[]; removed: string[] };
  changedRows: { status: "added" | "removed" | "modified"; key: string; changes: string }[];
};

export function parseCsv(source: string): CsvTable {
  if (!source.trim()) throw new Error("The CSV is empty. Choose a file with a header row.");
  const matrix: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (character === '"') {
      if (quoted && source[index + 1] === '"') {
        cell += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && source[index + 1] === "\n") index += 1;
      row.push(cell);
      if (row.some((value) => value.length > 0)) matrix.push(row);
      row = [];
      cell = "";
    } else {
      cell += character;
    }
  }
  if (quoted) throw new Error("The CSV has an unclosed quoted field.");
  row.push(cell);
  if (row.some((value) => value.length > 0)) matrix.push(row);
  const first = matrix.shift();
  if (!first) throw new Error("The CSV needs a header row.");
  const headers = first.map((header, index) => (index === 0 ? header.replace(/^\uFEFF/, "") : header).trim());
  if (headers.some((header) => !header)) throw new Error("Every CSV column needs a header.");
  if (new Set(headers).size !== headers.length) throw new Error("CSV headers must be unique.");
  const rows = matrix.map((values, rowIndex) => {
    if (values.length !== headers.length) {
      throw new Error(`Row ${rowIndex + 2} has ${values.length} fields; expected ${headers.length}.`);
    }
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
  return { headers, rows };
}

function keyed(table: CsvTable, key: string, label: string): Map<string, Record<string, string>> {
  if (!table.headers.includes(key)) throw new Error(`${label} CSV does not contain the “${key}” key column.`);
  const result = new Map<string, Record<string, string>>();
  for (const row of table.rows) {
    const value = row[key] ?? "";
    if (!value) throw new Error(`${label} CSV has a blank key. Every row needs a “${key}” value.`);
    if (result.has(value)) throw new Error(`${label} CSV has duplicate key “${value}”. Choose a unique key.`);
    result.set(value, row);
  }
  return result;
}

export function diffCsv(oldTable: CsvTable, newTable: CsvTable, key: string): BrowserDiff {
  const oldRows = keyed(oldTable, key, "Old");
  const newRows = keyed(newTable, key, "New");
  const common = oldTable.headers.filter((name) => newTable.headers.includes(name) && name !== key);
  const schema = {
    added: newTable.headers.filter((name) => !oldTable.headers.includes(name)),
    removed: oldTable.headers.filter((name) => !newTable.headers.includes(name))
  };
  const columnChanges = Object.fromEntries(common.map((name) => [name, 0]));
  const changedRows: BrowserDiff["changedRows"] = [];
  const counts = { added: 0, removed: 0, modified: 0, unchanged: 0 };

  for (const [value, oldRow] of oldRows) {
    const newRow = newRows.get(value);
    if (!newRow) {
      counts.removed += 1;
      if (changedRows.length < 8) changedRows.push({ status: "removed", key: value, changes: "Row removed" });
      continue;
    }
    const changed = common.filter((name) => oldRow[name] !== newRow[name]);
    if (changed.length) {
      counts.modified += 1;
      changed.forEach((name) => { columnChanges[name] = (columnChanges[name] ?? 0) + 1; });
      if (changedRows.length < 8) {
        changedRows.push({
          status: "modified",
          key: value,
          changes: changed.map((name) => `${name}: ${oldRow[name] || "NULL"} → ${newRow[name] || "NULL"}`).join("; ")
        });
      }
    } else {
      counts.unchanged += 1;
    }
  }
  for (const value of newRows.keys()) {
    if (!oldRows.has(value)) {
      counts.added += 1;
      if (changedRows.length < 8) changedRows.push({ status: "added", key: value, changes: "Row added" });
    }
  }
  return { counts, columnChanges, schema, changedRows };
}
