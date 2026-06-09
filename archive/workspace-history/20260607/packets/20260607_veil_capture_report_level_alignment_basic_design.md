# VEIL Capture Report Level Alignment Basic Design

## 1. Current Gap

- 採用語の候補列挙はある
- どれが `必須 / 推奨 / 観察` かが report から見えない
- `保留` と `観察` の差も report では弱い

## 2. Target Format

```text
採用:
- [必須] current state → 今の状態（候補1）
- [推奨] current issue → 現在の課題（候補1）
- [観察] close path → 完了経路（候補1）

保留:
- workflow label

同期:
- sync 完了

返答前検査:
- main task の日本語文章は別途 lint 対象
```

## 3. Design Direction

- 候補2 / 候補3 は必要時のみ残す
- level は採用語の先頭で見せる
- `観察` は採用済みでも hard gate ではないと明示する
