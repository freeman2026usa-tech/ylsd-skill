"""读取公开仓库里的编号指令。list 列目录；get <编号> 取正文并核对 SHA-256。先试 GitHub，再试 Gitee，都不通用本机。"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_URLS = [
    "https://raw.githubusercontent.com/<用户名>/ylsd-skill/main/skills/ylsd/numbered-prompts",
    "https://gitee.com/<用户名>/ylsd-skill/raw/main/skills/ylsd/numbered-prompts",
]
ROOT = Path(__file__).resolve().parents[1] / "numbered-prompts"
CODE = re.compile(r"^[0-9]{3}$")
TITLE = re.compile(r"^# ([0-9]{3})｜(.+)$", re.M)
SECTIONS = ("## 用户要完成的事", "## 需要的输入", "## 执行步骤", "## 交付结果", "## 验收标准", "## 适用边界")


def fetch(path):
    for base in BASE_URLS:
        try:
            with urllib.request.urlopen(f"{base}/{path}", timeout=8) as r:
                return r.read(), base
        except Exception:
            continue
    return None, None


def load_catalog():
    raw, base = fetch("catalog.json")
    if raw is None:
        local = ROOT / "catalog.json"
        if local.is_file():
            return json.loads(local.read_text(encoding="utf-8")), "本机旧目录（联网失败）"
        return None, None
    place = "GitHub" if "github" in base else "Gitee"
    return json.loads(raw.decode("utf-8")), place


def main(argv):
    if len(argv) < 2 or argv[1] not in ("list", "get"):
        print("用法：numbered-prompts.py list | get <三位编号>")
        return 2
    catalog, place = load_catalog()
    if catalog is None:
        print("读不到编号目录")
        return 1
    items = catalog.get("items", [])
    if argv[1] == "list":
        print(f"{place} 当前共有 {len(items)} 个编号：")
        for it in sorted(items, key=lambda x: x["id"]):
            print(f"- /ylsd {it['id']}｜{it['title']}：{it['purpose']}")
        return 0
    if len(argv) < 3 or not CODE.match(argv[2]):
        print("编号必须是三位数字")
        return 2
    code = argv[2]
    item = next((it for it in items if it["id"] == code), None)
    if item is None:
        if place and place.startswith("本机"):
            print(f"本机目录里没有编号 {code}（联网没取到最新目录）")
        else:
            print(f"编号 {code} 没发布过")
        return 1
    body, _ = fetch(f"{code}/PROMPT.md")
    if body is None:
        local = ROOT / code / "PROMPT.md"
        if not local.is_file():
            print(f"读不到编号 {code} 的正文")
            return 1
        body = local.read_bytes()
    if hashlib.sha256(body).hexdigest() != item["sha256"]:
        print(f"编号 {code} 的正文和目录对不上，停止")
        return 1
    text = body.decode("utf-8")
    m = TITLE.search(text)
    if m is None or m.group(1) != code or any(s not in text for s in SECTIONS):
        print(f"编号 {code} 的正文结构不完整，停止")
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
