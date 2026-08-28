import { type BrowserDiff, type CsvTable, diffCsv, parseCsv } from "./diff";

const sampleOld = "id,name,status,amount\nA-101,Aster,open,125\nA-102,Bram,open,80\nA-103,Cleo,hold,42";
const sampleNew = "id,name,status,amount,region\nA-101,Aster,closed,125,north\nA-102,Bram,open,84,south\nA-104,Dara,open,55,west";

if (new URLSearchParams(location.search).get("demo") === "1" && !location.pathname.startsWith("/demo")) {
  location.replace("/demo/");
}

const byId = <T extends HTMLElement>(id: string): T | null => document.getElementById(id) as T | null;

const tabs = [...document.querySelectorAll<HTMLButtonElement>('[role="tab"]')];
function selectTab(tab: HTMLButtonElement): void {
  tabs.forEach((candidate) => {
    const selected = candidate === tab;
    candidate.setAttribute("aria-selected", String(selected));
    candidate.tabIndex = selected ? 0 : -1;
    const panel = byId(candidate.getAttribute("aria-controls") ?? "");
    if (panel) panel.hidden = !selected;
  });
}
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTab(tab));
  tab.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const next = tabs[(index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length];
    if (next) { selectTab(next); next.focus(); }
  });
});

const offlineNotice = byId("offline-notice");
function updateConnection(): void { if (offlineNotice) offlineNotice.hidden = navigator.onLine; }
window.addEventListener("online", updateConnection);
window.addEventListener("offline", updateConnection);
updateConnection();

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => { void navigator.serviceWorker.register("/sw.js").catch(() => undefined); });
}

const oldInput = byId<HTMLInputElement>("old-file");
const newInput = byId<HTMLInputElement>("new-file");
const keySelect = byId<HTMLSelectElement>("key-column");
const compareButton = byId<HTMLButtonElement>("compare-button");
const resultPanel = byId<HTMLDivElement>("demo-result");
const status = byId<HTMLParagraphElement>("demo-status");
let oldTable: CsvTable | undefined;
let newTable: CsvTable | undefined;
const inDemo = location.pathname.startsWith("/demo");

function setStatus(message: string, kind: "normal" | "error" | "success" = "normal"): void {
  if (!status) return;
  status.textContent = message;
  status.className = `demo-status${kind === "normal" ? "" : ` ${kind}`}`;
}

function renderList(target: HTMLElement | null, entries: string[]): void {
  if (!target) return;
  target.replaceChildren(...entries.map((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    return item;
  }));
}

function updateKeys(): void {
  if (!keySelect || !compareButton) return;
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
}

function renderResult(result: BrowserDiff): void {
  (Object.entries(result.counts) as [keyof BrowserDiff["counts"], number][]).forEach(([name, count]) => {
    const metric = byId(`${name}-count`);
    if (metric) metric.textContent = count.toLocaleString();
  });
  renderList(byId("column-changes"), Object.entries(result.columnChanges).filter(([, count]) => count > 0).map(([name, count]) => `${name} — ${count}`) || ["No value-column changes"]);
  const schema = [...result.schema.added.map((name) => `Added: ${name}`), ...result.schema.removed.map((name) => `Removed: ${name}`)];
  renderList(byId("schema-changes"), schema.length ? schema : ["No schema changes"]);
  const changedColumns = Object.entries(result.columnChanges).filter(([, count]) => count > 0);
  const proofColumns = byId("proof-columns");
  if (proofColumns) proofColumns.textContent = changedColumns.length
    ? changedColumns.map(([name, count]) => `${name} ${count}`).join(" · ")
    : "none";
  const proofSchema = byId("proof-schema");
  if (proofSchema) proofSchema.textContent = schema.length
    ? [...result.schema.added.map((name) => `${name} added`), ...result.schema.removed.map((name) => `${name} removed`)].join(" · ")
    : "unchanged";
  const proofRow = byId("proof-row");
  const example = result.changedRows.find((change) => change.status === "modified") ?? result.changedRows[0];
  if (proofRow) proofRow.textContent = example ? `${example.key} · ${example.changes}` : "No changed rows";
  const table = byId<HTMLTableElement>("change-table");
  if (!table || !keySelect) return;
  table.replaceChildren();
  const header = table.createTHead().insertRow();
  ["Status", `Key (${keySelect.value})`, "Change"].forEach((label) => {
    const cell = document.createElement("th"); cell.scope = "col"; cell.textContent = label; header.append(cell);
  });
  const body = table.createTBody();
  result.changedRows.forEach((change) => {
    const row = body.insertRow();
    const state = row.insertCell(); state.textContent = change.status === "modified" ? "changed" : change.status; state.className = `status-${change.status}`;
    row.insertCell().textContent = change.key; row.insertCell().textContent = change.changes;
  });
}

function loadSample(): void {
  if (inDemo) sessionStorage.setItem("demo:sample-comparison", "loaded");
  oldTable = parseCsv(sampleOld);
  newTable = parseCsv(sampleNew);
  const oldName = byId("old-file-name"); const newName = byId("new-file-name");
  if (oldName) oldName.textContent = "sample-old.csv · 3 rows";
  if (newName) newName.textContent = "sample-new.csv · 3 rows";
  updateKeys();
  if (keySelect) keySelect.value = "id";
  void compare();
}

async function compare(): Promise<void> {
  if (!oldTable || !newTable || !keySelect || !compareButton || !resultPanel) return;
  compareButton.disabled = true;
  setStatus("Comparing rows in this tab…");
  await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
  try {
    const result = diffCsv(oldTable, newTable, keySelect.value);
    renderResult(result);
    resultPanel.hidden = false;
    const total = result.counts.added + result.counts.removed + result.counts.modified;
    const schemaCount = result.schema.added.length + result.schema.removed.length;
    setStatus(`Comparison complete: ${total} changed rows and ${schemaCount} schema ${schemaCount === 1 ? "change" : "changes"}.`, "success");
  } catch (error) {
    resultPanel.hidden = true;
    setStatus(error instanceof Error ? error.message : "The comparison could not be completed.", "error");
  } finally {
    compareButton.disabled = false;
  }
}

async function loadFile(input: HTMLInputElement, side: "old" | "new"): Promise<void> {
  const file = input.files?.[0];
  if (!file) return;
  try {
    const table = parseCsv(await file.text());
    if (side === "old") oldTable = table; else newTable = table;
    const filename = byId(`${side}-file-name`);
    if (filename) filename.textContent = `${file.name} · ${table.rows.length} rows`;
    if (resultPanel) resultPanel.hidden = true;
    updateKeys();
    setStatus("Files ready. Confirm the primary key, then compare rows.");
  } catch (error) {
    setStatus(error instanceof Error ? error.message : "Could not read that CSV.", "error");
  }
}

if (oldInput && newInput && keySelect && compareButton && resultPanel) {
  oldInput.addEventListener("change", () => void loadFile(oldInput, "old"));
  newInput.addEventListener("change", () => void loadFile(newInput, "new"));
  compareButton.addEventListener("click", () => void compare());
  byId<HTMLButtonElement>("sample-button")?.addEventListener("click", loadSample);
  if (inDemo) {
    loadSample();
    byId<HTMLButtonElement>("reset-demo")?.addEventListener("click", loadSample);
    byId<HTMLAnchorElement>("start-real")?.addEventListener("click", () => {
      Object.keys(sessionStorage).filter((key) => key.startsWith("demo:")).forEach((key) => sessionStorage.removeItem(key));
    });
  }
}

const announcer = byId("route-announcer");
if (announcer) announcer.textContent = document.title;
const routeHeading = document.querySelector<HTMLElement>("main h1");
if (routeHeading) {
  routeHeading.tabIndex = -1;
  requestAnimationFrame(() => routeHeading.focus({ preventScroll: true }));
}
