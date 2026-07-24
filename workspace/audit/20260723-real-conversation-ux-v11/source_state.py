"""Scoped execution-source state for the v11 evaluator."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def record(root: Path, path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("execution source is outside project root") from exc
    data = resolved.read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def compute(root: Path, inventory: list[Path]) -> dict[str, Any]:
    if not inventory:
        raise ValueError("execution source inventory is empty")
    records = [record(root, path) for path in inventory]
    if len({item["path"] for item in records}) != len(records):
        raise ValueError("execution source inventory has duplicate paths")
    digest = hashlib.sha256()
    for item, path in zip(records, inventory):
        data = path.read_bytes()
        digest.update(item["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return {"inventory_sha256": digest.hexdigest(), "inventory": records}
