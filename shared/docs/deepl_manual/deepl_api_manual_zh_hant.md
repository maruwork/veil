# DeepL API 入門指南

**適用對象：** 首次使用 DeepL API 的使用者
**方案：** DeepL API Free（免費）
**建立日期：** 2026-05-27

> **注意：** 本指南依據撰寫時的資訊編製。DeepL 的方案、費用及操作步驟可能隨時變更，恕不另行通知。註冊前請務必至官方網站（`https://www.deepl.com/pro-api`）及官方文件（`https://developers.deepl.com/docs`）確認最新資訊。

---

## 1. DeepL API Free 概述

| 項目 | 內容 |
|---|---|
| 費用 | 免費 |
| 每月翻譯上限 | 500,000 字元（超過後須等至下個月才能繼續使用） |
| API 端點 | `https://api-free.deepl.com` |
| API 金鑰識別方式 | 金鑰末尾為 `:fx` |
| 翻譯資料用途 | 免費版翻譯內容可能用於改善 DeepL 服務 |

**注意事項 1：** 免費版與付費版的端點不同，免費版請務必使用 `api-free.deepl.com`。

**注意事項 2：** 訂閱 DeepL API Free 方案期間，**瀏覽器版及桌面應用程式版的 DeepL 翻譯將無法使用**。如需使用一般 DeepL 翻譯，請先登出帳號。

---

## 2. 帳號註冊與取得 API 金鑰

> **重要：** 目前 DeepL API Free 僅能透過**從 DeepL API Pro 降級**的方式取得，已無法直接註冊 API Free 方案。請依照以下步驟操作。

### 步驟一：註冊 API Pro

1. 前往 `https://www.deepl.com/pro-api`
2. 點選「Get started for free」或「Buy now」，註冊 API Pro 方案
3. 輸入電子郵件地址、密碼、姓名及地址
4. 輸入信用卡資訊以完成註冊
   - **此時將產生 API Pro 費用**，請立即進行下一步驟
   - **不支援 JCB 卡**，請備妥 VISA 或 Mastercard
   - 需使用支援 **3D Secure（身份驗證服務）**的卡片
   - **不接受銀行轉帳**，僅限信用卡或簽帳金融卡

### 步驟二：降級至 API Free

1. 登入後，前往 `https://www.deepl.com/your-account/plan`
2. 在方案變更選單中選擇「降級」
3. 選取 API Free 方案並確認
4. 降級完成後，API 金鑰末尾將顯示 `:fx`

> **注意：** 若降級前已產生 API Pro 費用，依 DeepL 取消政策，於簽約後 14 天內可申請退款。詳情請參閱 `https://support.deepl.com`。

### 步驟三：確認 API 金鑰

1. 登入後，前往 `https://www.deepl.com/your-account/keys`
2. 開啟「API Keys」分頁
3. 複製自動產生的 API 金鑰

API 金鑰範例：
```
279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

末尾的 `:fx` 為免費版的識別標誌。

---

## 3. API 金鑰管理

- **絕對不可公開。** 不得將其包含在 GitHub 或公開程式碼中。
- 基本做法是儲存於環境變數（如 `.env` 檔案）中使用。
- 若發生洩漏，請立即至 `https://www.deepl.com/your-account/keys` 將其停用並重新申請。

---

## 4. 動作確認

### 使用 curl（終端機）

```bash
curl -X POST 'https://api-free.deepl.com/v2/translate' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": ["Hello, world!"],
    "target_lang": "ZH-HANT"
  }'
```

成功時將回傳以下 JSON：

```json
{
  "translations": [
    {
      "detected_source_language": "EN",
      "text": "你好，世界！"
    }
  ]
}
```

### 使用 Python 確認

```python
import urllib.request
import json

API_KEY = "YOUR_API_KEY_HERE"
ENDPOINT = "https://api-free.deepl.com/v2/translate"

payload = json.dumps({
    "text": ["Hello, world!"],
    "target_lang": "ZH-HANT"
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
# 輸出：你好，世界！
```

---

## 5. 主要語言代碼一覽

| 語言 | 代碼 |
|---|---|
| 日語 | `JA` |
| 英語（美國） | `EN-US` |
| 英語（英國） | `EN-GB` |
| 韓語 | `KO` |
| 中文（簡體） | `ZH-HANS` |
| 中文（繁體） | `ZH-HANT` |
| 德語 | `DE` |
| 法語 | `FR` |
| 西班牙語 | `ES` |

完整清單請參閱 `https://developers.deepl.com/docs/resources/supported-languages`。

---

## 6. 整合至 VEIL

在 `app.py` 開頭從環境變數載入 API 金鑰。

### 建立 .env 檔案

```
DEEPL_API_KEY=279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

### 在 app.py 中新增

```python
import os

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
```

### 翻譯函式

```python
import urllib.request
import json

def translate(text, target_lang="ZH-HANT"):
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

### 啟動時傳入 API 金鑰

```bash
DEEPL_API_KEY=YOUR_KEY python app.py
```

---

## 7. 確認使用量

可透過 API 確認當月剩餘字元數：

```bash
curl 'https://api-free.deepl.com/v2/usage' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE'
```

回應內容：

```json
{
  "character_count": 12345,
  "character_limit": 500000
}
```

`character_count` 為本月已使用字元數，`character_limit` 為上限（免費版為 500,000）。

---

## 8. 常見錯誤

| 錯誤 | 原因 | 處理方式 |
|---|---|---|
| `403 Forbidden` | API 金鑰無效或錯誤 | 重新確認金鑰，免費版金鑰末尾應為 `:fx` |
| `456 Quota Exceeded` | 已超過每月字元數上限 | 等至下個月或升級至付費方案 |
| `Connection refused` | 端點錯誤 | 免費版使用 `api-free.deepl.com`，付費版使用 `api.deepl.com` |
| `400 Bad Request` | 請求格式不正確 | 確認 `target_lang` 的值（例：`ZH-HANT`、`EN-US`） |

---

## 9. 參考連結

- 官方文件：`https://developers.deepl.com/docs`
- API 金鑰管理：`https://www.deepl.com/your-account/keys`
- 支援語言一覽：`https://developers.deepl.com/docs/resources/supported-languages`
- 使用量確認：`https://api-free.deepl.com/v2/usage`
