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
import subprocess
import sys
import tempfile
import threading
from typing import Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_CLI = PROJECT_ROOT / "shared" / "tools" / "veil-db.py"
AUDIT_ROOT = PROJECT_ROOT / "workspace" / "audit"
RESULT_ATTRIBUTE = "data-veil-e2e"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


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


def find_browser() -> Path:
    for candidate in browser_candidates():
        if candidate.is_file():
            return candidate.resolve()
    raise RuntimeError("No supported Edge/Chrome/Chromium binary found. Set VEIL_BROWSER_BINARY.")


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
    ordinary_diagnostic_empty: false,
    existing_match_diagnostic_empty: false,
    diagnostic_item_count: 0,
    full_review_action_visible: false,
    diagnostic_contract_marked: false,
    locale_english: false,
    locale_japanese: false,
    full_review_copy_success: false,
    full_review_copy_fallback: false,
    explicit_change_exception: false,
    fine_tune_form_loaded: false,
    direct_write_attempts: []
  };
  const pause = () => new Promise(resolve => setTimeout(resolve, 60));
  const analyze = async text => {
    const input = document.getElementById('capture-input');
    input.value = text;
    document.getElementById('capture-analyze-btn').click();
    await pause();
    return [...document.querySelectorAll('.capture-result-line')];
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
    let previewRows = await analyze('root clutter root clutter should be reviewed later.');
    result.ordinary_diagnostic_empty = Boolean(
      previewRows.length === 0 &&
      !document.getElementById('capture-copy-exceptions-btn').classList.contains('hidden')
    );

    previewRows = await analyze('Use current state consistently in every handoff.');
    result.existing_match_diagnostic_empty = Boolean(
      previewRows.length === 0 &&
      !document.getElementById('capture-copy-exceptions-btn').classList.contains('hidden')
    );

    const fullReviewText = 'Use decision boundary consistently. Always use release boundary.';
    previewRows = await analyze(fullReviewText);
    const exceptionTerms = previewRows.map(row => row.textContent.trim());
    result.diagnostic_item_count = previewRows.length;
    result.full_review_action_visible = Boolean(
      previewRows.length === 2 &&
      exceptionTerms.includes('decision boundary') &&
      exceptionTerms.includes('release boundary') &&
      !document.getElementById('capture-copy-exceptions-btn').classList.contains('hidden')
    );
    const diagnosticContract = analyzeCaptureOutcomes(fullReviewText);
    result.diagnostic_contract_marked = Boolean(
      diagnosticContract.contract_version === '1' &&
      diagnosticContract.analysis_mode === 'raw-text-diagnostic' &&
      diagnosticContract.diagnostic_only === true &&
      diagnosticContract.write_allowed === false
    );

    applyLocale('ja');
    result.locale_japanese = Boolean(
      document.documentElement.lang === 'ja' &&
      document.getElementById('capture-copy-exceptions-btn').textContent === '完全なAI確認依頼をコピー'
    );
    applyLocale('en');
    result.locale_english = Boolean(
      document.documentElement.lang === 'en' &&
      document.getElementById('capture-copy-exceptions-btn').textContent === 'Copy complete AI review request'
    );

    let copiedText = '';
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async text => {
          copiedText = text;
        }
      }
    });
    document.getElementById('capture-copy-exceptions-btn').click();
    await pause();
    result.full_review_copy_success = Boolean(
      copiedText.includes('decision boundary') &&
      copiedText.includes('release boundary') &&
      copiedText.includes('contract v2') &&
      copiedText.includes('separate critic pass') &&
      copiedText.includes(fullReviewText) &&
      !copiedText.includes('upsert-rule')
    );

    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: async () => { throw new Error('clipboard denied'); } }
    });
    window.prompt = (message, text) => {
      result.full_review_copy_fallback = Boolean(
        message &&
        text &&
        text.includes('decision boundary') &&
        text.includes('release boundary') &&
        text.includes('contract v2') &&
        text.includes('separate critic pass') &&
        !text.includes('upsert-rule')
      );
      return null;
    };
    document.getElementById('capture-copy-exceptions-btn').click();
    await pause();

    previewRows = await analyze('Change current state to present condition.');
    result.explicit_change_exception = Boolean(
      previewRows.length === 1 &&
      previewRows[0].textContent.trim() === 'current state'
    );
    if (previewRows.length) previewRows[0].click();
    await pause();
    result.fine_tune_form_loaded = Boolean(
      document.getElementById('new-term').value === 'current state' &&
      document.getElementById('new-preferred').value === 'present condition'
    );
  } catch (error) {
    result.error = String(error && error.stack ? error.stack : error);
  }

  result.ok = Boolean(
    result.ordinary_diagnostic_empty &&
    result.existing_match_diagnostic_empty &&
    result.diagnostic_item_count === 2 &&
    result.full_review_action_visible &&
    result.diagnostic_contract_marked &&
    result.locale_english &&
    result.locale_japanese &&
    result.full_review_copy_success &&
    result.full_review_copy_fallback &&
    result.explicit_change_exception &&
    result.fine_tune_form_loaded &&
    result.direct_write_attempts.length === 0 &&
    !result.error
  );
  document.documentElement.setAttribute(
    'data-veil-e2e',
    btoa(JSON.stringify(result))
  );
})();
</script>
"""


def inject_harness(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if RESULT_ATTRIBUTE in content or "</body>" not in content:
        raise RuntimeError("unexpected generated HTML boundary")
    path.write_text(content.replace("</body>", harness_script() + "\n</body>", 1), encoding="utf-8", newline="\n")


@contextmanager
def serve(directory: Path) -> Iterator[str]:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
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


def run_browser(browser: Path, url: str, profile_dir: Path) -> tuple[dict[str, object], str]:
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--virtual-time-budget=4000",
        f"--user-data-dir={profile_dir}",
        "--dump-dom",
        url,
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"browser failed ({completed.returncode}): {completed.stderr}")
    return parse_result(completed.stdout), completed.stderr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run VEIL generated-review browser E2E without external packages.")
    parser.add_argument("--json", action="store_true", help="Output a JSON result.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    browser = find_browser()
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-e2e-", dir=AUDIT_ROOT) as temporary:
        run_dir = Path(temporary)
        db = run_dir / "veil.db"
        html_path = run_dir / "veil-e2e.html"
        run_db("init-db", "--db", str(db))
        run_db(
            "upsert-rule",
            "--db", str(db),
            "--term", "current state",
            "--preferred", "present state",
        )
        run_db("export-html", "--db", str(db), "--html-path", str(html_path))
        inject_harness(html_path)
        with serve(run_dir) as url:
            result, browser_stderr = run_browser(browser, url, run_dir / "browser-profile")

    payload = {
        "status": "ok" if result.get("ok") else "error",
        "browser": str(browser),
        "result": result,
        "browser_warnings": [line for line in browser_stderr.splitlines() if line.strip()],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"VEIL browser E2E: {payload['status']}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
