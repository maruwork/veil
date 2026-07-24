"""Tests for CLI localization and embedded HTML locale packs."""
from __future__ import annotations

import pytest

import shared.tools.veil_locale as veil_locale
from shared.tools.veil_html_assets import (
    _HTML_UI_AR,
    _HTML_UI_BY_LANG,
    _HTML_UI_EN,
    _HTML_UI_JA,
    _HTML_UI_KO,
    _HTML_UI_ZH_HANS,
    _HTML_UI_ZH_HANT,
    get_html_ui_for_lang,
)


@pytest.fixture(autouse=True)
def reset_locale_cache():
    veil_locale._lang = None
    veil_locale._strings = {}
    veil_locale._fallback = {}
    yield
    veil_locale._lang = None
    veil_locale._strings = {}
    veil_locale._fallback = {}


def test_detect_lang_env_en(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "en")
    assert veil_locale.detect_lang() == "en"


def test_detect_lang_env_ja(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "ja")
    assert veil_locale.detect_lang() == "ja"


def test_detect_lang_normalizes_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "JA_JP")
    assert veil_locale.detect_lang() == "ja"


def test_t_returns_localized_cli_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "en")
    assert veil_locale.t("db.maintain_batch_help") == (
        "Change or retire existing rules from validated JSON."
    )
    monkeypatch.setenv("VEIL_LANG", "ja")
    veil_locale._lang = None
    veil_locale._strings = {}
    veil_locale._fallback = {}
    assert veil_locale.t("db.maintain_batch_help") == (
        "検証済み JSON から既存ルールを変更または廃止する。"
    )


def test_t_missing_key_returns_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "en")
    assert veil_locale.t("nonexistent.key.foo") == "nonexistent.key.foo"


def test_t_formats_kwargs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VEIL_LANG", "en")
    assert "/foo/bar" in veil_locale.t("sync.updated", path="/foo/bar")


def test_embedded_html_supports_only_complete_locales() -> None:
    assert set(_HTML_UI_BY_LANG) == {"en", "ja"}
    assert get_html_ui_for_lang("ja-JP") == _HTML_UI_JA
    assert get_html_ui_for_lang("en-US") == _HTML_UI_EN
    assert get_html_ui_for_lang("ko") == _HTML_UI_EN


def test_embedded_html_locale_packs_have_identical_keys() -> None:
    assert set(_HTML_UI_EN) == set(_HTML_UI_JA)
    assert _HTML_UI_JA["review_title"] == "会話を確認する"
    assert _HTML_UI_JA["change_title"] == "ルール変更を依頼する"
    assert _HTML_UI_JA["show_alternatives"] == "代替表現を表示"


def test_compatibility_exports_fall_back_to_english() -> None:
    for ui in (_HTML_UI_KO, _HTML_UI_ZH_HANS, _HTML_UI_ZH_HANT, _HTML_UI_AR):
        assert ui is _HTML_UI_EN
