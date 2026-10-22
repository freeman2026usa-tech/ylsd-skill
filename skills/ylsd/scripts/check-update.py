"""查有没有新版：一天最多联网一次读公开仓库的 UPDATE.json，有新版打一行提醒，没有就什么都不打。

用法：python check-update.py <本机版本号>
任何错误都静默退出，不影响入口干活。先试 GitHub，再试 Gitee。
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

URLS = [
    "https://raw.githubusercontent.com/<用户名>/ylsd-skill/main/UPDATE.json",
    "https://gitee.com/<用户名>/ylsd-skill/raw/main/UPDATE.json",
]
CACHE = Path.home() / ".ylsd" / "update_check_at"
TTL = 86400
VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def higher(remote, local):
    return tuple(int(x) for x in remote.split(".")) > tuple(int(x) for x in local.split("."))


def main(argv):
    if len(argv) < 2 or not VERSION.match(argv[1]):
        return 0
    local = argv[1]
    now = int(time.time())
    try:
        if CACHE.is_file():
            last = int(CACHE.read_text(encoding="utf-8").strip() or 0)
            if 0 <= now - last < TTL:
                return 0
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(str(now), encoding="utf-8")
    except Exception:
        return 0
    data = None
    for url in URLS:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
                break
        except Exception:
            continue
    if not isinstance(data, dict):
        return 0
    remote = data.get("version", "")
    notice = str(data.get("notice", "")).strip()
    if not isinstance(remote, str) or not VERSION.match(remote):
        return 0
    if not (1 <= len(notice) <= 80) or any(c in notice for c in "\r\n\t"):
        return 0
    if higher(remote, local):
        print(f"ylsd-skill v{remote}：{notice} 回复 1，我现在帮你更新。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
