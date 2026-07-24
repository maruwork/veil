#!/usr/bin/env python3
"""Disposable HTML request -> maintenance -> HTML freshness acceptance."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.tools.veil_delivery_freshness import verify_manifest
from shared.tools.veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG


DB_CLI = PROJECT_ROOT / "shared" / "tools" / "veil-db.py"
CONTROLLED_SOURCES = (
    ".github/workflows/ci.yml",
    "shared/tools/veil-db.py",
    "shared/tools/veil_rule_store.py",
    "shared/tools/veil_delivery_freshness.py",
    "shared/tools/veil_html_assets.py",
    "shared/tools/veil_html_review.py",
    "shared/tools/veil_review_template.html",
    "skills/claude-code/veil-capture.md",
    "skills/codex/veil-capture/SKILL.md",
    "tests/browser_e2e_runner.py",
    "tests/test_browser_e2e_runner.py",
    "tests/html_delivery_acceptance.py",
    "tests/test_html_delivery_acceptance.py",
)


class ChangeButtonParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs}
        classes = set((values.get("class") or "").split())
        if tag == "button" and "request-change-btn" in classes:
            self.rows.append(
                {
                    "term": str(values.get("data-term") or ""),
                    "current_preferred": str(values.get("data-preferred") or ""),
                }
            )


def _db(*args: str, check: bool = True) -> dict[str, Any]:
    environment = {**os.environ, "VEIL_LANG": "en", "PYTHONUTF8": "1"}
    completed = subprocess.run(
        [sys.executable, "-B", str(DB_CLI), *args, "--json"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"veil-db failed ({completed.returncode}): {completed.stdout}\n{completed.stderr}"
        )
    payload = json.loads(completed.stdout)
    payload["_returncode"] = completed.returncode
    return payload


def _manifest_inputs(db: Path, html: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "template": _HTML_TEMPLATE,
        "ui_by_lang": _HTML_UI_BY_LANG,
        "rows": rows,
        "settings": {
            "db_path": db.as_posix(),
            "html_path": html.as_posix(),
            "default_lang": "en",
        },
    }


def source_fingerprint() -> str:
    digest = hashlib.sha256()
    for relative in CONTROLLED_SOURCES:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((PROJECT_ROOT / relative).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_state() -> tuple[str, bool]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    dirty = (
        subprocess.run(
            ["git", "diff", "--quiet", "--", *CONTROLLED_SOURCES],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        != 0
    )
    return head, dirty


def run_acceptance(directory: Path) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    db = directory / "veil.db"
    html = directory / "veil.html"
    maintenance = directory / "confirmed-maintenance.json"

    _db("init-db", "--db", str(db))
    _db(
        "upsert-rule",
        "--db",
        str(db),
        "--term",
        "current state",
        "--preferred",
        "present state",
    )
    _db(
        "upsert-rule",
        "--db",
        str(db),
        "--term",
        "old lane",
        "--preferred",
        "approved lane",
    )
    _db("export-html", "--db", str(db), "--html-path", str(html))

    before_content = html.read_text(encoding="utf-8")
    before_rows = _db("readback", "--db", str(db))["rows"]
    before_freshness = verify_manifest(
        before_content,
        **_manifest_inputs(db, html, before_rows),
    )
    parser = ChangeButtonParser()
    parser.feed(before_content)
    selected = {row["term"]: row for row in parser.rows}
    operations = [
        {
            "action": "change",
            **selected["current state"],
            "preferred": "current condition",
            "reason": "disposable integration acceptance",
        },
        {
            "action": "retire",
            **selected["old lane"],
            "preferred": None,
            "reason": "disposable integration acceptance",
        },
    ]
    maintenance.write_text(
        json.dumps(
            {"contract_version": "1", "operations": operations},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    applied = _db(
        "maintain-batch",
        "--db",
        str(db),
        "--input-json",
        str(maintenance),
    )
    changed_rows = _db("readback", "--db", str(db))["rows"]
    stale_before_regeneration = verify_manifest(
        before_content,
        **_manifest_inputs(db, html, changed_rows),
    )

    _db("export-html", "--db", str(db), "--html-path", str(html))
    final_content = html.read_text(encoding="utf-8")
    final_rows = _db("readback", "--db", str(db))["rows"]
    final_freshness = verify_manifest(
        final_content,
        **_manifest_inputs(db, html, final_rows),
    )
    rows_by_term = {row["term_original"]: row for row in final_rows}
    head, dirty = git_state()
    result = {
        "status": "ok",
        "temp_only": True,
        "source_fingerprint_sha256": source_fingerprint(),
        "git_head": head,
        "controlled_sources_dirty": dirty,
        "html_selected_contract": selected,
        "applied_status": applied["status"],
        "applied_atomic": applied["atomic"],
        "applied_count": applied["processed_count"],
        "before_freshness": before_freshness,
        "stale_before_regeneration": stale_before_regeneration,
        "final_freshness": final_freshness,
        "changed_preferred": rows_by_term["current state"]["preferred"],
        "retired_status": rows_by_term["old lane"]["status"],
        "changed_visible": "current condition" in final_content,
        "retired_hidden": "old lane" not in final_content,
        "generated_html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
    }
    result["ok"] = (
        result["applied_status"] == "ok"
        and result["applied_atomic"] is True
        and result["applied_count"] == 2
        and result["before_freshness"] == "OK"
        and result["stale_before_regeneration"] == "STALE"
        and result["final_freshness"] == "OK"
        and result["changed_preferred"] == "current condition"
        and result["retired_status"] == "retired"
        and result["changed_visible"] is True
        and result["retired_hidden"] is True
    )
    result["status"] = "ok" if result["ok"] else "error"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="veil-html-delivery-") as temporary:
        result = run_acceptance(Path(temporary))
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
