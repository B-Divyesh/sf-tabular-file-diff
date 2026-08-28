import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "node_modules/pyodide");
const destination = resolve(root, "site/public/playground/pyodide");
const vendored = resolve(root, "vendor/pyodide-packages");

await mkdir(destination, { recursive: true });
const lock = JSON.parse(await readFile(resolve(source, "pyodide-lock.json"), "utf8"));
for (const name of [
  "pyodide.js",
  "pyodide.asm.js",
  "pyodide.asm.wasm",
  "python_stdlib.zip",
  "pyodide-lock.json"
]) {
  await copyFile(resolve(source, name), resolve(destination, name));
}

for (const name of [
  "duckdb-1.1.2-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "numpy-2.0.2-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pandas-2.2.3-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pyarrow-18.1.0-cp312-cp312-pyodide_2024_0_wasm32.whl",
  "pyodide_unix_timezones-1.0.0-py3-none-any.whl",
  "python_dateutil-2.9.0.post0-py2.py3-none-any.whl",
  "pytz-2024.1-py2.py3-none-any.whl",
  "six-1.16.0-py2.py3-none-any.whl"
]) {
  const input = resolve(vendored, name);
  const bytes = await readFile(input);
  const packageName = Object.keys(lock.packages).find((key) => lock.packages[key].file_name === name);
  if (!packageName || createHash("sha256").update(bytes).digest("hex") !== lock.packages[packageName].sha256) {
    throw new Error(`Vendored Pyodide package failed its lock-file hash: ${name}`);
  }
  await copyFile(input, resolve(destination, name));
}
