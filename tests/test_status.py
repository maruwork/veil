"""Tests for shared/runtime/veil-status.py"""
from __future__ import annotations

import json
from pathlib import Path

from .helpers import PROJECT_ROOT, db_cmd, status_cmd


def test_version():
    r = status_cmd("--version", check=False)
    assert "1.0.4" in r.stdout


def test_json_db_missing(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--json")
    payload = json.loads(r.stdout)
    assert payload["db_exists"] is False
    assert r.returncode == 0


def test_json_db_present(tmp_path: Path):
    db = str(tmp_path / "veil.db")
    from .helpers import db_cmd
    db_cmd("init-db", "--db", db)
    r = status_cmd("--db", db, "--json")
    payload = json.loads(r.stdout)
    assert payload["db_exists"] is True
    assert payload["rule_count"] == 0


def test_check_db_missing_exits_1(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--check", "--json", check=False)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    assert payload["has_error"] is True


def test_check_db_missing_text_output(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--check", check=False)
    assert r.returncode == 1
    assert "[ERROR]" in r.stdout


def test_json_db_corrupted(tmp_path: Path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    r = status_cmd("--db", str(db), "--json")
    payload = json.loads(r.stdout)
    assert payload["db_exists"] is True
    assert payload["db_error"]["reason"] == "store.db_unreadable"


def test_check_db_corrupted_exits_1(tmp_path: Path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    r = status_cmd("--db", str(db), "--check", "--json", check=False)
    payload = json.loads(r.stdout)
    assert r.returncode == 1
    assert payload["has_error"] is True


def test_check_complete_setup_exits_0(tmp_path: Path):
    home = tmp_path / "home"
    veil_dir = home / ".veil"
    claude_dir = home / ".claude" / "commands"
    codex_dir = home / ".agents" / "skills" / "veil-capture"
    veil_dir.mkdir(parents=True)
    claude_dir.mkdir(parents=True)
    codex_dir.mkdir(parents=True)

    env = {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "HOMEDRIVE": home.drive,
        "HOMEPATH": home.as_posix()[len(home.drive):].replace("/", "\\"),
    }

    db = veil_dir / "veil.db"
    html = veil_dir / "veil.html"
    target = tmp_path / "CLAUDE.md"
    target.write_text("# Target\n", encoding="utf-8")
    (claude_dir / "veil-capture.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "claude-code" / "veil-capture.md").read_bytes())
    (codex_dir / "SKILL.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "codex" / "veil-capture" / "SKILL.md").read_bytes())
    (veil_dir / "targets.json").write_text(json.dumps([str(target)]), encoding="utf-8")

    db_cmd("init-db", "--db", str(db), env_overrides=env)
    db_cmd("upsert-rule", "--db", str(db), "--term", "current state", "--preferred", "present state", env_overrides=env)
    db_cmd("export-html", "--db", str(db), "--html-path", str(html), env_overrides=env)

    r = status_cmd("--db", str(db), "--check", "--json", check=False, env_overrides=env)
    payload = json.loads(r.stdout)
    assert r.returncode == 0
    assert payload["has_error"] is False
    assert any(item["label"].endswith("veil.db") and item["level"] == "OK" for item in payload["items"])
    assert any(item["label"].endswith("veil.html") and item["level"] == "OK" for item in payload["items"])


def test_check_brand_new_install_without_targets_stays_non_error(tmp_path: Path):
    home = tmp_path / "home"
    veil_dir = home / ".veil"
    claude_dir = home / ".claude" / "commands"
    codex_dir = home / ".agents" / "skills" / "veil-capture"
    veil_dir.mkdir(parents=True)
    claude_dir.mkdir(parents=True)
    codex_dir.mkdir(parents=True)

    env = {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "HOMEDRIVE": home.drive,
        "HOMEPATH": home.as_posix()[len(home.drive):].replace("/", "\\"),
    }

    db = veil_dir / "veil.db"
    html = veil_dir / "veil.html"
    (claude_dir / "veil-capture.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "claude-code" / "veil-capture.md").read_bytes())
    (codex_dir / "SKILL.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "codex" / "veil-capture" / "SKILL.md").read_bytes())

    db_cmd("init-db", "--db", str(db), env_overrides=env)
    db_cmd("export-html", "--db", str(db), "--html-path", str(html), env_overrides=env)

    r = status_cmd("--db", str(db), "--check", "--json", check=False, env_overrides=env)
    payload = json.loads(r.stdout)

    assert r.returncode == 0
    assert payload["has_error"] is False
    assert any(item["label"].endswith("targets.json") and item["level"] == "WARN" for item in payload["items"])


def test_check_missing_required_delivery_members_exits_1(tmp_path: Path):
    home = tmp_path / "home"
    veil_dir = home / ".veil"
    veil_dir.mkdir(parents=True)
    env = {
        "HOME": str(home), "USERPROFILE": str(home),
        "HOMEDRIVE": home.drive, "HOMEPATH": home.as_posix()[len(home.drive):].replace("/", "\\"),
    }
    db = veil_dir / "veil.db"
    db_cmd("init-db", "--db", str(db), env_overrides=env)
    result = status_cmd("--db", str(db), "--check", "--json", check=False, env_overrides=env)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["has_error"] is True
    assert sum(item["level"] == "MISSING" for item in payload["items"]) == 3


def test_check_stale_installed_skill_exits_1(tmp_path: Path):
    home = tmp_path / "home"
    veil_dir = home / ".veil"
    claude_dir = home / ".claude" / "commands"
    codex_dir = home / ".agents" / "skills" / "veil-capture"
    veil_dir.mkdir(parents=True)
    claude_dir.mkdir(parents=True)
    codex_dir.mkdir(parents=True)
    env = {
        "HOME": str(home), "USERPROFILE": str(home),
        "HOMEDRIVE": home.drive, "HOMEPATH": home.as_posix()[len(home.drive):].replace("/", "\\"),
    }
    db = veil_dir / "veil.db"
    html = veil_dir / "veil.html"
    db_cmd("init-db", "--db", str(db), env_overrides=env)
    db_cmd("export-html", "--db", str(db), "--html-path", str(html), env_overrides=env)
    (claude_dir / "veil-capture.md").write_text("stale", encoding="utf-8")
    (codex_dir / "SKILL.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "codex" / "veil-capture" / "SKILL.md").read_bytes())
    result = status_cmd("--db", str(db), "--check", "--json", check=False, env_overrides=env)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(item["label"].endswith("veil-capture.md") and item["level"] == "STALE" for item in payload["items"])


def test_check_malformed_html_manifest_is_error(tmp_path: Path):
    home = tmp_path / "home"
    veil_dir = home / ".veil"
    claude_dir = home / ".claude" / "commands"
    codex_dir = home / ".agents" / "skills" / "veil-capture"
    veil_dir.mkdir(parents=True)
    claude_dir.mkdir(parents=True)
    codex_dir.mkdir(parents=True)
    env = {"HOME": str(home), "USERPROFILE": str(home), "HOMEDRIVE": home.drive, "HOMEPATH": home.as_posix()[len(home.drive):].replace("/", "\\")}
    db = veil_dir / "veil.db"
    html = veil_dir / "veil.html"
    db_cmd("init-db", "--db", str(db), env_overrides=env)
    db_cmd("export-html", "--db", str(db), "--html-path", str(html), env_overrides=env)
    html.write_text(html.read_text(encoding="utf-8").replace('"format":1', '"format":'), encoding="utf-8")
    (claude_dir / "veil-capture.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "claude-code" / "veil-capture.md").read_bytes())
    (codex_dir / "SKILL.md").write_bytes((Path(PROJECT_ROOT) / "skills" / "codex" / "veil-capture" / "SKILL.md").read_bytes())
    result = status_cmd("--db", str(db), "--check", "--json", check=False, env_overrides=env)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert any(item["label"].endswith("veil.html") and item["level"] == "ERROR" for item in payload["items"])
