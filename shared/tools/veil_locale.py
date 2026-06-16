from __future__ import annotations

import json
import os
from pathlib import Path

_LOCALE_DIR = Path(__file__).resolve().parents[2] / "locale"
_lang: str | None = None
_strings: dict = {}
_fallback: dict = {}


def detect_lang() -> str:
    if os.environ.get("VEIL_LANG"):
        return os.environ["VEIL_LANG"].split("_")[0].split("-")[0].lower()
    config_path = os.path.expanduser("~/.veil/config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, encoding="utf-8") as f:
                cfg = json.load(f)
            if cfg.get("lang"):
                return str(cfg["lang"]).split("_")[0].split("-")[0].lower()
        except Exception:
            pass
    try:
        import locale as _locale
        loc = _locale.getlocale()[0] or ""
        if not loc:
            lang_env = os.environ.get("LANG") or os.environ.get("LC_ALL") or os.environ.get("LANGUAGE") or ""
            loc = lang_env.split(".")[0] if lang_env else ""
    except Exception:
        loc = ""
    if loc.startswith("ja"):
        return "ja"
    return "en"


def _load(lang: str) -> dict:
    path = _LOCALE_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _get_nested(d: dict, key: str) -> str | None:
    cur: object = d
    for part in key.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur if isinstance(cur, str) else None


def t(key: str, **kwargs: object) -> str:
    global _lang, _strings, _fallback
    if _lang is None:
        _lang = detect_lang()
        _strings = _load(_lang)
        if _lang != "en":
            _fallback = _load("en")
    value = _get_nested(_strings, key) or _get_nested(_fallback, key) or key
    if kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value
    return value
