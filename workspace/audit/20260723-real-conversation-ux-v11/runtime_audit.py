"""Production deny hooks used by the v11 evaluator and its real-core boundary."""
from __future__ import annotations

from typing import Any


class RuntimeAudit:
    def __init__(self) -> None:
        self.canonical_db_access_attempts = 0
        self.raw_text_fallback_attempts = 0

    def deny_db_connect(self, *args: Any, **kwargs: Any) -> None:
        self.canonical_db_access_attempts += 1
        raise RuntimeError("canonical DB access is forbidden during v11 evaluation")

    def deny_raw_text_fallback(self, *args: Any, **kwargs: Any) -> None:
        self.raw_text_fallback_attempts += 1
        raise RuntimeError("raw-text fallback is forbidden during v11 evaluation")

    def snapshot(self) -> dict[str, int]:
        return {
            "canonical_db_access_attempts": self.canonical_db_access_attempts,
            "raw_text_fallback_attempts": self.raw_text_fallback_attempts,
        }
