# DeepL API 利用開始マニュアル

**対象：** DeepL APIを初めて使う方  
**プラン：** DeepL API Free（無料）  
**作成日：** 2026-05-27

> **注意：** 本マニュアルは作成時点の情報に基づいています。DeepLのプラン・料金・手順は予告なく変更される場合があります。登録前に必ず公式サイト（`https://www.deepl.com/pro-api`）および公式ドキュメント（`https://developers.deepl.com/docs`）で最新情報をご確認ください。

---

## 1. DeepL API Free の概要

| 項目 | 内容 |
|---|---|
| 料金 | 無料 |
| 月間翻訳上限 | 500,000文字（超過した場合は翌月まで使用不可） |
| APIエンドポイント | `https://api-free.deepl.com` |
| APIキーの見分け方 | キーの末尾が `:fx` |
| 翻訳データの扱い | 無料版はDeepLのサービス改善に使用される可能性あり |

**注意1：** 無料版と有料版でエンドポイントが異なる。無料版は必ず `api-free.deepl.com` を使う。

**注意2：** DeepL API Freeプランに加入中は、**ブラウザ版・デスクトップアプリ版のDeepL翻訳が使用できなくなる**。通常のDeepL翻訳を使いたい場合はログアウトすれば利用可能。

---

## 2. アカウント登録とAPIキーの取得

> **重要：** DeepL API Freeは現在、**DeepL API Proからのダウングレード経由でのみ**取得できる。直接API Freeに登録することはできなくなっている。以下の手順に従うこと。

### ステップ1：API Proに登録する

1. `https://www.deepl.com/pro-api` にアクセス
2. 「Get started for free」または「Buy now」からAPI Proプランに登録
3. メールアドレス・パスワード・氏名・住所を入力
4. クレジットカード情報を入力して登録を完了する
   - この時点では**API Proの料金が発生する**。すぐに次のステップへ進むこと
   - **JCBカードは使用不可。** VISAまたはMastercardを用意すること
   - **3Dセキュア（本人認証サービス）**に対応したカードが必要
   - **銀行振込は不可。** クレジットカードまたはデビットカードのみ

### ステップ2：API Freeにダウングレードする

1. ログイン後、`https://www.deepl.com/your-account/plan` にアクセス
2. プラン変更メニューから「ダウングレード」を選択
3. API Freeプランを選択して確定する
4. ダウングレードが完了するとAPIキーの末尾が `:fx` になる

> **注意：** ダウングレード前にAPI Proの料金が発生した場合、DeepLのキャンセルポリシーに従い契約締結から14日以内であれば返金申請が可能。詳細は `https://support.deepl.com` を参照。

### ステップ3：APIキーの確認

1. ログイン後、`https://www.deepl.com/your-account/keys` にアクセス
2. 「API Keys」タブを開く
3. 自動生成されたAPIキーをコピーする

APIキーの例：
```
279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

末尾の `:fx` が無料版の印。

---

## 3. APIキーの管理

- **絶対に公開しない。** GitHubや公開コードに含めてはいけない。
- 環境変数（`.env`ファイル等）に保存して使うのが基本。
- 漏洩した場合は `https://www.deepl.com/your-account/keys` から即座に無効化して新しいキーを発行できる。

---

## 4. 動作確認

### curlで確認（ターミナル）

```bash
curl -X POST 'https://api-free.deepl.com/v2/translate' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": ["Hello, world!"],
    "target_lang": "JA"
  }'
```

成功すると以下のようなJSONが返ってくる：

```json
{
  "translations": [
    {
      "detected_source_language": "EN",
      "text": "こんにちは、世界！"
    }
  ]
}
```

### Pythonで確認

```python
import urllib.request
import json

API_KEY = "YOUR_API_KEY_HERE"
ENDPOINT = "https://api-free.deepl.com/v2/translate"

payload = json.dumps({
    "text": ["Hello, world!"],
    "target_lang": "JA"
}).encode()

req = urllib.request.Request(
    ENDPOINT,
    data=payload,
    headers={
        "Authorization": f"DeepL-Auth-Key {API_KEY}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(req) as res:
    result = json.loads(res.read())
    print(result["translations"][0]["text"])
# → こんにちは、世界！
```

---

## 5. 主な言語コード一覧

| 言語 | コード |
|---|---|
| 日本語 | `JA` |
| 英語（米国） | `EN-US` |
| 英語（英国） | `EN-GB` |
| 韓国語 | `KO` |
| 中国語（簡体） | `ZH-HANS` |
| 中国語（繁体） | `ZH-HANT` |
| ドイツ語 | `DE` |
| フランス語 | `FR` |
| スペイン語 | `ES` |

完全なリストは `https://developers.deepl.com/docs/resources/supported-languages` を参照。

---

## 6. VEILへの組み込み方

`app.py` の冒頭に環境変数からAPIキーを読み込む。

### .envファイルを作成

```
DEEPL_API_KEY=279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

### app.pyに追記

```python
import os

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
```

### 翻訳関数

```python
import urllib.request
import json

def translate(text, target_lang="JA"):
    payload = json.dumps({
        "text": [text],
        "target_lang": target_lang
    }).encode()

    req = urllib.request.Request(
        DEEPL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read())
        return result["translations"][0]["text"]
```

### 起動時にAPIキーを渡す

```bash
DEEPL_API_KEY=YOUR_KEY python app.py
```

---

## 7. 使用量の確認

月間残り文字数をAPIで確認できる：

```bash
curl 'https://api-free.deepl.com/v2/usage' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE'
```

レスポンス：

```json
{
  "character_count": 12345,
  "character_limit": 500000
}
```

`character_count` が今月の使用済み文字数、`character_limit` が上限（無料版は500,000）。

---

## 8. よくあるエラー

| エラー | 原因 | 対処 |
|---|---|---|
| `403 Forbidden` | APIキーが無効または間違っている | キーを再確認。無料版キーは末尾が `:fx` |
| `456 Quota Exceeded` | 月間文字数上限超過 | 翌月まで待つか有料プランに移行 |
| `Connection refused` | エンドポイントが間違っている | 無料版は `api-free.deepl.com`、有料版は `api.deepl.com` |
| `400 Bad Request` | リクエスト形式が正しくない | `target_lang` の値を確認（例：`JA`、`EN-US`） |

---

## 9. 参考リンク

- 公式ドキュメント：`https://developers.deepl.com/docs`
- APIキー管理：`https://www.deepl.com/your-account/keys`
- 対応言語一覧：`https://developers.deepl.com/docs/resources/supported-languages`
- 使用量確認：`https://api-free.deepl.com/v2/usage`
