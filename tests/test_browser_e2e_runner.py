from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser_e2e_runner import BrowserStartupError, DevToolsConnection


def test_devtools_transport_timeout_is_classified_as_startup_error() -> None:
    connection = DevToolsConnection.__new__(DevToolsConnection)
    connection._next_id = 1
    connection._send_text = lambda _text: None
    connection._recv_text = lambda: (_ for _ in ()).throw(TimeoutError("timed out"))

    with pytest.raises(
        BrowserStartupError,
        match="DevTools transport failed during Runtime.enable",
    ):
        connection.call("Runtime.enable")
