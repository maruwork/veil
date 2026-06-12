#!/usr/bin/env python3
from __future__ import annotations

import html as _html
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")
DEFAULT_DB_PATH = os.path.join(CONFIG_DIR, "veil.db")
DEFAULT_HTML_PATH = os.path.join(CONFIG_DIR, "veil.html")

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="__UI_LANG__">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__UI_TITLE__</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    background: #ffffff;
    color: #1a1a1a;
    padding: 32px 24px;
  }
  header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 32px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 16px;
  }
  header h1 { font-size: 18px; font-weight: 600; letter-spacing: 0.08em; color: #000; }
  header span { font-size: 12px; color: #666; }
  .search-bar { margin-bottom: 24px; }
  .search-bar input {
    width: 100%;
    max-width: 360px;
    padding: 8px 12px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 6px;
    color: #1a1a1a;
    font-size: 13px;
    outline: none;
  }
  .search-bar input:focus { border-color: #aaa; }
  .search-bar input::placeholder { color: #bbb; }
  table { width: 100%; max-width: 900px; border-collapse: collapse; }
  thead th {
    text-align: left;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.06em;
    color: #666;
    text-transform: uppercase;
    border-bottom: 1px solid #e0e0e0;
  }
  tbody tr { border-bottom: 1px solid #f0f0f0; transition: background 0.1s; }
  tbody tr:hover { background: #f8f8f8; }
  td { padding: 10px 12px; vertical-align: middle; }
  .term { font-family: "SFMono-Regular", Consolas, monospace; font-size: 13px; color: #2563eb; }
  .section-label {
    display: inline-block;
    width: 20px;
    font-size: 11px;
    font-weight: 600;
    color: #444;
    text-transform: uppercase;
    margin-right: 4px;
  }
  .cell { display: flex; align-items: center; gap: 8px; }
  .preferred { font-weight: 500; color: #1a1a1a; }
  .alt { color: #555; font-size: 13px; }
  .copy-btn {
    flex-shrink: 0;
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px 4px;
    border-radius: 3px;
    color: #444;
    font-size: 11px;
    line-height: 1;
    transition: color 0.1s, background 0.1s;
    opacity: 0;
  }
  tr:hover .copy-btn { opacity: 1; }
  .copy-btn:hover { color: #555; background: #ebebeb; }
  .copy-btn.copied { color: #6dbf7a; opacity: 1; }
  .hidden { display: none; }
</style>
</head>
<body>
<header>
  <h1>VEIL</h1>
  <span id="count">__UI_COUNT_INIT__</span>
</header>
<div class="search-bar">
  <input type="text" id="search" placeholder="__UI_SEARCH_PLACEHOLDER__" oninput="filterRows()">
</div>
<p style="font-size:13px;color:#666;margin-bottom:16px;">__UI_INSTRUCTION__</p>
<table>
  <thead>
    <tr>
      <th style="width:220px">__UI_COL_TERM__</th>
      <th style="width:220px">__UI_COL_PREFERRED__</th>
      <th style="width:220px">__UI_COL_ALT2__</th>
      <th>__UI_COL_ALT3__</th>
    </tr>
  </thead>
  <tbody id="tbody">
__ROWS__
  </tbody>
</table>
<script>
  const _copyInstruction = "__UI_COPY_INSTRUCTION__";
  const _copyBtn = "__UI_COPY_BTN__";
  const _copyDone = "__UI_COPY_DONE__";
  const _countRegistered = "__UI_COUNT_REGISTERED__";
  const _countMatching = "__UI_COUNT_MATCHING__";

  function copy(btn) {
    const term = btn.dataset.term;
    const candidate = btn.dataset.alt;
    const text = _copyInstruction.replace('{term}', term).replace('{candidate}', candidate);
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = _copyDone;
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = _copyBtn;
        btn.classList.remove('copied');
      }, 1500);
    });
  }
  function filterRows() {
    const q = document.getElementById('search').value.toLowerCase();
    const rows = document.querySelectorAll('#tbody tr');
    let visible = 0;
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      if (!q || text.includes(q)) {
        row.classList.remove('hidden');
        visible++;
      } else {
        row.classList.add('hidden');
      }
    });
    document.getElementById('count').textContent =
      (q ? _countMatching : _countRegistered).replace('{n}', visible);
  }
</script>
</body>
</html>
"""

_HTML_UI_EN: dict[str, str] = {
    "lang": "en",
    "title": "VEIL — Vocabulary Rules",
    "search_placeholder": "Search terms...",
    "instruction": "To change the preferred form of a registered term, click Copy on a candidate cell and paste into the AI chat.",
    "col_term": "Term",
    "col_preferred": "Preferred (candidate 1)",
    "col_alt2": "Candidate 2",
    "col_alt3": "Candidate 3",
    "copy_btn": "Copy",
    "copy_done": "✓",
    "count_registered": "{n} terms registered",
    "count_matching": "{n} terms matching",
    "copy_instruction": "Change '{term}' to '{candidate}'",
}

RULE_LINE_RE = re.compile(r"^\s*-\s*(?P<original>.+?)\s*(?:→|->)\s*(?P<preferred>.+?)\s*$")
LEADING_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_original TEXT NOT NULL,
    term_normalized TEXT NOT NULL,
    preferred TEXT NOT NULL,
    preferred_alt_2 TEXT,
    preferred_alt_3 TEXT,
    status TEXT NOT NULL,
    category_hint TEXT,
    note TEXT,
    source_context TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rules_term_normalized ON rules(term_normalized);
"""


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def first_preferred(rhs: str) -> str:
    return parse_preferred_variants(rhs)[0] or ""


def parse_preferred_variants(rhs: str) -> tuple[str | None, str | None, str | None]:
    parts = []
    for raw in re.split(r"[、,|]", rhs):
        cleaned = re.sub(r"[（(](?:候補\d+|keep)[)）]", "", raw).strip()
        if cleaned:
            parts.append(cleaned)
    while len(parts) < 3:
        parts.append(None)
    return parts[0], parts[1], parts[2]


def simple_singularize_token(token: str) -> str:
    if len(token) <= 3:
        return token
    if token.endswith("yses") and len(token) > 5:
        return token[:-4] + "ysis"
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if re.search(r"(ches|shes|xes|zes|sses)$", token):
        return token[:-2]
    if token.endswith("ses") and token[:-2].endswith("s"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s") and not token.endswith(("ss", "is", "us", "as", "os", "ews")):
        return token[:-1]
    return token


def normalize_term(term: str) -> str:
    term = LEADING_BULLET_RE.sub("", term.strip())
    term = re.sub(r"[\-_]+", " ", term.lower())
    term = re.sub(r"\s+", " ", term).strip()
    tokens = [simple_singularize_token(tok) for tok in term.split(" ") if tok]
    return " ".join(tokens)


def load_rules_from_markdown_dir(rules_dir: str) -> dict[str, object]:
    if not os.path.isdir(rules_dir):
        return {
            "status": "skip",
            "reason": "store.no_rules_dir",
            "rules_dir": rules_dir,
            "files_seen": 0,
            "rules": [],
            "conflicts": [],
            "warnings": [],
        }

    rules: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    selected_by_normalized: dict[str, dict[str, object]] = {}
    conflicts_by_key: dict[str, list[dict[str, object]]] = defaultdict(list)
    files_seen = 0

    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        files_seen += 1
        path = os.path.join(rules_dir, fname)
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.readlines()
        except OSError as exc:
            warnings.append({"file": fname, "line": 0, "warning_key": "store.load_failed", "warning_args": {"exc": str(exc)}})
            continue

        for line_no, line in enumerate(lines, start=1):
            match = RULE_LINE_RE.match(line)
            stripped = line.strip()
            if not match:
                if stripped.startswith("-"):
                    warnings.append(
                        {
                            "file": fname,
                            "line": line_no,
                            "warning_key": "store.rule_parse_ignored",
                            "content": stripped,
                        }
                    )
                continue

            original = match.group("original").strip()
            preferred, preferred_alt_2, preferred_alt_3 = parse_preferred_variants(match.group("preferred"))
            if not original or not preferred:
                warnings.append(
                    {
                        "file": fname,
                        "line": line_no,
                        "warning_key": "store.empty_original_or_preferred",
                    }
                )
                continue

            normalized = normalize_term(original)
            entry = {
                "term_original": original,
                "term_normalized": normalized,
                "preferred": preferred,
                "preferred_alt_2": preferred_alt_2,
                "preferred_alt_3": preferred_alt_3,
                "status": "active",
                "category_hint": None,
                "note": None,
                "source_context": f"{fname}:{line_no}",
                "source_file": fname,
                "source_line": line_no,
            }
            rules.append(entry)

            if normalized not in selected_by_normalized:
                selected_by_normalized[normalized] = entry
            else:
                selected = selected_by_normalized[normalized]
                if (
                    selected["term_original"] != entry["term_original"]
                    or selected["preferred"] != entry["preferred"]
                ):
                    conflicts_by_key[normalized].append(entry)

    conflicts = []
    for normalized, ignored in conflicts_by_key.items():
        conflicts.append(
            {
                "normalized": normalized,
                "selected": selected_by_normalized[normalized],
                "ignored": ignored,
            }
        )

    return {
        "status": "ok",
        "rules_dir": rules_dir,
        "files_seen": files_seen,
        "rules": rules,
        "selected_rules": list(selected_by_normalized.values()),
        "conflicts": conflicts,
        "warnings": warnings,
    }


def ensure_db_parent(db_path: str) -> None:
    parent = os.path.dirname(os.path.abspath(db_path))
    if parent:
        os.makedirs(parent, exist_ok=True)


def open_db(db_path: str) -> sqlite3.Connection:
    ensure_db_parent(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with open_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


def replace_rules_from_markdown(db_path: str, rules_dir: str) -> dict[str, object]:
    parsed = load_rules_from_markdown_dir(rules_dir)
    if parsed["status"] != "ok":
        return parsed

    init_db(db_path)
    imported_at = now_utc_iso()
    with open_db(db_path) as conn:
        conn.execute("DELETE FROM rules")
        for entry in parsed["selected_rules"]:
            conn.execute(
                """
                INSERT INTO rules (
                    term_original,
                    term_normalized,
                    preferred,
                    preferred_alt_2,
                    preferred_alt_3,
                    status,
                    category_hint,
                    note,
                    source_context,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["term_original"],
                    entry["term_normalized"],
                    entry["preferred"],
                    entry["preferred_alt_2"],
                    entry["preferred_alt_3"],
                    entry["status"],
                    entry["category_hint"],
                    entry["note"],
                    entry["source_context"],
                    imported_at,
                    imported_at,
                ),
            )
        conn.commit()

    payload = dict(parsed)
    payload["db_path"] = db_path
    payload["imported_count"] = len(parsed["selected_rules"])
    return payload


def choose_mirror_filename(term_original: str) -> str:
    stripped = term_original.strip()
    if stripped:
        first = stripped[0].lower()
        if "a" <= first <= "z":
            return f"{first}.md"
    return "special.md"


def upsert_rule(
    db_path: str,
    term_original: str,
    preferred: str,
    preferred_alt_2: str | None = None,
    preferred_alt_3: str | None = None,
    status: str = "active",
    category_hint: str | None = None,
    note: str | None = None,
    source_context: str | None = None,
) -> dict[str, object]:
    original = term_original.strip()
    preferred_1 = preferred.strip()
    if not original or not preferred_1:
        return {
            "status": "skip",
            "reason": "store.empty_term",
            "db_path": db_path,
        }

    normalized = normalize_term(original)
    now = now_utc_iso()
    init_db(db_path)
    with open_db(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, created_at
            FROM rules
            WHERE term_normalized = ?
            ORDER BY id
            LIMIT 1
            """,
            (normalized,),
        ).fetchone()
        if row:
            conn.execute(
                """
                UPDATE rules
                SET
                    term_original = ?,
                    preferred = ?,
                    preferred_alt_2 = ?,
                    preferred_alt_3 = ?,
                    status = ?,
                    category_hint = ?,
                    note = ?,
                    source_context = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    original,
                    preferred_1,
                    preferred_alt_2,
                    preferred_alt_3,
                    status,
                    category_hint,
                    note,
                    source_context,
                    now,
                    row["id"],
                ),
            )
            rule_id = row["id"]
            action = "updated"
            created_at = row["created_at"]
        else:
            cursor = conn.execute(
                """
                INSERT INTO rules (
                    term_original,
                    term_normalized,
                    preferred,
                    preferred_alt_2,
                    preferred_alt_3,
                    status,
                    category_hint,
                    note,
                    source_context,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    original,
                    normalized,
                    preferred_1,
                    preferred_alt_2,
                    preferred_alt_3,
                    status,
                    category_hint,
                    note,
                    source_context,
                    now,
                    now,
                ),
            )
            rule_id = cursor.lastrowid
            action = "inserted"
            created_at = now
        conn.commit()

    return {
        "status": "ok",
        "db_path": db_path,
        "action": action,
        "row": {
            "id": rule_id,
            "term_original": original,
            "term_normalized": normalized,
            "preferred": preferred_1,
            "preferred_alt_2": preferred_alt_2,
            "preferred_alt_3": preferred_alt_3,
            "status": status,
            "category_hint": category_hint,
            "note": note,
            "source_context": source_context,
            "created_at": created_at,
            "updated_at": now,
        },
    }


def readback_rules(db_path: str) -> dict[str, object]:
    if not os.path.exists(db_path):
        return {
            "status": "skip",
            "reason": "store.no_db_file",
            "db_path": db_path,
            "summary": {"total": 0},
            "rows": [],
        }

    init_db(db_path)
    query = """
        SELECT
            id,
            term_original,
            term_normalized,
            preferred,
            preferred_alt_2,
            preferred_alt_3,
            status,
            category_hint,
            note,
            source_context,
            created_at,
            updated_at
        FROM rules
        ORDER BY term_normalized, id
    """

    with open_db(db_path) as conn:
        rows = [dict(row) for row in conn.execute(query).fetchall()]
        summary = {
            "total": conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0],
        }

    return {
        "status": "ok",
        "db_path": db_path,
        "summary": summary,
        "rows": rows,
    }


def render_markdown_mirror_from_rows(rows: list[dict[str, object]]) -> dict[str, str]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "active":
            continue
        grouped[choose_mirror_filename(str(row["term_original"]))].append(row)

    rendered: dict[str, str] = {}
    for filename, entries in grouped.items():
        title = Path(filename).stem
        parts = [f"# {title}", ""]
        entries_sorted = sorted(
            entries,
            key=lambda r: (str(r["term_normalized"]), str(r["term_original"]).lower(), int(r["id"])),
        )
        for row in entries_sorted:
            preferreds = [row["preferred"], row.get("preferred_alt_2"), row.get("preferred_alt_3")]
            preferred_text = "、".join([str(item).strip() for item in preferreds if item and str(item).strip()])
            parts.append(f"- {row['term_original']} → {preferred_text}")
        rendered[filename] = "\n".join(parts).rstrip() + "\n"
    return rendered


def export_markdown_mirror_from_db(db_path: str, rules_dir: str) -> dict[str, object]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return {
            "status": payload["status"],
            "reason": payload.get("reason"),
            "db_path": db_path,
            "rules_dir": rules_dir,
            "written_files": [],
            "removed_files": [],
        }

    os.makedirs(rules_dir, exist_ok=True)
    existing_files = {name for name in os.listdir(rules_dir) if name.endswith(".md")}
    rendered = render_markdown_mirror_from_rows(payload["rows"])
    removed_files: list[str] = []
    for stale in sorted(existing_files - set(rendered.keys())):
        os.remove(os.path.join(rules_dir, stale))
        removed_files.append(stale)

    written_files: list[str] = []
    for filename, content in sorted(rendered.items()):
        path = os.path.join(rules_dir, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        written_files.append(filename)

    return {
        "status": "ok",
        "db_path": db_path,
        "rules_dir": rules_dir,
        "written_files": written_files,
        "removed_files": removed_files,
        "row_count": len(payload["rows"]),
    }


def load_rule_index_from_db(db_path: str) -> tuple[dict[str, dict[str, str]], list[dict[str, object]]]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return {}, []

    index: dict[str, dict[str, str]] = {}
    for row in payload["rows"]:
        if row.get("status") != "active":
            continue
        source_context = row.get("source_context") or db_path
        if ":" in source_context:
            left, right = source_context.split(":", 1)
            # Single letter before ":" = Windows drive letter, not file:line
            source_file = left if (right.isdigit() and len(left) > 1) else source_context
        else:
            source_file = source_context
        normalized = row["term_normalized"]
        if normalized not in index:
            index[normalized] = {
                "original": row["term_original"],
                "preferred": row["preferred"],
                "source_file": source_file,
            }
    return index, []


def _render_alt_cell(term: str, alt: str | None, copy_btn: str = "Copy") -> str:
    if not alt or not str(alt).strip():
        return ""
    return (
        f'<div class="cell">'
        f'<span class="alt">{_html.escape(str(alt))}</span>'
        f'<button class="copy-btn" data-term="{_html.escape(term)}" data-alt="{_html.escape(str(alt))}" onclick="copy(this)">{_html.escape(copy_btn)}</button>'
        f'</div>'
    )


def _build_html_content(rows_html: str, count: int, ui: dict[str, str]) -> str:
    import json as _json

    def js(key: str, default: str) -> str:
        return _json.dumps(ui.get(key, default), ensure_ascii=False)[1:-1]

    def h(key: str, default: str) -> str:
        return _html.escape(ui.get(key, default))

    count_init = ui.get("count_registered", "{n} terms registered").replace("{n}", str(count))
    content = _HTML_TEMPLATE
    content = content.replace("__UI_LANG__", h("lang", "en"))
    content = content.replace("__UI_TITLE__", h("title", "VEIL — Vocabulary Rules"))
    content = content.replace("__UI_COUNT_INIT__", _html.escape(count_init))
    content = content.replace("__UI_SEARCH_PLACEHOLDER__", h("search_placeholder", "Search terms..."))
    content = content.replace("__UI_INSTRUCTION__", h("instruction", "To change the preferred form, click Copy and paste into the AI chat."))
    content = content.replace("__UI_COL_TERM__", h("col_term", "Term"))
    content = content.replace("__UI_COL_PREFERRED__", h("col_preferred", "Preferred (candidate 1)"))
    content = content.replace("__UI_COL_ALT2__", h("col_alt2", "Candidate 2"))
    content = content.replace("__UI_COL_ALT3__", h("col_alt3", "Candidate 3"))
    content = content.replace("__UI_COPY_INSTRUCTION__", js("copy_instruction", "Change '{term}' to '{candidate}'"))
    content = content.replace("__UI_COPY_BTN__", js("copy_btn", "Copy"))
    content = content.replace("__UI_COPY_DONE__", js("copy_done", "✓"))
    content = content.replace("__UI_COUNT_REGISTERED__", js("count_registered", "{n} terms registered"))
    content = content.replace("__UI_COUNT_MATCHING__", js("count_matching", "{n} terms matching"))
    content = content.replace("__ROWS__", rows_html)
    return content


def export_html_from_db(db_path: str, html_path: str, ui: dict[str, str] | None = None) -> dict[str, object]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return {
            "status": payload["status"],
            "reason": payload.get("reason"),
            "db_path": db_path,
            "html_path": html_path,
        }

    resolved_ui = ui if ui is not None else _HTML_UI_EN
    copy_btn = resolved_ui.get("copy_btn", "Copy")

    active_rows = [r for r in payload["rows"] if r.get("status") == "active"]  # type: ignore[union-attr]
    rows_sorted = sorted(
        active_rows,
        key=lambda r: (str(r["term_normalized"]), str(r["term_original"]).lower()),
    )

    row_parts: list[str] = []
    for row in rows_sorted:
        term = str(row["term_original"])
        preferred = str(row["preferred"])
        alt2 = row.get("preferred_alt_2")
        alt3 = row.get("preferred_alt_3")
        first_char = term[0] if term else "?"
        section = first_char.upper() if first_char.isalpha() else "?"
        row_parts.append(
            f"    <tr>\n"
            f"      <td><span class=\"section-label\">{_html.escape(section)}</span>"
            f"<span class=\"term\">{_html.escape(term)}</span></td>\n"
            f"      <td><span class=\"preferred\">{_html.escape(preferred)}</span></td>\n"
            f"      <td>{_render_alt_cell(term, str(alt2) if alt2 else None, copy_btn)}</td>\n"
            f"      <td>{_render_alt_cell(term, str(alt3) if alt3 else None, copy_btn)}</td>\n"
            f"    </tr>"
        )

    count = len(rows_sorted)
    content = _build_html_content("\n".join(row_parts), count, resolved_ui)

    os.makedirs(os.path.dirname(os.path.abspath(html_path)), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    return {
        "status": "ok",
        "db_path": db_path,
        "html_path": html_path,
        "row_count": count,
    }


def load_rules_for_lint_from_db(db_path: str) -> list[dict[str, str]]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return []

    return [
        {
            "original": row["term_original"],
            "preferred": row["preferred"],
        }
        for row in payload["rows"]
        if row.get("status") == "active"
    ]
