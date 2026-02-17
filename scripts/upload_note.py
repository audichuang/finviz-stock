#!/usr/bin/env python3
"""
upload_note.py — 上傳報告到 Fast Note Sync Service

透過 REST API 將 markdown 報告上傳/更新到 Obsidian Vault。
環境變數（由 doppler 注入）:
  FAST_NOTE_URL    — 伺服器 URL (e.g. https://note.example.com)
  FAST_NOTE_TOKEN  — API Token
  FAST_NOTE_VAULT  — Vault 名稱 (e.g. Obsidian)

用法:
  doppler run -p finviz -c dev -- python3 scripts/upload_note.py <file.md>
  doppler run -p finviz -c dev -- python3 scripts/upload_note.py <file.md> --path "finviz-stock/daily_2026-02-17.md"
  echo "# content" | doppler run -p finviz -c dev -- python3 scripts/upload_note.py --stdin --path "finviz-stock/report.md"
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def upload_note(base_url: str, token: str, vault: str, path: str, content: str) -> dict:
    """上傳或更新筆記到 Fast Note Sync Service"""
    url = f"{base_url.rstrip('/')}/api/note"
    payload = json.dumps({
        "vault": vault,
        "path": path,
        "content": content,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": token,
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("status"):
                return result
            else:
                print(f"上傳失敗: {result.get('message', 'unknown error')}", file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="上傳報告到 Fast Note Sync")
    parser.add_argument("file", nargs="?", help="要上傳的 markdown 檔案")
    parser.add_argument("--stdin", action="store_true", help="從 stdin 讀取內容")
    parser.add_argument("--path", "-p", help="Vault 內的筆記路徑 (預設: finviz-stock/<filename>)")
    parser.add_argument("--vault", "-v", help="覆寫 Vault 名稱 (預設用環境變數)")
    args = parser.parse_args()

    # 環境變數
    base_url = os.environ.get("FAST_NOTE_URL")
    token = os.environ.get("FAST_NOTE_TOKEN")
    vault = args.vault or os.environ.get("FAST_NOTE_VAULT", "Obsidian")

    if not base_url or not token:
        print("錯誤: 需要設定 FAST_NOTE_URL 和 FAST_NOTE_TOKEN 環境變數", file=sys.stderr)
        print("請確認已用 doppler: doppler run -p finviz -c dev -- python3 scripts/upload_note.py ...", file=sys.stderr)
        sys.exit(1)

    # 讀取內容
    if args.stdin:
        content = sys.stdin.read()
        if not args.path:
            print("錯誤: 使用 --stdin 時必須指定 --path", file=sys.stderr)
            sys.exit(1)
        note_path = args.path
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        note_path = args.path or f"finviz-stock/{os.path.basename(args.file)}"
    else:
        parser.print_help()
        sys.exit(1)

    result = upload_note(base_url, token, vault, note_path, content)
    data = result.get("data", {})
    print(f"✅ 上傳成功: {note_path}", file=sys.stderr)
    print(f"   版本: {data.get('version', '?')} | ID: {data.get('id', '?')}", file=sys.stderr)


if __name__ == "__main__":
    main()
