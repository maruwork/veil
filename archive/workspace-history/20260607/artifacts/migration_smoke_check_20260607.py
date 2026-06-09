import os
import sqlite3
import tempfile
import importlib.util

spec = importlib.util.spec_from_file_location("appmod", "app.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fd, path = tempfile.mkstemp(suffix=".db")
os.close(fd)

try:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE vocab ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "original TEXT UNIQUE NOT NULL, "
        "p1 TEXT DEFAULT '', "
        "p2 TEXT DEFAULT '', "
        "p3 TEXT DEFAULT '', "
        "cat INTEGER DEFAULT 1, "
        "use_count INTEGER DEFAULT 0)"
    )
    conn.execute(
        "INSERT INTO vocab (original, p1, cat, use_count) "
        "VALUES (?, ?, ?, ?)",
        ("current state", "今の状態", 1, 2),
    )
    conn.commit()
    conn.close()

    mod.DB_PATH = path
    mod.init_db()

    conn = sqlite3.connect(path)
    row = conn.execute(
        "SELECT original, p1, cat, use_count, created_at, updated_at "
        "FROM vocab WHERE original = ?",
        ("current state",),
    ).fetchone()
    conn.close()
    print(row[0], row[1], row[2], row[3], bool(row[4]), bool(row[5]))
finally:
    if os.path.exists(path):
        os.remove(path)
