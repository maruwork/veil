import asyncio
import base64
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets


ROOT = Path(r"C:\Users\f_tan\project\veil")
OUT = ROOT / "workspace"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
PORT = 9222
URL = "http://127.0.0.1:8080"


class CDPClient:
    def __init__(self, websocket):
        self.websocket = websocket
        self.next_id = 1

    async def call(
        self,
        method: str,
        params: dict | None = None,
        timeout: float = 10.0,
        session_id: str | None = None,
    ):
        cid = self.next_id
        self.next_id += 1
        payload = {"id": cid, "method": method, "params": params or {}}
        if session_id:
            payload["sessionId"] = session_id
        await self.websocket.send(json.dumps(payload))
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            msg = json.loads(raw)
            if msg.get("id") == cid:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})
        raise TimeoutError(f"Timed out waiting for {method}")

    async def wait_for_event(self, method: str, timeout: float = 10.0, session_id: str | None = None):
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            msg = json.loads(raw)
            if msg.get("method") == method and (session_id is None or msg.get("sessionId") == session_id):
                return msg
        raise TimeoutError(f"Timed out waiting for event {method}")


def wait_http(url: str, timeout: float = 10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as res:
                return res.read().decode("utf-8")
        except Exception:
            time.sleep(0.5)
    raise TimeoutError(f"HTTP not ready: {url}")


def launch_edge():
    user_data_dir = Path(tempfile.mkdtemp(prefix="veil-edge-"))
    proc = subprocess.Popen(
        [
            str(EDGE),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-allow-origins=*",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={user_data_dir}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc, user_data_dir


def get_browser_ws_url():
    raw = wait_http(f"http://127.0.0.1:{PORT}/json/version")
    data = json.loads(raw)
    return data["webSocketDebuggerUrl"]


async def eval_js(cdp: CDPClient, expression: str, session_id: str):
    result = await cdp.call(
        "Runtime.evaluate",
        {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        },
        timeout=15,
        session_id=session_id,
    )
    return result.get("result", {}).get("value")


async def save_screenshot(cdp: CDPClient, name: str, session_id: str):
    data = (await cdp.call("Page.captureScreenshot", {"format": "png"}, timeout=15, session_id=session_id))["data"]
    path = OUT / name
    path.write_bytes(base64.b64decode(data))
    return str(path)


async def run():
    proc, user_data_dir = launch_edge()
    report = {}
    try:
        ws_url = get_browser_ws_url()
        async with websockets.connect(
            ws_url,
            max_size=20_000_000,
            origin=f"http://127.0.0.1:{PORT}",
        ) as websocket:
            cdp = CDPClient(websocket)
            target_id = (await cdp.call("Target.createTarget", {"url": "about:blank"}))["targetId"]
            session_id = (await cdp.call("Target.attachToTarget", {"targetId": target_id, "flatten": True}))["sessionId"]
            await cdp.call("Page.enable", session_id=session_id)
            await cdp.call("Runtime.enable", session_id=session_id)
            await cdp.call("Page.navigate", {"url": URL}, session_id=session_id)
            await cdp.wait_for_event("Page.loadEventFired", timeout=15, session_id=session_id)
            await asyncio.sleep(1.0)

            report["initial_dom"] = await eval_js(
                cdp,
                """
                JSON.stringify({
                  title: document.title,
                  reviewButton: document.getElementById('btn-review-next')?.textContent?.trim(),
                  dropButton: document.getElementById('btn-drop-bulk')?.textContent?.trim(),
                  auditSummary: document.getElementById('audit-summary')?.textContent?.trim(),
                  listText: Array.from(document.querySelectorAll('#vlist .vi')).slice(0, 4).map(el => el.textContent.trim()),
                })
                """,
                session_id,
            )
            report["initial_screenshot"] = await save_screenshot(cdp, "ui_live_initial_20260607.png", session_id)

            await eval_js(cdp, "focusNextReview();", session_id)
            await asyncio.sleep(0.5)
            report["review_dom"] = await eval_js(
                cdp,
                """
                JSON.stringify({
                  currentReview: document.getElementById('current-review')?.textContent?.trim(),
                  currentReviewDisplay: getComputedStyle(document.getElementById('current-review')).display,
                  orig: document.getElementById('orig')?.value,
                  pref1: document.getElementById('pref1')?.value,
                  highlighted: !!document.querySelector('#vlist .vi-current-review'),
                })
                """,
                session_id,
            )
            report["review_screenshot"] = await save_screenshot(cdp, "ui_live_review_20260607.png", session_id)

            await eval_js(
                cdp,
                """
                (() => {
                  const orig = document.getElementById('orig');
                  orig.value = 'manual-switch';
                  orig.dispatchEvent(new Event('input', { bubbles: true }));
                  return true;
                })()
                """,
                session_id,
            )
            await asyncio.sleep(0.5)
            report["manual_switch_dom"] = await eval_js(
                cdp,
                """
                JSON.stringify({
                  currentReview: document.getElementById('current-review')?.textContent?.trim(),
                  currentReviewDisplay: getComputedStyle(document.getElementById('current-review')).display,
                  orig: document.getElementById('orig')?.value,
                  highlighted: !!document.querySelector('#vlist .vi-current-review'),
                })
                """,
                session_id,
            )
            report["manual_switch_screenshot"] = await save_screenshot(cdp, "ui_live_manual_switch_20260607.png", session_id)

            report["bulk_confirm_message"] = await eval_js(
                cdp,
                """
                (() => {
                  let captured = null;
                  const origConfirm = window.confirm;
                  window.confirm = (msg) => { captured = msg; return false; };
                  bulkDeleteDropCandidates();
                  window.confirm = origConfirm;
                  return captured;
                })()
                """,
                session_id,
            )

            report["sort_dom"] = await eval_js(
                cdp,
                """
                (() => {
                  toggleSort();
                  return JSON.stringify({
                    sortButton: document.getElementById('btn-sort')?.textContent?.trim(),
                    firstItems: Array.from(document.querySelectorAll('#vlist .vi .vo')).slice(0, 4).map(el => el.textContent.trim()),
                  });
                })()
                """,
                session_id,
            )

            print(json.dumps(report, ensure_ascii=False, indent=2))
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        shutil.rmtree(user_data_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(run())
