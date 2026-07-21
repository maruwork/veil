#!/usr/bin/env python3
from __future__ import annotations

from contextlib import closing
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from shared.tools.veil_capture_taxonomy import capture_taxonomy_payload
    from shared.tools.veil_delivery_freshness import render_with_manifest
    from shared.tools.veil_html_review import render_review_html
    from shared.tools.veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG, get_html_ui_for_lang
except ModuleNotFoundError:
    from veil_capture_taxonomy import capture_taxonomy_payload  # type: ignore[no-redef]
    from veil_delivery_freshness import render_with_manifest  # type: ignore[no-redef]
    from veil_html_review import render_review_html  # type: ignore[no-redef]
    from veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG, get_html_ui_for_lang  # type: ignore[no-redef]

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_DB_PATH = os.path.join(CONFIG_DIR, "veil.db")
DEFAULT_HTML_PATH = os.path.join(CONFIG_DIR, "veil.html")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLED_PROFILE_SEED_PATH = str(REPO_ROOT / "shared" / "default-profile" / "technical-writing-default.json")
DB_CLI_PATH = (REPO_ROOT / "shared" / "tools" / "veil-db.py").as_posix()
PROTECTED_REPO_DIR_NAMES = ("common", "archive")
PROTECTED_REPO_DIRS = tuple((REPO_ROOT / name).resolve() for name in PROTECTED_REPO_DIR_NAMES)


RULE_LINE_RE = re.compile(r"^\s*-\s*(?P<original>.+?)\s*(?:->|→)\s*(?P<preferred>.+?)\s*$")
LEADING_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
LEVEL_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s*(?P<level>required|recommended|observe|必須|推奨|観察)\s*$",
    re.IGNORECASE,
)

PROFILE_LEVEL_REQUIRED = "required"
PROFILE_LEVEL_RECOMMENDED = "recommended"
PROFILE_LEVEL_OBSERVE = "observe"
PROFILE_LEVEL_DEFAULT = PROFILE_LEVEL_REQUIRED
PROFILE_LEVELS = (
    PROFILE_LEVEL_REQUIRED,
    PROFILE_LEVEL_RECOMMENDED,
    PROFILE_LEVEL_OBSERVE,
)
PROFILE_LEVEL_TO_HEADING = {
    PROFILE_LEVEL_REQUIRED: "Required",
    PROFILE_LEVEL_RECOMMENDED: "Recommended",
    PROFILE_LEVEL_OBSERVE: "Observe",
}
PROFILE_LEVEL_ALIASES = {
    "required": PROFILE_LEVEL_REQUIRED,
    "require": PROFILE_LEVEL_REQUIRED,
    "must": PROFILE_LEVEL_REQUIRED,
    "mandatory": PROFILE_LEVEL_REQUIRED,
    "必須": PROFILE_LEVEL_REQUIRED,
    "recommended": PROFILE_LEVEL_RECOMMENDED,
    "recommend": PROFILE_LEVEL_RECOMMENDED,
    "should": PROFILE_LEVEL_RECOMMENDED,
    "推奨": PROFILE_LEVEL_RECOMMENDED,
    "observe": PROFILE_LEVEL_OBSERVE,
    "observation": PROFILE_LEVEL_OBSERVE,
    "watch": PROFILE_LEVEL_OBSERVE,
    "観察": PROFILE_LEVEL_OBSERVE,
}
HEADING_TO_PROFILE_LEVEL = {heading: level for level, heading in PROFILE_LEVEL_TO_HEADING.items()}
HEADING_TO_PROFILE_LEVEL.update(
    {
        "required": PROFILE_LEVEL_REQUIRED,
        "recommended": PROFILE_LEVEL_RECOMMENDED,
        "observe": PROFILE_LEVEL_OBSERVE,
    }
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_original TEXT NOT NULL,
    term_normalized TEXT NOT NULL UNIQUE,
    preferred TEXT NOT NULL,
    preferred_alt_2 TEXT,
    preferred_alt_3 TEXT,
    status TEXT NOT NULL,
    profile_level TEXT NOT NULL DEFAULT 'required',
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
    for raw in re.split(r"\s*(?:\||｜)\s*", rhs):
        cleaned = re.sub(
            r"^[\[(]?\s*(?:candidate\s*\d+|keep(?:\s+current)?)\s*[\])]?[:.\-]?\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        ).strip()
        if cleaned:
            parts.append(cleaned)
    while len(parts) < 3:
        parts.append(None)
    return parts[0], parts[1], parts[2]


def canonicalize_profile_level(level: str | None, default: str | None = PROFILE_LEVEL_DEFAULT) -> str | None:
    normalized = (level or "").strip().lower()
    if not normalized:
        return default
    return PROFILE_LEVEL_ALIASES.get(normalized, default)


def profile_level_heading(level: str | None) -> str:
    canonical = canonicalize_profile_level(level) or PROFILE_LEVEL_DEFAULT
    return PROFILE_LEVEL_TO_HEADING.get(canonical, PROFILE_LEVEL_TO_HEADING[PROFILE_LEVEL_DEFAULT])


def empty_profile_level_counts() -> dict[str, int]:
    return {
        "required_count": 0,
        "recommended_count": 0,
        "observe_count": 0,
        "legacy_flat_count": 0,
        "total_rules": 0,
    }


def add_profile_level_count(counts: dict[str, int], level: str | None, legacy_flat: bool = False) -> None:
    counts["total_rules"] += 1
    canonical = canonicalize_profile_level(level) or PROFILE_LEVEL_DEFAULT
    if canonical == PROFILE_LEVEL_RECOMMENDED:
        counts["recommended_count"] += 1
    elif canonical == PROFILE_LEVEL_OBSERVE:
        counts["observe_count"] += 1
    else:
        counts["required_count"] += 1
    if legacy_flat:
        counts["legacy_flat_count"] += 1


def get_protected_repo_dir_name(path: str) -> str | None:
    candidate = Path(path).resolve(strict=False)
    for protected_root in PROTECTED_REPO_DIRS:
        try:
            candidate.relative_to(protected_root)
            return protected_root.name
        except ValueError:
            continue
    return None


def build_protected_output_payload(path_key: str, path: str) -> dict[str, Any]:
    return {
        "status": "error",
        "reason": "store.protected_output_path",
        path_key: path,
        "protected_root": get_protected_repo_dir_name(path),
        "error": path,
    }


def db_error_payload(db_path: str, exc: sqlite3.Error) -> dict[str, Any]:
    return {
        "status": "error",
        "reason": "store.db_unreadable",
        "db_path": db_path,
        "summary": {"total": 0},
        "rows": [],
        "error": str(exc),
    }


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


def load_rules_from_seed_file(seed_path: str) -> dict[str, Any]:
    if not os.path.exists(seed_path):
        return {
            "status": "skip",
            "reason": "store.no_seed_file",
            "seed_file": seed_path,
            "files_seen": 0,
            "rules": [],
            "selected_rules": [],
            "conflicts": [],
            "warnings": [],
        }

    try:
        with open(seed_path, encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "error",
            "reason": "store.seed_unreadable",
            "seed_file": seed_path,
            "files_seen": 1,
            "rules": [],
            "selected_rules": [],
            "conflicts": [],
            "warnings": [],
            "error": str(exc),
        }

    raw_rules = raw.get("rules") if isinstance(raw, dict) else raw
    if not isinstance(raw_rules, list):
        return {
            "status": "error",
            "reason": "store.seed_invalid_format",
            "seed_file": seed_path,
            "files_seen": 1,
            "rules": [],
            "selected_rules": [],
            "conflicts": [],
            "warnings": [],
        }

    rules: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    selected_by_normalized: dict[str, dict[str, Any]] = {}
    conflicts_by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_name = os.path.basename(seed_path)

    for idx, raw_entry in enumerate(raw_rules, start=1):
        if not isinstance(raw_entry, dict):
            warnings.append(
                {
                    "file": source_name,
                    "line": idx,
                    "warning_key": "store.seed_entry_ignored",
                }
            )
            continue

        original = str(raw_entry.get("term_original") or raw_entry.get("term") or "").strip()
        preferred = str(raw_entry.get("preferred") or "").strip()
        if not original or not preferred:
            warnings.append(
                {
                    "file": source_name,
                    "line": idx,
                    "warning_key": "store.empty_original_or_preferred",
                }
            )
            continue

        normalized = normalize_term(original)
        entry = {
            "term_original": original,
            "term_normalized": normalized,
            "preferred": preferred,
            "preferred_alt_2": raw_entry.get("preferred_alt_2"),
            "preferred_alt_3": raw_entry.get("preferred_alt_3"),
            "status": str(raw_entry.get("status") or "active"),
            "profile_level": canonicalize_profile_level(str(raw_entry.get("profile_level") or PROFILE_LEVEL_DEFAULT))
            or PROFILE_LEVEL_DEFAULT,
            "category_hint": raw_entry.get("category_hint"),
            "note": raw_entry.get("note"),
            "source_context": str(raw_entry.get("source_context") or f"{source_name}:{idx}"),
            "source_file": source_name,
            "source_line": idx,
            "legacy_flat": False,
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
        "seed_file": seed_path,
        "files_seen": 1,
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


def open_db_readonly(db_path: str) -> sqlite3.Connection:
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    existing = {
        str(row["name"])
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _existing_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {
        str(row["name"])
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }


def init_db(db_path: str) -> None:
    if get_protected_repo_dir_name(db_path) is not None:
        raise ValueError(f"store.protected_output_path:{db_path}")
    with closing(open_db(db_path)) as conn:
        conn.executescript(SCHEMA_SQL)
        _ensure_column(conn, "rules", "profile_level", "TEXT NOT NULL DEFAULT 'required'")
        conn.commit()


def replace_rules_from_seed(db_path: str, seed_file: str) -> dict[str, Any]:
    if get_protected_repo_dir_name(db_path) is not None:
        return build_protected_output_payload("db_path", db_path)
    parsed = load_rules_from_seed_file(seed_file)
    if parsed["status"] != "ok":
        return parsed

    imported_at = now_utc_iso()
    try:
        init_db(db_path)
        with closing(open_db(db_path)) as conn:
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
                        profile_level,
                        category_hint,
                        note,
                        source_context,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry["term_original"],
                        entry["term_normalized"],
                        entry["preferred"],
                        entry["preferred_alt_2"],
                        entry["preferred_alt_3"],
                        entry["status"],
                        entry["profile_level"],
                        entry["category_hint"],
                        entry["note"],
                        entry["source_context"],
                        imported_at,
                        imported_at,
                    ),
                )
            conn.commit()
    except sqlite3.Error as exc:
        return db_error_payload(db_path, exc)

    payload = dict(parsed)
    payload["db_path"] = db_path
    payload["imported_count"] = len(parsed["selected_rules"])
    return payload


def upsert_rule(
    db_path: str,
    term_original: str,
    preferred: str,
    preferred_alt_2: str | None = None,
    preferred_alt_3: str | None = None,
    status: str = "active",
    profile_level: str = PROFILE_LEVEL_DEFAULT,
    category_hint: str | None = None,
    note: str | None = None,
    source_context: str | None = None,
) -> dict[str, Any]:
    if get_protected_repo_dir_name(db_path) is not None:
        return build_protected_output_payload("db_path", db_path)
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
    canonical_level = canonicalize_profile_level(profile_level, default=None)
    if canonical_level is None:
        return {
            "status": "error",
            "reason": "store.invalid_profile_level",
            "db_path": db_path,
            "input_level": profile_level,
        }
    try:
        init_db(db_path)
        with closing(open_db(db_path)) as conn:
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
                        profile_level = ?,
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
                        canonical_level,
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
                        profile_level,
                        category_hint,
                        note,
                        source_context,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        original,
                        normalized,
                        preferred_1,
                        preferred_alt_2,
                        preferred_alt_3,
                        status,
                        canonical_level,
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
    except sqlite3.Error as exc:
        return db_error_payload(db_path, exc)

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
            "profile_level": canonical_level,
            "category_hint": category_hint,
            "note": note,
            "source_context": source_context,
            "created_at": created_at,
            "updated_at": now,
        },
    }


def delete_rule(db_path: str, term_original: str) -> dict[str, Any]:
    if get_protected_repo_dir_name(db_path) is not None:
        return build_protected_output_payload("db_path", db_path)
    original = term_original.strip()
    if not original:
        return {
            "status": "skip",
            "reason": "store.empty_term",
            "db_path": db_path,
        }

    normalized = normalize_term(original)
    try:
        init_db(db_path)
        with closing(open_db(db_path)) as conn:
            row = conn.execute(
                """
                SELECT
                    id,
                    term_original,
                    term_normalized,
                    preferred,
                    preferred_alt_2,
                    preferred_alt_3,
                    status,
                    profile_level,
                    category_hint,
                    note,
                    source_context,
                    created_at,
                    updated_at
                FROM rules
                WHERE term_normalized = ?
                ORDER BY id
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()
            if row is None:
                return {
                    "status": "skip",
                    "reason": "store.rule_not_found",
                    "db_path": db_path,
                    "term_original": original,
                    "term_normalized": normalized,
                }
            conn.execute("DELETE FROM rules WHERE id = ?", (row["id"],))
            conn.commit()
    except sqlite3.Error as exc:
        return db_error_payload(db_path, exc)

    return {
        "status": "ok",
        "db_path": db_path,
        "action": "deleted",
        "row": dict(row),
    }


def readback_rules(db_path: str) -> dict[str, Any]:
    if not os.path.exists(db_path):
        return {
            "status": "skip",
            "reason": "store.no_db_file",
            "db_path": db_path,
            "summary": {"total": 0},
            "rows": [],
        }

    try:
        with closing(open_db_readonly(db_path)) as conn:
            columns = _existing_columns(conn, "rules")
            if not columns:
                return {
                    "status": "error",
                    "reason": "store.db_unreadable",
                    "db_path": db_path,
                    "summary": {"total": 0},
                    "rows": [],
                    "error": "rules table not found",
                }
            select_parts = [
                "id",
                "term_original",
                "term_normalized",
                "preferred",
                "preferred_alt_2" if "preferred_alt_2" in columns else "NULL AS preferred_alt_2",
                "preferred_alt_3" if "preferred_alt_3" in columns else "NULL AS preferred_alt_3",
                "status" if "status" in columns else "'active' AS status",
                "profile_level" if "profile_level" in columns else f"'{PROFILE_LEVEL_DEFAULT}' AS profile_level",
                "category_hint" if "category_hint" in columns else "NULL AS category_hint",
                "note" if "note" in columns else "NULL AS note",
                "source_context" if "source_context" in columns else "NULL AS source_context",
                "created_at" if "created_at" in columns else "'' AS created_at",
                "updated_at" if "updated_at" in columns else "'' AS updated_at",
            ]
            query = (
                "SELECT\n            "
                + ",\n            ".join(select_parts)
                + "\n        FROM rules\n        ORDER BY term_normalized, id"
            )
            rows = [dict(row) for row in conn.execute(query).fetchall()]
            summary = {
                "total": conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0],
            }
    except sqlite3.Error as exc:
        return db_error_payload(db_path, exc)

    return {
        "status": "ok",
        "db_path": db_path,
        "summary": summary,
        "rows": rows,
    }


def load_rule_index_from_db(db_path: str) -> tuple[str, dict[str, dict[str, str]], list[dict[str, Any]], dict[str, Any] | None]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return payload["status"], {}, [], payload

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
    return "ok", index, [], None


def export_html_from_db(
    db_path: str,
    html_path: str,
    ui: dict[str, str] | None = None,
) -> dict[str, Any]:
    if get_protected_repo_dir_name(html_path) is not None:
        return build_protected_output_payload("html_path", html_path)
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return {
            "status": payload["status"],
            "reason": payload.get("reason"),
            "db_path": db_path,
            "html_path": html_path,
            "error": payload.get("error"),
        }
    rows = payload["rows"]  # type: ignore[assignment]

    resolved_ui = ui if ui is not None else _HTML_UI_EN
    capture_config = capture_taxonomy_payload()
    content = render_review_html(
        rows,
        resolved_ui,
        template=_HTML_TEMPLATE,
        ui_by_lang=_HTML_UI_BY_LANG,
        capture_config=capture_config,
        db_cli_path=DB_CLI_PATH,
        db_path=db_path,
        html_path=html_path,
    )
    content = render_with_manifest(
        content,
        template=_HTML_TEMPLATE,
        ui_by_lang=_HTML_UI_BY_LANG,
        capture_taxonomy=capture_config,
        rows=rows,
        settings={
            "db_cli_path": DB_CLI_PATH,
            "db_path": Path(db_path).as_posix(),
            "html_path": Path(html_path).as_posix(),
            "default_lang": str(resolved_ui.get("lang", "en")),
        },
    )

    os.makedirs(os.path.dirname(os.path.abspath(html_path)), exist_ok=True)
    try:
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        return {
            "status": "error",
            "reason": "store.html_write_failed",
            "db_path": db_path,
            "html_path": html_path,
            "error": str(exc),
        }

    return {
        "status": "ok",
        "db_path": db_path,
        "html_path": html_path,
        "row_count": sum(1 for row in rows if row.get("status") == "active"),
        "source_type": "db",
    }


def load_rules_for_lint_from_db(db_path: str) -> tuple[str, list[dict[str, str]], dict[str, Any] | None]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return payload["status"], [], payload

    return "ok", [
        {
            "original": row["term_original"],
            "preferred": row["preferred"],
        }
        for row in payload["rows"]
        if row.get("status") == "active"
    ], None
