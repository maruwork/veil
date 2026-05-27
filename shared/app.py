import sqlite3
import json
import re
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = os.path.join(os.path.dirname(__file__), "vocab.db")
ENV_PATH = r"C:\Users\f_tan\keys\veil\env\.env"

def load_env(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

load_env(ENV_PATH)

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
    c.execute("""
        CREATE TABLE IF NOT EXISTS vocab (
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


def is_katakana(text):
    kat = sum(1 for c in text if '゠' <= c <= 'ヿ')
    return kat > len(text) * 0.5 if text else False


def generate_translation(word):
    deepl_key = os.environ.get("DEEPL_API_KEY", "")
    if not deepl_key:
        return None
    import urllib.request
    req_body = json.dumps({
        "text": [word],
        "source_lang": "EN",
        "target_lang": "JA"
    }).encode()
    req = urllib.request.Request(
        "https://api-free.deepl.com/v2/translate",
        data=req_body,
        headers={
            "Authorization": f"DeepL-Auth-Key {deepl_key}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            result = data["translations"][0]["text"]
            if is_katakana(result):
                return {"p1": "", "p2": result, "p3": ""}
            return {"p1": result, "p2": "", "p3": ""}
    except Exception:
        return None


def increment_count(original):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE vocab SET use_count=use_count+1, updated_at=CURRENT_TIMESTAMP WHERE original=?", (original,))
    conn.commit()
    conn.close()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/style.css":
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "style.css"), "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/main.js":
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "main.js"), "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/vocab":
            self.send_json(get_all_vocab())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        if self.path == "/vocab/upsert":
            upsert_vocab(
                body.get("original", ""),
                body.get("p1", ""),
                body.get("p2", ""),
                body.get("p3", ""),
                body.get("cat", 1)
            )
            self.send_json({"ok": True})

        elif self.path == "/vocab/delete":
            delete_vocab(body.get("id"))
            self.send_json({"ok": True})

        elif self.path == "/vocab/increment":
            increment_count(body.get("original", ""))
            self.send_json({"ok": True})

        elif self.path == "/vocab/generate":
            word = body.get("word", "")
            gen = generate_translation(word) or {"p1": "", "p2": "", "p3": ""}
            self.send_json(gen)

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    init_db()
    port = 8080
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"VEIL起動: http://localhost:{port}")
    server.serve_forever()
