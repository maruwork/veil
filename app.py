import sqlite3
import json
import re
import os
import sys
import threading
import subprocess
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

SYNC_SCRIPT = os.path.join(os.path.dirname(__file__), "veil-sync.py")
SYNC_LOG = os.path.join(os.path.expanduser("~"), ".veil", "sync-error.log")


def _log_sync_error(msg):
    print(msg, file=sys.stderr)
    try:
        os.makedirs(os.path.dirname(SYNC_LOG), exist_ok=True)
        with open(SYNC_LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def trigger_sync():
    def _run():
        if not os.path.exists(SYNC_SCRIPT):
            return
        try:
            text = get_vocab_prompt().encode("utf-8")
            result = subprocess.run(
                [sys.executable, SYNC_SCRIPT, "--stdin"],
                input=text, timeout=10, capture_output=True
            )
            if result.returncode != 0:
                msg = result.stderr.decode("utf-8", errors="replace").strip()
                _log_sync_error(f"[veil-sync] 同期失敗 (exit {result.returncode}): {msg}")
        except subprocess.TimeoutExpired:
            _log_sync_error("[veil-sync] 同期タイムアウト")
        except Exception as e:
            _log_sync_error(f"[veil-sync] 同期エラー: {e}")
    threading.Thread(target=_run, daemon=True).start()

DB_PATH = os.path.join(os.path.dirname(__file__), "vocab.db")

SEEDS = [
    ("active",        "アクティブ", "",          "",       1),
    ("close record",  "完了記録",   "",          "",       1),
    ("close",         "完了",       "クローズ",  "",       1),
    ("live",          "実行中",     "",          "",       1),
    ("stale",         "古くなった", "",          "",       1),
    ("pass",          "通過",       "パス",      "合格",   1),
    ("passed",        "通過",       "パス",      "合格",   1),
    ("reroute",       "切り替え",   "リルート",  "",       7),
    ("stale blocker", "古くなった障害", "",      "",       1),
    ("blocker",       "障害",       "ブロッカー","",       1),
    ("judgment",      "判定",       "",          "",       1),
    ("canon",         "仕様",       "",          "",       6),
    ("record",        "記録",       "",          "",       1),
    ("side program",  "別プログラム","",         "",       1),
    ("executable",    "実行可能な", "",          "",       1),
    ("verification",  "検証",       "",          "",       1),
    ("claim",         "申請",       "",          "",       1),
    ("verdict",       "判定値",     "",          "",       1),
    ("current",       "現行の",     "",          "",       1),
    ("workflow",      "ワークフロー","",         "",       1),
    ("summary",       "集計",       "サマリー",  "",       1),
    ("aggregate",     "集計",       "",          "",       1),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("PRAGMA table_info(vocab)")
    cols = [r[1] for r in c.fetchall()]

    if not cols:
        c.execute("""
            CREATE TABLE vocab (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                original   TEXT UNIQUE NOT NULL,
                p1         TEXT DEFAULT '',
                p2         TEXT DEFAULT '',
                p3         TEXT DEFAULT '',
                cat        INTEGER DEFAULT 1,
                use_count  INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    elif 'lang_pair' in cols:
        # マイグレーション: lang_pair カラムを削除（en-ja のみ保持）
        conn.executescript("""
            ALTER TABLE vocab RENAME TO vocab_old;
            CREATE TABLE vocab (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                original   TEXT UNIQUE NOT NULL,
                p1         TEXT DEFAULT '',
                p2         TEXT DEFAULT '',
                p3         TEXT DEFAULT '',
                cat        INTEGER DEFAULT 1,
                use_count  INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT OR IGNORE INTO vocab (id, original, p1, p2, p3, cat, use_count, created_at, updated_at)
            SELECT id, original, p1, p2, p3, cat, use_count, created_at, updated_at
            FROM vocab_old WHERE lang_pair = 'en-ja';
            DROP TABLE vocab_old;
        """)

    for row in SEEDS:
        c.execute(
            "INSERT OR IGNORE INTO vocab (original, p1, p2, p3, cat) VALUES (?,?,?,?,?)",
            row
        )
    conn.commit()
    conn.close()


def get_all_vocab():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, original, p1, p2, p3, cat, use_count FROM vocab ORDER BY use_count DESC, id ASC")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "o": r[1], "p1": r[2], "p2": r[3], "p3": r[4], "cat": r[5], "n": r[6]} for r in rows]


def upsert_vocab(original, p1, p2, p3, cat):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO vocab (original, p1, p2, p3, cat)
           VALUES (?,?,?,?,?)
           ON CONFLICT(original) DO UPDATE SET
             p1=excluded.p1, p2=excluded.p2, p3=excluded.p3,
             cat=excluded.cat, updated_at=CURRENT_TIMESTAMP""",
        (original, p1, p2, p3, cat)
    )
    conn.commit()
    conn.close()


def delete_vocab(vocab_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM vocab WHERE id=?", (vocab_id,))
    conn.commit()
    conn.close()


def get_vocab_prompt():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT original, p1 FROM vocab
        WHERE cat IN (1,5,6,7) AND p1 != ''
        ORDER BY use_count DESC, id ASC
    """)
    rows = c.fetchall()
    conn.close()
    if not rows:
        return ""
    lines = ["以下の語彙ルールに従って出力してください："]
    for original, p1 in rows:
        lines.append(f"- {original} → {p1}")
    return "\n".join(lines)


def increment_count(original):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE vocab SET use_count=use_count+1, updated_at=CURRENT_TIMESTAMP WHERE original=?", (original,))
    conn.commit()
    conn.close()


STATIC_EXTS = {'.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html'}
UI_DIR = os.path.join(os.path.dirname(__file__), "ui")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _cors_origin(self):
        return "http://127.0.0.1:8080"

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, rel_path):
        base_dir = os.path.normpath(UI_DIR)
        target = os.path.normpath(os.path.join(base_dir, rel_path.lstrip('/')))
        if not target.lower().startswith((base_dir + os.sep).lower()) and target.lower() != base_dir.lower():
            return False
        ext = os.path.splitext(target)[1].lower()
        if ext not in STATIC_EXTS or not os.path.isfile(target):
            return False
        self.send_response(200)
        self.send_header("Content-Type", STATIC_EXTS[ext] + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.end_headers()
        with open(target, "rb") as f:
            self.wfile.write(f.read())
        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", self._cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        base = urllib.parse.urlparse(self.path).path
        if base == "/":
            try:
                with open(os.path.join(UI_DIR, "index.html"), "rb") as f:
                    body = f.read()
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif base == "/vocab":
            self.send_json(get_all_vocab())
        elif base == "/vocab/prompt":
            body = get_vocab_prompt().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", self._cors_origin())
            self.end_headers()
            self.wfile.write(body)
        elif base == "/manual":
            try:
                with open(os.path.join(os.path.dirname(__file__), "docs", "manual.html"), "rb") as f:
                    body = f.read()
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif not self._serve_static(base):
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(min(length, 1_048_576)))
        except (ValueError, json.JSONDecodeError):
            self.send_response(400)
            self.end_headers()
            return

        if self.path == "/vocab/upsert":
            original = body.get("original", "").strip()
            if not original:
                self.send_json({"error": "original is required"}, status=400)
                return
            upsert_vocab(
                original,
                body.get("p1", ""),
                body.get("p2", ""),
                body.get("p3", ""),
                body.get("cat", 1),
            )
            self.send_json({"ok": True})
            trigger_sync()

        elif self.path == "/vocab/delete":
            delete_vocab(body.get("id"))
            self.send_json({"ok": True})
            trigger_sync()

        elif self.path == "/vocab/increment":
            increment_count(body.get("original", ""))
            self.send_json({"ok": True})

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    init_db()
    port = 8080
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"VEIL起動 (port {port}) — http://127.0.0.1:{port}")
    server.serve_forever()
