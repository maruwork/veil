import sqlite3
import json
import re
import os
import importlib.util
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from veil_audit_core import VALID_STATUSES, audit_rows, filter_results, summarize_results

DB_PATH = os.path.join(os.path.dirname(__file__), "vocab.db")
CURRENT_COLUMNS = [
    'id', 'original', 'p1', 'p2', 'p3',
    'cat', 'use_count', 'created_at', 'updated_at'
]
DEFAULT_SQL = {
    'id': "NULL",
    'original': "''",
    'p1': "''",
    'p2': "''",
    'p3': "''",
    'cat': "1",
    'use_count': "0",
    'created_at': "CURRENT_TIMESTAMP",
    'updated_at': "CURRENT_TIMESTAMP",
}

SEEDS = [
    ("close record",  "完了記録",   "",          "",       1),
    ("close",         "完了",       "クローズ",  "",       1),
    ("current state", "今の状態",   "",          "",       1),
    ("blocker",       "障害",       "ブロッカー","",       1),
    ("stale blocker", "古くなった障害", "",      "",       1),
    ("verification",  "検証",       "",          "",       1),
    ("summary",       "集計",       "サマリー",  "",       1),
]


def load_normalize_helper():
    script_path = os.path.join(os.path.dirname(__file__), "veil-normalize.py")
    spec = importlib.util.spec_from_file_location("veil_normalize_helper", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("veil-normalize.py を読み込めません。")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NORMALIZE_HELPER = load_normalize_helper()
CURRENT_SEED_SET = {row[0] for row in SEEDS}


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
    elif cols and cols != CURRENT_COLUMNS:
        # Rebuild into the current single-surface schema while preserving known fields.
        select_exprs = []
        for name in CURRENT_COLUMNS:
            select_exprs.append(name if name in cols else f"{DEFAULT_SQL[name]} AS {name}")
        select_sql = ", ".join(select_exprs)
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
        """)
        c.execute(
            "INSERT OR IGNORE INTO vocab ({cols}) SELECT {select_sql} FROM vocab_old".format(
                cols=", ".join(CURRENT_COLUMNS),
                select_sql=select_sql,
            )
        )
        c.execute("DROP TABLE vocab_old")

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


def get_audit_rows():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, original, p1, p2, p3, cat, use_count FROM vocab ORDER BY use_count DESC, id ASC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0], "original": r[1], "p1": r[2], "p2": r[3], "p3": r[4],
            "cat": r[5], "use_count": r[6],
        }
        for r in rows
    ]


def get_audit_payload(statuses=None):
    results = audit_rows(get_audit_rows(), CURRENT_SEED_SET, NORMALIZE_HELPER.classify_candidate_hint)
    filtered = filter_results(results, statuses)
    return {
        "summary": summarize_results(results),
        "filters": {"statuses": statuses or []},
        "results": filtered,
    }


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
    if vocab_id is None:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM vocab WHERE id=?", (vocab_id,))
    conn.commit()
    conn.close()


def delete_vocab_batch(vocab_ids):
    ids = [int(v) for v in vocab_ids if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
    if not ids:
        return 0
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executemany("DELETE FROM vocab WHERE id=?", [(v,) for v in ids])
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted


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
        parsed = urllib.parse.urlparse(self.path)
        base = parsed.path
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
        elif base == "/vocab/audit":
            query = urllib.parse.parse_qs(parsed.query)
            raw_statuses = query.get("status", [])
            statuses = [s for s in raw_statuses if s in VALID_STATUSES]
            self.send_json(get_audit_payload(statuses))
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

        elif self.path == "/vocab/delete":
            delete_vocab(body.get("id"))
            self.send_json({"ok": True})

        elif self.path == "/vocab/delete-batch":
            deleted_count = delete_vocab_batch(body.get("ids", []))
            self.send_json({"ok": True, "deleted_count": deleted_count})

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
