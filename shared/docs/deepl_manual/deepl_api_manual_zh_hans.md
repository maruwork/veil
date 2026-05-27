# DeepL API 入门指南

**适用对象：** 首次使用 DeepL API 的用户
**方案：** DeepL API Free（免费）
**创建日期：** 2026-05-27

> **注意：** 本指南依据撰写时的信息编制。DeepL 的方案、费用及操作步骤可能随时变更，恕不另行通知。注册前请务必前往官方网站（`https://www.deepl.com/pro-api`）及官方文档（`https://developers.deepl.com/docs`）确认最新信息。

---

## 1. DeepL API Free 概述

| 项目 | 内容 |
|---|---|
| 费用 | 免费 |
| 每月翻译上限 | 500,000 字符（超出后须等到下个月才能继续使用） |
| API 端点 | `https://api-free.deepl.com` |
| API 密钥识别方式 | 密钥末尾为 `:fx` |
| 翻译数据用途 | 免费版翻译内容可能用于改善 DeepL 服务 |

**注意事项 1：** 免费版与付费版的端点不同，免费版请务必使用 `api-free.deepl.com`。

**注意事项 2：** 订阅 DeepL API Free 方案期间，**浏览器版及桌面应用程序版的 DeepL 翻译将无法使用**。如需使用普通 DeepL 翻译，请先退出登录。

---

## 2. 账号注册与获取 API 密钥

> **重要：** 目前 DeepL API Free 仅能通过**从 DeepL API Pro 降级**的方式获取，已无法直接注册 API Free 方案。请按照以下步骤操作。

### 步骤一：注册 API Pro

1. 前往 `https://www.deepl.com/pro-api`
2. 点击「Get started for free」或「Buy now」，注册 API Pro 方案
3. 输入电子邮件地址、密码、姓名及地址
4. 输入信用卡信息以完成注册
   - **此时将产生 API Pro 费用**，请立即进行下一步骤
   - **不支持 JCB 卡**，请准备 VISA 或 Mastercard
   - 需使用支持 **3D Secure（身份验证服务）**的卡片
   - **不接受银行转账**，仅限信用卡或借记卡

### 步骤二：降级至 API Free

1. 登录后，前往 `https://www.deepl.com/your-account/plan`
2. 在方案变更菜单中选择「降级」
3. 选择 API Free 方案并确认
4. 降级完成后，API 密钥末尾将显示 `:fx`

> **注意：** 若降级前已产生 API Pro 费用，依 DeepL 取消政策，于签约后 14 天内可申请退款。详情请参阅 `https://support.deepl.com`。

### 步骤三：确认 API 密钥

1. 登录后，前往 `https://www.deepl.com/your-account/keys`
2. 打开「API Keys」标签页
3. 复制自动生成的 API 密钥

API 密钥示例：
```
279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

末尾的 `:fx` 为免费版的识别标志。

---

## 3. API 密钥管理

- **绝对不可公开。** 不得将其包含在 GitHub 或公开代码中。
- 基本做法是存储于环境变量（如 `.env` 文件）中使用。
- 若发生泄露，请立即前往 `https://www.deepl.com/your-account/keys` 将其停用并重新申请。

---

## 4. 动作确认

### 使用 curl（终端）

```bash
curl -X POST 'https://api-free.deepl.com/v2/translate' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": ["Hello, world!"],
    "target_lang": "ZH-HANS"
  }'
```

成功时将返回以下 JSON：

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

### 使用 Python 确认

```python
import urllib.request
import json

API_KEY = "YOUR_API_KEY_HERE"
ENDPOINT = "https://api-free.deepl.com/v2/translate"

payload = json.dumps({
    "text": ["Hello, world!"],
    "target_lang": "ZH-HANS"
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
# 输出：你好，世界！
```

---

## 5. 主要语言代码一览

| 语言 | 代码 |
|---|---|
| 日语 | `JA` |
| 英语（美国） | `EN-US` |
| 英语（英国） | `EN-GB` |
| 韩语 | `KO` |
| 中文（简体） | `ZH-HANS` |
| 中文（繁体） | `ZH-HANT` |
| 德语 | `DE` |
| 法语 | `FR` |
| 西班牙语 | `ES` |

完整列表请参阅 `https://developers.deepl.com/docs/resources/supported-languages`。

---

## 6. 集成至 VEIL

在 `app.py` 开头从环境变量载入 API 密钥。

### 创建 .env 文件

```
DEEPL_API_KEY=279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

### 在 app.py 中添加

```python
import os

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
```

### 翻译函数

```python
import urllib.request
import json

def translate(text, target_lang="ZH-HANS"):
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

### 启动时传入 API 密钥

```bash
DEEPL_API_KEY=YOUR_KEY python app.py
```

---

## 7. 确认使用量

可通过 API 确认当月剩余字符数：

```bash
curl 'https://api-free.deepl.com/v2/usage' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE'
```

返回内容：

```json
{
  "character_count": 12345,
  "character_limit": 500000
}
```

`character_count` 为本月已使用字符数，`character_limit` 为上限（免费版为 500,000）。

---

## 8. 常见错误

| 错误 | 原因 | 处理方式 |
|---|---|---|
| `403 Forbidden` | API 密钥无效或错误 | 重新确认密钥，免费版密钥末尾应为 `:fx` |
| `456 Quota Exceeded` | 已超出每月字符数上限 | 等到下个月或升级至付费方案 |
| `Connection refused` | 端点错误 | 免费版使用 `api-free.deepl.com`，付费版使用 `api.deepl.com` |
| `400 Bad Request` | 请求格式不正确 | 确认 `target_lang` 的值（例：`ZH-HANS`、`EN-US`） |

---

## 9. 参考链接

- 官方文档：`https://developers.deepl.com/docs`
- API 密钥管理：`https://www.deepl.com/your-account/keys`
- 支持语言一览：`https://developers.deepl.com/docs/resources/supported-languages`
- 使用量确认：`https://api-free.deepl.com/v2/usage`
