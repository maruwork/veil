"""Tests for shared/tools/veil_locale.py"""
from __future__ import annotations

import pytest

import shared.tools.veil_locale as veil_locale


@pytest.fixture(autouse=True)
def reset_locale_cache():
    """Reset module-level cache so each test starts fresh."""
    veil_locale._lang = None
    veil_locale._strings = {}
    veil_locale._fallback = {}
    yield
    veil_locale._lang = None
    veil_locale._strings = {}
    veil_locale._fallback = {}


def test_detect_lang_env_en(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    assert veil_locale.detect_lang() == "en"


def test_detect_lang_env_ja(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "ja")
    assert veil_locale.detect_lang() == "ja"


def test_detect_lang_normalizes_locale(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "JA_JP")
    assert veil_locale.detect_lang() == "ja"


def test_t_returns_english_string(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    result = veil_locale.t("sync.description")
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != "sync.description"


def test_t_returns_japanese_string(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "ja")
    result = veil_locale.t("sync.description")
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != "sync.description"


def test_t_missing_key_returns_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    result = veil_locale.t("nonexistent.key.foo")
    assert result == "nonexistent.key.foo"


def test_t_formats_kwargs(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    result = veil_locale.t("sync.updated", path="/foo/bar")
    assert "/foo/bar" in result
