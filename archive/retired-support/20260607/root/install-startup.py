#!/usr/bin/env python3
"""
VEIL サーバーを Windows ログイン時に自動起動するタスクを登録する

使い方:
  python shared/runtime/install-startup.py          # 自動起動を登録
  python shared/runtime/install-startup.py --remove # 登録を解除
  python shared/runtime/install-startup.py --status # 登録状態を確認
"""

import sys
import os
import subprocess
from pathlib import Path

TASK_NAME = "VEIL Server"
ROOT = Path(__file__).resolve().parents[2]
APP_PATH = str(ROOT / "archive" / "retired-support" / "20260607" / "root" / "app.py")


def get_pythonw():
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pythonw if os.path.exists(pythonw) else sys.executable


def cmd_install():
    pythonw = get_pythonw()
    tr = f'"{pythonw}" "{APP_PATH}"'
    result = subprocess.run(
        ["schtasks", "/Create",
         "/TN", TASK_NAME,
         "/TR", tr,
         "/SC", "ONLOGON",
         "/RL", "LIMITED",
         "/F"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"登録完了: 次回Windowsログイン時から自動起動します")
        print(f"  実行ファイル: {pythonw}")
        print(f"  スクリプト: {APP_PATH}")
        ans = input("\n今すぐ起動しますか？ [y/N]: ").strip().lower()
        if ans == "y":
            subprocess.run(["schtasks", "/Run", "/TN", TASK_NAME])
            print("起動しました")
    else:
        print(f"登録失敗:\n{result.stderr}")
        print("\n管理者権限で実行してみてください:")
        print("  右クリック → 管理者として実行")


def cmd_remove():
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("自動起動の登録を解除しました")
    else:
        print(f"解除失敗（未登録の可能性があります）:\n{result.stderr}")


def cmd_status():
    result = subprocess.run(
        ["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("未登録です")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        cmd_install()
    elif args[0] == "--remove":
        cmd_remove()
    elif args[0] == "--status":
        cmd_status()
    else:
        print(__doc__)
