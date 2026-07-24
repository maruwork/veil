from __future__ import annotations

from pathlib import Path


_HTML_TEMPLATE = Path(__file__).with_name("veil_review_template.html").read_text(encoding="utf-8")


_HTML_UI_EN: dict[str, str] = {
    "lang": "en",
    "title": "VEIL rulebook",
    "rulebook_title": "VEIL rulebook",
    "rulebook_description": "Review the terminology currently delivered to your AI tools. This page never changes the canonical store directly.",
    "generated_label": "Generated",
    "rulebook_heading": "Registered rules",
    "search_placeholder": "Search source or preferred wording...",
    "no_match": "No matching rule. To review new wording, use Review a conversation below.",
    "empty_rulebook": "No rules are registered yet. VEIL normally asks only when a durable choice is needed.",
    "actions_title": "Actions",
    "actions_description": "Use these only for an intentional review or maintenance request. Normal task-close review runs in the installed VEIL Skill.",
    "review_title": "Review a conversation",
    "review_description": "Recovery route: copy the complete conversation into one request for the installed VEIL Skill.",
    "review_label": "Exact conversation text",
    "review_placeholder": "Paste the exact conversation to review...",
    "review_copy_btn": "Copy review request",
    "review_copied": "Review request copied. Paste it into an AI chat with VEIL installed.",
    "review_request_header": "Run the installed VEIL capture workflow on the exact conversation below.",
    "review_request_instruction": "Use evidence-backed semantic frames (contract v2) and a separate critic pass. Keep automatic outcomes silent, ask at most one combined question for durable exceptions, and do not write before acceptance.",
    "change_title": "Request a rule change",
    "change_description": "Select Request change on a registered rule. Copying a request does not save the change.",
    "change_empty": "Choose Request change on a rule above.",
    "selected_term_label": "Source wording: ",
    "selected_preferred_label": "Current preferred wording: ",
    "change_intent_label": "Requested operation",
    "change_option": "Change preferred wording",
    "retire_option": "Retire this rule",
    "requested_preferred_label": "New preferred wording",
    "change_reason_label": "Reason",
    "change_reason_help": "Optional. Keep it concise.",
    "change_copy_btn": "Copy change request",
    "cancel_btn": "Cancel",
    "request_change_btn": "Request change",
    "request_change_for": "Request a change for {term}",
    "change_missing": "Enter the new preferred wording.",
    "change_copied": "Change request copied. The rule changes only after confirmation in VEIL.",
    "change_request_header": "Run the installed VEIL rule-maintenance workflow for the request below.",
    "change_request_confirm": "Show the exact requested operation once and obtain confirmation before applying one validated atomic maintenance batch. After success, regenerate veil.html and update existing sync targets.",
    "request_operation": "Operation: {value}",
    "request_term": "Source wording: {value}",
    "request_current": "Current preferred wording: {value}",
    "request_requested": "Requested preferred wording: {value}",
    "request_reason": "Reason: {value}",
    "show_alternatives": "Show alternatives",
    "count_registered": "{n} rules registered",
    "count_matching": "{n} rules matching",
    "copy_manual": "Clipboard access is unavailable. Copy this request manually:",
    "copy_manual_done": "Manual copy dialog opened.",
}


_HTML_UI_JA: dict[str, str] = {
    "lang": "ja",
    "title": "VEIL ルール台帳",
    "rulebook_title": "VEIL ルール台帳",
    "rulebook_description": "AIツールへ配布されている用語ルールを確認できます。この画面は正本を直接変更しません。",
    "generated_label": "生成日時",
    "rulebook_heading": "登録済みルール",
    "search_placeholder": "元の表現または推奨表現を検索...",
    "no_match": "一致するルールはありません。新しい表現を確認する場合は、下の「会話を確認する」を使ってください。",
    "empty_rulebook": "ルールはまだ登録されていません。VEILは、継続的な判断が必要な場合だけ確認します。",
    "actions_title": "操作",
    "actions_description": "意図的な確認または保守依頼にだけ使用します。通常のタスク終了時の確認は、インストール済みVEIL Skillが行います。",
    "review_title": "会話を確認する",
    "review_description": "復旧用の導線です。会話全文を、インストール済みVEIL Skillへの一つの依頼としてコピーします。",
    "review_label": "確認する会話の全文",
    "review_placeholder": "確認する会話をそのまま貼り付け...",
    "review_copy_btn": "確認依頼をコピー",
    "review_copied": "確認依頼をコピーしました。VEILがインストールされたAIチャットへ貼り付けてください。",
    "review_request_header": "次の会話全文に、インストール済みVEIL captureを実行してください。",
    "review_request_instruction": "根拠付き意味フレーム（contract v2）と独立したcritic確認を使ってください。自動処理の結果は表示せず、継続的な例外がある場合だけ一つにまとめて確認し、承認前に書き込まないでください。",
    "change_title": "ルール変更を依頼する",
    "change_description": "登録済みルールの「変更を依頼」を選んでください。依頼をコピーしただけでは変更されません。",
    "change_empty": "上のルールから「変更を依頼」を選んでください。",
    "selected_term_label": "元の表現: ",
    "selected_preferred_label": "現在の推奨表現: ",
    "change_intent_label": "依頼する操作",
    "change_option": "推奨表現を変更",
    "retire_option": "このルールを廃止",
    "requested_preferred_label": "新しい推奨表現",
    "change_reason_label": "理由",
    "change_reason_help": "任意です。簡潔に入力してください。",
    "change_copy_btn": "変更依頼をコピー",
    "cancel_btn": "キャンセル",
    "request_change_btn": "変更を依頼",
    "request_change_for": "{term} の変更を依頼",
    "change_missing": "新しい推奨表現を入力してください。",
    "change_copied": "変更依頼をコピーしました。VEILで確認した後にだけルールが変更されます。",
    "change_request_header": "次の依頼に、インストール済みVEILのルール保守処理を実行してください。",
    "change_request_confirm": "依頼内容を一度だけ明示して確認を取り、検証済みの原子的な保守バッチとして適用してください。成功後にveil.htmlを再生成し、既存の同期先を更新してください。",
    "request_operation": "操作: {value}",
    "request_term": "元の表現: {value}",
    "request_current": "現在の推奨表現: {value}",
    "request_requested": "新しい推奨表現: {value}",
    "request_reason": "理由: {value}",
    "show_alternatives": "代替表現を表示",
    "count_registered": "登録済みルール: {n}件",
    "count_matching": "一致するルール: {n}件",
    "copy_manual": "クリップボードを使用できません。次の依頼を手動でコピーしてください:",
    "copy_manual_done": "手動コピー画面を開きました。",
}


# Compatibility exports remain importable, but only English and Japanese are
# embedded in generated HTML until other locales have complete accepted copy.
_HTML_UI_KO = _HTML_UI_EN
_HTML_UI_ZH_HANS = _HTML_UI_EN
_HTML_UI_ZH_HANT = _HTML_UI_EN
_HTML_UI_AR = _HTML_UI_EN

_HTML_UI_BY_LANG: dict[str, dict[str, str]] = {
    "en": _HTML_UI_EN,
    "ja": _HTML_UI_JA,
}


def get_html_ui_for_lang(lang: str) -> dict[str, str]:
    key = str(lang or "en").lower().replace("_", "-")
    if key.startswith("ja"):
        key = "ja"
    else:
        key = "en"
    return dict(_HTML_UI_BY_LANG[key])
