/* The Python worker is deliberately outside the Vite bundle. It is loaded only
   on the demo route, and every runtime request stays on this origin. */
const RUNTIME_ROOT = "/playground/pyodide/";
const PACKAGE_WHEEL = "/playground/tabular_file_diff-0.1.0-py3-none-any.whl";
const RUNTIME_CACHE = "tdiff-shell-v5";
const RUNTIME_FILES = [
  "pyodide.js",
  "pyodide.asm.js",
  "pyodide.asm.wasm",
  "python_stdlib.zip",
  "pyodide-lock.json",
  "duckdb-1.1.2-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "numpy-2.0.2-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pandas-2.2.3-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pyarrow-18.1.0-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pyodide_unix_timezones-1.0.0-py3-none-any.whl",
  "python_dateutil-2.9.0.post0-py2.py3-none-any.whl",
  "pytz-2024.1-py2.py3-none-any.whl",
  "six-1.16.0-py2.py3-none-any.whl"
].map((name) => `${RUNTIME_ROOT}${name}`);

let runtimePromise;
let comparisonQueue = Promise.resolve();

const networkFetch = self.fetch.bind(self);
self.fetch = async (input, init) => {
  const request = new Request(input, init);
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) {
    return networkFetch(request);
  }
  const cached = await caches.match(request, { ignoreVary: true });
  if (cached) return cached;
  const response = await networkFetch(request);
  if (response.ok) {
    const cache = await caches.open(RUNTIME_CACHE);
    await cache.put(request, response.clone());
  }
  return response;
};

function progress(message) {
  self.postMessage({ type: "progress", message });
}

async function startRuntime() {
  progress("Loading local Python runtime…");
  self.importScripts(`${RUNTIME_ROOT}pyodide.js`);
  const runtime = await self.loadPyodide({ indexURL: RUNTIME_ROOT });
  progress("Loading local DuckDB and PyArrow…");
  await runtime.loadPackage(["duckdb", "pyarrow"]);
  progress("Loading the tabular-file-diff wheel…");
  await runtime.loadPackage(PACKAGE_WHEEL);
  const versions = JSON.parse(await runtime.runPythonAsync(`
import json
import duckdb
import pyarrow
import tabular_file_diff
json.dumps({
    "package": tabular_file_diff.__version__,
    "duckdb": duckdb.__version__,
    "pyarrow": pyarrow.__version__,
    "module": tabular_file_diff.__file__,
})
  `));
  progress("Saving the package for offline use…");
  const cache = await caches.open(RUNTIME_CACHE);
  await cache.addAll([...RUNTIME_FILES, PACKAGE_WHEEL]);
  self.postMessage({ type: "ready", versions });
  return runtime;
}

function runtime() {
  if (!runtimePromise) runtimePromise = startRuntime();
  return runtimePromise;
}

function safeName(prefix, name) {
  const lower = String(name).toLowerCase();
  const compound = lower.endsWith(".csv.gz") ? ".csv.gz" : "";
  const suffix = compound || (lower.match(/\.(csv|parquet|pq|arrow|ipc|feather)$/)?.[0] ?? ".data");
  return `/tmp/tdiff-playground-${prefix}${suffix}`;
}

async function compare(message) {
  const pyodide = await runtime();
  const oldPath = safeName("old", message.old.name);
  const newPath = safeName("new", message.new.name);
  const reportPath = "/tmp/tdiff-playground-report.html";
  pyodide.FS.writeFile(oldPath, new Uint8Array(message.old.bytes));
  pyodide.FS.writeFile(newPath, new Uint8Array(message.new.bytes));
  pyodide.globals.set("playground_old", oldPath);
  pyodide.globals.set("playground_new", newPath);
  pyodide.globals.set("playground_key", message.key);
  pyodide.globals.set("playground_tolerance", message.tolerance);
  pyodide.globals.set("playground_report", reportPath);
  try {
    return JSON.parse(await pyodide.runPythonAsync(`
import json
from pathlib import Path
from tabular_file_diff import diff_files
from tabular_file_diff.report import write_html

playground_result = diff_files(
    playground_old,
    playground_new,
    key=playground_key,
    tolerance=playground_tolerance,
    max_rows=8,
)
write_html(playground_result, playground_report)
json.dumps({
    "result": playground_result.to_dict(),
    "report": Path(playground_report).read_text(encoding="utf-8"),
}, default=str)
    `));
  } finally {
    for (const path of [oldPath, newPath, reportPath]) {
      try { pyodide.FS.unlink(path); } catch { /* already absent */ }
    }
  }
}

self.addEventListener("message", (event) => {
  if (event.data?.type !== "compare") return;
  comparisonQueue = comparisonQueue.then(async () => {
    try {
      const output = await compare(event.data);
      self.postMessage({ type: "result", id: event.data.id, ...output });
    } catch (error) {
      self.postMessage({
        type: "error",
        id: event.data.id,
        message: error instanceof Error ? error.message : String(error)
      });
    }
  });
});

void runtime().catch((error) => {
  self.postMessage({ type: "fatal", message: error instanceof Error ? error.message : String(error) });
});
