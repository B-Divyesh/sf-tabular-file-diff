import { type BrowserDiff, type CsvTable, diffCsv, parseCsv } from "./diff";

const element = <T extends HTMLElement>(id: string): T => {
  const found = document.getElementById(id);
  if (!found) throw new Error(`Missing page element: ${id}`);
  return found as T;
};

let oldTable: CsvTable | undefined;
let newTable: CsvTable | undefined;

const oldInput = element<HTMLInputElement>("old-file");
const newInput = element<HTMLInputElement>("new-file");
const keySelect = element<HTMLSelectElement>("key-column");
const compareButton = element<HTMLButtonElement>("compare-button");
const resultPanel = element<HTMLDivElement>("demo-result");
const status = element<HTMLParagraphElement>("demo-status");

function setStatus(message: string, kind: "normal" | "error" | "success" = "normal"): void {
  status.textContent = message;
  status.className = `demo-status${kind === "normal" ? "" : ` ${kind}`}`;
}

function updateKeys(): void {
  keySelect.replaceChildren();
  if (!oldTable || !newTable) {
    keySelect.append(new Option("Select two CSV files first"));
    keySelect.disabled = true;
    compareButton.disabled = true;
    return;
  }
  const common = oldTable.headers.filter((header) => newTable?.headers.includes(header));
  if (!common.length) {
    keySelect.append(new Option("No shared columns"));
    keySelect.disabled = true;
    compareButton.disabled = true;
    setStatus("These files have no shared column to use as a key.", "error");
    return;
  }
  common.forEach((header) => keySelect.append(new Option(header, header)));
  keySelect.disabled = false;
  compareButton.disabled = false;
  setStatus("Files ready. Confirm the primary key, then compare rows.");
}

async function loadFile(input: HTMLInputElement, side: "old" | "new"): Promise<void> {
  const file = input.files?.[0];
  if (!file) return;
  try {
    setStatus(`Reading ${file.name}…`);
    const table = parseCsv(await file.text());
    if (side === "old") oldTable = table;
    else newTable = table;
    element(`${side}-file-name`).textContent = `${file.name} · ${table.rows.length.toLocaleString()} rows`;
    resultPanel.hidden = true;
    updateKeys();
  } catch (error) {
    if (side === "old") oldTable = undefined;
    else newTable = undefined;
    updateKeys();
    setStatus(error instanceof Error ? error.message : "Could not read that CSV.", "error");
  }
}

function renderList(target: HTMLElement, entries: string[]): void {
  target.replaceChildren();
  entries.forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    target.append(item);
  });
}

function renderResult(result: BrowserDiff): void {
  (Object.entries(result.counts) as [keyof BrowserDiff["counts"], number][]).forEach(([name, count]) => {
    element(`${name}-count`).textContent = count.toLocaleString();
  });
  const columns = Object.entries(result.columnChanges)
    .filter(([, count]) => count > 0)
    .map(([name, count]) => `${name} — ${count.toLocaleString()}`);
  renderList(element("column-changes"), columns.length ? columns : ["No value-column changes"]);
  const schema = [
    ...result.schema.added.map((name) => `Added: ${name}`),
    ...result.schema.removed.map((name) => `Removed: ${name}`)
  ];
  renderList(element("schema-changes"), schema.length ? schema : ["No schema changes"]);

  const table = element<HTMLTableElement>("change-table");
  table.replaceChildren();
  if (!result.changedRows.length) {
    const body = table.createTBody();
    const cell = body.insertRow().insertCell();
    cell.textContent = "No changed rows";
    return;
  }
  const header = table.createTHead().insertRow();
  ["Status", `Key (${keySelect.value})`, "Change"].forEach((label) => {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = label;
    header.append(cell);
  });
  const body = table.createTBody();
  result.changedRows.forEach((change) => {
    const row = body.insertRow();
    const state = row.insertCell();
    state.textContent = change.status;
    state.className = `status-${change.status}`;
    row.insertCell().textContent = change.key;
    row.insertCell().textContent = change.changes;
  });
}

async function compare(): Promise<void> {
  if (!oldTable || !newTable) return;
  compareButton.disabled = true;
  compareButton.textContent = "Comparing…";
  setStatus("Comparing rows in this tab…");
  await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  try {
    const result = diffCsv(oldTable, newTable, keySelect.value);
    renderResult(result);
    resultPanel.hidden = false;
    const total = result.counts.added + result.counts.removed + result.counts.modified;
    const schemaCount = result.schema.added.length + result.schema.removed.length;
    setStatus(
      total || schemaCount
        ? `Comparison complete: ${total.toLocaleString()} changed rows and ${schemaCount} schema changes.`
        : "No differences found. Every keyed row and column matches.",
      "success"
    );
  } catch (error) {
    resultPanel.hidden = true;
    setStatus(error instanceof Error ? error.message : "The comparison could not be completed.", "error");
  } finally {
    compareButton.disabled = false;
    compareButton.textContent = "Compare rows";
  }
}

oldInput.addEventListener("change", () => void loadFile(oldInput, "old"));
newInput.addEventListener("change", () => void loadFile(newInput, "new"));
compareButton.addEventListener("click", () => void compare());

element<HTMLButtonElement>("sample-button").addEventListener("click", () => {
  oldTable = parseCsv("id,name,status,amount\nA-101,Aster,open,125\nA-102,Bram,open,80\nA-103,Cleo,hold,42");
  newTable = parseCsv("id,name,status,amount,region\nA-101,Aster,closed,125,north\nA-102,Bram,open,84,south\nA-104,Dara,open,55,west");
  element("old-file-name").textContent = "sample-old.csv · 3 rows";
  element("new-file-name").textContent = "sample-new.csv · 3 rows";
  resultPanel.hidden = true;
  updateKeys();
  keySelect.value = "id";
  setStatus("Sample ready. Primary key “id” selected; choose Compare rows.");
});

document.querySelectorAll<HTMLButtonElement>("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy ?? "");
      button.textContent = "Copied";
      window.setTimeout(() => { button.textContent = "Copy"; }, 1600);
    } catch {
      button.textContent = "Select command";
    }
  });
});

const tabs = [...document.querySelectorAll<HTMLButtonElement>('[role="tab"]')];
function selectTab(tab: HTMLButtonElement): void {
  tabs.forEach((candidate) => {
    const selected = candidate === tab;
    candidate.setAttribute("aria-selected", String(selected));
    candidate.tabIndex = selected ? 0 : -1;
    const panel = document.getElementById(candidate.getAttribute("aria-controls") ?? "");
    if (panel) panel.hidden = !selected;
  });
}
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTab(tab));
  tab.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const next = tabs[(index + offset + tabs.length) % tabs.length];
    if (next) { selectTab(next); next.focus(); }
  });
});

const offlineNotice = element("offline-notice");
function updateConnection(): void { offlineNotice.hidden = navigator.onLine; }
window.addEventListener("online", updateConnection);
window.addEventListener("offline", updateConnection);
updateConnection();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => { void navigator.serviceWorker.register("/sw.js").catch(() => undefined); });
}
