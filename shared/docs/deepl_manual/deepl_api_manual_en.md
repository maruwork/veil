# DeepL API Getting Started Guide

**Target:** First-time DeepL API users
**Plan:** DeepL API Free
**Created:** 2026-05-27

> **Notice:** This guide is based on information available at the time of writing. DeepL's plans, pricing, and procedures may change without notice. Always check the official website (`https://www.deepl.com/pro-api`) and documentation (`https://developers.deepl.com/docs`) for the latest information before registering.

---

## 1. Overview of DeepL API Free

| Item | Details |
|---|---|
| Price | Free |
| Monthly character limit | 500,000 characters (unavailable until next month if exceeded) |
| API endpoint | `https://api-free.deepl.com` |
| How to identify your API key | Key ends with `:fx` |
| Translation data usage | Free plan translations may be used to improve DeepL services |

**Note 1:** The endpoint differs between the free and paid plans. Always use `api-free.deepl.com` for the free plan.

**Note 2:** While subscribed to DeepL API Free, **the browser-based and desktop app versions of DeepL are unavailable**. Log out to use regular DeepL translation.

---

## 2. Account Registration and API Key Acquisition

> **Important:** DeepL API Free can currently only be obtained by **downgrading from DeepL API Pro**. Direct registration for API Free is no longer available. Follow the steps below.

### Step 1: Register for API Pro

1. Go to `https://www.deepl.com/pro-api`
2. Click "Get started for free" or "Buy now" to register for the API Pro plan
3. Enter your email address, password, name, and address
4. Enter your credit card information to complete registration
   - **API Pro charges apply at this point.** Proceed to the next step immediately
   - **JCB cards are not accepted.** Use VISA or Mastercard
   - A card with **3D Secure (identity verification)** support is required
   - **Bank transfers are not accepted.** Credit or debit cards only

### Step 2: Downgrade to API Free

1. After logging in, go to `https://www.deepl.com/your-account/plan`
2. Select "Downgrade" from the plan change menu
3. Select the API Free plan and confirm
4. Once the downgrade is complete, your API key will end with `:fx`

> **Note:** If API Pro charges have been incurred before downgrading, a refund request may be possible within 14 days of signing up, per DeepL's cancellation policy. See `https://support.deepl.com` for details.

### Step 3: Retrieve Your API Key

1. After logging in, go to `https://www.deepl.com/your-account/keys`
2. Open the "API Keys" tab
3. Copy the auto-generated API key

Example API key:
```
279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

The `:fx` suffix identifies the free plan.

---

## 3. Managing Your API Key

- **Never make it public.** Do not include it in GitHub repos or public code.
- Store it in an environment variable (e.g., `.env` file).
- If leaked, immediately invalidate it and generate a new one at `https://www.deepl.com/your-account/keys`.

---

## 4. Testing the API

### Using curl (terminal)

```bash
curl -X POST 'https://api-free.deepl.com/v2/translate' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": ["Hello, world!"],
    "target_lang": "JA"
  }'
```

A successful response looks like this:

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

### Using Python

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
# Output: こんにちは、世界！
```

---

## 5. Common Language Codes

| Language | Code |
|---|---|
| Japanese | `JA` |
| English (US) | `EN-US` |
| English (UK) | `EN-GB` |
| Korean | `KO` |
| Chinese (Simplified) | `ZH-HANS` |
| Chinese (Traditional) | `ZH-HANT` |
| German | `DE` |
| French | `FR` |
| Spanish | `ES` |

See `https://developers.deepl.com/docs/resources/supported-languages` for the full list.

---

## 6. Integrating with VEIL

Load the API key from an environment variable at the top of `app.py`.

### Create a .env file

```
DEEPL_API_KEY=279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

### Add to app.py

```python
import os

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
```

### Translation function

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

### Pass the API key on startup

```bash
DEEPL_API_KEY=YOUR_KEY python app.py
```

---

## 7. Checking Usage

Check remaining monthly characters via API:

```bash
curl 'https://api-free.deepl.com/v2/usage' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE'
```

Response:

```json
{
  "character_count": 12345,
  "character_limit": 500000
}
```

`character_count` is the number of characters used this month; `character_limit` is the cap (500,000 for the free plan).

---

## 8. Common Errors

| Error | Cause | Fix |
|---|---|---|
| `403 Forbidden` | Invalid or incorrect API key | Re-check the key. Free plan keys end with `:fx` |
| `456 Quota Exceeded` | Monthly character limit exceeded | Wait until next month or upgrade to a paid plan |
| `Connection refused` | Wrong endpoint | Free plan: `api-free.deepl.com`; Paid plan: `api.deepl.com` |
| `400 Bad Request` | Incorrect request format | Check the `target_lang` value (e.g., `JA`, `EN-US`) |

---

## 9. Reference Links

- Official documentation: `https://developers.deepl.com/docs`
- API key management: `https://www.deepl.com/your-account/keys`
- Supported languages: `https://developers.deepl.com/docs/resources/supported-languages`
- Usage check: `https://api-free.deepl.com/v2/usage`
