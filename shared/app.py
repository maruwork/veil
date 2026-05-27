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

LANG_TO_DEEPL = {
    'en-ja':      'JA',
    'en-ko':      'KO',
    'en-zh-hans': 'ZH',
    'en-zh-hant': 'ZH-HANT',
}

def trigger_sync(lang_pair='en-ja'):
    def _run():
        if not os.path.exists(SYNC_SCRIPT):
            return
        try:
            text = get_vocab_prompt(lang_pair).encode("utf-8")
            subprocess.run(
                [sys.executable, SYNC_SCRIPT, "--stdin"],
                input=text, timeout=10, capture_output=True
            )
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()

DB_PATH = os.path.join(os.path.dirname(__file__), "vocab.db")

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

# プロジェクト直下の .env を優先して読む
load_env(os.path.join(os.path.dirname(__file__), ".env"))
# 個人設定パス（任意）
_CUSTOM_ENV = r"C:\Users\f_tan\keys\veil\env\.env"
load_env(_CUSTOM_ENV)

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
        # 新規作成
        c.execute("""
            CREATE TABLE vocab (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                original   TEXT NOT NULL,
                p1         TEXT DEFAULT '',
                p2         TEXT DEFAULT '',
                p3         TEXT DEFAULT '',
                cat        INTEGER DEFAULT 1,
                use_count  INTEGER DEFAULT 0,
                lang_pair  TEXT NOT NULL DEFAULT 'en-ja',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(original, lang_pair)
            )
        """)
    elif 'lang_pair' not in cols:
        # マイグレーション: lang_pair カラム追加 + UNIQUE制約の変更
        conn.executescript("""
            ALTER TABLE vocab RENAME TO vocab_old;
            CREATE TABLE vocab (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                original   TEXT NOT NULL,
                p1         TEXT DEFAULT '',
                p2         TEXT DEFAULT '',
                p3         TEXT DEFAULT '',
                cat        INTEGER DEFAULT 1,
                use_count  INTEGER DEFAULT 0,
                lang_pair  TEXT NOT NULL DEFAULT 'en-ja',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(original, lang_pair)
            );
            INSERT INTO vocab (id, original, p1, p2, p3, cat, use_count, created_at, updated_at, lang_pair)
            SELECT id, original, p1, p2, p3, cat, use_count, created_at, updated_at, 'en-ja'
            FROM vocab_old;
            DROP TABLE vocab_old;
        """)

    for row in SEEDS:
        c.execute(
            "INSERT OR IGNORE INTO vocab (original, p1, p2, p3, cat, lang_pair) VALUES (?,?,?,?,?,'en-ja')",
            row
        )
    conn.commit()
    conn.close()


def get_all_vocab(lang_pair='en-ja'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT id, original, p1, p2, p3, cat, use_count FROM vocab
                 WHERE lang_pair=? ORDER BY use_count DESC, id ASC""", (lang_pair,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "o": r[1], "p1": r[2], "p2": r[3], "p3": r[4], "cat": r[5], "n": r[6]} for r in rows]


def upsert_vocab(original, p1, p2, p3, cat, lang_pair='en-ja'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO vocab (original, p1, p2, p3, cat, lang_pair)
           VALUES (?,?,?,?,?,?)
           ON CONFLICT(original, lang_pair) DO UPDATE SET
             p1=excluded.p1, p2=excluded.p2, p3=excluded.p3,
             cat=excluded.cat, updated_at=CURRENT_TIMESTAMP""",
        (original, p1, p2, p3, cat, lang_pair)
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


def generate_translation(word, lang_pair='en-ja'):
    deepl_key = os.environ.get("DEEPL_API_KEY", "")
    if not deepl_key:
        return None
    target_lang = LANG_TO_DEEPL.get(lang_pair, 'JA')
    req_body = json.dumps({
        "text": [word],
        "source_lang": "EN",
        "target_lang": target_lang
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
            # JA のみカタカナ判定で p2 に振り分け
            if lang_pair == 'en-ja' and is_katakana(result):
                return {"p1": "", "p2": result, "p3": ""}
            return {"p1": result, "p2": "", "p3": ""}
    except Exception:
        return None


def get_vocab_prompt(lang_pair='en-ja'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT original, p1, p2, p3 FROM vocab
        WHERE lang_pair=? AND cat IN (1,5,6,7) AND (p1 != '' OR p2 != '' OR p3 != '')
        ORDER BY use_count DESC, id ASC
    """, (lang_pair,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return ""
    lines = ["以下の語彙ルールに従って出力してください："]
    for original, p1, p2, p3 in rows:
        variants = " / ".join(x for x in [p1, p2, p3] if x)
        lines.append(f"- {original} → {variants}")
    return "\n".join(lines)


def increment_count(original, lang_pair='en-ja'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE vocab SET use_count=use_count+1, updated_at=CURRENT_TIMESTAMP
                 WHERE original=? AND lang_pair=?""", (original, lang_pair))
    conn.commit()
    conn.close()


def _parse_lang(path):
    qs = urllib.parse.urlparse(path).query
    return urllib.parse.parse_qs(qs).get('lang', ['en-ja'])[0]


STATIC_EXTS = {'.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html'}


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

    def _serve_static(self, rel_path):
        base_dir = os.path.normpath(os.path.dirname(__file__))
        target = os.path.normpath(os.path.join(base_dir, rel_path.lstrip('/')))
        if not target.startswith(base_dir + os.sep) and target != base_dir:
            return False
        ext = os.path.splitext(target)[1].lower()
        if ext not in STATIC_EXTS or not os.path.isfile(target):
            return False
        self.send_response(200)
        self.send_header("Content-Type", STATIC_EXTS[ext] + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(target, "rb") as f:
            self.wfile.write(f.read())
        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        base = urllib.parse.urlparse(self.path).path
        if base == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
                self.wfile.write(f.read())
        elif base == "/vocab":
            self.send_json(get_all_vocab(_parse_lang(self.path)))
        elif base == "/vocab/prompt":
            body = get_vocab_prompt(_parse_lang(self.path)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
        elif base == "/manual":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "docs", "manual.html"), "rb") as f:
                self.wfile.write(f.read())
        elif not self._serve_static(base):
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        lang = body.get("lang", "en-ja")

        if self.path == "/vocab/upsert":
            upsert_vocab(
                body.get("original", ""),
                body.get("p1", ""),
                body.get("p2", ""),
                body.get("p3", ""),
                body.get("cat", 1),
                lang
            )
            self.send_json({"ok": True})
            trigger_sync(lang)

        elif self.path == "/vocab/delete":
            delete_vocab(body.get("id"))
            self.send_json({"ok": True})
            trigger_sync(lang)

        elif self.path == "/vocab/increment":
            increment_count(body.get("original", ""), lang)
            self.send_json({"ok": True})

        elif self.path == "/vocab/generate":
            word = body.get("word", "")
            gen = generate_translation(word, lang) or {"p1": "", "p2": "", "p3": ""}
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
