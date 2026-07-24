from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from browser_e2e_runner import BrowserStartupError, DevToolsConnection, _close_browser_process


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


def test_browser_cleanup_does_not_propagate_a_descendant_pipe_timeout() -> None:
    class StuckPipeProcess:
        def __init__(self) -> None:
            self.terminated = False
            self.killed = False

        def poll(self):
            return None

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

        def communicate(self, timeout: float):
            raise __import__("subprocess").TimeoutExpired("browser", timeout)

    process = StuckPipeProcess()

    assert _close_browser_process(process) == ""
    assert process.terminated is True
    assert process.killed is True
