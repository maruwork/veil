# VEIL seed 語彙整合 実装計画

Status: Draft
Date: 2026-06-07

## 1. ゴール

`app.py` の seed 語彙を、少数で高確度の集合へ整理する。

## 2. 道のり

1. `SEEDS` を監査する
2. 残す語と外す語を決める
3. `app.py` を更新する
4. seed の位置づけを文書へ補足する
5. py_compile で確認する

## 3. タスク

1. `SEEDS` を最小限へ整理する
2. `docs/manual.html` に helper seed の位置づけを足す
3. `docs/veil-design.md` に seed 方針を足す
4. `python -m py_compile app.py` を行う

## 4. 検査

- `python -m py_compile app.py`
- seed 一覧を読み直し、不自然な `project 固有` / 曖昧語が消えている

## 5. 完了の定義

- 新規 DB の初期状態が説明しやすくなる
- 今の段階導入ルールと seed が逆向きでなくなる
