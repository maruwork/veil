#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Iterator
from urllib.parse import urlparse
from urllib.request import urlopen

from html_delivery_acceptance import git_state, source_fingerprint


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_CLI = PROJECT_ROOT / "shared" / "tools" / "veil-db.py"
AUDIT_ROOT = PROJECT_ROOT / "workspace" / "audit"
RESULT_ATTRIBUTE = "data-veil-e2e"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class QuietHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        if isinstance(sys.exc_info()[1], (ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def browser_candidates() -> list[Path]:
    explicit = os.environ.get("VEIL_BROWSER_BINARY")
    values = [
        explicit,
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    return [Path(value) for value in values if value]


def find_browsers() -> list[Path]:
    found: list[Path] = []
    for candidate in browser_candidates():
        if candidate.is_file():
            resolved = candidate.resolve()
            if resolved not in found:
                found.append(resolved)
    if not found:
        raise RuntimeError(
            "No supported Edge/Chrome/Chromium binary found. Set VEIL_BROWSER_BINARY."
        )
    return found


def run_db(*args: str) -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(DB_CLI), *args],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise RuntimeError(f"veil-db failed ({completed.returncode}): {completed.stdout}\n{completed.stderr}")


def harness_script() -> str:
    return r"""
<script id="veil-e2e-harness">
(async () => {
  const result = {
    rulebook_first: false,
    search_filters: false,
    no_match_routes_to_review: false,
    single_review_action: false,
    empty_review_disabled: false,
    full_review_copy_success: false,
    full_review_copy_fallback: false,
    locale_english: false,
    locale_japanese: false,
    change_prefilled: false,
    change_request_copy: false,
    retire_request_copy: false,
    invalid_change_blocked: false,
    native_controls_focusable: false,
    direct_write_attempts: []
  };
  const pause = () => new Promise(resolve => setTimeout(resolve, 80));
  const input = (element, value) => {
    element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
  };

  window.fetch = (...args) => {
    result.direct_write_attempts.push('fetch');
    return Promise.reject(new Error('E2E blocked fetch'));
  };
  window.XMLHttpRequest = function XMLHttpRequest() {
    result.direct_write_attempts.push('XMLHttpRequest');
  };
  window.WebSocket = function WebSocket() {
    result.direct_write_attempts.push('WebSocket');
  };
  if (window.indexedDB && window.indexedDB.open) {
    window.indexedDB.open = (...args) => {
      result.direct_write_attempts.push('indexedDB');
      throw new Error('E2E blocked indexedDB');
    };
  }

  try {
    const rulebook = document.getElementById('rulebook-heading').closest('.panel');
    const actions = document.getElementById('actions-heading').closest('.panel');
    result.rulebook_first = Boolean(
      rulebook.compareDocumentPosition(actions) & Node.DOCUMENT_POSITION_FOLLOWING
    );
    result.single_review_action = document.querySelectorAll('#review-copy-btn').length === 1;
    result.empty_review_disabled = document.getElementById('review-copy-btn').disabled === true;

    const search = document.getElementById('search');
    input(search, 'current status');
    await pause();
    result.search_filters = Boolean(
      document.querySelectorAll('.rule-row:not(.hidden)').length === 1 &&
      document.querySelector('.rule-row:not(.hidden) .term').textContent === 'current state'
    );
    input(search, 'no such rule');
    await pause();
    result.no_match_routes_to_review = Boolean(
      !document.getElementById('no-match').classList.contains('hidden') &&
      document.getElementById('review-input')
    );
    input(search, '');

    let copiedText = '';
    applyLocale('en');
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: async text => { copiedText = text; } }
    });
    const exactConversation = '  User: Keep "decision boundary".\nAI: Understood.\n日本語も保持する。  ';
    input(document.getElementById('review-input'), exactConversation);
    document.getElementById('review-copy-btn').click();
    await pause();
    result.full_review_copy_success = Boolean(
      copiedText.includes('Run the installed VEIL capture workflow') &&
      copiedText.includes('contract v2') &&
      copiedText.includes('separate critic pass') &&
      copiedText.includes(exactConversation) &&
      !copiedText.includes('upsert-rule')
    );
    if (!result.full_review_copy_success) {
      result.review_copy_diagnostics = {
        header: copiedText.includes('Run the installed VEIL capture workflow'),
        contract: copiedText.includes('contract v2'),
        critic: copiedText.includes('separate critic pass'),
        exact: copiedText.includes(exactConversation),
        safe: !copiedText.includes('upsert-rule'),
        length: copiedText.length
      };
    }

    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: async () => { throw new Error('clipboard denied'); } }
    });
    window.prompt = (message, text) => {
      result.full_review_copy_fallback = Boolean(
        message && text && text.includes(exactConversation) && text.includes('contract v2')
      );
      return null;
    };
    document.getElementById('review-copy-btn').click();
    await pause();

    applyLocale('ja');
    result.locale_japanese = Boolean(
      document.documentElement.lang === 'ja' &&
      document.getElementById('review-heading').textContent === '会話を確認する' &&
      document.querySelector('.alternatives summary').textContent === '代替表現を表示'
    );
    applyLocale('en');
    result.locale_english = Boolean(
      document.documentElement.lang === 'en' &&
      document.getElementById('review-heading').textContent === 'Review a conversation' &&
      document.querySelector('.alternatives summary').textContent === 'Show alternatives'
    );

    copiedText = '';
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: async text => { copiedText = text; } }
    });
    document.querySelector('.request-change-btn').click();
    await pause();
    result.change_prefilled = Boolean(
      document.getElementById('selected-term').textContent === 'current state' &&
      document.getElementById('selected-preferred').textContent === 'present state' &&
      document.getElementById('change-intent').value === 'change'
    );
    input(document.getElementById('requested-preferred'), 'current condition');
    input(document.getElementById('change-reason'), 'Accepted project wording');
    document.getElementById('change-copy-btn').click();
    await pause();
    result.change_request_copy = Boolean(
      copiedText.includes('Change preferred wording') &&
      copiedText.includes('Source wording: current state') &&
      copiedText.includes('Current preferred wording: present state') &&
      copiedText.includes('Requested preferred wording: current condition') &&
      copiedText.includes('one validated atomic maintenance batch') &&
      !copiedText.includes('maintain-batch')
    );

    copiedText = '';
    const intent = document.getElementById('change-intent');
    intent.value = 'retire';
    intent.dispatchEvent(new Event('change', { bubbles: true }));
    document.getElementById('change-copy-btn').click();
    await pause();
    result.retire_request_copy = Boolean(
      copiedText.includes('Retire this rule') &&
      copiedText.includes('Source wording: current state') &&
      !copiedText.includes('Requested preferred wording:')
    );

    copiedText = 'unchanged';
    intent.value = 'change';
    intent.dispatchEvent(new Event('change', { bubbles: true }));
    input(document.getElementById('requested-preferred'), '');
    document.getElementById('change-form').dispatchEvent(
      new Event('submit', { bubbles: true, cancelable: true })
    );
    await pause();
    result.invalid_change_blocked = Boolean(
      copiedText === 'unchanged' &&
      document.getElementById('status').classList.contains('error')
    );

    const visibleControls = [...document.querySelectorAll(
      'button:not(.hidden), input:not(.hidden), textarea:not(.hidden), select:not(.hidden), summary'
    )].filter(element => !element.closest('.hidden'));
    result.native_controls_focusable = Boolean(
      visibleControls.length >= 8 &&
      visibleControls.every(element => {
        element.focus();
        return document.activeElement === element &&
          (!element.hasAttribute('tabindex') || Number(element.getAttribute('tabindex')) <= 0);
      })
    );
  } catch (error) {
    result.error = String(error && error.stack ? error.stack : error);
  }

  result.ok = Boolean(
    result.rulebook_first &&
    result.search_filters &&
    result.no_match_routes_to_review &&
    result.single_review_action &&
    result.empty_review_disabled &&
    result.full_review_copy_success &&
    result.full_review_copy_fallback &&
    result.locale_english &&
    result.locale_japanese &&
    result.change_prefilled &&
    result.change_request_copy &&
    result.retire_request_copy &&
    result.invalid_change_blocked &&
    result.native_controls_focusable &&
    result.direct_write_attempts.length === 0 &&
    !result.error
  );
  document.documentElement.setAttribute(
    'data-veil-e2e',
    btoa(unescape(encodeURIComponent(JSON.stringify(result))))
  );
})();
</script>
"""


def inject_harness(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if RESULT_ATTRIBUTE in content or "</body>" not in content:
        raise RuntimeError("unexpected generated HTML boundary")
    path.write_text(content.replace("</body>", harness_script() + "\n</body>", 1), encoding="utf-8")


@contextmanager
def serve(directory: Path) -> Iterator[str]:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
    server = QuietHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/veil-e2e.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def parse_result(dom: str) -> dict[str, object]:
    marker = f'{RESULT_ATTRIBUTE}="'
    start = dom.find(marker)
    if start < 0:
        raise RuntimeError("browser DOM did not contain the E2E result marker")
    start += len(marker)
    end = dom.find('"', start)
    if end < 0:
        raise RuntimeError("browser DOM contained a malformed E2E result marker")
    encoded = html.unescape(dom[start:end])
    return json.loads(base64.b64decode(encoded).decode("utf-8"))


class BrowserStartupError(RuntimeError):
    """Browser process or DevTools transport did not become usable."""


class DevToolsConnection:
    def __init__(self, websocket_url: str) -> None:
        parsed = urlparse(websocket_url)
        if parsed.scheme != "ws" or parsed.hostname is None or parsed.port is None:
            raise BrowserStartupError(f"unsupported DevTools URL: {websocket_url}")
        try:
            self._socket = socket.create_connection(
                (parsed.hostname, parsed.port),
                timeout=10,
            )
            key = base64.b64encode(os.urandom(16)).decode("ascii")
            request = (
                f"GET {parsed.path or '/'} HTTP/1.1\r\n"
                f"Host: {parsed.hostname}:{parsed.port}\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            )
            self._socket.sendall(request.encode("ascii"))
            response = bytearray()
            while b"\r\n\r\n" not in response:
                chunk = self._socket.recv(4096)
                if not chunk:
                    raise BrowserStartupError(
                        "DevTools WebSocket handshake closed early"
                    )
                response.extend(chunk)
        except BrowserStartupError:
            raise
        except (OSError, TimeoutError) as exc:
            raise BrowserStartupError(
                f"DevTools WebSocket connection failed: {exc}"
            ) from exc
        if not response.startswith(b"HTTP/1.1 101"):
            raise BrowserStartupError(
                f"DevTools WebSocket handshake failed: {response[:200]!r}"
            )
        self._next_id = 1

    def close(self) -> None:
        try:
            self._socket.close()
        except OSError:
            pass

    def _send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        mask = os.urandom(4)
        length = len(payload)
        if length < 126:
            header = bytes((0x81, 0x80 | length))
        elif length < 65536:
            header = bytes((0x81, 0x80 | 126)) + struct.pack("!H", length)
        else:
            header = bytes((0x81, 0x80 | 127)) + struct.pack("!Q", length)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self._socket.sendall(header + mask + masked)

    def _recv_exact(self, length: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < length:
            chunk = self._socket.recv(length - len(chunks))
            if not chunk:
                raise BrowserStartupError("DevTools WebSocket closed")
            chunks.extend(chunk)
        return bytes(chunks)

    def _recv_text(self) -> str:
        while True:
            first, second = self._recv_exact(2)
            opcode = first & 0x0F
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask = self._recv_exact(4) if second & 0x80 else None
            payload = self._recv_exact(length)
            if mask is not None:
                payload = bytes(
                    value ^ mask[index % 4] for index, value in enumerate(payload)
                )
            if opcode == 0x8:
                raise BrowserStartupError("DevTools WebSocket sent close frame")
            if opcode == 0x9:
                self._send_control(0xA, payload)
                continue
            if opcode == 0x1:
                return payload.decode("utf-8")

    def _send_control(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self._socket.sendall(bytes((0x80 | opcode, 0x80 | len(payload))) + mask + masked)

    def call(self, method: str, params: dict[str, object] | None = None) -> dict[str, object]:
        request_id = self._next_id
        self._next_id += 1
        try:
            self._send_text(
                json.dumps(
                    {"id": request_id, "method": method, "params": params or {}},
                    ensure_ascii=False,
                )
            )
            while True:
                message = json.loads(self._recv_text())
                if message.get("id") == request_id:
                    if "error" in message:
                        raise RuntimeError(f"DevTools {method} failed: {message['error']}")
                    return message.get("result", {})
        except (OSError, TimeoutError, json.JSONDecodeError) as exc:
            raise BrowserStartupError(
                f"DevTools transport failed during {method}: {exc}"
            ) from exc


def _wait_for_devtools(profile_dir: Path, process: subprocess.Popen[bytes]) -> tuple[int, str]:
    active_port = profile_dir / "DevToolsActivePort"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise BrowserStartupError(
                f"browser exited before DevTools startup: {process.returncode}"
            )
        if active_port.is_file():
            try:
                lines = active_port.read_text(encoding="utf-8").splitlines()
            except OSError:
                time.sleep(0.05)
                continue
            if len(lines) >= 2:
                return int(lines[0]), lines[1]
        time.sleep(0.05)
    raise BrowserStartupError("browser DevTools startup timed out")


def _page_websocket(port: int, expected_url: str) -> str:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            with urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2) as response:
                targets = json.load(response)
            for target in targets:
                if target.get("type") == "page" and target.get("url") == expected_url:
                    return str(target["webSocketDebuggerUrl"])
        except (OSError, ValueError):
            pass
        time.sleep(0.05)
    raise BrowserStartupError("browser page target did not become available")


def _runtime_value(connection: DevToolsConnection, expression: str) -> object:
    payload = connection.call(
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
    )
    return payload["result"].get("value")  # type: ignore[index]


def _dispatch_key(
    connection: DevToolsConnection,
    key: str,
    code: str,
    virtual_key: int,
    *,
    modifiers: int = 0,
) -> None:
    common = {
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": virtual_key,
        "modifiers": modifiers,
        "text": {"Enter": "\r", " ": " "}.get(key, ""),
        "unmodifiedText": {"Enter": "\r", " ": " "}.get(key, ""),
        "autoRepeat": False,
        "location": 0,
        "isKeypad": False,
    }
    down_type = "keyDown" if common["text"] else "rawKeyDown"
    connection.call("Input.dispatchKeyEvent", {"type": down_type, **common})
    connection.call("Input.dispatchKeyEvent", {"type": "keyUp", **common})
    time.sleep(0.04)


def _insert_text(connection: DevToolsConnection, text: str) -> None:
    connection.call("Input.insertText", {"text": text})
    time.sleep(0.04)


def _close_browser_process(process: subprocess.Popen[bytes]) -> str:
    """Best-effort cleanup must never hide a completed product assertion."""

    if process.poll() is None:
        process.terminate()
    try:
        _stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            _stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # Descendant browser processes can retain stderr after the launched
            # process exits. The temporary profile is still removed by the
            # caller; report no warning rather than crashing the E2E runner.
            return ""
    return stderr.decode("utf-8", errors="replace") if stderr else ""


def run_keyboard_browser(
    browser: Path,
    url: str,
    profile_dir: Path,
) -> tuple[dict[str, object], str]:
    command = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-software-rasterizer",
        "--in-process-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-debugging-port=0",
        f"--user-data-dir={profile_dir}",
        "about:blank",
    ]
    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    connection: DevToolsConnection | None = None
    try:
        port, _browser_path = _wait_for_devtools(profile_dir, process)
        page_websocket = _page_websocket(port, "about:blank")
        time.sleep(0.5)
        connection = DevToolsConnection(page_websocket)
        connection.call("Runtime.enable")
        connection.call("DOM.enable")
        connection.call("Page.enable")
        connection.call("Page.bringToFront")
        connection.call("Page.navigate", {"url": url})
        time.sleep(1)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if _runtime_value(connection, "document.readyState") == "complete":
                break
            time.sleep(0.05)
        else:
            raise BrowserStartupError("browser page load timed out")

        _runtime_value(
            connection,
            """
            (() => {
              window.__keyboardCopied = '';
              Object.defineProperty(navigator, 'clipboard', {
                configurable: true,
                value: { writeText: async text => { window.__keyboardCopied = text; } }
              });
              applyLocale('en');
              return true;
            })()
            """,
        )
        focus_trace: list[str] = []

        def focus_id() -> str:
            value = _runtime_value(
                connection,
                "document.activeElement.id || document.activeElement.className || document.activeElement.tagName",
            )
            focus_trace.append(str(value))
            return str(value)

        search_object = connection.call(
            "Runtime.evaluate",
            {
                "expression": "document.getElementById('search')",
                "returnByValue": False,
            },
        )
        connection.call(
            "DOM.focus",
            {"objectId": search_object["result"]["objectId"]},  # type: ignore[index]
        )
        search_focus = focus_id() == "search"
        _insert_text(connection, "current state")
        _dispatch_key(connection, "Tab", "Tab", 9)
        alternative_summary_focus = focus_id() == "SUMMARY"
        _dispatch_key(connection, "Tab", "Tab", 9)
        change_button_focus = "request-change-btn" in focus_id()
        _dispatch_key(connection, "Enter", "Enter", 13)
        change_opened = focus_id() == "requested-preferred"

        _dispatch_key(connection, "Tab", "Tab", 9, modifiers=8)
        select_focus = focus_id() == "change-intent"
        _dispatch_key(connection, "ArrowDown", "ArrowDown", 40)
        select_retire = _runtime_value(
            connection, "document.getElementById('change-intent').value"
        ) == "retire"
        _dispatch_key(connection, "ArrowUp", "ArrowUp", 38)
        select_change = _runtime_value(
            connection, "document.getElementById('change-intent').value"
        ) == "change"
        _dispatch_key(connection, "Tab", "Tab", 9)
        _insert_text(connection, "current condition")
        _dispatch_key(connection, "Tab", "Tab", 9)
        reason_focus = focus_id() == "change-reason"
        _insert_text(connection, "keyboard acceptance")
        _dispatch_key(connection, "Enter", "Enter", 13)
        submitted_request = str(
            _runtime_value(connection, "window.__keyboardCopied")
        )
        form_submitted = (
            "Source wording: current state" in submitted_request
            and "Requested preferred wording: current condition" in submitted_request
        )
        _dispatch_key(connection, "Tab", "Tab", 9)
        copy_focus = focus_id() == "change-copy-btn"
        _dispatch_key(connection, "Tab", "Tab", 9)
        cancel_focus = focus_id() == "change-cancel-btn"
        _dispatch_key(connection, "Enter", "Enter", 13)
        form_cancelled = bool(
            _runtime_value(
                connection,
                "document.getElementById('change-form').classList.contains('hidden')",
            )
        )

        _dispatch_key(connection, "Tab", "Tab", 9)
        returned_to_search = focus_id() == "search"
        for _ in range(20):
            _dispatch_key(connection, "Backspace", "Backspace", 8)
        search_cleared = _runtime_value(
            connection, "document.getElementById('search').value"
        ) == ""
        for _ in range(3):
            _dispatch_key(connection, "Tab", "Tab", 9)
        review_focus = focus_id() == "review-input"
        exact_conversation = 'User: Keep "decision boundary".\nAI: Understood.'
        _insert_text(connection, exact_conversation)
        _dispatch_key(connection, "Tab", "Tab", 9)
        review_copy_focus = focus_id() == "review-copy-btn"
        _dispatch_key(connection, " ", "Space", 32)
        copied_review = str(_runtime_value(connection, "window.__keyboardCopied"))
        review_copied = exact_conversation in copied_review

        result = {
            "initial_search_anchor": search_focus,
            "tab_search": search_focus,
            "tab_alternative_summary": alternative_summary_focus,
            "tab_change_button": change_button_focus,
            "enter_opens_change": change_opened,
            "shift_tab_select": select_focus,
            "select_arrow_retire": select_retire,
            "select_arrow_change": select_change,
            "tab_reason": reason_focus,
            "enter_submits_form": form_submitted,
            "tab_copy": copy_focus,
            "tab_cancel": cancel_focus,
            "enter_cancels_form": form_cancelled,
            "tab_returns_search": returned_to_search,
            "keyboard_clears_search": search_cleared,
            "tab_review_input": review_focus,
            "tab_review_copy": review_copy_focus,
            "space_copies_review": review_copied,
            "focus_trace": focus_trace,
        }
        result["ok"] = all(value for key, value in result.items() if key != "focus_trace")
        return result, ""
    finally:
        if connection is not None:
            connection.close()
        _close_browser_process(process)
        if process.returncode not in (0, None, -15, 1):
            # Browser warnings are returned separately; product assertions stay
            # in the structured result above.
            pass


def run_browser(browser: Path, url: str, profile_dir: Path) -> tuple[dict[str, object], str]:
    command = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--disable-gpu-compositing",
        "--disable-software-rasterizer",
        "--in-process-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-debugging-port=0",
        f"--user-data-dir={profile_dir}",
        "about:blank",
    ]
    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    connection: DevToolsConnection | None = None
    result: dict[str, object] | None = None
    stderr_text = ""
    try:
        port, _browser_path = _wait_for_devtools(profile_dir, process)
        page_websocket = _page_websocket(port, "about:blank")
        time.sleep(0.5)
        connection = DevToolsConnection(page_websocket)
        connection.call("Runtime.enable")
        connection.call("Page.enable")
        connection.call("Page.bringToFront")
        connection.call("Page.navigate", {"url": url})
        time.sleep(1)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            encoded = _runtime_value(
                connection,
                "document.documentElement.getAttribute('data-veil-e2e')",
            )
            if encoded:
                dom = str(
                    _runtime_value(connection, "document.documentElement.outerHTML")
                )
                result = parse_result(dom)
                break
            time.sleep(0.05)
        else:
            raise BrowserStartupError("functional browser harness startup timed out")
    except RuntimeError as exc:
        raise BrowserStartupError(
            f"functional browser DevTools unavailable: {exc}"
        ) from exc
    finally:
        if connection is not None:
            connection.close()
        stderr_text = _close_browser_process(process)
    if result is None:
        raise BrowserStartupError("functional browser harness produced no result")
    return result, stderr_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VEIL generated-review browser E2E without external packages.")
    parser.add_argument("--json", action="store_true", help="Output a JSON result.")
    parser.add_argument("--output", type=Path, help="Optional JSON acceptance record path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    browsers = find_browsers()
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-e2e-", dir=AUDIT_ROOT) as temporary:
        run_dir = Path(temporary)
        db = run_dir / "veil.db"
        html_path = run_dir / "veil-e2e.html"
        keyboard_path = run_dir / "veil-keyboard.html"
        run_db("init-db", "--db", str(db))
        run_db(
            "upsert-rule",
            "--db", str(db),
            "--term", "current state",
            "--preferred", "present state",
            "--preferred-alt-2", "current status",
        )
        run_db("export-html", "--db", str(db), "--html-path", str(html_path))
        shutil.copyfile(html_path, keyboard_path)
        inject_harness(html_path)
        startup_attempts: list[dict[str, object]] = []
        with serve(run_dir) as url:
            keyboard_url = keyboard_path.resolve().as_uri()
            for browser_index, browser in enumerate(browsers):
                browser_started = False
                for attempt in range(1, 3):
                    profile_suffix = f"{browser_index}-{attempt}"
                    try:
                        result, browser_stderr = run_browser(
                            browser,
                            url,
                            run_dir / f"browser-profile-{profile_suffix}",
                        )
                        functional_startup = "ok"
                    except BrowserStartupError as exc:
                        result = {"ok": False, "startup_error": str(exc)}
                        browser_stderr = ""
                        functional_startup = "error"
                    time.sleep(0.5)
                    try:
                        keyboard_result, keyboard_stderr = run_keyboard_browser(
                            browser,
                            keyboard_url,
                            run_dir / f"keyboard-browser-profile-{profile_suffix}",
                        )
                        keyboard_startup = "ok"
                    except BrowserStartupError as exc:
                        keyboard_result = {"ok": False, "startup_error": str(exc)}
                        keyboard_stderr = ""
                        keyboard_startup = "error"
                    except RuntimeError as exc:
                        keyboard_result = {"ok": False, "execution_error": str(exc)}
                        keyboard_stderr = ""
                        keyboard_startup = "ok"
                    startup_attempts.append(
                        {
                            "browser": str(browser),
                            "attempt": attempt,
                            "functional_startup": functional_startup,
                            "keyboard_startup": keyboard_startup,
                        }
                    )
                    if functional_startup == "ok" and keyboard_startup == "ok":
                        browser_started = True
                        break
                    time.sleep(1)
                if browser_started:
                    break

    overall_ok = bool(result.get("ok") and keyboard_result.get("ok"))
    head, dirty = git_state()
    payload = {
        "status": "ok" if overall_ok else "error",
        "browser": str(browser),
        "source_fingerprint_sha256": source_fingerprint(),
        "git_head": head,
        "controlled_sources_dirty": dirty,
        "result": result,
        "functional_startup": functional_startup,
        "keyboard_result": keyboard_result,
        "keyboard_startup": keyboard_startup,
        "startup_attempts": startup_attempts,
        "browser_warnings": [
            line
            for line in (browser_stderr + "\n" + keyboard_stderr).splitlines()
            if line.strip()
        ],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    if args.json:
        print(rendered)
    else:
        print(f"VEIL browser E2E: {payload['status']}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
