import { describe, expect, it } from "vitest";
import { diffCsv, parseCsv } from "./diff";

describe("browser CSV demo", () => {
  it("parses quoted commas and CRLF", () => {
    const table = parseCsv('id,name\r\n1,"Ada, A."\r\n');
    expect(table.rows).toEqual([{ id: "1", name: "Ada, A." }]);
  });

  it("reports keyed row, column, and schema changes", () => {
    const oldTable = parseCsv("id,name,score\n1,Ada,10\n2,Lin,20\n3,Sam,30");
    const newTable = parseCsv("id,name,score,active\n1,Ada,10,true\n2,Lin,21,true\n4,Mae,40,true");
    const result = diffCsv(oldTable, newTable, "id");
    expect(result.counts).toEqual({ added: 1, removed: 1, modified: 1, unchanged: 1 });
    expect(result.columnChanges.score).toBe(1);
    expect(result.schema.added).toEqual(["active"]);
  });

  it("rejects duplicate and blank keys", () => {
    const duplicate = parseCsv("id,name\n1,Ada\n1,Lin");
    const blank = parseCsv("id,name\n,Ada");
    const valid = parseCsv("id,name\n1,Ada");
    expect(() => diffCsv(duplicate, valid, "id")).toThrow(/duplicate key/);
    expect(() => diffCsv(blank, valid, "id")).toThrow(/blank key/);
  });

  it("rejects malformed rows", () => {
    expect(() => parseCsv("id,name\n1,Ada,extra")).toThrow(/expected 2/);
    expect(() => parseCsv('id,name\n1,"Ada')).toThrow(/unclosed/);
  });
});
