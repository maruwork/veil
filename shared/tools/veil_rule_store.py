#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")
DEFAULT_DB_PATH = os.path.join(CONFIG_DIR, "veil.db")

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
    for raw in re.split(r"[、,]", rhs):
        cleaned = re.sub(r"[（(]候補\d+[)）]", "", raw).strip()
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
            "reason": "rules directory が見つかりません。",
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
            warnings.append({"file": fname, "line": 0, "warning": f"読み込み失敗: {exc}"})
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
                            "warning": "rule 行として解釈できないため無視した",
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
                        "warning": "original または preferred が空のため無視した",
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
        for entry in parsed["rules"]:
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
    payload["imported_count"] = len(parsed["rules"])
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
            "reason": "term_original または preferred が空です。",
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
            "reason": "db file が見つかりません。",
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
        source_context = row.get("source_context") or db_path
        source_file = source_context.split(":", 1)[0] if ":" in source_context else source_context
        normalized = row["term_normalized"]
        if normalized not in index:
            index[normalized] = {
                "original": row["term_original"],
                "preferred": row["preferred"],
                "source_file": source_file,
            }
    return index, []


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
    ]
