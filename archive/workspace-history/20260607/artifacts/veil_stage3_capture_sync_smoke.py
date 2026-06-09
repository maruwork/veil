from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import readback_rules


SMOKE_DIR = ROOT / "workspace" / "veil_stage3_smoke"
DB_PATH = SMOKE_DIR / "veil.db"
RULES_DIR = SMOKE_DIR / "rules"
CONFIG_DIR = SMOKE_DIR / "config"
TARGET_PATH = SMOKE_DIR / "TARGET.md"


def main() -> int:
    if SMOKE_DIR.exists():
        shutil.rmtree(SMOKE_DIR)
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_PATH.write_text("# target\n", encoding="utf-8")

    for args in [
        [sys.executable, str(ROOT / "shared" / "tools" / "veil-db.py"), "init-db", "--db", str(DB_PATH)],
        [
            sys.executable,
            str(ROOT / "shared" / "tools" / "veil-db.py"),
            "upsert-rule",
            "--db",
            str(DB_PATH),
            "--term",
            "current state",
            "--preferred",
            "今の状態",
            "--level",
            "必須",
            "--source-context",
            "smoke:1",
        ],
        [
            sys.executable,
            str(ROOT / "shared" / "tools" / "veil-db.py"),
            "upsert-rule",
            "--db",
            str(DB_PATH),
            "--term",
            "summary",
            "--preferred",
            "要約",
            "--level",
            "推奨",
            "--source-context",
            "smoke:2",
        ],
        [
            sys.executable,
            str(ROOT / "shared" / "tools" / "veil-db.py"),
            "export-mirror",
            "--db",
            str(DB_PATH),
            "--rules-dir",
            str(RULES_DIR),
        ],
    ]:
        result = subprocess.run(
            args,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.stderr or result.stdout or "veil-db cli failed")

    sync_add = subprocess.run(
        [
            sys.executable,
            str(ROOT / "shared" / "runtime" / "veil-sync.py"),
            "--config-dir",
            str(CONFIG_DIR),
            "--db",
            str(DB_PATH),
            "--rules-dir",
            str(RULES_DIR),
            "--add",
            str(TARGET_PATH),
            "--quiet",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if sync_add.returncode != 0:
        raise SystemExit(f"sync add failed: {sync_add.stderr or sync_add.stdout}")

    target_text = TARGET_PATH.read_text(encoding="utf-8")
    if "VEIL_START" not in target_text or "current state" not in target_text or "summary" not in target_text:
        raise SystemExit("sync target content check failed")

    readback = readback_rules(str(DB_PATH))
    summary = readback["summary"]
    print(
        "STAGE3-SMOKE:"
        f" total={summary['total']},"
        f" required={summary['required']},"
        f" recommended={summary['recommended']},"
        f" observe={summary['observe']},"
        f" mirror_files={len(list(RULES_DIR.glob('*.md')))}"
    )
    print(f"MIRROR: {', '.join(sorted(path.name for path in RULES_DIR.glob('*.md')))}")
    print(f"SYNC-TARGET: {TARGET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
