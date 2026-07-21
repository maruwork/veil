"""Tests for shared/tools/veil_locale.py"""
from __future__ import annotations

import pytest

import shared.tools.veil_locale as veil_locale
from shared.tools.veil_html_assets import _HTML_UI_AR, _HTML_UI_EN, _HTML_UI_JA, _HTML_UI_KO, _HTML_UI_ZH_HANS, _HTML_UI_ZH_HANT


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


def test_t_returns_localized_japanese_help_text(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "ja")
    assert veil_locale.t("sync.config_dir_help") == "VEIL の設定ディレクトリ。既定: ~/.veil"
    assert veil_locale.t("sync.db_help") == "SQLite 正準 DB のパス。既定: ~/.veil/veil.db"
    assert veil_locale.t("status.canonical_found", path="C:/tmp/veil.db") == "正準 DB:    C:/tmp/veil.db"
    assert veil_locale.t("db.description") == "VEIL の SQLite 正準 DB CLI。"


def test_t_returns_localized_japanese_capture_text(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "ja")
    assert veil_locale.t("html.capture_none") == "プレビュー候補はありません。"
    assert veil_locale.t("html.capture_description") == (
        "原文を貼り付けると、専門用語より会話内の未定義語を優先するローカル草案プレビューを生成します。"
        "完全な AI 判定ではありません。"
    )
    assert veil_locale.t("html.capture_current_label") == "（現在）"
    assert veil_locale.t("html.capture_candidate1_label") == "（候補 1）"
    assert veil_locale.t("html.capture_candidate2_label") == "（候補 2）"
    assert veil_locale.t("html.capture_keep_current") == "現状維持"
    assert veil_locale.t("html.capture_copy_prompt_btn") == "AI 用プロンプトをコピー"
    assert veil_locale.t("html.capture_copy_prompt_copied") == "AI 用プロンプトをコピーしました。"
    assert veil_locale.t("html.capture_note") == (
        "これは未定義語向けのローカルプレビューです。より厳密な判断が必要な場合は"
        "「AI 用プロンプトをコピー」を使ってチャット側で確認してください。"
    )
    assert veil_locale.t("html.capture_ready") == "草案プレビューを生成しました。行を押すと登録フォームへ反映されます。"
    assert veil_locale.t("html.capture_loaded", term="status") == "「status」を登録フォームへ反映しました。まだ登録は完了していません。"
    assert veil_locale.t("html.capture_footer") == (
        "候補 1 は現在のローカル草案プレビューです。チャット側で見直したい場合は"
        "「AI 用プロンプトをコピー」を使ってください。"
    )
    assert veil_locale.t("html.field_term") == "用語"
    assert veil_locale.t("html.field_preferred") == "推奨表現"
    assert veil_locale.t("html.copy_btn") == "コピー"
    assert veil_locale.t("html.delete_btn") == "削除"
    assert veil_locale.t("html.copy_manual_done") == "手動コピー用プロンプトを開きました。"


def test_t_missing_key_returns_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    result = veil_locale.t("nonexistent.key.foo")
    assert result == "nonexistent.key.foo"


def test_t_formats_kwargs(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    result = veil_locale.t("sync.updated", path="/foo/bar")
    assert "/foo/bar" in result


def test_embedded_html_english_locale_stays_in_sync(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "en")
    expected = {key: value for key, value in _HTML_UI_EN.items() if key != "lang"}
    actual = {key: veil_locale.t(f"html.{key}") for key in expected}

    assert actual == expected


def test_embedded_html_japanese_locale_stays_in_sync(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VEIL_LANG", "ja")
    expected = {key: value for key, value in _HTML_UI_JA.items() if key != "lang"}
    actual = {key: veil_locale.t(f"html.{key}") for key in expected}

    assert actual == expected


def test_embedded_non_english_locales_do_not_reference_english_prompt_label() -> None:
    for ui in (_HTML_UI_KO, _HTML_UI_ZH_HANS, _HTML_UI_ZH_HANT, _HTML_UI_AR):
        assert "Copy AI Prompt" not in ui["capture_note"]
        assert "Copy AI Prompt" not in ui["capture_footer"]
