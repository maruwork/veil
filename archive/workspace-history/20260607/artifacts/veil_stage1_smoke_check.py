#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "workspace" / "veil_stage1_smoke.db"
RULES_DIR = ROOT / "workspace" / "veil_stage1_rules_fixture"
CLI_PATH = ROOT / "shared" / "tools" / "veil-db.py"


def run(*args: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), *args],
        cwd=str(ROOT),
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )
    return completed.stdout


def main() -> int:
    if DB_PATH.exists():
        DB_PATH.unlink()

    run("init-db", "--db", str(DB_PATH))
    import_payload = json.loads(run("import-rules", "--db", str(DB_PATH), "--rules-dir", str(RULES_DIR), "--json"))
    readback_payload = json.loads(run("readback", "--db", str(DB_PATH), "--json"))

    assert import_payload["status"] == "ok"
    assert import_payload["imported_count"] == 5
    assert len(import_payload["conflicts"]) == 0
    assert readback_payload["status"] == "ok"
    assert readback_payload["summary"] == {
        "total": 5,
        "required": 2,
        "recommended": 2,
        "observe": 1,
    }

    levels = [row["level"] for row in readback_payload["rows"]]
    assert levels.count("必須") == 2
    assert levels.count("推奨") == 2
    assert levels.count("観察") == 1

    print(
        "STAGE1-SMOKE: "
        f"db={DB_PATH}, total={readback_payload['summary']['total']}, "
        f"required={readback_payload['summary']['required']}, "
        f"recommended={readback_payload['summary']['recommended']}, "
        f"observe={readback_payload['summary']['observe']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
