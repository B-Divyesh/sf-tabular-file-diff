import { displayRows, schemaLines, type PackageResult } from "./package-result";

const sampleOld = "id,name,status,amount\nA-101,Aster,open,125\nA-102,Bram,open,80\nA-103,Cleo,hold,42\n";
const sampleNew = "id,name,status,amount,region\nA-101,Aster,closed,125,north\nA-102,Bram,open,84,south\nA-104,Dara,open,55,west\n";
const encoder = new TextEncoder();

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

type Snapshot = { name: string; bytes: ArrayBuffer };
type RuntimeVersions = { package: string; duckdb: string; pyarrow: string; module: string };
type WorkerMessage =
  | { type: "progress"; message: string }
  | { type: "ready"; versions: RuntimeVersions }
  | { type: "result"; id: number; result: PackageResult; report: string }
  | { type: "error" | "fatal"; id?: number; message: string };

const oldInput = byId<HTMLInputElement>("old-file");
const newInput = byId<HTMLInputElement>("new-file");
const keyInput = byId<HTMLInputElement>("key-column");
const toleranceInput = byId<HTMLInputElement>("tolerance");
const compareButton = byId<HTMLButtonElement>("compare-button");
const resultPanel = byId<HTMLDivElement>("demo-result");
const status = byId<HTMLParagraphElement>("demo-status");
const engineProof = byId<HTMLParagraphElement>("engine-proof");
const oldEditor = byId<HTMLTextAreaElement>("old-editor");
const newEditor = byId<HTMLTextAreaElement>("new-editor");
const sampleFormat = byId<HTMLSelectElement>("sample-format");
const packageOutput = byId<HTMLElement>("package-output");
const downloadReport = byId<HTMLButtonElement>("download-report");
const inDemo = location.pathname.startsWith("/demo");

let oldSnapshot: Snapshot | undefined;
let newSnapshot: Snapshot | undefined;
let packageWorker: Worker | undefined;
let nextRequest = 0;
let latestRequest = 0;
let latestReport: string | undefined;
const requests = new Map<number, { resolve: (value: { result: PackageResult; report: string }) => void; reject: (error: Error) => void }>();

function setStatus(message: string, kind: "normal" | "error" | "success" = "normal"): void {
  if (!status) return;
  status.textContent = message;
  status.className = `demo-status${kind === "normal" ? "" : ` ${kind}`}`;
}

function setEngine(message: string, ready = false): void {
  if (!engineProof) return;
  engineProof.textContent = message;
  engineProof.dataset.packageReady = String(ready);
}

function plainError(message: string): string {
  const last = message.split("\n").map((line) => line.trim()).filter(Boolean).at(-1) ?? message;
  return last.replace(/^(tabular_file_diff\.core\.)?DiffError:\s*/, "");
}

async function cacheCurrentPage(): Promise<void> {
  if (!("caches" in window)) return;
  const resources = [...document.querySelectorAll<HTMLLinkElement | HTMLScriptElement>('link[rel="stylesheet"][href], link[rel="icon"][href], script[src]')]
    .map((element) => element instanceof HTMLLinkElement ? element.href : element.src)
    .filter((url) => url.startsWith(location.origin));
  const cache = await caches.open("tdiff-shell-v5");
  const urls = [location.href, "/demo/", "/playground/worker.js", "/playground/pyodide/pyodide.js", ...resources]
    .map((url) => new URL(url, location.origin).href);
  await cache.addAll([...new Set(urls)]);
  document.documentElement.dataset.offlineReady = "true";
}

function startPackageWorker(): Worker {
  if (packageWorker) return packageWorker;
  packageWorker = new Worker("/playground/worker.js");
  packageWorker.addEventListener("message", (event: MessageEvent<WorkerMessage>) => {
    const message = event.data;
    if (message.type === "progress") {
      setEngine(message.message);
      return;
    }
    if (message.type === "ready") {
      setEngine(`Wheel ${message.versions.package} · DuckDB ${message.versions.duckdb} · PyArrow ${message.versions.pyarrow}`, true);
      document.documentElement.dataset.packageModule = message.versions.module;
      void cacheCurrentPage().catch(() => setStatus("Package is ready. Offline saving failed; stay online to compare.", "error"));
      return;
    }
    if (message.type === "fatal") {
      setEngine("The local package could not start.");
      setStatus(`The local package could not start. ${plainError(message.message)} Reload while online and try again.`, "error");
      for (const pending of requests.values()) pending.reject(new Error(message.message));
      requests.clear();
      return;
    }
    const pending = requests.get(message.id ?? -1);
    if (!pending) return;
    requests.delete(message.id ?? -1);
    if (message.type === "result") pending.resolve({ result: message.result, report: message.report });
    else pending.reject(new Error(message.message));
  });
  packageWorker.addEventListener("error", (event) => {
    setEngine("The local package could not start.");
    setStatus(`The local package stopped. ${event.message || "Reload and try again."}`, "error");
  });
  return packageWorker;
}

function compareWithPackage(oldFile: Snapshot, newFile: Snapshot, key: string, tolerance: number): Promise<{ result: PackageResult; report: string }> {
  const worker = startPackageWorker();
  const id = ++nextRequest;
  return new Promise((resolve, reject) => {
    requests.set(id, { resolve, reject });
    const oldBytes = oldFile.bytes.slice(0);
    const newBytes = newFile.bytes.slice(0);
    worker.postMessage({ type: "compare", id, old: { name: oldFile.name, bytes: oldBytes }, new: { name: newFile.name, bytes: newBytes }, key, tolerance }, [oldBytes, newBytes]);
  });
}

function renderList(target: HTMLElement | null, entries: string[]): void {
  if (!target) return;
  target.replaceChildren(...entries.map((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    return item;
  }));
}

function renderResult(result: PackageResult, report: string): void {
  for (const name of ["added", "removed", "modified", "unchanged"] as const) {
    const metric = byId(`${name}-count`);
    if (metric) metric.textContent = result.counts[name].toLocaleString();
  }
  const changedColumns = Object.entries(result.column_changes).filter(([, count]) => count > 0);
  renderList(byId("column-changes"), changedColumns.length ? changedColumns.map(([name, count]) => `${name} — ${count}`) : ["No value-column changes"]);
  const schema = schemaLines(result);
  renderList(byId("schema-changes"), schema.length ? schema : ["No schema changes"]);
  const proofColumns = byId("proof-columns");
  if (proofColumns) proofColumns.textContent = changedColumns.length ? changedColumns.map(([name, count]) => `${name} ${count}`).join(" · ") : "none";
  const proofSchema = byId("proof-schema");
  if (proofSchema) {
    const proof = [
      ...Object.keys(result.schema.added).map((name) => `${name} added`),
      ...Object.keys(result.schema.removed).map((name) => `${name} removed`),
      ...Object.keys(result.schema.type_changed).map((name) => `${name} type changed`)
    ];
    proofSchema.textContent = proof.length ? proof.join(" · ") : "unchanged";
  }
  const rows = displayRows(result);
  const example = rows.find((change) => change.status === "modified") ?? rows[0];
  const proofRow = byId("proof-row");
  if (proofRow) proofRow.textContent = example ? `${example.key} · ${example.changes}` : "No changed rows";
  const table = byId<HTMLTableElement>("change-table");
  if (table) {
    table.replaceChildren();
    const header = table.createTHead().insertRow();
    ["Status", `Key (${result.keys.join(", ")})`, "Change"].forEach((label) => {
      const cell = document.createElement("th"); cell.scope = "col"; cell.textContent = label; header.append(cell);
    });
    const body = table.createTBody();
    rows.forEach((change) => {
      const row = body.insertRow();
      const state = row.insertCell(); state.textContent = change.status === "modified" ? "changed" : change.status; state.className = `status-${change.status}`;
      row.insertCell().textContent = change.key;
      row.insertCell().textContent = change.changes;
    });
  }
  if (packageOutput) packageOutput.textContent = JSON.stringify(result, null, 2);
  latestReport = report;
  if (downloadReport) {
    downloadReport.disabled = false;
  }
  resultPanel?.setAttribute("aria-busy", "false");
}

async function compare(): Promise<void> {
  if (!oldSnapshot || !newSnapshot || !keyInput || !compareButton || !resultPanel) return;
  const key = keyInput.value.trim();
  if (!key) {
    setStatus("Enter the primary key shared by both files.", "error");
    keyInput.focus();
    return;
  }
  const tolerance = Number(toleranceInput?.value ?? 0);
  if (!Number.isFinite(tolerance) || tolerance < 0) {
    setStatus("Enter a tolerance of zero or more.", "error");
    toleranceInput?.focus();
    return;
  }
  compareButton.disabled = true;
  resultPanel.hidden = false;
  resultPanel.setAttribute("aria-busy", "true");
  setStatus("Running the packaged comparison locally…");
  const request = ++latestRequest;
  try {
    const output = await compareWithPackage(oldSnapshot, newSnapshot, key, tolerance);
    if (request !== latestRequest) return;
    renderResult(output.result, output.report);
    const total = output.result.counts.added + output.result.counts.removed + output.result.counts.modified;
    const schemaCount = schemaLines(output.result).length;
    setStatus(`Package comparison complete: ${total} changed rows and ${schemaCount} schema ${schemaCount === 1 ? "change" : "changes"}.`, "success");
  } catch (error) {
    if (request !== latestRequest) return;
    resultPanel.hidden = true;
    setStatus(`${plainError(error instanceof Error ? error.message : String(error))} Check the files and primary key, then try again.`, "error");
  } finally {
    if (request === latestRequest) compareButton.disabled = false;
  }
}

function setCsvEditors(oldText: string, newText: string): void {
  if (oldEditor) { oldEditor.disabled = false; oldEditor.value = oldText; }
  if (newEditor) { newEditor.disabled = false; newEditor.value = newText; }
}

async function sampleSnapshot(side: "old" | "new", format: string): Promise<Snapshot> {
  if (format === "csv") {
    const source = side === "old" ? sampleOld : sampleNew;
    return { name: `sample-${side}.csv`, bytes: encoder.encode(source).buffer };
  }
  const suffix = format === "gzip" ? "csv.gz" : format;
  const asset = format === "gzip" ? `sample-${side}.csv-gzip.bin` : `sample-${side}.${suffix}`;
  const response = await fetch(`/samples/${asset}`);
  if (!response.ok) throw new Error(`The ${format} sample could not be loaded.`);
  return { name: `sample-${side}.${suffix}`, bytes: await response.arrayBuffer() };
}

async function loadSample(format = sampleFormat?.value ?? "csv"): Promise<void> {
  if (inDemo) sessionStorage.setItem("demo:sample-comparison", format);
  setStatus(`Loading the ${format === "gzip" ? "gzip CSV" : format.toUpperCase()} sample…`);
  try {
    [oldSnapshot, newSnapshot] = await Promise.all([sampleSnapshot("old", format), sampleSnapshot("new", format)]);
    const oldName = byId("old-file-name"); const newName = byId("new-file-name");
    if (oldName) oldName.textContent = oldSnapshot.name;
    if (newName) newName.textContent = newSnapshot.name;
    if (format === "csv") setCsvEditors(sampleOld, sampleNew);
    else {
      if (oldEditor) { oldEditor.value = `Binary ${oldSnapshot.name} selected`; oldEditor.disabled = true; }
      if (newEditor) { newEditor.value = `Binary ${newSnapshot.name} selected`; newEditor.disabled = true; }
    }
    if (keyInput) keyInput.value = "id";
    if (toleranceInput) toleranceInput.value = "0";
    if (oldInput) oldInput.value = "";
    if (newInput) newInput.value = "";
    await compare();
  } catch (error) {
    setStatus(`${plainError(error instanceof Error ? error.message : String(error))} Reload while online and try again.`, "error");
  }
}

async function loadFile(input: HTMLInputElement, side: "old" | "new"): Promise<void> {
  const file = input.files?.[0];
  if (!file) return;
  const snapshot = { name: file.name, bytes: await file.arrayBuffer() };
  if (side === "old") oldSnapshot = snapshot; else newSnapshot = snapshot;
  const filename = byId(`${side}-file-name`);
  if (filename) filename.textContent = file.name;
  const editor = side === "old" ? oldEditor : newEditor;
  if (editor) {
    if (/\.csv$/i.test(file.name)) { editor.disabled = false; editor.value = await file.text(); }
    else { editor.disabled = true; editor.value = `Binary ${file.name} selected`; }
  }
  setStatus("Files ready. Confirm the primary key, then compare rows.");
}

function updateFromEditor(side: "old" | "new", editor: HTMLTextAreaElement): void {
  const snapshot = { name: `${side}-edited.csv`, bytes: encoder.encode(editor.value).buffer };
  if (side === "old") oldSnapshot = snapshot; else newSnapshot = snapshot;
  const input = side === "old" ? oldInput : newInput;
  if (input) input.value = "";
  const filename = byId(`${side}-file-name`);
  if (filename) filename.textContent = `${side}-edited.csv`;
  setStatus("CSV text changed. Compare rows to update the package output.");
}

if (oldInput && newInput && keyInput && compareButton && resultPanel && inDemo) {
  oldInput.addEventListener("change", () => void loadFile(oldInput, "old"));
  newInput.addEventListener("change", () => void loadFile(newInput, "new"));
  oldEditor?.addEventListener("input", () => updateFromEditor("old", oldEditor));
  newEditor?.addEventListener("input", () => updateFromEditor("new", newEditor));
  compareButton.addEventListener("click", () => void compare());
  byId<HTMLButtonElement>("sample-button")?.addEventListener("click", () => void loadSample());
  byId<HTMLButtonElement>("reset-demo")?.addEventListener("click", () => void loadSample("csv"));
  byId<HTMLAnchorElement>("start-real")?.addEventListener("click", () => {
    Object.keys(sessionStorage).filter((key) => key.startsWith("demo:")).forEach((key) => sessionStorage.removeItem(key));
  });
  void loadSample("csv");
}

byId<HTMLButtonElement>("copy-snippet")?.addEventListener("click", async (event) => {
  const button = event.currentTarget as HTMLButtonElement;
  const snippet = byId<HTMLElement>("python-snippet")?.textContent ?? "";
  try {
    await navigator.clipboard.writeText(snippet);
    button.textContent = "Copied Python snippet";
  } catch {
    setStatus("Copy was blocked. Select the Python snippet and copy it manually.", "error");
  }
});

downloadReport?.addEventListener("click", () => {
  if (!latestReport) return;
  const url = URL.createObjectURL(new Blob([latestReport], { type: "text/html" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "tdiff-report.html";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
});

const announcer = byId("route-announcer");
if (announcer) announcer.textContent = document.title;
const routeHeading = document.querySelector<HTMLElement>("main h1");
if (routeHeading) {
  routeHeading.tabIndex = -1;
  requestAnimationFrame(() => routeHeading.focus({ preventScroll: true }));
}
