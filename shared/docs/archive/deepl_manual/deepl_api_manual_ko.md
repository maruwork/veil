# DeepL API 시작 가이드

**대상：** DeepL API를 처음 사용하는 분
**플랜：** DeepL API Free（무료）
**작성일：** 2026-05-27

> **주의：** 이 가이드는 작성 시점의 정보를 기반으로 합니다. DeepL의 플랜·요금·절차는 예고 없이 변경될 수 있습니다. 등록 전에 반드시 공식 사이트（`https://www.deepl.com/pro-api`）및 공식 문서（`https://developers.deepl.com/docs`）에서 최신 정보를 확인하십시오.

---

## 1. DeepL API Free 개요

| 항목 | 내용 |
|---|---|
| 요금 | 무료 |
| 월간 번역 한도 | 500,000자（초과 시 다음 달까지 사용 불가） |
| API 엔드포인트 | `https://api-free.deepl.com` |
| API 키 구별 방법 | 키 끝에 `:fx` 표시 |
| 번역 데이터 처리 | 무료 플랜의 번역 내용은 DeepL 서비스 개선에 활용될 수 있음 |

**주의사항 1：** 무료 버전과 유료 버전의 엔드포인트가 다릅니다. 무료 버전은 반드시 `api-free.deepl.com`을 사용하십시오.

**주의사항 2：** DeepL API Free 플랜 구독 중에는 **브라우저 버전 및 데스크톱 앱 버전의 DeepL 번역을 사용할 수 없습니다**. 일반 DeepL 번역을 사용하려면 로그아웃하면 됩니다.

---

## 2. 계정 등록 및 API 키 취득

> **중요：** 현재 DeepL API Free는 **DeepL API Pro에서 다운그레이드하는 방식**으로만 취득할 수 있습니다. API Free에 직접 등록하는 것은 더 이상 불가능합니다. 아래 절차를 따르십시오.

### 1단계：API Pro 등록

1. `https://www.deepl.com/pro-api` 접속
2. 「Get started for free」또는 「Buy now」를 클릭하여 API Pro 플랜 등록
3. 이메일 주소·비밀번호·이름·주소 입력
4. 신용카드 정보를 입력하여 등록 완료
   - **이 시점에서 API Pro 요금이 발생합니다.** 즉시 다음 단계로 진행하십시오
   - **JCB 카드는 사용 불가.** VISA 또는 Mastercard를 준비하십시오
   - **3D Secure（본인 인증 서비스）**를 지원하는 카드가 필요합니다
   - **은행 이체는 불가.** 신용카드 또는 직불카드만 가능합니다

### 2단계：API Free로 다운그레이드

1. 로그인 후 `https://www.deepl.com/your-account/plan` 접속
2. 플랜 변경 메뉴에서 「다운그레이드」선택
3. API Free 플랜을 선택하고 확정
4. 다운그레이드 완료 후 API 키 끝에 `:fx`가 표시됩니다

> **주의：** 다운그레이드 전에 API Pro 요금이 발생한 경우, DeepL 취소 정책에 따라 계약 체결 후 14일 이내에 환불 신청이 가능합니다. 자세한 내용은 `https://support.deepl.com`을 참조하십시오.

### 3단계：API 키 확인

1. 로그인 후 `https://www.deepl.com/your-account/keys` 접속
2. 「API Keys」탭 열기
3. 자동 생성된 API 키 복사

API 키 예시：
```
279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

끝의 `:fx`가 무료 버전의 표시입니다.

---

## 3. API 키 관리

- **절대 공개하지 마십시오.** GitHub나 공개 코드에 포함해서는 안 됩니다.
- 환경 변수（`.env` 파일 등）에 저장하여 사용하는 것이 기본입니다.
- 유출된 경우 즉시 `https://www.deepl.com/your-account/keys`에서 무효화하고 새 키를 발급받으십시오.

---

## 4. 동작 확인

### curl 사용（터미널）

```bash
curl -X POST 'https://api-free.deepl.com/v2/translate' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": ["Hello, world!"],
    "target_lang": "KO"
  }'
```

성공하면 다음과 같은 JSON이 반환됩니다：

```json
{
  "translations": [
    {
      "detected_source_language": "EN",
      "text": "안녕하세요, 세계!"
    }
  ]
}
```

### Python으로 확인

```python
import urllib.request
import json

API_KEY = "YOUR_API_KEY_HERE"
ENDPOINT = "https://api-free.deepl.com/v2/translate"

payload = json.dumps({
    "text": ["Hello, world!"],
    "target_lang": "KO"
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
# 출력：안녕하세요, 세계!
```

---

## 5. 주요 언어 코드 목록

| 언어 | 코드 |
|---|---|
| 일본어 | `JA` |
| 영어（미국） | `EN-US` |
| 영어（영국） | `EN-GB` |
| 한국어 | `KO` |
| 중국어（간체） | `ZH-HANS` |
| 중국어（번체） | `ZH-HANT` |
| 독일어 | `DE` |
| 프랑스어 | `FR` |
| 스페인어 | `ES` |

전체 목록은 `https://developers.deepl.com/docs/resources/supported-languages`를 참조하십시오.

---

## 6. VEIL에 통합하기

`app.py` 상단에 환경 변수에서 API 키를 불러옵니다.

### .env 파일 생성

```
DEEPL_API_KEY=279a2e9d-83b3-c416-7e2d-f721593e42a0:fx
```

### app.py에 추가

```python
import os

DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY", "")
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"
```

### 번역 함수

```python
import urllib.request
import json

def translate(text, target_lang="KO"):
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

### 시작 시 API 키 전달

```bash
DEEPL_API_KEY=YOUR_KEY python app.py
```

---

## 7. 사용량 확인

API로 이번 달 남은 문자 수를 확인할 수 있습니다：

```bash
curl 'https://api-free.deepl.com/v2/usage' \
  --header 'Authorization: DeepL-Auth-Key YOUR_API_KEY_HERE'
```

응답：

```json
{
  "character_count": 12345,
  "character_limit": 500000
}
```

`character_count`는 이번 달 사용한 문자 수, `character_limit`는 한도（무료 버전은 500,000）입니다.

---

## 8. 자주 발생하는 오류

| 오류 | 원인 | 대처 방법 |
|---|---|---|
| `403 Forbidden` | API 키가 유효하지 않거나 잘못됨 | 키를 다시 확인. 무료 버전 키는 끝이 `:fx` |
| `456 Quota Exceeded` | 월간 문자 수 한도 초과 | 다음 달까지 기다리거나 유료 플랜으로 업그레이드 |
| `Connection refused` | 엔드포인트 오류 | 무료 버전：`api-free.deepl.com`，유료 버전：`api.deepl.com` |
| `400 Bad Request` | 요청 형식이 올바르지 않음 | `target_lang` 값 확인（예：`KO`、`EN-US`） |

---

## 9. 참고 링크

- 공식 문서：`https://developers.deepl.com/docs`
- API 키 관리：`https://www.deepl.com/your-account/keys`
- 지원 언어 목록：`https://developers.deepl.com/docs/resources/supported-languages`
- 사용량 확인：`https://api-free.deepl.com/v2/usage`
