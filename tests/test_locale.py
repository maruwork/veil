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
    assert veil_locale.t("html.capture_title") == "AI確認の復旧"
    assert veil_locale.t("html.capture_none") == (
        "ローカル診断では例外候補が見つかりませんでした。意味を扱うAI確認は完了していません。"
    )
    assert "AIが1回だけ自動実行" in veil_locale.t("sync.runtime_instruction")
    assert "1件も確定されていません" in veil_locale.t("store.batch_write_failed")
    assert veil_locale.t("html.capture_exceptions_copy_btn") == "完全なAI確認依頼をコピー"
    assert veil_locale.t("html.capture_exceptions_prompt_header") == (
        "次の原文にインストール済みVEIL captureを実行してください。"
    )
    assert veil_locale.t("html.capture_exceptions_propose_marker") == "［推奨表現を提案］"
    assert veil_locale.t("html.capture_exceptions_prompt_footer") == (
        "意味フレームcontract v2と独立criticを使い、HTML診断を意味理解の証拠にせず、"
        "承認前は書き込まないでください。"
    )
    assert veil_locale.t("html.capture_description") == (
        "原文を貼り付け、完全なAI確認依頼を1回コピーします。任意のローカル診断は正規表現ベースで、"
        "判断の見落としや誤分類があり得ます。"
    )
    assert veil_locale.t("html.capture_current_label") == "（現在）"
    assert veil_locale.t("html.capture_candidate1_label") == "（推奨）"
    assert veil_locale.t("html.capture_candidate2_label") == "（代替）"
    assert veil_locale.t("html.capture_keep_current") == "現在の表記を維持"
    assert veil_locale.t("html.capture_note") == (
        "復旧専用です。ローカル診断は会話を理解できた証拠ではありません。"
        "書込み前に全文をAIへ渡してください。"
    )
    assert veil_locale.t("html.capture_ready") == (
        "ローカル診断で確認候補が見つかりました。書込み前に全文をAIへ渡してください。"
    )
    assert veil_locale.t("html.capture_loaded", term="status") == (
        "「status」は診断プレビュー由来です。保存前にAIで確認してください。"
    )
    assert veil_locale.t("html.capture_footer") == (
        "ローカルプレビューは診断専用です。通常フローの判断は意味を扱うAI確認が担当します。"
    )
    assert veil_locale.t("html.field_term") == "用語"
    assert veil_locale.t("html.field_preferred") == "推奨表現"
    assert veil_locale.t("html.field_alt2") == "代替表現 1"
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
