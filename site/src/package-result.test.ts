import { describe, expect, it } from "vitest";
import { displayRows, schemaLines, type PackageResult } from "./package-result";

const result: PackageResult = {
  keys: ["id"],
  counts: { old: 2, new: 2, added: 1, removed: 1, modified: 1, unchanged: 0 },
  column_changes: { value: 1 },
  schema: { added: { region: "VARCHAR" }, removed: {}, type_changed: {} },
  rows: {
    added: [{ id: 3, value: "new" }],
    removed: [{ id: 2, value: "old" }],
    modified: [{ id: 1, old__value: "before", new__value: "after" }]
  }
};

describe("package result adapter", () => {
  it("turns DiffResult rows into accessible display rows", () => {
    expect(displayRows(result)).toEqual([
      { status: "added", key: "3", changes: "New row" },
      { status: "removed", key: "2", changes: "Row removed" },
      { status: "modified", key: "1", changes: "value: before → after" }
    ]);
  });

  it("labels schema changes without relying on color", () => {
    expect(schemaLines(result)).toEqual(["Added: region"]);
  });
});
