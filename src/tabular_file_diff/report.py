"""Self-contained HTML report rendering."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .core import DiffResult


def _value(value: Any) -> str:
    if value is None:
        return "NULL"
    return str(value)


def _table(title: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return f'<section><h2>{escape(title)}</h2><p class="empty">No rows in this group.</p></section>'
    columns = list(rows[0])
    head = "".join(f'<th scope="col">{escape(name)}</th>' for name in columns)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{escape(_value(row.get(name)))}</td>" for name in columns)
        + "</tr>"
        for row in rows
    )
    return (
        f'<section><h2>{escape(title)}</h2><div class="table-wrap"><table>'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>"
    )


def render_html(result: DiffResult) -> str:
    """Render a portable report with no external assets or scripts."""
    schema_items: list[str] = []
    schema_items.extend(
        f"Added <code>{escape(name)}</code> ({escape(kind)})"
        for name, kind in result.schema.added.items()
    )
    schema_items.extend(
        f"Removed <code>{escape(name)}</code> ({escape(kind)})"
        for name, kind in result.schema.removed.items()
    )
    schema_items.extend(
        f"Changed <code>{escape(name)}</code>: {escape(old)} → {escape(new)}"
        for name, (old, new) in result.schema.type_changed.items()
    )
    schema = (
        "".join(f"<li>{item}</li>" for item in schema_items) or "<li>No schema changes</li>"
    )
    columns = (
        "".join(
            f'<tr><th scope="row">{escape(name)}</th><td>{count:,}</td></tr>'
            for name, count in result.column_changes.items()
        )
        or '<tr><td colspan="2">No comparable value columns</td></tr>'
    )
    truncated = (
        '<p class="notice">Row tables are sampled; headline counts cover all rows.</p>'
        if result.tables_truncated
        else ""
    )
    status = "Differences found" if result.has_changes else "No differences"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(status)} · tabular-file-diff</title>
<style>
:root{{--night:#101a25;--surface:#172534;--paper:#f5ebd3;--muted:#c6bda8;--brass:#f2c14e;--coral:#ef6a57;--jade:#62c6a5;--sky:#72b6d9;--line:#425366}}*{{box-sizing:border-box}}body{{margin:0;background:var(--night);color:var(--paper);font:16px/1.55 system-ui,sans-serif}}main{{width:min(1120px,calc(100% - 32px));margin:auto;padding:56px 0 80px}}h1,h2{{font-family:"Arial Narrow",sans-serif;text-transform:uppercase;letter-spacing:.08em}}h1{{font-size:clamp(2.4rem,8vw,5.5rem);line-height:.9;margin:.2em 0}}h2{{margin-top:3rem;color:var(--brass)}}.eyebrow{{color:var(--brass);font-weight:800;letter-spacing:.16em}}.route{{color:var(--muted);overflow-wrap:anywhere}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);margin:40px 0}}.metric{{background:var(--surface);padding:24px}}.metric b{{display:block;font:700 2rem ui-monospace,monospace}}.add b{{color:var(--jade)}}.remove b{{color:var(--coral)}}.modify b{{color:var(--sky)}}.notice{{border-left:4px solid var(--brass);padding:12px 16px;background:var(--surface)}}.table-wrap{{overflow:auto;border:1px solid var(--line)}}table{{border-collapse:collapse;width:100%;font:14px/1.45 ui-monospace,monospace;font-variant-numeric:tabular-nums}}th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}}th{{color:var(--brass)}}code{{color:var(--jade)}}.empty{{color:var(--muted)}}@media(max-width:650px){{main{{padding-top:32px}}.metrics{{grid-template-columns:1fr 1fr}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
</style></head><body><main><p class="eyebrow">Tabular file diff / offline report</p><h1>{escape(status)}</h1>
<p class="route">{escape(result.old_path)} → {escape(result.new_path)}<br>Key: {escape(", ".join(result.keys))}</p>
<div class="metrics"><div class="metric add">Added<b>{result.added_count:,}</b></div><div class="metric remove">Removed<b>{result.removed_count:,}</b></div><div class="metric modify">Modified<b>{result.modified_count:,}</b></div><div class="metric">Unchanged<b>{result.unchanged_count:,}</b></div></div>
{truncated}<section><h2>Schema</h2><ul>{schema}</ul></section><section><h2>Changes by column</h2><table><tbody>{columns}</tbody></table></section>
{_table("Added rows", result.added.to_pylist())}{_table("Removed rows", result.removed.to_pylist())}{_table("Modified rows", result.modified.to_pylist())}
</main></body></html>"""


def write_html(result: DiffResult, path: str | Path) -> Path:
    """Write a self-contained UTF-8 report."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(result), encoding="utf-8")
    return output
